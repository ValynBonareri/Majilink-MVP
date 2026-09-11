from pathlib import Path
import numpy as np
import tifffile


def find_dem():
    base_dir = Path(__file__).resolve().parent.parent
    dem_dir = base_dir / "data" / "raw" / "cop_dem"

    dem_files = list(dem_dir.rglob("*_DEM.tif"))

    dem_files = [
        path for path in dem_files
        if "\\DEM\\" in str(path) or "/DEM/" in str(path)
    ]

    if not dem_files:
        raise FileNotFoundError(
            f"No Copernicus DEM GeoTIFF found in {dem_dir}"
        )

    return dem_files[0]


def read_dem_metadata(tif):
    tags = tif.pages[0].tags

    scale_tag = tags.get("ModelPixelScaleTag")
    tiepoint_tag = tags.get("ModelTiepointTag")

    if scale_tag is None or tiepoint_tag is None:
        raise ValueError("DEM is missing GeoTIFF coordinate metadata.")

    scale = scale_tag.value
    tiepoint = tiepoint_tag.value

    pixel_width = float(scale[0])
    pixel_height = float(scale[1])

    origin_x = float(tiepoint[3])
    origin_y = float(tiepoint[4])

    return pixel_width, pixel_height, origin_x, origin_y


def calculate_slope(elevation, pixel_width, pixel_height, latitude):
    meters_per_degree_lat = 111_320
    meters_per_degree_lon = (
        111_320 * np.cos(np.radians(latitude))
    )

    dx = pixel_width * meters_per_degree_lon
    dy = pixel_height * meters_per_degree_lat

    gradient_y, gradient_x = np.gradient(
        elevation.astype(float),
        dy,
        dx,
    )

    slope_radians = np.arctan(
        np.sqrt(gradient_x ** 2 + gradient_y ** 2)
    )

    return np.degrees(slope_radians)


def assess_terrain_risk(latitude, longitude):
    dem_path = find_dem()

    with tifffile.TiffFile(dem_path) as tif:
        elevation_data = tif.asarray()

        pixel_width, pixel_height, origin_x, origin_y = (
            read_dem_metadata(tif)
        )

    height, width = elevation_data.shape

    # Copernicus DEM is north-up.
    col = int((longitude - origin_x) / pixel_width)
    row = int((origin_y - latitude) / pixel_height)

    if row < 0 or row >= height or col < 0 or col >= width:
        raise ValueError(
            "The requested coordinate is outside the DEM coverage."
        )

    elevation = float(elevation_data[row, col])

    if not np.isfinite(elevation):
        raise ValueError(
            "No valid DEM elevation exists at this location."
        )

    row_start = max(row - 1, 0)
    row_end = min(row + 2, height)
    col_start = max(col - 1, 0)
    col_end = min(col + 2, width)

    elevation_window = elevation_data[
        row_start:row_end,
        col_start:col_end,
    ]

    if elevation_window.shape == (3, 3):
        local_slope = calculate_slope(
            elevation_window,
            pixel_width,
            pixel_height,
            latitude,
        )

        centre_slope = local_slope[1, 1]
    else:
        centre_slope = 0.0

    if centre_slope < 2:
        risk_level = 1
        risk_score = 25
        risk_label = "LOW"
    elif centre_slope < 5:
        risk_level = 2
        risk_score = 50
        risk_label = "ELEVATED"
    elif centre_slope < 10:
        risk_level = 3
        risk_score = 75
        risk_label = "HIGH"
    else:
        risk_level = 4
        risk_score = 100
        risk_label = "VERY HIGH"

    return {
        "latitude": latitude,
        "longitude": longitude,
        "elevation_m": round(elevation, 2),
        "slope_degrees": round(float(centre_slope), 2),
        "terrain_risk": {
            "level": risk_level,
            "score": risk_score,
            "label": risk_label,
        },
    }