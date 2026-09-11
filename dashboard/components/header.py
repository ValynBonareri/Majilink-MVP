import streamlit as st


def render_header() -> None:
    st.markdown('<div class="tr-brand">TERRARISK</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="tr-tagline">Climate &amp; Flood Risk Intelligence for Real Estate</div>',
        unsafe_allow_html=True,
    )
