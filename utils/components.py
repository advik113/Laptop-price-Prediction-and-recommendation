"""
utils/components.py
----------------------------------------------------------------------
Reusable HTML/Streamlit component builders — v2.1 (No JavaScript).
No ML / data logic lives here.
----------------------------------------------------------------------
"""

import streamlit as st


# ── Theme Initialisation ─────────────────────────────────────────────────────

def init_theme():
    """Call once from app.py before any rendering to seed session state."""
    if "theme" not in st.session_state:
        st.session_state.theme = "dark"


def get_theme() -> str:
    return st.session_state.get("theme", "dark")


def toggle_theme():
    st.session_state.theme = "light" if get_theme() == "dark" else "dark"


# ── CSS Injection ─────────────────────────────────────────────────────────────

def inject_css(path="assets/style.css"):
    """Inject stylesheet. Theme is applied via a body class using pure CSS."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            css = f.read()
    except FileNotFoundError:
        css = ""

    theme = get_theme()
    # We apply the theme by injecting a class on a wrapper div,
    # and the CSS uses that selector. No JS needed.
    theme_class = "theme-dark" if theme == "dark" else "theme-light"

    st.markdown(
    f'<div id="theme-root" class="{theme_class}" style="display:none;"></div>',
    unsafe_allow_html=True
)

    # Inject theme override block based on current theme selection
    if theme == "light":
        st.markdown("""
        <style>
        :root {
          --bg-base:      #f5f6fa;
          --bg-surface:   #ffffff;
          --bg-elevated:  #f0f1f8;
          --bg-overlay:   #e8eaf4;
          --glass-bg:     rgba(255,255,255,0.80);
          --glass-bg-md:  rgba(255,255,255,0.92);
          --glass-bg-lg:  rgba(255,255,255,0.96);
          --glass-border: rgba(0,0,0,0.08);
          --glass-border-strong: rgba(0,0,0,0.14);
          --text-primary:   #0f1117;
          --text-secondary: #4b5168;
          --text-tertiary:  #8b91a8;
          --text-inverse:   #ffffff;
          --accent-dim:     rgba(99,102,241,0.10);
          --accent-border:  rgba(99,102,241,0.25);
          --grad-subtle: linear-gradient(135deg, rgba(99,102,241,.07), rgba(139,92,246,.05) 60%, rgba(6,182,212,.04));
          --shadow-sm: 0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.05);
          --shadow-md: 0 4px 16px rgba(0,0,0,0.10);
          --shadow-lg: 0 12px 40px rgba(0,0,0,0.14);
        }
        body, [data-testid="stAppViewContainer"] {
          background-color: #f5f6fa !important;
          color: #0f1117 !important;
        }
        [data-testid="stSidebar"] {
          background-color: #ffffff !important;
        }
        [data-testid="stHeader"] {
          background-color: rgba(245,246,250,0.85) !important;
        }
        .stMarkdown, .stText, p, div {
          color: inherit;
        }
        label { color: #4b5168 !important; }
        .stDataFrame { color: #0f1117 !important; }
        </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <style>
        body, [data-testid="stAppViewContainer"] {
          background-color: #08090e !important;
          color: #f1f2f6 !important;
        }
        [data-testid="stSidebar"] {
          background-color: #0d0f17 !important;
        }
        [data-testid="stHeader"] {
          background-color: rgba(8,9,14,0.85) !important;
        }
        </style>
        """, unsafe_allow_html=True)


# ── Sticky Command-Bar Header ─────────────────────────────────────────────────

def render_header(page_name: str, model_ok: bool = True, data_ok: bool = True, num_rows: int = 1303):
    """Floating sticky header with breadcrumb and status beacon."""
    status_cls   = "live" if model_ok else "demo"
    status_label = "Live Model" if model_ok else "Demo Mode"
    data_label   = f"{num_rows:,} rows" if data_ok else "Sample data"

    st.markdown(f"""
    <div class="cmd-header" id="cmd-header">
        <div class="cmd-header-left">
            <div class="cmd-breadcrumb">
                <span>💻 Smart Laptop Advisor</span>
                <span class="sep">›</span>
                <span class="page-name">{page_name}</span>
            </div>
        </div>
        <div class="cmd-header-right">
            <span class="header-pill">📦 {data_label}</span>
            <span class="status-beacon {status_cls}">{status_label}</span>
            <span class="header-pill">R² 0.918</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── Sidebar Brand Block ───────────────────────────────────────────────────────

def sidebar_brand():
    st.markdown("""
    <div class="sb-brand">
        <div class="sb-logo-icon">💻</div>
        <div class="sb-brand-text">
            <div class="sb-brand-name">Smart Laptop Advisor</div>
            <div class="sb-brand-sub">AI Price Intelligence</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def sidebar_nav_label(label: str):
    st.markdown(f'<div class="sb-nav-group-label">{label}</div>', unsafe_allow_html=True)


def sidebar_metric_card(model_ok: bool, data_ok: bool):
    status_color = "#22c55e" if model_ok else "#f59e0b"
    status_label = "Live model" if model_ok else "Demo mode"
    st.markdown(f"""
    <div class="sb-info-section">
        <div class="sb-metric-card">
            <div class="sb-metric-row">
                <span class="mk">Status</span>
                <span class="mv" style="color:{status_color}">{status_label}</span>
            </div>
            <div class="sb-metric-row">
                <span class="mk">R² Score</span>
                <span class="mv">0.9182</span>
            </div>
            <div class="sb-metric-row">
                <span class="mk">Algorithm</span>
                <span class="mv">XGBoost</span>
            </div>
            <div class="sb-metric-row">
                <span class="mk">Dataset</span>
                <span class="mv">{"Loaded" if data_ok else "Sample"}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def sidebar_footer():
    st.markdown("""
    <div class="sb-footer">
        Built with Streamlit · Plotly · XGBoost<br>
        © 2026 Smart Laptop Advisor
    </div>
    """, unsafe_allow_html=True)


# ── Page-level components ─────────────────────────────────────────────────────

def hero(eyebrow: str, title_html: str, subtitle: str):
    st.markdown(f"""
    <div class="hero-wrap">
        <div class="hero-eyebrow">⚡ {eyebrow}</div>
        <div class="hero-title">{title_html}</div>
        <div class="hero-sub">{subtitle}</div>
    </div>
    """, unsafe_allow_html=True)


def kpi_card(icon: str, value: str, label: str, delta: str = None, delta_state: str = "up") -> str:
    delta_html = ""
    if delta:
        delta_html = f'<div class="kpi-delta {delta_state}">{delta}</div>'
    return f"""
    <div class="kpi-card fade-up">
        <div class="kpi-icon">{icon}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-label">{label}</div>
        {delta_html}
    </div>
    """


def section_head(title: str, caption: str = ""):
    caption_html = f'<div class="section-caption">{caption}</div>' if caption else ""
    st.markdown(f"""
    <div class="section-head">
        <div>
            <div class="section-title">{title}</div>
            {caption_html}
        </div>
    </div>
    """, unsafe_allow_html=True)


def form_section_label(label: str):
    """Styled section divider for multi-step forms."""
    st.markdown(f'<div class="form-section-label">{label}</div>', unsafe_allow_html=True)


def glass_card_open(extra_class: str = ""):
    st.markdown(f'<div class="glass-card hover-lift {extra_class}">', unsafe_allow_html=True)


def glass_card_close():
    st.markdown('</div>', unsafe_allow_html=True)


def pill(text: str, kind: str = "") -> str:
    return f'<span class="pill {kind}">{text}</span>'


def rank_row(rank: int, name: str, value: float, max_value: float) -> str:
    pct = max(4, int((value / max_value) * 100))
    return f"""
    <div class="rank-row">
        <div class="rank-num">{rank:02d}</div>
        <div class="rank-name">{name}</div>
        <div class="rank-bar-bg"><div class="rank-bar-fill" style="width:{pct}%"></div></div>
        <div class="rank-val">{value:.2f}</div>
    </div>
    """


def cmp_row(label: str, val_a: str, val_b: str, winner: str = None) -> str:
    a_cls = "v win" if winner == "a" else "v"
    b_cls = "v win" if winner == "b" else "v"
    return f"""
    <div class="cmp-row">
        <div class="{a_cls}">{val_a}</div>
        <div class="k">{label}</div>
        <div class="{b_cls}">{val_b}</div>
    </div>
    """


def foot_note(text: str):
    st.markdown(f'<div class="foot-note">{text}</div>', unsafe_allow_html=True)
