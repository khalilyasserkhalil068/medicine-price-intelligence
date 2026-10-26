"""
Theme module for the Medicine Price & Alternatives Intelligence Streamlit app.

Design goals
------------
1. ONE palette, TWO themes. Every surface / text colour is chosen from a token
   set that is picked at runtime, so the app is fully readable in BOTH
   Streamlit's Light and Dark mode.
2. No hard-coded *page* colours with ``!important``: that is what made the app
   unreadable and unmixable with Streamlit's built-in theme switcher.
3. Plotly tips are switched OFF by default (``PLOTLY_CONFIG``). Plotly's default
   ``showTips`` is True, which makes it pop up
   "Double-click on legend to isolate one trace" / "Double-click to zoom back out"
   tooltips over the charts. Those floating hints are removed here.

Brand palette (kept from the original design):
- #522D60 Royal Velvet Purple
- #80426E Plum Wine
- #F2A67B Sunset Peach
- #FFD38B Golden Warm Sand
"""

from string import Template
from typing import Any, Optional

import streamlit as st

# --------------------------------------------------------------------------- #
# Brand palette (theme independent)
# --------------------------------------------------------------------------- #
COLOR_PURPLE_DARK = "#522D60"
COLOR_PLUM = "#80426E"
COLOR_PEACH = "#F2A67B"
COLOR_GOLD = "#FFD38B"
COLOR_GOLD_SOFT = "#FFF2D9"
COLOR_PEACH_SOFT = "#FDECE4"

# Kept for backwards compatibility with older imports.
COLOR_BG_LIGHT = "#FAF7F9"
COLOR_SURFACE = "#FFFFFF"
COLOR_TEXT_DARK = "#281432"
COLOR_TEXT_MUTED = "#6B5872"

PLOTLY_PALETTE = [
    "#522D60",  # Royal Purple
    "#80426E",  # Plum Wine
    "#F2A67B",  # Sunset Peach
    "#FFD38B",  # Golden Sand
    "#3A1E45",  # Deep Aubergine
    "#A3588E",  # Light Plum
    "#D9845B",  # Deep Coral
    "#E6BE75",  # Muted Gold
]

PLOTLY_CONTINUOUS = [
    [0.0, "#522D60"],
    [0.35, "#80426E"],
    [0.70, "#F2A67B"],
    [1.0, "#FFD38B"],
]

# --------------------------------------------------------------------------- #
# Plotly configuration
# --------------------------------------------------------------------------- #
# showTips=False removes Plotly's "Double-click ..." floating hints.
PLOTLY_CONFIG: dict[str, Any] = {
    "showTips": False,
    "displaylogo": False,
    "scrollZoom": False,
    "modeBarButtonsToRemove": ["lasso2d", "select2d"],
}

_DARK_TOKENS = {
    "bg_top": "#140D1A",
    "bg_bottom": "#1F1228",
    "surface": "#251932",
    "surface_alt": "#2E2040",
    "surface_soft": "rgba(255, 255, 255, 0.04)",
    "text": "#F3EBF8",
    "text_muted": "#BFACC9",
    "heading": "#EBD9F3",
    "accent_text": "#F0D9A8",
    "border": "rgba(255, 211, 139, 0.18)",
    "border_strong": "rgba(255, 211, 139, 0.34)",
    "grid": "rgba(255, 255, 255, 0.07)",
    "axis_line": "rgba(255, 211, 139, 0.25)",
    "metric_bg": "#2A1C39",
    "shadow": "0 4px 16px -2px rgba(0, 0, 0, 0.45)",
    "shadow_hover": "0 8px 24px -4px rgba(242, 166, 123, 0.32)",
    "chart_paper": "rgba(37, 25, 50, 0.85)",
    "chart_plot": "rgba(20, 13, 26, 0.35)",
    "legend_bg": "rgba(37, 25, 50, 0.85)",
    "scroll_track": "#241832",
    "scroll_thumb": "#80426E",
}

