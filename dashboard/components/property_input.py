import streamlit as st


def render_property_input(defaults: dict) -> tuple[str, float, float, bool]:
    st.markdown('<div class="tr-section-title">Assess a Property</div>', unsafe_allow_html=True)

    property_name = st.text_input(
        "Property name",
        value=defaults.get("name", ""),
        placeholder="e.g. Nairobi Test Property",
    )

    col1, col2 = st.columns(2)
    with col1:
        latitude = st.number_input(
            "Latitude",
            value=float(defaults.get("latitude", -1.2921)),
            format="%.6f",
            help="Latitude in decimal degrees.",
        )
    with col2:
        longitude = st.number_input(
            "Longitude",
            value=float(defaults.get("longitude", 36.8219)),
            format="%.6f",
            help="Longitude in decimal degrees.",
        )

    submitted = st.button("Analyse Property", type="primary", use_container_width=True)
    return property_name, latitude, longitude, submitted
