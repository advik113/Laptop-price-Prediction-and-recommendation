"""
app.py — Smart Laptop Advisor  v2.1
----------------------------------------------------------------------
Entry point. Renders sticky command-bar header, collapsible sidebar
(logo, grouped nav, model snapshot, theme toggle) and routes to the
selected page module.

No JavaScript is used anywhere in this application.
Run with:  streamlit run app.py
----------------------------------------------------------------------
"""

import streamlit as st
from utils.components import (
    inject_css, init_theme, get_theme, toggle_theme,
    render_header, sidebar_brand, sidebar_nav_label,
    sidebar_metric_card, sidebar_footer,
)
from utils.data_loader import load_model, load_dataset

from page_modules import (
    home, prediction, analytics, model_performance,
    feature_importance, recommendation, comparison, about,
)

st.set_page_config(
    page_title="Smart Laptop Advisor",
    page_icon="💻",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Session state bootstrap ──────────────────────────────────────────────────
init_theme()

if "active_page" not in st.session_state:
    st.session_state.active_page = "Dashboard"

# ── CSS (must come before any HTML) ─────────────────────────────────────────
inject_css("assets/style.css")

# ── Page registry ────────────────────────────────────────────────────────────
NAV_GROUPS = {
    "Main": [
        ("Dashboard",          "🏠", home),
        ("Price Prediction",   "💰", prediction),
    ],
    "Analytics": [
        ("Analytics",          "📊", analytics),
        ("Model Performance",  "🎯", model_performance),
        ("Feature Importance", "🔍", feature_importance),
    ],
    "Tools": [
        ("Recommendation",     "🎁", recommendation),
        ("Compare Laptops",    "⚖️",  comparison),
    ],
    "Info": [
        ("About Project",      "ℹ️",  about),
    ],
}

# Flat lookup for router
PAGES = {label: module for group in NAV_GROUPS.values() for label, _, module in group}

# ── Model / data status (cached) ─────────────────────────────────────────────
_, model_ok = load_model()
df, data_ok  = load_dataset()

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    sidebar_brand()

    # Theme toggle
    theme = get_theme()
    theme_label = "☀️ Light Mode" if theme == "dark" else "🌙 Dark Mode"
    if st.button(theme_label, key="theme_toggle", use_container_width=True):
        toggle_theme()
        st.rerun()

    # Grouped navigation
    active = st.session_state.active_page
    for group_label, items in NAV_GROUPS.items():
        sidebar_nav_label(group_label)
        for label, icon, _ in items:
            is_active = (active == label)
            css_class = "sb-nav-item active" if is_active else "sb-nav-item"
            st.markdown(f'<div class="{css_class}">', unsafe_allow_html=True)
            if st.button(f"{icon}  {label}", key=f"nav_{label}", use_container_width=True):
                st.session_state.active_page = label
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div style="margin-top:16px;"></div>', unsafe_allow_html=True)
    sidebar_nav_label("Model Status")
    sidebar_metric_card(model_ok, data_ok)
    sidebar_footer()

# ── Sticky header ─────────────────────────────────────────────────────────────
render_header(st.session_state.active_page, model_ok, data_ok, len(df))

# ── Page router ──────────────────────────────────────────────────────────────
PAGES[st.session_state.active_page].render()
