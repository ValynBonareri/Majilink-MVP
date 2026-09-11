import streamlit as st


def render_findings(findings: list[str]) -> None:
    st.markdown('<div class="tr-section-title">Key Findings</div>', unsafe_allow_html=True)
    if not findings:
        st.info("No additional findings are available for this assessment.")
        return
    for finding in findings:
        st.markdown(f'<div class="tr-finding">• {finding}</div>', unsafe_allow_html=True)


def render_recommendations(recommendations: list[str]) -> None:
    st.markdown('<div class="tr-section-title">Decision Guidance</div>', unsafe_allow_html=True)
    if not recommendations:
        st.info("No decision guidance is available for this assessment.")
        return
    for recommendation in recommendations:
        st.info(recommendation)
