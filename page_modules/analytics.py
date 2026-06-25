"""page_modules/analytics.py — BI-style analytics dashboard v2.0."""

import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from utils.components import section_head, kpi_card, foot_note
from utils.data_loader import load_dataset

# Shared Plotly theme — matches CSS token --bg-base
_PLOT = dict(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter", color="#9da3b8", size=12),
    margin=dict(l=10, r=10, t=28, b=10),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11)),
)
_SEQ = ["#6366f1", "#8b5cf6", "#a855f7", "#06b6d4", "#22d3ee", "#3b82f6", "#ec4899", "#f59e0b"]


def _style(fig, h=340):
    fig.update_layout(**_PLOT, height=h)
    fig.update_xaxes(showgrid=False, color="#9da3b8", linecolor="rgba(255,255,255,0.06)")
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.05)", color="#9da3b8", linecolor="rgba(0,0,0,0)")
    return fig


def render():
    df, data_ok = load_dataset()

    section_head(
        "Analytics Dashboard",
        "Exploratory analysis across the laptop dataset"
        + ("" if data_ok else " — showing sample data until data/laptop_data.csv is added"),
    )

    # ── Top KPI row ──────────────────────────────────────────────────────────
    avg_price  = df["Price"].mean()
    med_price  = df["Price"].median()
    max_price  = df["Price"].max()
    n_brands   = df["Company"].nunique()

    cols = st.columns(4)
    for col, (icon, val, lbl) in zip(cols, [
        ("💰", f"₹{avg_price:,.0f}", "Avg Price"),
        ("📊", f"₹{med_price:,.0f}", "Median Price"),
        ("🚀", f"₹{max_price:,.0f}", "Max Price"),
        ("🏷️", str(n_brands),       "Brands"),
    ]):
        with col:
            st.markdown(kpi_card(icon, val, lbl), unsafe_allow_html=True)

    # ── Filters row ──────────────────────────────────────────────────────────
    st.write("")
    f1, f2, f3 = st.columns(3)
    with f1:
        brands_f = st.multiselect("Filter by Brand", sorted(df["Company"].unique()), default=[])
    with f2:
        types_f  = st.multiselect("Filter by Type",  sorted(df["TypeName"].unique()), default=[])
    with f3:
        price_max   = int(df["Price"].max())
        price_range = st.slider("Price Range (₹)", 0, price_max, (0, price_max), step=1000)

    fdf = df.copy()
    if brands_f:
        fdf = fdf[fdf["Company"].isin(brands_f)]
    if types_f:
        fdf = fdf[fdf["TypeName"].isin(types_f)]
    fdf = fdf[(fdf["Price"] >= price_range[0]) & (fdf["Price"] <= price_range[1])]

    if fdf.empty:
        st.info("No records match the current filters. Adjust the filters above.")
        return

    # ── Row 1: Brand distribution + Price histogram ───────────────────────────
    st.write("")
    section_head("Distribution Overview")
    r1c1, r1c2 = st.columns(2)

    with r1c1:
        st.markdown("**Brand Distribution**")
        vc = fdf["Company"].value_counts().reset_index()
        vc.columns = ["Company", "Count"]
        fig = px.bar(vc, x="Company", y="Count", color="Company", color_discrete_sequence=_SEQ)
        fig.update_layout(showlegend=False)
        fig.update_traces(marker_line_width=0)
        st.plotly_chart(_style(fig), use_container_width=True)

    with r1c2:
        st.markdown("**Price Distribution**")
        fig = px.histogram(fdf, x="Price", nbins=32, color_discrete_sequence=["#6366f1"])
        fig.update_traces(marker_line_width=0)
        st.plotly_chart(_style(fig), use_container_width=True)

    # ── Row 2: RAM + CPU brand ────────────────────────────────────────────────
    section_head("Specs Analysis")
    r2c1, r2c2 = st.columns(2)

    with r2c1:
        st.markdown("**RAM Distribution**")
        vc = fdf["Ram"].value_counts().sort_index().reset_index()
        vc.columns = ["RAM (GB)", "Count"]
        fig = px.bar(vc, x="RAM (GB)", y="Count", color_discrete_sequence=["#06b6d4"])
        fig.update_traces(marker_line_width=0)
        st.plotly_chart(_style(fig), use_container_width=True)

    with r2c2:
        st.markdown("**CPU Brand Share**")
        vc = fdf["CPU_Brand"].value_counts().reset_index()
        vc.columns = ["CPU", "Count"]
        fig = px.pie(vc, names="CPU", values="Count", color_discrete_sequence=_SEQ, hole=0.52)
        fig.update_traces(textfont_color="white", textfont_size=11)
        st.plotly_chart(_style(fig), use_container_width=True)

    # ── Row 3: GPU avg price + Storage ────────────────────────────────────────
    section_head("Value Analysis")
    r3c1, r3c2 = st.columns(2)

    with r3c1:
        st.markdown("**Avg Price by GPU Brand**")
        gpu_avg = fdf.groupby("GPU_Brand")["Price"].mean().reset_index()
        fig = px.bar(gpu_avg, x="GPU_Brand", y="Price", color="GPU_Brand", color_discrete_sequence=_SEQ)
        fig.update_layout(showlegend=False)
        fig.update_traces(marker_line_width=0)
        st.plotly_chart(_style(fig), use_container_width=True)

    with r3c2:
        st.markdown("**Avg Storage (GB)**")
        storage_cols = [c for c in ["SSD", "HDD"] if c in fdf.columns]
        if storage_cols:
            s_avg = fdf[storage_cols].mean().reset_index()
            s_avg.columns = ["Type", "Avg GB"]
            fig = px.bar(s_avg, x="Type", y="Avg GB", color="Type", color_discrete_sequence=_SEQ)
            fig.update_layout(showlegend=False)
            fig.update_traces(marker_line_width=0)
            st.plotly_chart(_style(fig), use_container_width=True)

    # ── Heatmap ───────────────────────────────────────────────────────────────
    st.write("")
    section_head("Correlation Heatmap", "Numeric features")
    numeric_cols = fdf.select_dtypes(include=[np.number]).columns.tolist()
    corr = fdf[numeric_cols].corr()
    fig = go.Figure(data=go.Heatmap(
        z=corr.values, x=corr.columns, y=corr.columns,
        colorscale=[[0, "#0d0f17"], [0.5, "#6366f1"], [1, "#06b6d4"]],
        zmin=-1, zmax=1,
        text=np.round(corr.values, 2), texttemplate="%{text}",
        textfont=dict(size=9, color="#f1f2f6"),
    ))
    st.plotly_chart(_style(fig, h=460), use_container_width=True)

    foot_note(f"Showing {len(fdf):,} of {len(df):,} records after filters.")
