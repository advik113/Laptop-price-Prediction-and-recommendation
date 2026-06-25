"""page_modules/comparison.py — Side-by-side laptop comparison v2.0."""

import streamlit as st
import plotly.graph_objects as go
from utils.components import (
    section_head, glass_card_open, glass_card_close, cmp_row, foot_note, form_section_label,
)
from utils.data_loader import predict_price, COMPANIES, TYPENAMES, CPU_BRANDS, GPU_BRANDS


def _laptop_form(label: str, key_prefix: str):
    st.markdown(f"""
    <div style="font-size:13px; font-weight:700; color:var(--text-primary);
        letter-spacing:-.01em; margin-bottom:12px; padding-bottom:8px;
        border-bottom:2px solid {'#6366f1' if key_prefix=='a' else '#06b6d4'};">
        {label}
    </div>
    """, unsafe_allow_html=True)

    company   = st.selectbox("Company",    COMPANIES,   key=f"{key_prefix}_company")
    typename  = st.selectbox("Type",       TYPENAMES,   key=f"{key_prefix}_type")
    ram       = st.selectbox("RAM (GB)",   [4, 8, 16, 32, 64], index=1, key=f"{key_prefix}_ram")
    ssd       = st.selectbox("SSD (GB)",   [0, 128, 256, 512, 1024], index=2, key=f"{key_prefix}_ssd")
    hdd       = st.selectbox("HDD (GB)",   [0, 500, 1000], index=0, key=f"{key_prefix}_hdd")
    cpu_brand = st.selectbox("CPU Brand",  CPU_BRANDS,  index=2, key=f"{key_prefix}_cpu")
    cpu_speed = st.slider("CPU Speed (GHz)", 1.0, 4.5, 2.6, 0.1, key=f"{key_prefix}_speed")
    gpu_brand = st.selectbox("GPU Brand",  GPU_BRANDS,  index=1, key=f"{key_prefix}_gpu")
    weight    = st.number_input("Weight (kg)", 0.8, 4.5, 1.8, 0.1, key=f"{key_prefix}_weight")
    ppi       = st.slider("PPI", 100, 280, 141, key=f"{key_prefix}_ppi")

    return dict(
        company=company, typename=typename, ram=ram, ssd=ssd, hdd=hdd, hybrid=0,
        flash_storage=0, cpu_brand=cpu_brand, cpu_speed=cpu_speed, gpu_brand=gpu_brand,
        weight=weight, ppi=ppi, inches=15.6, touchscreen=False, ips=True, os="Windows",
    )