_LIGHT_TOKENS = {
    "bg_top": "#FAF7F9",
    "bg_bottom": "#F3EDF4",
    "surface": "#FFFFFF",
    "surface_alt": "#F7F1F6",
    "surface_soft": "rgba(82, 45, 96, 0.04)",
    "text": "#241430",
    "text_muted": "#6B5872",
    "heading": "#522D60",
    "accent_text": "#522D60",
    "border": "rgba(128, 66, 110, 0.15)",
    "border_strong": "rgba(128, 66, 110, 0.30)",
    "grid": "rgba(128, 66, 110, 0.08)",
    "axis_line": "rgba(128, 66, 110, 0.20)",
    "metric_bg": "#FFFFFF",
    "shadow": "0 4px 16px -2px rgba(82, 45, 96, 0.06)",
    "shadow_hover": "0 8px 24px -4px rgba(242, 166, 123, 0.20)",
    "chart_paper": "rgba(255, 255, 255, 0.85)",
    "chart_plot": "rgba(250, 247, 249, 0.50)",
    "legend_bg": "rgba(255, 255, 255, 0.75)",
    "scroll_track": "#F3ECF2",
    "scroll_thumb": "#80426E",
}


def is_dark_mode() -> bool:
    """Return True when Streamlit is currently rendering in Dark mode.

    ``st.context.theme`` reflects the theme actually applied to the browser
    session, so the CSS rebuilt here always matches what the user sees. Falls
    back to Light mode when the context is unavailable (e.g. bare mode).
    """
    try:
        theme = st.context.theme  # type: ignore[attr-defined]
        theme_type = getattr(theme, "type", None)
        if isinstance(theme_type, str):
            return theme_type.lower() == "dark"
        if isinstance(theme, str):
            return theme.lower() == "dark"
    except Exception:
        pass
    return False


def get_theme_tokens() -> dict[str, str]:
    """Active colour tokens for the current Streamlit theme."""
    tokens = dict(_DARK_TOKENS if is_dark_mode() else _LIGHT_TOKENS)
    tokens.update(
        {
            "purple": COLOR_PURPLE_DARK,
            "plum": COLOR_PLUM,
            "peach": COLOR_PEACH,
            "gold": COLOR_GOLD,
        }
    )
    return tokens


