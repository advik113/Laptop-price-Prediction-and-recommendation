"""page_modules/about.py — About the project v2.0."""

import streamlit as st
from utils.components import section_head, glass_card_open, glass_card_close, pill, foot_note

WORKFLOW = [
    ("01", "Data Collection",
     "Gathered a real-world laptop specifications dataset (~1,300 listings) spanning brands, configurations and prices."),
    ("02", "Cleaning & Feature Engineering",
     "Parsed RAM/storage strings into numerics, computed PPI from resolution, extracted CPU/GPU brand & tier, encoded categoricals."),
    ("03", "Model Benchmarking",
     "Trained and compared Linear Regression, Random Forest and XGBoost on identical train/test splits."),
    ("04", "Hyperparameter Tuning",
     "Tuned XGBoost via grid/random search, lifting R² from 0.9125 to 0.9182 while reducing MAE and RMSE."),
    ("05", "Application Layer",
     "Wrapped the trained pipeline in this Streamlit dashboard — prediction, analytics, recommendation and comparison tools."),
]

TECH = [
    ("🐍", "Python",          "Core language for the ML pipeline & app logic",    "accent"),
    ("📈", "XGBoost",         "Final tuned regression model (R² = 0.918)",        "success"),
    ("🧮", "Scikit-learn",    "Preprocessing, train/test split, baseline models", ""),
    ("🐼", "Pandas / NumPy",  "Data wrangling & feature engineering",             ""),
    ("🎈", "Streamlit",       "Interactive multi-page web application",           "warn"),
    ("📊", "Plotly",          "Interactive BI-style charts & dashboards",         ""),
]


def render():
    section_head("About This Project", "Smart Laptop Price Prediction & Recommendation System")

    # Overview
    glass_card_open()
    st.markdown("""
    <div style="font-size:15px; color:var(--text-primary); font-weight:600; margin-bottom:10px; letter-spacing:-.01em;">Project Overview</div>
    <div style="font-size:13.5px; color:var(--text-secondary); line-height:1.75;">
        This system estimates a fair market price for a laptop from its specifications,
        and goes further with a recommendation engine (best laptop for your budget and use case)
        and a side-by-side comparison tool. Built end-to-end: real dataset →
        feature engineering → model benchmarking → tuned XGBoost → production-style dashboard.
    </div>
    """, unsafe_allow_html=True)
    glass_card_close()

    # Workflow
    st.write("")
    section_head("Project Workflow")
    for num, title, desc in WORKFLOW:
        glass_card_open()
        c1, c2 = st.columns([0.07, 0.93])
        with c1:
            st.markdown(f'<div class="tl-dot">{num}</div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
                <div class="tl-title">{title}</div>
                <div class="tl-desc">{desc}</div>
            """, unsafe_allow_html=True)
        glass_card_close()

    # Technologies
    st.write("")
    section_head("Technologies Used")
    tech_cols = st.columns(3)
    for i, (icon, name, desc, kind) in enumerate(TECH):
        with tech_cols[i % 3]:
            glass_card_open()
            st.markdown(f"""
                <div style="display:flex; align-items:center; gap:10px; margin-bottom:10px;">
                    <div class="kpi-icon" style="width:34px; height:34px; font-size:15px; margin-bottom:0;">{icon}</div>
                    <div>
                        <div style="font-weight:700; font-size:14px; color:var(--text-primary);">{name}</div>
                    </div>
                </div>
                <div style="font-size:12.5px; color:var(--text-secondary); line-height:1.6;">{desc}</div>
            """, unsafe_allow_html=True)
            glass_card_close()

    # Dataset stats
    st.write("")
    section_head("Dataset Information")
    glass_card_open()
    d1, d2, d3, d4 = st.columns(4)
    for col, (val, label) in zip([d1, d2, d3, d4], [
        ("~1,303", "Rows"),
        ("17",     "Engineered Features"),
        ("19",     "Brands"),
        ("6",      "Form Factor Types"),
    ]):
        with col:
            st.markdown(f"""
                <div style="font-family:'JetBrains Mono',monospace; font-weight:700; font-size:26px; color:var(--text-primary); letter-spacing:-.02em;">{val}</div>
                <div style="font-size:12px; color:var(--text-tertiary); margin-top:4px;">{label}</div>
            """, unsafe_allow_html=True)

    st.write("")
    feature_pills = ["Company","TypeName","Inches","RAM","Weight","Touchscreen","IPS",
                     "PPI","SSD","HDD","Hybrid","Flash","CPU Brand","CPU Speed","GPU Brand","OS","Category"]
    pills_html = " ".join(pill(f) for f in feature_pills)
    st.markdown(f'<div style="display:flex; flex-wrap:wrap; gap:6px; margin-top:8px;">{pills_html}</div>', unsafe_allow_html=True)
    glass_card_close()

    # Author
    st.write("")
    section_head("Author")
    glass_card_open()
    c1, c2 = st.columns([0.12, 0.88])
    with c1:
        st.markdown("""
        <div class="sb-logo-icon" style="width:56px; height:56px; font-size:24px;">🎓</div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
            <div style="font-weight:700; font-size:17px; color:var(--text-primary); letter-spacing:-.01em;">Your Name Here</div>
            <div style="font-size:13px; color:var(--text-secondary); margin-top:3px;">Final Year B.Tech / B.Sc — Data Science</div>
            <div style="font-size:12px; color:var(--text-tertiary); margin-top:8px; line-height:1.6;">
                Replace this section with your name, institution, and links (GitHub · LinkedIn · Email).
            </div>
        """, unsafe_allow_html=True)
    glass_card_close()

    foot_note("Smart Laptop Advisor · Final Year Data Science Capstone Project")
