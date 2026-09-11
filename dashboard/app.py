import json
from pathlib import Path

import streamlit as st

from components.findings import render_findings, render_recommendations
from components.header import render_header
from components.property_input import render_property_input
from components.risk_cards import render_overall_risk, render_risk_cards
from components.theme import apply_theme


BASE_DIR = Path(__file__).resolve().parent
MOCK_DATA_PATH = BASE_DIR / "mock_data.json"


@st.cache_data
def load_mock_assessment() -> dict:
    with MOCK_DATA_PATH.open(encoding="utf-8") as file:
        return json.load(file)

def build_assessment_for_property(
    data: dict,
    name: str,
    latitude: float,
    longitude: float
) -> dict:

    from risk_engine.property_risk import assess_property

    result = assess_property(
        latitude,
        longitude
    )

    flood = result["flood"]

    return {
        "property": {
            "name": name.strip() or "Unnamed Property",
            "latitude": latitude,
            "longitude": longitude,
            "location": "Kenya",
        },

        "assessment": {
            "overall_risk": result["overall"]["level"],
            "flood_risk": max(
                item["score"]
                for item in flood.values()
            ),
            "rainfall_risk": result["rainfall"]["rainfall_risk"]["level"],
            "terrain_risk": result["terrain"]["terrain_risk"]["level"],
            "waterway_risk": 1,
        },

        "metrics": {
            "elevation_m": result["terrain"]["elevation_m"],
            "slope_degrees": result["terrain"]["slope_degrees"],
            "distance_to_waterway_m": "Not yet calculated",
        },

        "findings": [
            (
                f"Rainfall exposure: "
                f"{result['rainfall']['rainfall_risk']['label']}"
            ),
            (
                f"Terrain exposure: "
                f"{result['terrain']['terrain_risk']['label']}"
            ),
            (
                f"Riverine flood exposure: "
                f"{flood['100yr']['rating']}"
            ),
        ],

        "recommendations": [
            "Use detailed flood and drainage assessment "
            "before acquisition or major development."
        ],

        "metadata": {
            "assessment_date": "2026-09-01",
            "data_coverage": "2025 rainfall + available flood and DEM data",
        },

        "engine_result": result,
    }


def render_property_overview(assessment: dict) -> None:
    prop = assessment["property"]
    metrics = assessment.get("metrics", {})

    st.markdown('<div class="tr-section-title">Property Overview</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            f"<div class='tr-card'><strong>{prop['name']}</strong><br>"
            f"<span class='tr-muted'>{prop.get('location', 'Kenya')}</span><br><br>"
            f"Latitude: {prop['latitude']:.6f}<br>"
            f"Longitude: {prop['longitude']:.6f}</div>",
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"<div class='tr-card'><strong>Key Metrics</strong><br><br>"
            f"Elevation: {metrics.get('elevation_m', '—')} m<br>"
            f"Slope: {metrics.get('slope_degrees', '—')}°<br>"
            f"Distance to waterway: {metrics.get('distance_to_waterway_m', '—')} m</div>",
            unsafe_allow_html=True,
        )


def main() -> None:
    st.set_page_config(
        page_title="TerraRisk",
        page_icon="🌍",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    apply_theme()
    render_header()

    mock = load_mock_assessment()
    defaults = mock["property"]
    name, latitude, longitude, submitted = render_property_input(defaults)

    if submitted:
        with st.spinner("Preparing property assessment..."):
            st.session_state["assessment"] = build_assessment_for_property(
                mock, name, latitude, longitude
            )

    assessment = st.session_state.get("assessment")
    if assessment is None:
        st.markdown(
            "<div class='tr-card'><strong>Ready to assess.</strong><br>"
            "Enter the property details above and select <b>Analyse Property</b>.</div>",
            unsafe_allow_html=True,
        )
        return

    st.success("Assessment loaded using MVP demonstration data.")
    render_property_overview(assessment)

    st.markdown('<div class="tr-section-title">Risk Summary</div>', unsafe_allow_html=True)
    render_overall_risk(assessment["assessment"]["overall_risk"])
    st.write("")
    render_risk_cards(
        {
            "flood": assessment["assessment"]["flood_risk"],
            "rainfall": assessment["assessment"]["rainfall_risk"],
            "terrain": assessment["assessment"]["terrain_risk"],
            "waterway": assessment["assessment"]["waterway_risk"],
        }
    )

    render_findings(assessment.get("findings", []))
    render_recommendations(assessment.get("recommendations", []))

    with st.expander("Data & Methodology"):
        metadata = assessment.get("metadata", {})
        st.write(f"**Assessment date:** {metadata.get('assessment_date', '—')}")
        st.write(f"**Data coverage:** {metadata.get('data_coverage', '—')}")
        st.write("**Current status:** Frontend demonstration using mock assessment data.")
        st.write(
            "Risk 1–4 classifications are prototype decision-support classifications and "
            "do not replace site-specific engineering, hydrological, environmental or regulatory due diligence."
        )

    st.markdown(
        "<div class='tr-footer'>TerraRisk MVP • Kenya asset-level climate and flood risk intelligence</div>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
