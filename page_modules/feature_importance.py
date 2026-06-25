"""page_modules/feature_importance.py — Feature importance dashboard v2.0."""

import streamlit as st
import plotly.graph_objects as go
from utils.components import section_head, rank_row, glass_card_open, glass_card_close, foot_note

FEATURES = [
    ("RAM",       0.284, "Memory is the strongest single price driver — more RAM almost always means a higher-tier machine."),
    ("Form Factor",0.171,"Form factor (Gaming, Ultrabook, Workstation) captures a bundle of premium-build signals at once."),
    ("CPU Brand",  0.154,"Processor tier (i3 → i7 / Ryzen) directly tracks performance segment and price."),
    ("CPU Speed",  0.122,"Clock speed adds finer-grained separation within the same CPU brand tier."),
    ("PPI",        0.098,"Pixel density — a proxy for premium high-resolution displays."),
    ("SSD",        0.087,"Solid-state capacity correlates strongly with modern, higher-spec builds."),
    ("GPU",        0.061,"Dedicated GPU presence (especially Nvidia) pushes price up for gaming & creative use."),
]


def render():
    section_head("Feature Importance", "What the model learned to rely on for pricing")

    # ── Rank rows ─────────────────────────────────────────────────────────────
    max_val = max(f[1] for f in FEATURES)
    glass_card_open()
    html = ""
    for i, (name, val, _) in enumerate(FEATURES, start=1):
        html += rank_row(i, name, val, max_val)
    st.markdown(html, unsafe_allow_html=True)
    glass_card_close()

    # ── Horizontal bar chart ──────────────────────────────────────────────────
    st.write("")
    section_head("Importance Chart")

    names = [f[0] for f in FEATURES][::-1]
    vals  = [f[1] for f in FEATURES][::-1]

    # Gradient via a colorscale trick — single trace, each bar gets a shade
    normalised = [v / max(vals) for v in vals]
    bar_colors = [
        f"rgba({int(99+56*n)},{int(102+90*n)},{int(241-65*n)},1)"
        for n in normalised
    ]

    fig = go.Figure(go.Bar(
        x=vals, y=names, orientation="h",
        marker=dict(color=bar_colors, line=dict(width=0)),
        text=[f"{v:.1%}" for v in vals],
        textposition="outside",
        textfont=dict(color="#f1f2f6", size=11.5, family="JetBrains Mono"),
    ))
    fig.update_layout(
        height=340,
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,.05)", tickfont=dict(color="#9da3b8")),
        yaxis=dict(tickfont=dict(color="#f1f2f6", size=13)),
        font=dict(family="Inter"), margin=dict(t=10, l=0, r=50, b=10),
    )
    st.plotly_chart(fig, use_container_width=True)

    # ── Explanation cards ─────────────────────────────────────────────────────
    st.write("")
    section_head("What Each Feature Means")
    cols = st.columns(2)
    for i, (name, val, explanation) in enumerate(FEATURES):
        with cols[i % 2]:
            glass_card_open()
            st.markdown(f"""
                <div style="display:flex; justify-content:space-between; align-items:baseline; margin-bottom:8px;">
                    <span style="font-weight:700; font-size:14px; color:var(--text-primary); letter-spacing:-.01em;">{name}</span>
                    <span style="font-family:'JetBrains Mono',monospace; color:var(--accent); font-weight:700; font-size:14px;">{val:.1%}</span>
                </div>
                <div style="font-size:12.5px; color:var(--text-secondary); line-height:1.65;">{explanation}</div>
            """, unsafe_allow_html=True)
            glass_card_close()

    foot_note("Importance scores shown are illustrative placeholders — replace with model.feature_importances_ from your trained pipeline.")