# --------------------------------------------------------------------------- #
# CSS
# --------------------------------------------------------------------------- #
_CSS_TEMPLATE = Template(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&display=swap');

        /* ---------- Fonts ---------- */
        /* Emoji fonts are appended so glyphs never fall back to a text font,
           which is what caused emoji/text collisions. */
        html, body, p, span, label, div, input, button, select, textarea {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont,
                         'Segoe UI', Roboto, 'Apple Color Emoji', 'Segoe UI Emoji',
                         'Noto Color Emoji', sans-serif;
        }
        body, p, label, li {
            color: $text;
            line-height: 1.6;
        }

        /* ---------- Page shell ---------- */
        .stApp {
            background: linear-gradient(180deg, $bg_top 0%, $bg_bottom 100%);
        }
        .block-container {
            padding-top: 2rem !important;
            padding-bottom: 3.5rem !important;
            max-width: 1500px;
        }

        /* ---------- Headings ---------- */
        /* No negative letter-spacing and an explicit line-height: negative
           tracking plus inherited line-height is what made headings collide
           with adjacent emoji/inline elements. */
        h1, h2, h3 {
            color: $heading !important;
            font-weight: 800 !important;
            letter-spacing: 0 !important;
            line-height: 1.28 !important;
            margin-top: 0.4rem !important;
        }
        h4, h5, h6 {
            color: $accent_text !important;
            font-weight: 700 !important;
            letter-spacing: 0 !important;
            line-height: 1.35 !important;
        }
        [data-testid="stMarkdownContainer"] p {
            line-height: 1.65;
        }

        /* ---------- Hero ---------- */
        .luxury-hero {
            background: linear-gradient(135deg, #3D1C49 0%, $purple 45%, $plum 100%);
            padding: 2.2rem 2.4rem;
            border-radius: 1.25rem;
            color: #FFFFFF;
            margin-bottom: 2rem;
            border: 1px solid rgba(255, 211, 139, 0.25);
            box-shadow: 0 12px 30px -8px rgba(82, 45, 96, 0.35);
            position: relative;
            overflow: hidden;
        }
        .luxury-hero::after {
            content: '';
            position: absolute;
            top: -50px;
            right: -50px;
            width: 180px;
            height: 180px;
            background: radial-gradient(circle, rgba(255, 211, 139, 0.2) 0%, transparent 70%);
            border-radius: 50%;
            pointer-events: none;
        }
        .luxury-hero h1, .luxury-hero h2, .luxury-hero h3 {
            color: #FFFFFF !important;
            font-weight: 800;
            line-height: 1.3;
        }
        .luxury-hero p {
            color: #F8EBF4 !important;
            font-size: 1rem;
            line-height: 1.65;
        }

        /* ---------- Cards ---------- */
        .luxury-card {
            background: $surface;
            border: 1px solid $border;
            border-radius: 1rem;
            padding: 1.3rem;
            box-shadow: $shadow;
            margin-bottom: 0.8rem;
            transition: border-color 0.2s ease, box-shadow 0.2s ease;
            display: flex;
            flex-direction: column;
        }
        .luxury-card:hover {
            border-color: $peach;
            box-shadow: $shadow_hover;
        }
        .luxury-card p { color: $text_muted !important; }
        .luxury-card h4 { color: $heading !important; }
        .card-emoji {
            font-size: 1.7rem;
            line-height: 1.4;
            margin-bottom: 0.45rem;
            display: block;
            font-family: 'Apple Color Emoji', 'Segoe UI Emoji', 'Noto Color Emoji', sans-serif;
        }

        /* ---------- Eyebrow / highlight variants ---------- */
        /* Both of these must follow the theme: they previously hard-coded a
           near-white surface and a dark plum text colour, which became
           unreadable once Dark mode was switched on. */
        .hero-eyebrow {
            display: inline-block;
            padding: 0.25rem 0.85rem;
            border-radius: 9999px;
            background: $surface_soft;
            border: 1px solid $border_strong;
            font-size: 0.78rem;
            font-weight: 700;
            color: $accent_text;
            margin-bottom: 0.6rem;
            text-transform: uppercase;
            letter-spacing: 0.06em;
        }
        .highlight-card {
            background: linear-gradient(135deg, $surface 0%, $surface_alt 100%);
            border-left: 5px solid $purple;
        }

        /* ---------- Badges ---------- */
        .badge-gold, .badge-peach, .badge-purple {
            padding: 0.28rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.78rem;
            font-weight: 700;
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
            line-height: 1.45;
            white-space: nowrap;
            vertical-align: middle;
        }
        .badge-gold {
            background: linear-gradient(135deg, $gold_soft, $gold);
            color: #5C3A00;
            border: 1px solid rgba(255, 211, 139, 0.6);
        }
        .badge-peach {
            background: linear-gradient(135deg, $peach_soft, $peach);
            color: #632C10;
            border: 1px solid rgba(242, 166, 123, 0.5);
        }
        .badge-purple {
            background: linear-gradient(135deg, $purple, $plum);
            color: #FFFFFF;
            border: 1px solid rgba(255, 211, 139, 0.3);
        }

        /* ---------- Sidebar status list (overlap fix) ----------
           The original markup was <br>-separated lines containing inline
           <code> chips. The chips' padding made them taller than the line box,
           so every row overlapped the next one. Each row is now a flex line. */
        .status-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 0.5rem;
            padding: 0.3rem 0;
            line-height: 1.5;
            border-bottom: 1px dashed rgba(255, 211, 139, 0.14);
        }
        .status-row:last-child { border-bottom: none; }
        .status-label {
            font-size: 0.82rem;
            color: #F8EDF5;
            line-height: 1.5;
            min-width: 0;
            overflow-wrap: anywhere;
        }
        .status-chip {
            flex: 0 0 auto;
            font-size: 0.7rem;
            font-weight: 700;
            line-height: 1.4;
            padding: 0.1rem 0.5rem;
            border-radius: 9999px;
            background: rgba(255, 211, 139, 0.14);
            border: 1px solid rgba(255, 211, 139, 0.3);
            color: $gold;
            white-space: nowrap;
        }

        /* ---------- Metrics ---------- */
        [data-testid="stMetric"] {
            background: $metric_bg;
            border: 1px solid $border;
            border-radius: 1rem;
            padding: 0.95rem 1.1rem;
            box-shadow: $shadow;
            transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
        }
        [data-testid="stMetric"]:hover {
            transform: translateY(-2px);
            border-color: $peach;
            box-shadow: $shadow_hover;
        }
        [data-testid="stMetricLabel"] {
            color: $text_muted !important;
            font-size: 0.78rem !important;
            font-weight: 600 !important;
            text-transform: uppercase;
            letter-spacing: 0.03em;
            line-height: 1.45 !important;
        }
        [data-testid="stMetricLabel"] p {
            color: $text_muted !important;
            overflow-wrap: anywhere;
        }
        [data-testid="stMetricValue"] {
            color: $accent_text !important;
            font-size: 1.6rem !important;
            font-weight: 800 !important;
            line-height: 1.35 !important;
            letter-spacing: 0 !important;
            overflow-wrap: anywhere;
        }
        [data-testid="stMetricDelta"] {
            font-weight: 700 !important;
            font-size: 0.85rem !important;
        }

        /* ---------- Buttons ---------- */
        .stButton > button,
        .stDownloadButton > button,
        [data-testid="stDownloadButton"] > button {
            background: linear-gradient(135deg, $peach 0%, #E28C60 100%) !important;
            color: #FFFFFF !important;
            border: none !important;
            border-radius: 0.75rem !important;
            padding: 0.55rem 1.4rem !important;
            font-weight: 700 !important;
            font-size: 0.9rem !important;
            line-height: 1.4 !important;
            box-shadow: 0 4px 12px rgba(242, 166, 123, 0.35) !important;
            transition: all 0.2s ease !important;
        }
        .stButton > button p,
        .stButton > button span,
        .stDownloadButton > button p,
        .stDownloadButton > button span,
        [data-testid="stDownloadButton"] > button p,
        [data-testid="stDownloadButton"] > button span {
            color: #FFFFFF !important;
            font-weight: 700 !important;
        }
        .stButton > button:hover,
        .stDownloadButton > button:hover,
        [data-testid="stDownloadButton"] > button:hover {
            background: linear-gradient(135deg, #E28C60 0%, #C76F43 100%) !important;
            transform: translateY(-1px) !important;
            box-shadow: 0 6px 18px rgba(242, 166, 123, 0.45) !important;
        }

        /* ---------- Page links ---------- */
        div[data-testid="stPageLink"] a {
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            gap: 0.5rem !important;
            background: linear-gradient(135deg, $purple 0%, $plum 100%) !important;
            border: 1px solid rgba(255, 211, 139, 0.3) !important;
            border-radius: 0.75rem !important;
            padding: 0.6rem 1.1rem !important;
            font-weight: 700 !important;
            font-size: 0.87rem !important;
            line-height: 1.4 !important;
            text-decoration: none !important;
            box-shadow: 0 4px 12px rgba(82, 45, 96, 0.2) !important;
            transition: all 0.25s ease !important;
        }
        div[data-testid="stPageLink"] a p,
        div[data-testid="stPageLink"] a span {
            color: #FFFFFF !important;
            font-weight: 700 !important;
        }
        div[data-testid="stPageLink"] a:hover {
            background: linear-gradient(135deg, $peach 0%, #E28C60 100%) !important;
            border-color: $gold !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 18px rgba(242, 166, 123, 0.35) !important;
        }
        div[data-testid="stPageLink"] a:hover p,
        div[data-testid="stPageLink"] a:hover span { color: #FFFFFF !important; }

        /* ---------- Inputs ---------- */
        div[data-baseweb="select"] > div {
            border-radius: 0.75rem !important;
            border-color: $border_strong !important;
            background-color: $surface !important;
        }
        div[data-baseweb="select"] > div:focus-within {
            border-color: $peach !important;
            box-shadow: 0 0 0 2px rgba(242, 166, 123, 0.25) !important;
        }
        div[data-baseweb="tag"] {
            background: linear-gradient(135deg, rgba(82, 45, 96, 0.12), rgba(128, 66, 110, 0.18)) !important;
            border: 1px solid rgba(128, 66, 110, 0.3) !important;
            border-radius: 9999px !important;
        }
        div[data-baseweb="tag"] span { color: $accent_text !important; font-weight: 600 !important; }
        input[type="text"], input[type="number"], textarea {
            border-radius: 0.75rem !important;
            border-color: $border_strong !important;
            background-color: $surface !important;
            color: $text !important;
        }
        input[type="text"]:focus, input[type="number"]:focus, textarea:focus {
            border-color: $peach !important;
            box-shadow: 0 0 0 2px rgba(242, 166, 123, 0.25) !important;
        }

        /* ---------- Radio / checkbox ---------- */
        div[data-testid="stRadio"] label, div[data-testid="stCheckbox"] label {
            font-weight: 600 !important;
            color: $text !important;
        }
        div[data-testid="stRadio"] label p { color: $text !important; }
        div[data-testid="stRadio"] [role="radiogroup"] { gap: 1.2rem; flex-wrap: wrap; }

        /* ---------- Tabs ---------- */
        .stTabs [data-baseweb="tab-list"] {
            gap: 0.6rem;
            border-bottom: 2px solid $border;
        }
        .stTabs [data-baseweb="tab"] {
            border-radius: 0.6rem 0.6rem 0 0;
            padding: 0.6rem 1.2rem;
            font-weight: 700;
            color: $text_muted;
        }
        .stTabs [aria-selected="true"] {
            color: $accent_text !important;
            border-bottom-color: $peach !important;
        }

        /* ---------- Expanders / alerts / tables ---------- */
        div[data-testid="stExpander"] {
            background: $surface !important;
            border: 1px solid $border !important;
            border-radius: 0.85rem !important;
            box-shadow: $shadow !important;
            margin-bottom: 1rem !important;
        }
        div[data-testid="stExpander"] summary {
            font-weight: 700 !important;
            color: $heading !important;
        }
        div[data-testid="stExpander"] summary p { color: $heading !important; }
        div[data-testid="stExpander"] p { color: $text !important; }
        div[data-testid="stAlert"] { border-radius: 0.85rem !important; font-size: 0.92rem !important; }
        [data-testid="stDataFrame"] {
            border-radius: 0.85rem;
            overflow: hidden;
            border: 1px solid $border;
            box-shadow: $shadow;
        }

        /* ---------- Sidebar (brand gradient in both themes) ---------- */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #2D1435 0%, $purple 60%, $plum 100%) !important;
        }
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] li { color: #F8EDF5; }
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3 { color: $gold !important; }
        [data-testid="stSidebar"] h4,
        [data-testid="stSidebar"] h5,
        [data-testid="stSidebar"] h6 { color: $peach !important; }
        [data-testid="stSidebar"] hr { border-color: rgba(255, 211, 139, 0.2) !important; }
        [data-testid="stSidebarNavLink"] {
            border-radius: 0.6rem !important;
            margin: 0.12rem 0 !important;
            transition: background 0.2s ease !important;
        }
        [data-testid="stSidebarNavLink"] span { line-height: 1.5 !important; }
        [data-testid="stSidebarNavLink"]:hover { background: rgba(255, 211, 139, 0.12) !important; }
        [data-testid="stSidebarNavLink"][aria-current="page"] {
            background: linear-gradient(135deg, rgba(242, 166, 123, 0.25) 0%, rgba(255, 211, 139, 0.18) 100%) !important;
            border-left: 3px solid $gold !important;
        }
        [data-testid="stSidebarNavLink"][aria-current="page"] span {
            color: $gold !important;
            font-weight: 700 !important;
        }
        .sidebar-hero-emoji {
            font-size: 2.6rem;
            line-height: 1.35;
            margin-bottom: 0.4rem;
            display: block;
            font-family: 'Apple Color Emoji', 'Segoe UI Emoji', 'Noto Color Emoji', sans-serif;
        }

        /* ---------- Scrollbars ---------- */
        ::-webkit-scrollbar { width: 7px; height: 7px; }
        ::-webkit-scrollbar-track { background: $scroll_track; }
        ::-webkit-scrollbar-thumb { background: $scroll_thumb; border-radius: 4px; }
        ::-webkit-scrollbar-thumb:hover { background: $purple; }
    </style>
    """
)


def html_block(markup: str) -> str:
    """Return ``markup`` as ONE safe Markdown HTML block.

    Streamlit renders markdown in the browser, and two markdown rules break a
    normally-indented Python HTML string:

    1. **A blank line ENDS an HTML block.** An expression such as
       ``{"" if cond else "<span>..</span>"}`` collapses to a blank line when the
       condition is false, which closes the HTML block early.
    2. **A line indented by 4+ spaces starts an INDENTED CODE BLOCK.** Once the
       block above is closed, the remaining (indented) markup is treated as code
       and printed on the page as raw text instead of being rendered.

    Together those two rules are why raw ``<div>``/``<p>`` tags leaked onto the
    "Selected Medicine Overview" card. Stripping the indentation and dropping
    blank lines removes both failure modes.
    """
    lines = [line.strip() for line in str(markup).strip().splitlines()]
    return "\n".join(line for line in lines if line)


def apply_luxury_styles() -> None:
    """Inject the brand CSS for the theme Streamlit is currently using."""
    tokens = get_theme_tokens()
    tokens["gold_soft"] = COLOR_GOLD_SOFT
    tokens["peach_soft"] = COLOR_PEACH_SOFT
    st.markdown(_CSS_TEMPLATE.substitute(tokens), unsafe_allow_html=True)


def get_luxury_chart_layout(title: Optional[str] = None, height: int = 400) -> dict:
    """Consistent, theme-aware Plotly layout settings."""
    tokens = get_theme_tokens()
    layout = dict(
        font=dict(family="Plus Jakarta Sans", color=tokens["text"]),
        paper_bgcolor=tokens["chart_paper"],
        plot_bgcolor=tokens["chart_plot"],
        margin=dict(l=30, r=30, t=55 if title else 40, b=40),
        height=height,
        colorway=PLOTLY_PALETTE,
        hoverlabel=dict(font=dict(family="Plus Jakarta Sans", size=12)),
        xaxis=dict(
            gridcolor=tokens["grid"],
            linecolor=tokens["axis_line"],
            tickfont=dict(size=11, color=tokens["text_muted"]),
        ),
        yaxis=dict(
            gridcolor=tokens["grid"],
            linecolor=tokens["axis_line"],
            tickfont=dict(size=11, color=tokens["text_muted"]),
        ),
        legend=dict(
            font=dict(size=11, color=tokens["text"]),
            bgcolor=tokens["legend_bg"],
            bordercolor=tokens["border"],
            borderwidth=1,
        ),
    )
    if title:
        layout["title"] = dict(
            text=f"<b>{title}</b>",
            font=dict(family="Plus Jakarta Sans", size=15, color=tokens["heading"]),
            x=0.02,
            xanchor="left",
        )
    return layout
