from pathlib import Path
import numpy as np
import tifffile


FLOOD_FILES = {
    "10yr": "converted_10yr.tif",
    "25yr": "converted_25yr.tif",
    "50yr": "converted_50yr.tif",
    "100yr": "converted_100yr.tif",
}

def get_flood_directory():
    return (
        Path(__file__).resolve().parent.parent
        / "data"
        / "raw"
        / "flood"
    )


def get_raster_coordinates(tif):
    tags = tif.pages[0].tags

    scale_tag = tags.get("ModelPixelScaleTag")
    tiepoint_tag = tags.get("ModelTiepointTag")

    if scale_tag is None or tiepoint_tag is None:
        raise ValueError(
            "Flood raster is missing GeoTIFF coordinate metadata."
        )

    scale = scale_tag.value
    tiepoint = tiepoint_tag.value

    pixel_width = float(scale[0])
    pixel_height = float(scale[1])

    origin_x = float(tiepoint[3])
    origin_y = float(tiepoint[4])

    return pixel_width, pixel_height, origin_x, origin_y


def analyze_flood_raster(
    raster_path,
    latitude,
    longitude,
    neighborhood_size=5,
):
    with tifffile.TiffFile(raster_path) as tif:
        data = tif.asarray().astype(float)

        pixel_width, pixel_height, origin_x, origin_y = (
            get_raster_coordinates(tif)
        )

    height, width = data.shape

    col = int((longitude - origin_x) / pixel_width)
    row = int((origin_y - latitude) / pixel_height)

    if row < 0 or row >= height or col < 0 or col >= width:
        raise ValueError(
            f"Coordinate ({latitude}, {longitude}) "
            "is outside flood raster coverage."
        )

    half = neighborhood_size // 2

    row_start = max(row - half, 0)
    row_end = min(row + half + 1, height)

    col_start = max(col - half, 0)
    col_end = min(col + half + 1, width)

    neighborhood = data[
        row_start:row_end,
        col_start:col_end,
    ]

    neighborhood[neighborhood < 0] = np.nan

    property_depth = float(data[row, col])

    if not np.isfinite(property_depth) or property_depth < 0:
        property_depth = 0.0

    valid = neighborhood[np.isfinite(neighborhood)]

    if valid.size == 0:
        maximum_depth = 0.0
        average_depth = 0.0
        flooded_cells = 0
        total_cells = 0
    else:
        maximum_depth = float(np.max(valid))
        average_depth = float(np.mean(valid))
        flooded_cells = int(np.sum(valid > 0))
        total_cells = int(valid.size)

    flooded_percentage = (
        flooded_cells / total_cells * 100
        if total_cells > 0
        else 0.0
    )

    return {
        "property_depth_m": round(property_depth, 3),
        "maximum_nearby_depth_m": round(maximum_depth, 3),
        "average_nearby_depth_m": round(average_depth, 3),
        "flooded_cells": flooded_cells,
        "total_cells": total_cells,
        "flooded_percentage": round(flooded_percentage, 2),
    }


def classify_flood_risk(analysis):
    property_depth = analysis["property_depth_m"]
    maximum_depth = analysis["maximum_nearby_depth_m"]

    if property_depth >= 1.0 or maximum_depth >= 1.0:
        level = 4
        score = 100
        label = "VERY HIGH"
    elif property_depth >= 0.5 or maximum_depth >= 0.5:
        level = 3
        score = 75
        label = "HIGH"
    elif property_depth > 0 or maximum_depth > 0:
        level = 2
        score = 50
        label = "ELEVATED"
    else:
        level = 1
        score = 25
        label = "LOW"

    return {
        "level": level,
        "score": score,
        "label": label,
    }


def assess_flood_risk(latitude, longitude):
    flood_directory = get_flood_directory()
    results = {}

    for return_period, filename in FLOOD_FILES.items():
        raster_path = flood_directory / filename

        if not raster_path.exists():
            raise FileNotFoundError(
                f"Flood raster not found: {raster_path}"
            )

        analysis = analyze_flood_raster(
            raster_path,
            latitude,
            longitude,
        )

        risk = classify_flood_risk(analysis)

        results[return_period] = {
            "analysis": analysis,
            "rating": risk["label"],
            "score": risk["score"],
        }

    return results