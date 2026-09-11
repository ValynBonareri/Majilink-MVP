import pandas as pd
from pathlib import Path


def assess_rainfall_risk(latitude, longitude, csv_path):
    csv_path = Path(csv_path)

    if not csv_path.exists():
        raise FileNotFoundError(
            f"Rainfall dataset not found: {csv_path}"
        )

    df = pd.read_csv(csv_path)

    if df.empty:
        raise ValueError("Rainfall dataset is empty.")

    df["distance"] = (
        (df["latitude"] - latitude) ** 2
        + (df["longitude"] - longitude) ** 2
    ) ** 0.5

    closest = df.loc[df["distance"].idxmin()]

    rainfall = df[
        (df["latitude"] == closest["latitude"])
        & (df["longitude"] == closest["longitude"])
    ].copy()

    annual_rainfall = rainfall["rainfall_mm"].sum()
    max_monthly = rainfall["rainfall_mm"].max()

    if max_monthly < 100:
        risk_level = 1
        risk_score = 25
        risk_label = "LOW"
    elif max_monthly < 200:
        risk_level = 2
        risk_score = 50
        risk_label = "ELEVATED"
    elif max_monthly < 300:
        risk_level = 3
        risk_score = 75
        risk_label = "HIGH"
    else:
        risk_level = 4
        risk_score = 100
        risk_label = "VERY HIGH"

    return {
        "latitude": float(closest["latitude"]),
        "longitude": float(closest["longitude"]),
        "annual_rainfall_mm": round(float(annual_rainfall), 2),
        "maximum_monthly_rainfall_mm": round(float(max_monthly), 2),
        "rainfall_risk": {
            "level": risk_level,
            "score": risk_score,
            "label": risk_label,
        },
    }