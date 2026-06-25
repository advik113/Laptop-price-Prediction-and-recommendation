"""page_modules/home.py — Landing dashboard v2.0."""

import streamlit as st
import plotly.graph_objects as go
from utils.components import (
    hero, kpi_card, section_head, glass_card_open, glass_card_close, pill, foot_note,
)
from utils.data_loader import load_dataset


def render():
    df, data_ok = load_dataset()

    hero(
        eyebrow="Final Year Data Science Project",
        title_html='Predict laptop prices with <span class="grad-text">AI-grade precision.</span>',
        subtitle=(
            "An end-to-end ML system that estimates fair market prices from real specifications — "
            "Company, CPU, GPU, RAM, storage, display and more — "
            "powered by a tuned XGBoost regression model with R² = 0.918."
        ),
    )

    # CTA buttons
    c1, c2, c3 = st.columns([1, 1, 4])
    with c1:
        if st.button("🚀  Predict Price", type="primary", use_container_width=True):
            st.session_state.active_page = "Price Prediction"
            st.rerun()
    with c2:
        if st.button("📊  View Analytics", type="secondary", use_container_width=True):
            st.session_state.active_page = "Analytics"
            st.rerun()

    # ── KPI row ──────────────────────────────────────────────────────────────
    st.write("")
    section_head("Project Snapshot", "Metrics from the trained pipeline")

    n_records  = len(df) if data_ok else 1303
    n_features = 17
    n_brands   = df["Company"].nunique() if data_ok else 19

    cols = st.columns(4)
    kpis = [
        ("📦", f"{n_records:,}", "Training Records",    "Cleaned & feature-engineered", "up"),
        ("🎯", "0.9182",        "XGBoost R² Score",     "+0.57 pts over base model",    "up"),
        ("🧬", str(n_features), "Engineered Features",  "Specs, ratios & one-hot cols", "flat"),
        ("🏷️", str(n_brands),   "Laptop Brands",        "Budget to Ultra-Premium",       "flat"),
    ]
    for col, (icon, val, label, delta, state) in zip(cols, kpis):
        with col:
            st.markdown(kpi_card(icon, val, label, delta, state), unsafe_allow_html=True)

    # ── Model comparison chart ────────────────────────────────────────────────
    st.write("")
    section_head("Model Benchmarks", "R² Score across all trained candidates — higher is better")

    g1, g2 = st.columns([3, 1])
    with g1:
        models = ["Linear Regression", "Random Forest", "XGBoost", "Tuned XGBoost"]
        scores = [0.8176, 0.9040, 0.9125, 0.9182]
        bar_colors = ["rgba(99,102,241,.3)", "rgba(99,102,241,.55)", "rgba(99,102,241,.75)", "#6366f1"]

        fig = go.Figure(go.Bar(
            x=scores, y=models, orientation="h",
            marker=dict(color=bar_colors, line=dict(width=0)),
            text=[f"{s:.4f}" for s in scores],
            textposition="outside",
            textfont=dict(color="#f1f2f6", family="JetBrains Mono", size=12),
        ))
        fig.update_layout(
            height=260,
            margin=dict(l=0, r=40, t=10, b=10),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(
                range=[0.75, 1.0],
                showgrid=True,
                gridcolor="rgba(255,255,255,0.06)",
                tickfont=dict(color="#9da3b8", size=11),
                title=None,
            ),
            yaxis=dict(tickfont=dict(color="#f1f2f6", size=12.5)),
            font=dict(family="Inter"),
        )
        st.plotly_chart(fig, use_container_width=True)

    with g2:
        glass_card_open()
        st.markdown(f"""
            <div style="font-size:11px; font-weight:700; letter-spacing:.08em; text-transform:uppercase; color:var(--accent); margin-bottom:10px;">Champion</div>
            {pill("Tuned XGBoost", "accent")}
            <div style="font-size:12.5px; color:var(--text-secondary); line-height:1.7; margin-top:14px;">
                Hyperparameter tuning lifted R² by
                <b style="color:var(--text-primary);">+0.57 pts</b> over base XGBoost and
                <b style="color:var(--text-primary);">+10 pts</b> over Linear Regression.
                Inference under <b style="color:var(--text-primary);">5 ms</b> per prediction.
            </div>
        """, unsafe_allow_html=True)
        glass_card_close()

    # ── Feature highlights ────────────────────────────────────────────────────
    st.write("")
    section_head("Why This System", "Built to behave like a production ML product, not a notebook demo")

    f1, f2, f3 = st.columns(3)
    highlights = [
        (f1, "⚙️", "Feature-Engineered Pipeline",
         "PPI from resolution, SSD/HDD/Hybrid split, CPU & GPU brand "
         "extraction — all baked into the trained model schema."),
        (f2, "🧠", "Model Selection, Not Guesswork",
         "Linear Regression, Random Forest and XGBoost benchmarked "
         "head-to-head; tuned XGBoost won on R², MAE and RMSE."),
        (f3, "🎁", "Beyond Prediction",
         "A recommendation engine and side-by-side comparison tool turn "
         "a single price estimate into a full buying-decision system."),
    ]
    for col, icon, title, desc in highlights:
        with col:
            glass_card_open()
            st.markdown(f"""
                <div class="kpi-icon" style="margin-bottom:12px;">{icon}</div>
                <div style="font-weight:700; font-size:14.5px; color:var(--text-primary); margin-bottom:6px; letter-spacing:-.01em;">{title}</div>
                <div style="font-size:13px; color:var(--text-secondary); line-height:1.65;">{desc}</div>
            """, unsafe_allow_html=True)
            glass_card_close()

    # ── Quick navigation cards ────────────────────────────────────────────────
    st.write("")
    section_head("Explore", "Jump to any section of the project")

    nav_cards = [
        ("💰", "Price Prediction", "Enter specs and get an instant estimated market price.", "Price Prediction"),
        ("📊", "Analytics", "Explore distributions, correlations and brand breakdowns.", "Analytics"),
        ("🎁", "Recommendation", "Find the best laptop for your budget and use case.", "Recommendation"),
        ("⚖️", "Compare Laptops", "Configure two laptops and compare specs side-by-side.", "Compare Laptops"),
    ]
    nav_cols = st.columns(4)
    for col, (icon, title, desc, target) in zip(nav_cols, nav_cards):
        with col:
            glass_card_open()
            st.markdown(f"""
                <div style="font-size:24px; margin-bottom:10px;">{icon}</div>
                <div style="font-weight:700; font-size:14px; color:var(--text-primary); margin-bottom:5px;">{title}</div>
                <div style="font-size:12px; color:var(--text-tertiary); line-height:1.55;">{desc}</div>
            """, unsafe_allow_html=True)
            if st.button(f"Open →", key=f"home_nav_{target}", use_container_width=True):
                st.session_state.active_page = target
                st.rerun()
            glass_card_close()

    foot_note("Smart Laptop Advisor · Final Year Data Science Capstone · Powered by XGBoost + Streamlit")
