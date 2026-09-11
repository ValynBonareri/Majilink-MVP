import streamlit as st


def apply_theme() -> None:
    st.markdown(
        """
        <style>
        :root {
            --tr-primary: #0b5cab;
            --tr-primary-dark: #083b6d;
            --tr-bg: #f5f8fc;
            --tr-border: #dfe7f1;
            --tr-text: #162235;
            --tr-muted: #66758a;
        }

        .stApp {
            background: var(--tr-bg);
            color: var(--tr-text);
        }

        .block-container {
            max-width: 1280px;
            padding-top: 2rem;
            padding-bottom: 3rem;
        }

        .tr-brand {
            font-size: 2rem;
            font-weight: 800;
            letter-spacing: .04em;
            color: var(--tr-primary-dark);
            margin-bottom: .1rem;
        }

        .tr-tagline {
            color: var(--tr-muted);
            font-size: 1rem;
            margin-bottom: 1.5rem;
        }

        .tr-section-title {
            font-size: 1.25rem;
            font-weight: 750;
            color: var(--tr-text);
            margin: 1.4rem 0 .7rem 0;
        }

        .tr-card {
            background: white;
            border: 1px solid var(--tr-border);
            border-radius: 14px;
            padding: 1.15rem 1.25rem;
            box-shadow: 0 2px 8px rgba(20, 45, 80, .04);
        }

        .tr-card-label {
            color: var(--tr-muted);
            font-size: .82rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: .06em;
        }

        .tr-risk-number {
            font-size: 2.15rem;
            font-weight: 850;
            margin-top: .25rem;
            color: var(--tr-primary-dark);
        }

        .tr-risk-level {
            font-size: .9rem;
            font-weight: 700;
            margin-top: -.1rem;
        }

        .tr-muted {
            color: var(--tr-muted);
        }

        .tr-finding {
            background: white;
            border: 1px solid var(--tr-border);
            border-radius: 10px;
            padding: .75rem 1rem;
            margin-bottom: .55rem;
        }

        .tr-overall {
            text-align: center;
            padding: 1.5rem;
            background: white;
            border: 1px solid var(--tr-border);
            border-radius: 16px;
            box-shadow: 0 3px 12px rgba(20, 45, 80, .05);
        }

        .tr-overall-number {
            font-size: 3.25rem;
            line-height: 1;
            font-weight: 900;
            color: var(--tr-primary);
        }

        .tr-overall-label {
            font-size: 1.05rem;
            font-weight: 750;
            margin-top: .5rem;
        }

        .tr-footer {
            color: var(--tr-muted);
            font-size: .78rem;
            padding-top: 2rem;
            border-top: 1px solid var(--tr-border);
            margin-top: 2rem;
        }

        div.stButton > button[kind="primary"] {
            border-radius: 9px;
            font-weight: 750;
            min-height: 2.8rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
