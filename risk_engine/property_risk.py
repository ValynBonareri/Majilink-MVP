import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import PROCESSED_DIR

from risk_engine.rainfall_risk import assess_rainfall_risk
from risk_engine.terrain_risk import assess_terrain_risk
from risk_engine.flood_risk import assess_flood_risk


def calculate_overall_risk(
    rainfall_result,
    terrain_result,
    flood_result
):
    rainfall_score = rainfall_result["rainfall_risk"]["score"]
    terrain_score = terrain_result["terrain_risk"]["score"]

    flood_scores = [
        result["score"]
        for result in flood_result.values()
    ]

    flood_score = max(flood_scores)

    overall_score = round(
        rainfall_score * 0.50
        + terrain_score * 0.25
        + flood_score * 0.25
    )

    if overall_score <= 25:
        risk_level = 1
        risk_label = "LOW"
    elif overall_score <= 50:
        risk_level = 2
        risk_label = "ELEVATED"
    elif overall_score <= 75:
        risk_level = 3
        risk_label = "HIGH"
    else:
        risk_level = 4
        risk_label = "VERY HIGH"

    return {
        "score": overall_score,
        "level": risk_level,
        "label": risk_label,
        "components": {
            "rainfall_score": rainfall_score,
            "terrain_score": terrain_score,
            "flood_score": flood_score,
        }
    }


def assess_property(latitude, longitude):

    rainfall = assess_rainfall_risk(
        latitude,
        longitude,
        PROCESSED_DIR / "nairobi_rainfall.csv"
    )

    terrain = assess_terrain_risk(
        latitude,
        longitude
    )

    flood = assess_flood_risk(
        latitude,
        longitude
    )

    overall = calculate_overall_risk(
        rainfall,
        terrain,
        flood
    )

    return {
        "location": {
            "latitude": latitude,
            "longitude": longitude,
        },
        "rainfall": rainfall,
        "terrain": terrain,
        "flood": flood,
        "overall": overall,
    }