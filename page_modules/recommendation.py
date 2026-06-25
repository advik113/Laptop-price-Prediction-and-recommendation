"""page_modules/recommendation.py — Recommendation engine v2.1."""

import streamlit as st
from utils.components import section_head, glass_card_open, glass_card_close, pill, foot_note
from utils.data_loader import load_dataset

PURPOSES = {
    "Student":       {"icon": "🎓", "weight": {"ram": 8,  "ssd": 256,  "cpu": "Intel Core i5", "gpu": "Intel"}},
    "Office":        {"icon": "💼", "weight": {"ram": 8,  "ssd": 256,  "cpu": "Intel Core i5", "gpu": "Intel"}},
    "Programming":   {"icon": "👨‍💻", "weight": {"ram": 16, "ssd": 512,  "cpu": "Intel Core i7", "gpu": "Intel"}},
    "Gaming":        {"icon": "🎮", "weight": {"ram": 16, "ssd": 512,  "cpu": "Intel Core i7", "gpu": "Nvidia"}},
    "Video Editing": {"icon": "🎬", "weight": {"ram": 32, "ssd": 1024, "cpu": "Intel Core i7", "gpu": "Nvidia"}},
}


def _score(row, purpose, budget):
    target = PURPOSES[purpose]["weight"]
    score  = 0
    
    # 1. RAM fit (max 30 pts): exact is 30, higher is 28 (still good), lower gets penalized.
    ram_diff = row["Ram"] - target["ram"]
    if ram_diff == 0:
        score += 30
    elif ram_diff > 0:
        score += 28
    else:
        score += max(0, 30 - abs(ram_diff) * 2)
        
    # 2. SSD score (max 25 pts)
    ssd_diff = row["SSD"] - target["ssd"]
    if ssd_diff == 0:
        score += 25
    elif ssd_diff > 0:
        score += 23
    else:
        score += max(0, 25 - abs(ssd_diff) / 20)
        
    # 3. CPU score (max 20 pts)
    if row["CPU_Brand"] == target["cpu"]:
        score += 20
    elif row["CPU_Brand"] == "Intel Core i7" and target["cpu"] == "Intel Core i5":
        score += 18  # upgrading is fine
    elif row["CPU_Brand"] == "Intel Core i5" and target["cpu"] == "Intel Core i7":
        score += 12  # downgrading CPU is penalized more
    else:
        score += 8
        
    # 4. GPU score (max 15 pts)
    if row["GPU_Brand"] == target["gpu"]:
        score += 15
    elif target["gpu"] == "Intel" and row["GPU_Brand"] in ["Intel", "AMD", "ARM"]:
        score += 12  # basic GPUs are equivalent for non-gaming
    else:
        score += 5
        
    # 5. Price fit (max 10 pts or penalty)
    row_price = row["Price"]
    if row_price <= budget:
        ratio = row_price / budget
        if ratio >= 0.8:
            score += 10
        else:
            score += 5 + int(5 * ratio)
    else:
        # Subtract 1 pt per ₹1,500 over budget
        score -= (row_price - budget) / 1500
        
    return score


def render():
    df, data_ok = load_dataset()

    section_head(
        "Laptop Recommendation",
        "Tell us your budget and use case — we'll surface the best matching machines"
        + ("" if data_ok else " — showing sample data until data/laptop_data.csv is added"),
    )

    # ── Filters ───────────────────────────────────────────────────────────────
    glass_card_open()

    st.markdown("""
    <div style="font-size:13px; color:var(--text-secondary); margin-bottom:16px;">
        Select your primary purpose and maximum budget. The recommendation engine scores
        each laptop on RAM, CPU tier, GPU class, and storage fit for your use case.
    </div>
    """, unsafe_allow_html=True)

    # Purpose selector (large icon buttons)
    purpose_labels = list(PURPOSES.keys())

    # Display as a horizontal radio-style toggle
    selected_purpose = st.radio(
        "Primary Purpose",
        purpose_labels,
        format_func=lambda p: f"{PURPOSES[p]['icon']}  {p}",
        horizontal=True,
    )

    budget = st.slider(
        "Maximum Budget (₹)",
        min_value=20_000, max_value=200_000, value=70_000, step=2_000,
        format="₹%d",
    )

    find_clicked = st.button("🔍  Find Recommendations", type="primary", use_container_width=True)
    glass_card_close()

    if find_clicked:
        # Score the laptops in the dataset
        scored_df = df.copy()
        scored_df["score"] = scored_df.apply(lambda r: _score(r, selected_purpose, budget), axis=1)

        # Deduplicate to show distinct laptop models
        scored_df = scored_df.drop_duplicates(subset=["Company", "TypeName", "Ram", "SSD", "HDD", "CPU_Brand", "GPU_Brand"])

        # Sort by score descending and get top 4
        ranked_df = scored_df.sort_values(by="score", ascending=False).head(4)

        st.write("")
        section_head(
            f"{PURPOSES[selected_purpose]['icon']}  Top Matches for {selected_purpose}",
            f"Ranked by spec fit · budget ₹{budget:,}",
        )

        cols = st.columns(4)
        for i, (col, (_, row)) in enumerate(zip(cols, ranked_df.iterrows()), start=1):
            price = row["Price"]
            within = price <= budget
            
            # Dynamically format a clean laptop name
            inches_str = f"{row['Inches']}″"
            laptop_name = f"{row['Company']} {row['TypeName']} ({inches_str})"
            
            # Format storage nicely
            storage_parts = []
            if row.get("SSD", 0) > 0:
                storage_parts.append(f"{int(row['SSD'])}GB SSD")
            if row.get("HDD", 0) > 0:
                storage_parts.append(f"{int(row['HDD'])}GB HDD")
            if row.get("Hybrid", 0) > 0:
                storage_parts.append(f"{int(row['Hybrid'])}GB Hybrid")
            if row.get("Flash_Storage", 0) > 0:
                storage_parts.append(f"{int(row['Flash_Storage'])}GB Flash")
            storage_str = " · ".join(storage_parts) if storage_parts else "No Storage"

            with col:
                st.markdown(f"""
                <div class="reco-card">
                    <div class="reco-rank">RANK #{i}</div>
                    <div class="reco-title">{laptop_name}</div>
                    <div class="reco-price">₹{price:,.0f}</div>
                    <div class="{'reco-badge within' if within else 'reco-badge over'}">
                        {'✅ Within budget' if within else '⚠️ Above budget'}
                    </div>
                    <div style="margin-top:12px; border-top:1px solid var(--glass-border); padding-top:10px;">
                        <div class="reco-spec">🧠 {row['CPU_Brand']} @ {row['CPU_Speed']}GHz</div>
                        <div class="reco-spec">💾 {int(row['Ram'])}GB RAM · {storage_str}</div>
                        <div class="reco-spec">🎨 {row['GPU_Brand']} GPU</div>
                        <div class="reco-spec">🏷️ {row['Company']} · {row['TypeName']}</div>
                    </div>
                    <div class="reco-match">
                        Optimised for <b style="color:var(--text-primary);">{selected_purpose}</b> workloads
                        based on RAM, CPU tier and GPU class.
                    </div>
                </div>
                """, unsafe_allow_html=True)

        st.write("")
        st.markdown(
            pill("✓ Live recommendation engine scoring the entire active dataset", "success"),
            unsafe_allow_html=True,
        )

    foot_note("Recommendations use the dataset loaded from utils/data_loader.py scored by a spec-match vector similarity algorithm.")
