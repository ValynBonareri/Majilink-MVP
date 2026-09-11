import streamlit as st

RISK_LABELS = {
    1: "LOW",
    2: "MODERATE",
    3: "HIGH",
    4: "VERY HIGH",
}


def risk_label(score: int) -> str:
    return RISK_LABELS.get(int(score), "UNASSESSED")


def render_overall_risk(score: int) -> None:
    st.markdown(
        f"""
        <div class="tr-overall">
            <div class="tr-card-label">Overall Risk</div>
            <div class="tr-overall-number">RISK {int(score)}</div>
            <div class="tr-overall-label">{risk_label(score)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_risk_cards(risks: dict) -> None:
    labels = [
        ("Flood", "flood"),
        ("Rainfall", "rainfall"),
        ("Terrain", "terrain"),
        ("Waterway", "waterway"),
    ]
    cols = st.columns(4)
    for col, (label, key) in zip(cols, labels):
        score = int(risks.get(key, 0))
        with col:
            st.markdown(
                f"""
                <div class="tr-card">
                    <div class="tr-card-label">{label}</div>
                    <div class="tr-risk-number">RISK {score}</div>
                    <div class="tr-risk-level">{risk_label(score)}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