def render():
    section_head("Laptop Comparison", "Configure two laptops and compare specs + estimated price side by side")

    glass_card_open()
    colA, colB = st.columns(2)
    with colA:
        laptop_a = _laptop_form("💻 Laptop A", "a")
    with colB:
        laptop_b = _laptop_form("💻 Laptop B", "b")

    compare_clicked = st.button("⚖️  Compare Laptops", type="primary", use_container_width=True)
    glass_card_close()

    if compare_clicked:
        price_a, _ = predict_price(laptop_a)
        price_b, _ = predict_price(laptop_b)

        # ── Price summary ─────────────────────────────────────────────────────
        st.write("")
        pc1, pc2 = st.columns(2)

        for col, laptop, price, accent in [
            (pc1, laptop_a, price_a, "#6366f1"),
            (pc2, laptop_b, price_b, "#06b6d4"),
        ]:
            with col:
                glass_card_open()
                st.markdown(f"""
                <div style="text-align:center; padding:8px 0;">
                    <div style="font-size:11px; font-weight:700; letter-spacing:.08em; text-transform:uppercase; color:{accent}; margin-bottom:8px;">
                        {'Laptop A' if accent=="#6366f1" else 'Laptop B'} · {laptop['company']}
                    </div>
                    <div style="font-family:'JetBrains Mono',monospace; font-weight:800; font-size:42px;
                        background:linear-gradient(135deg,{accent},{accent}cc); -webkit-background-clip:text;
                        background-clip:text; color:transparent; letter-spacing:-.02em;">
                        ₹{price:,.0f}
                    </div>
                    <div style="font-size:13px; color:var(--text-tertiary); margin-top:6px;">
                        {laptop['cpu_brand']} · {laptop['ram']}GB RAM · {laptop['ssd']+laptop['hdd']}GB Storage
                    </div>
                </div>
                """, unsafe_allow_html=True)
                glass_card_close()

        # ── Spec table ────────────────────────────────────────────────────────
        st.write("")
        section_head("Specification Comparison")
        glass_card_open()

        # Header row
        st.markdown("""
        <div style="display:flex; justify-content:space-between; padding:0 0 8px; border-bottom:1px solid var(--glass-border-strong); margin-bottom:4px;">
            <div style="flex:1; text-align:center; font-size:12px; font-weight:700; color:#6366f1;">Laptop A</div>
            <div style="flex:0 0 120px; text-align:center; font-size:11px; font-weight:600; color:var(--text-tertiary); text-transform:uppercase; letter-spacing:.06em;">Spec</div>
            <div style="flex:1; text-align:center; font-size:12px; font-weight:700; color:#06b6d4;">Laptop B</div>
        </div>
        """, unsafe_allow_html=True)

        specs = [
            ("CPU",     f"{laptop_a['cpu_brand']} @ {laptop_a['cpu_speed']}GHz",
                        f"{laptop_b['cpu_brand']} @ {laptop_b['cpu_speed']}GHz",
                        "a" if laptop_a["cpu_speed"] > laptop_b["cpu_speed"] else "b"),
            ("RAM",     f"{laptop_a['ram']} GB",    f"{laptop_b['ram']} GB",
                        "a" if laptop_a["ram"] > laptop_b["ram"] else "b"),
            ("Storage", f"{laptop_a['ssd']+laptop_a['hdd']} GB",
                        f"{laptop_b['ssd']+laptop_b['hdd']} GB",
                        "a" if (laptop_a["ssd"]+laptop_a["hdd"]) > (laptop_b["ssd"]+laptop_b["hdd"]) else "b"),
            ("GPU",     laptop_a["gpu_brand"], laptop_b["gpu_brand"], None),
            ("Weight",  f"{laptop_a['weight']} kg", f"{laptop_b['weight']} kg",
                        "a" if laptop_a["weight"] < laptop_b["weight"] else "b"),
            ("PPI",     str(laptop_a["ppi"]),  str(laptop_b["ppi"]),
                        "a" if laptop_a["ppi"] > laptop_b["ppi"] else "b"),
            ("Est. Price", f"₹{price_a:,.0f}", f"₹{price_b:,.0f}",
                        "a" if price_a < price_b else "b"),
        ]

        rows_html = ""
        for label, va, vb, winner in specs:
            rows_html += cmp_row(label, va, vb, winner)
        st.markdown(rows_html, unsafe_allow_html=True)
        glass_card_close()

        # ── Radar chart ───────────────────────────────────────────────────────
        st.write("")
        section_head("Spec Radar", "Normalised across 5 key dimensions")

        def _norm(l):
            gpu_score = {"Intel": 1, "AMD": 2, "ARM": 1.5, "Nvidia": 3}.get(l["gpu_brand"], 1)
            return [
                l["ram"] / 64,
                (l["ssd"] + l["hdd"]) / 1024,
                l["cpu_speed"] / 4.5,
                l["ppi"] / 280,
                gpu_score / 3,
            ]

        cats = ["RAM", "Storage", "CPU Speed", "PPI", "GPU Tier"]
        fig = go.Figure()

        for (name, color, fill_color, laptop) in [
            ("Laptop A", "#6366f1", "rgba(99,102,241,.20)", laptop_a),
            ("Laptop B", "#06b6d4", "rgba(6,182,212,.15)",  laptop_b),
        ]:
            scores = _norm(laptop)
            fig.add_trace(go.Scatterpolar(
                r=scores + [scores[0]],
                theta=cats + [cats[0]],
                fill="toself",
                name=name,
                line=dict(color=color, width=2),
                fillcolor=fill_color,
            ))

        fig.update_layout(
            polar=dict(
                bgcolor="rgba(0,0,0,0)",
                radialaxis=dict(
                    visible=True, range=[0, 1],
                    gridcolor="rgba(255,255,255,.07)", showticklabels=False,
                ),
                angularaxis=dict(color="#9da3b8"),
            ),
            showlegend=True,
            legend=dict(font=dict(color="#f1f2f6", size=12), bgcolor="rgba(0,0,0,0)"),
            paper_bgcolor="rgba(0,0,0,0)",
            height=420, margin=dict(t=20, b=20),
            font=dict(family="Inter"),
        )
        st.plotly_chart(fig, use_container_width=True)

    foot_note("Estimated prices use the same prediction pipeline as the Price Prediction page.")
