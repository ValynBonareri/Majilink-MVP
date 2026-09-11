# TerraRisk MVP

Starter project for the Kenya asset-level climate/flood risk prototype.

## Setup
From the TerraRisk folder:

    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    python -m pip install -r requirements.txt

## Test CHIRPS pipeline
The default configuration downloads 2025 only:

    python run_pipeline.py

Outputs:
- data/processed/rainfall/nairobi_rainfall.csv
- data/processed/rainfall/nairobi_rainfall_summary.csv

## Run dashboard

    streamlit run dashboard/app.py

The dashboard currently uses mock data. Connect the real risk engine/API during integration.

## Important
Risk 1–4 classifications and recommendations are prototype decision-support classifications, not Kenyan regulatory flood classifications or engineering determinations.

## Frontend Release 1

The dashboard has been refactored into reusable components and currently uses `dashboard/mock_data.json`.

Run it from the TerraRisk project folder:

    streamlit run dashboard/app.py

This release includes:
- TerraRisk branded application shell
- Property input form
- Mock assessment loading
- Overall Risk 1–4 display
- Flood, rainfall, terrain and waterway risk cards
- Property overview and metrics
- Key findings
- Decision guidance
- Data & methodology section

The function `build_assessment_for_property()` is the temporary frontend adapter. It is the intended integration point for the real risk engine/API later.
