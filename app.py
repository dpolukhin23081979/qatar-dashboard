import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import os

# ── Page config ───────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Qatar 2030 Labor Market Intelligence",
    page_icon="⛵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Palette ───────────────────────────────────────────────────────────────
BG_PAGE   = "#F5F2EE"
BG_CARD   = "#FFFFFF"
BG_RAISED = "#EDE8E2"
TXT_PRI   = "#1A1410"
TXT_SEC   = "#5A5248"
TXT_MUTED = "#9A9088"
ACCENT    = "#8B2635"
ACCENT_LT = "#C0564A"
SAND      = "#C49040"
BORDER    = "#E0D8D0"

# ── Custom CSS ────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; color: #1A1410; }
h1, h2, h3 { font-family: 'DM Serif Display', serif; color: #1A1410 !important; }
.main { background-color: #F5F2EE; }
.stApp { background-color: #F5F2EE; }
section[data-testid="stMain"] { background-color: #F5F2EE; }
div[data-testid="stTabs"] { background-color: #F5F2EE; }
button[data-baseweb="tab"] { color: #9A9088 !important; background: transparent !important; }
button[data-baseweb="tab"][aria-selected="true"] { color: #1A1410 !important; border-bottom-color: #8B2635 !important; }

.metric-card {
    background: #FFFFFF;
    border-radius: 12px;
    padding: 20px 24px;
    border: 1px solid #E0D8D0;
    border-left: 4px solid #8B2635;
    margin-bottom: 8px;
}
.metric-value { font-size: 2rem; font-weight: 600; color: #8B2635; line-height: 1; }
.metric-label { font-size: 0.8rem; color: #9A9088; text-transform: uppercase; letter-spacing: 0.08em; margin-top: 4px; }

.section-header {
    font-family: 'DM Serif Display', serif;
    font-size: 1.4rem;
    color: #1A1410 !important;
    border-bottom: 2px solid #8B2635;
    padding-bottom: 8px;
    margin: 24px 0 16px 0;
}

div[data-testid="stSidebarContent"] { background-color: #EDE8E2 !important; }
div[data-testid="stSidebarContent"] label { color: #1A1410 !important; }
div[data-testid="stSidebarContent"] p { color: #5A5248 !important; }
div[data-testid="stSidebarContent"] h1,
div[data-testid="stSidebarContent"] h2,
div[data-testid="stSidebarContent"] h3 { color: #1A1410 !important; }
div[data-testid="stMarkdownContainer"] p { color: #1A1410; }
div[data-testid="stCaptionContainer"] p { color: #9A9088 !important; }
div[data-testid="stDownloadButton"] button { background-color: #8B2635 !important; color: white !important; border: none; }
hr { border-color: #E0D8D0; }

div[data-baseweb="select"] > div { background-color: #FFFFFF !important; border-color: #E0D8D0 !important; }
div[data-baseweb="select"] * { color: #1A1410 !important; }
div[data-baseweb="popover"] { background-color: #FFFFFF !important; }
ul[data-baseweb="menu"] { background-color: #FFFFFF !important; }
ul[data-baseweb="menu"] li { color: #1A1410 !important; }
ul[data-baseweb="menu"] li:hover { background-color: #F5F2EE !important; }
div[data-baseweb="tag"] { background-color: #EDE8E2 !important; border-color: #E0D8D0 !important; }
div[data-baseweb="tag"] span { color: #1A1410 !important; }
div[data-baseweb="tag"] svg { fill: #5A5248 !important; }
div[data-testid="stMultiSelect"] * { color: #1A1410 !important; }
div[data-testid="stSlider"] * { color: #1A1410 !important; }
div[data-testid="stRadio"] * { color: #1A1410 !important; }
input { background-color: #FFFFFF !important; color: #1A1410 !important; }
div[data-testid="stTextInput"] input { border-color: #E0D8D0 !important; }
</style>
""", unsafe_allow_html=True)

# ── Data loading ──────────────────────────────────────────────────────────
DATA_DIR = Path("data")

@st.cache_data
def load_data():
    gap     = pd.read_csv(DATA_DIR / "scenario_gap_analysis.csv")
    matrix  = pd.read_csv(DATA_DIR / "scenario_skill_matrix.csv")
    calib   = pd.read_csv(DATA_DIR / "scenario_calibration.csv")
    sources = pd.read_csv(DATA_DIR / "scenario_sources_raw.csv")
    gap["gap_score"] = gap["gap_score"].clip(-1.0, 1.0)
    return gap, matrix, calib, sources

@st.cache_data
def load_optional(filename):
    path = DATA_DIR / filename
    if path.exists():
        return pd.read_csv(path)
    return None

gap_df, matrix_df, calib_df, sources_df = load_data()
coeff_df    = load_optional("scenario_coefficients.csv")
skill_wt_df = load_optional("scenario_skill_weights.csv")

# ── Constants ─────────────────────────────────────────────────────────────
SCENARIO_LABELS = {
    "S1": "S1: Diversification Acceleration",
    "S2": "S2: Hydrocarbon Dominance",
    "S3": "S3: Green Transition Pressure",
    "S4": "S4: Knowledge Economy Leap",
    "S5": "S5: Regional Hub & Geopolitical Pivot",
}
SCENARIO_COLORS = {
    "S1": "#C0564A",
    "S2": "#C49040",
    "S3": "#5A8A64",
    "S4": "#4A7A9B",
    "S5": "#8A6A80",
}
SECTOR_LABELS = {
    "technology_digital":       "Technology & Digital",
    "energy_lng":               "Energy & LNG",
    "healthcare":               "Healthcare",
    "education":                "Education",
    "finance_banking":          "Finance & Banking",
    "construction_real_estate": "Construction & Real Estate",
    "tourism_hospitality":      "Tourism & Hospitality",
    "cross_sector":             "Cross-Sector",
}
SECTOR_COLORS = {
    "technology_digital":       "#4A7A9B",
    "energy_lng":               "#C49040",
    "healthcare":               "#5A8A64",
    "education":                "#8A6A80",
    "finance_banking":          "#C0564A",
    "construction_real_estate": "#7A6A5A",
    "tourism_hospitality":      "#4A8A8A",
    "cross_sector":             "#9A9088",
}

ALL_SCENARIOS = ["S1", "S2", "S3", "S4", "S5"]

def img_path(filename):
    p = DATA_DIR / filename
    return p if p.exists() else None

def first_existing_column(df, candidates):
    for c in candidates:
        if c in df.columns:
            return c
    return None

def apply_chart_theme(fig, height=None):
    fig.update_layout(
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#F5F2EE",
        font=dict(color="#1A1410"),
        title_font=dict(color="#1A1410"),
    )
    fig.update_xaxes(gridcolor="#E0D8D0", linecolor="#E0D8D0", tickcolor="#9A9088")
    fig.update_yaxes(gridcolor="#E0D8D0", linecolor="#E0D8D0", tickcolor="#9A9088")
    if height is not None:
        fig.update_layout(height=height)
    return fig

# ── Helper: card HTML ─────────────────────────────────────────────────────
def card(content, extra_style=""):
    return f'<div class="metric-card" style="{extra_style}">{content}</div>'

def card_label(text):
    return f'<div style="font-size:0.7rem;color:#9A9088;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:8px;">{text}</div>'

def card_body(text):
    return f'<div style="font-size:0.9rem;color:#1A1410;line-height:1.6;">{text}</div>'

# ── Live coefficient dashboard ────────────────────────────────────────────
def render_live_coeff_dashboard(df):
    if df is None or df.empty:
        st.warning("No scenario coefficient data found. Add `scenario_coefficients.csv` to render this section.")
        return

    scenario_col  = first_existing_column(df, ["scenario", "scenario_id", "scenario_code"])
    source_col    = first_existing_column(df, ["source_id", "source", "source_name", "publication"])
    total_col     = first_existing_column(df, ["total_weighted", "weighted_score", "contribution", "total_score", "adjusted_weight"])
    quality_col   = first_existing_column(df, ["quality_weight", "source_quality_weight", "quality"])
    scenario_w_col= first_existing_column(df, ["scenario_weight", "scenario_coefficient", "scenario_coef", "coefficient"])
    penalty_col   = first_existing_column(df, ["signal_count_penalty", "signal_penalty", "penalty", "count_penalty"])

    if scenario_col is None or total_col is None:
        st.warning(f"Required columns missing. Available: {list(df.columns)}")
        st.dataframe(df, use_container_width=True, hide_index=True)
        return

    work = df.copy()
    if source_col is None:
        work["source_label"] = [f"Source {i+1}" for i in range(len(work))]
        source_col = "source_label"

    summary = (
        work.groupby(scenario_col, as_index=False)[total_col]
        .agg(["mean", "sum", "count"]).reset_index()
        .rename(columns={"mean": "avg_contribution", "sum": "total_contribution", "count": "n_sources"})
    )
    if scenario_col not in summary.columns:
        summary = summary.rename(columns={summary.columns[0]: scenario_col})
    summary["scenario_label"] = summary[scenario_col].map(SCENARIO_LABELS).fillna(summary[scenario_col])

    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(
            summary.sort_values("avg_contribution", ascending=False),
            x="scenario_label", y="avg_contribution",
            color=scenario_col, color_discrete_map=SCENARIO_COLORS,
            labels={"scenario_label": "", "avg_contribution": "Average weighted contribution"},
            title="Average source contribution by scenario",
        )
        apply_chart_theme(fig, 420)
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        top_sources = (
            work.groupby([scenario_col, source_col], as_index=False)[total_col]
            .sum().sort_values(total_col, ascending=False).head(20)
        )
        top_sources["scenario_label"] = top_sources[scenario_col].map(SCENARIO_LABELS).fillna(top_sources[scenario_col])
        fig = px.bar(
            top_sources.sort_values(total_col),
            x=total_col, y=source_col, color=scenario_col,
            color_discrete_map=SCENARIO_COLORS, orientation="h",
            labels={total_col: "Total weighted contribution", source_col: ""},
            title="Top contributing sources across scenarios",
            hover_data=["scenario_label"],
        )
        apply_chart_theme(fig, 420)
        st.plotly_chart(fig, use_container_width=True)

    metric_candidates = [c for c in [quality_col, scenario_w_col, penalty_col, total_col] if c is not None]
    if len(metric_candidates) >= 2:
        metric_map = work.groupby(scenario_col)[metric_candidates].mean(numeric_only=True).round(3)
        metric_map.index = metric_map.index.map(lambda x: SCENARIO_LABELS.get(x, x))
        fig = px.imshow(metric_map.T, color_continuous_scale="RdPu", text_auto=".2f",
                        aspect="auto", title="Coefficient mechanics by scenario (average values)")
        apply_chart_theme(fig, 420)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="section-header">Detailed coefficient table</div>', unsafe_allow_html=True)
    scenario_options = ["All"] + list(work[scenario_col].dropna().astype(str).unique())
    selected = st.selectbox("Scenario detail", scenario_options,
                            format_func=lambda x: "All" if x == "All" else SCENARIO_LABELS.get(x, x),
                            key="live_coeff_scenario")
    detail = work if selected == "All" else work[work[scenario_col].astype(str) == selected]
    sort_col = total_col if total_col in detail.columns else detail.columns[0]
    st.dataframe(detail.sort_values(sort_col, ascending=False), use_container_width=True, hide_index=True)

def render_live_skill_weight_dashboard(df):
    if df is None or df.empty:
        st.warning("No skill weight data found. Add `scenario_skill_weights.csv` to render this section.")
        return

    scenario_col = first_existing_column(df, ["scenario", "scenario_id", "scenario_code"])
    skill_col    = first_existing_column(df, ["skill_category", "skill", "skill_name"])
    sector_col   = first_existing_column(df, ["sector", "industry_sector", "sector_name"])
    weight_col   = first_existing_column(df, ["normalized_weight", "weight", "adjusted_weight", "score"])

    if scenario_col is None or skill_col is None or weight_col is None:
        st.warning(f"Required columns missing. Available: {list(df.columns)}")
        st.dataframe(df, use_container_width=True, hide_index=True)
        return

    work = df.copy()
    if sector_col is None:
        work["sector_fallback"] = "cross_sector"
        sector_col = "sector_fallback"

    work["scenario_label"] = work[scenario_col].map(SCENARIO_LABELS).fillna(work[scenario_col])
    work["sector_label"]   = work[sector_col].map(lambda x: SECTOR_LABELS.get(x, x))

    pivot = work.pivot_table(index=skill_col, columns=scenario_col, values=weight_col, aggfunc="mean").fillna(0)
    scenario_order = [s for s in ALL_SCENARIOS if s in pivot.columns] + [c for c in pivot.columns if c not in ALL_SCENARIOS]
    pivot = pivot[scenario_order]
    pivot["avg_weight"] = pivot.mean(axis=1)
    top_universal = pivot.sort_values("avg_weight", ascending=False).head(20).copy()
    heat = top_universal.drop(columns="avg_weight")
    heat.columns = [SCENARIO_LABELS.get(c, c) for c in heat.columns]

    bar_df = top_universal[["avg_weight"]].reset_index().sort_values("avg_weight")
    fig_bar = px.bar(bar_df, x="avg_weight", y=skill_col, orientation="h",
                     labels={"avg_weight": "Average normalized weight", skill_col: ""},
                     title="Most consistently important skills across scenarios")
    apply_chart_theme(fig_bar, 560)
    st.plotly_chart(fig_bar, use_container_width=True)

    fig_heat = px.imshow(heat, color_continuous_scale="RdPu",
                         zmin=0, zmax=max(1.0, float(heat.to_numpy().max()) if heat.size else 1.0),
                         text_auto=".2f", aspect="auto",
                         title="Cross-scenario skill importance matrix")
    fig_heat.update_traces(textfont=dict(size=12))
    apply_chart_theme(fig_heat, 560)
    st.plotly_chart(fig_heat, use_container_width=True)

# ── Sidebar ───────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div style="font-family:\'DM Serif Display\',serif;font-size:1.3rem;color:#1A1410;padding:8px 0;">⛵ Qatar 2030<br>Labor Market Intelligence</div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### Filters")

    selected_scenarios = st.multiselect(
        "Scenarios", options=ALL_SCENARIOS, default=ALL_SCENARIOS,
        format_func=lambda x: SCENARIO_LABELS[x]
    )
    all_sectors = sorted(gap_df["sector"].unique().tolist())
    selected_sectors = st.multiselect(
        "Sectors", options=all_sectors, default=all_sectors,
        format_func=lambda x: SECTOR_LABELS.get(x, x)
    )
    qat_filter  = st.selectbox("Qatarization Relevance", ["All", "high", "medium", "low"])
    time_filter = st.selectbox("Time Horizon", ["All", "near_term", "medium_term", "both"])

    st.markdown("---")
    st.markdown("**Data sources**")
    st.markdown(f"- 41 publications")
    st.markdown(f"- {len(sources_df)} skill signals")
    st.markdown(f"- {gap_df['skill_category'].nunique()} skill categories")
    st.markdown(f"- 5 scenarios · Horizon 2030")

# ── Filter helper ─────────────────────────────────────────────────────────
def apply_filters(df):
    d = df.copy()
    if selected_scenarios: d = d[d["scenario"].isin(selected_scenarios)]
    if selected_sectors:   d = d[d["sector"].isin(selected_sectors)]
    if qat_filter  != "All": d = d[d["qatarization_relevance"] == qat_filter]
    if time_filter != "All": d = d[d["time_horizon"] == time_filter]
    return d

gap_f    = apply_filters(gap_df)
matrix_f = matrix_df[matrix_df["scenario"].isin(selected_scenarios or ALL_SCENARIOS)]
sources_f= sources_df[sources_df["scenario"].isin(selected_scenarios or ALL_SCENARIOS)]

# ── Header ────────────────────────────────────────────────────────────────
st.markdown("# Qatar 2030 Labor Market Intelligence")
st.markdown("*Strategic Skill Demand Scenarios — Evidence-based workforce gap analysis for Manara & QNV 2030*")
st.markdown("---")

# ── KPI row ───────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)
top_gap = gap_f[gap_f["gap_score"] > 0]
with k1:
    st.markdown(f'<div class="metric-card"><div class="metric-value">{len(top_gap)}</div><div class="metric-label">Skill Gaps Identified</div></div>', unsafe_allow_html=True)
with k2:
    st.markdown(f'<div class="metric-card"><div class="metric-value">{gap_f["sector"].nunique()}</div><div class="metric-label">Sectors Covered</div></div>', unsafe_allow_html=True)
with k3:
    hq = top_gap[top_gap["qatarization_relevance"] == "high"]
    st.markdown(f'<div class="metric-card"><div class="metric-value">{len(hq)}</div><div class="metric-label">High Qatarization Priority</div></div>', unsafe_allow_html=True)
with k4:
    avg = top_gap["gap_score"].mean() if len(top_gap) > 0 else 0
    st.markdown(f'<div class="metric-card"><div class="metric-value">{avg:.2f}</div><div class="metric-label">Avg Gap Score</div><div style="font-size:0.72rem;color:#9A9088;margin-top:6px;">(0 = aligned · 1 = fully under-supplied)</div></div>', unsafe_allow_html=True)
with k5:
    st.markdown(f'<div class="metric-card"><div class="metric-value">41</div><div class="metric-label">Sources Analysed</div></div>', unsafe_allow_html=True)

st.markdown("---")

# ════════════════════════════════════════════════════════════════════
# TABS
# ════════════════════════════════════════════════════════════════════
tab_exec, tab0, tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "🏆 Executive Summary",
    "🗺️ Guide & Definitions",
    "📊 Skill Gap Analysis",
    "🏭 Industry Matrix",
    "🎯 Strategic Demand",
    "⚖️ Scenario Coefficients",
    "🧠 Skill Weights",
    "📚 Source Evidence",
    "📋 Data Explorer",
])

# ════════════════════════════════════════════════════════════════════
# TAB EXEC — EXECUTIVE SUMMARY
# ════════════════════════════════════════════════════════════════════
with tab_exec:
    st.markdown("## Executive Summary")
    st.caption("Auto-generated from your current filter selection. Adjust sidebar filters to explore different cuts.")

    gap_pos = gap_f[gap_f["gap_score"] > 0]
    if len(gap_pos) > 0:
        top_sector_key   = gap_pos.groupby("sector")["gap_score"].mean().idxmax()
        top_sector_label = SECTOR_LABELS.get(top_sector_key, top_sector_key)
        top_sector_score = gap_pos.groupby("sector")["gap_score"].mean().max()
        top_skill_row    = gap_pos.nlargest(1, "gap_score").iloc[0]
        top_skill_name   = top_skill_row["skill_category"]
        top_skill_score  = top_skill_row["gap_score"]
        top_skill_scenario = SCENARIO_LABELS.get(top_skill_row["scenario"], top_skill_row["scenario"])

        n_high_qat  = len(gap_pos[gap_pos["qatarization_relevance"] == "high"])
        pct_high_qat= int(round(100 * n_high_qat / len(gap_pos))) if len(gap_pos) > 0 else 0

        safe_bet_skills = (
            gap_pos.groupby("skill_category")["scenario"].nunique()
            .reset_index().rename(columns={"scenario": "n_scenarios"})
            .query("n_scenarios >= 4")
        )
        n_safe_bets = len(safe_bet_skills)

        st.markdown(f"""
<div style="background:#FFFFFF;border-left:4px solid #8B2635;border-radius:0 12px 12px 0;padding:20px 28px;margin-bottom:24px;line-height:2;border:1px solid #E0D8D0;border-left:4px solid #8B2635;">
<span style="font-size:1.05rem;color:#1A1410;">
📍 <b>{top_sector_label}</b> faces the largest average strategic skill gap (<b>{top_sector_score:.2f}</b>).<br>
🎯 The single most under-supplied skill is <b>{top_skill_name}</b> (gap score: <b>{top_skill_score:.2f}</b>, most critical in <b>{top_skill_scenario}</b>).<br>
⛵ <b>{pct_high_qat}%</b> of identified gaps are high Qatarization priority — national talent development, not just general hiring.<br>
✅ <b>{n_safe_bets}</b> skills are flagged as gaps in 4 or more scenarios — the safest Manara programme investment bets.
</span>
</div>
""", unsafe_allow_html=True)
    else:
        st.info("No positive skill gaps found for current filter selection.")

    st.markdown("---")

    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.markdown('<div class="section-header">Sectors Ranked by Strategic Skill Gap</div>', unsafe_allow_html=True)
        st.caption("Average gap score across all selected scenarios. Larger = further behind strategic targets.")
        sector_avg = (
            gap_pos.groupby("sector")["gap_score"].mean()
            .reset_index().sort_values("gap_score", ascending=False)
        )
        sector_avg["sector_label"] = sector_avg["sector"].map(lambda x: SECTOR_LABELS.get(x, x))
        fig_sector = px.bar(
            sector_avg, x="gap_score", y="sector_label", orientation="h",
            color="gap_score", color_continuous_scale="Reds",
            labels={"gap_score": "Avg Gap Score", "sector_label": ""},
            text=sector_avg["gap_score"].map(lambda v: f"{v:.2f}"),
        )
        fig_sector.update_traces(textposition="outside", textfont=dict(color="#1A1410", size=12))
        fig_sector.update_layout(
            coloraxis_showscale=False,
            yaxis=dict(autorange="reversed"),
            xaxis=dict(range=[0, sector_avg["gap_score"].max() * 1.25])
        )
        apply_chart_theme(fig_sector, 380)
        st.plotly_chart(fig_sector, use_container_width=True)

    with col_right:
        st.markdown('<div class="section-header">Qatarization Priority Split</div>', unsafe_allow_html=True)
        st.caption("Share of identified gaps by national talent development priority.")
        qat_split = gap_pos["qatarization_relevance"].value_counts().reset_index()
        qat_split.columns = ["relevance", "count"]
        fig_qat = px.pie(
            qat_split, values="count", names="relevance", hole=0.6,
            color="relevance",
            color_discrete_map={"high": "#8B2635", "medium": "#C49040", "low": "#4A7A9B"},
        )
        fig_qat.update_traces(textinfo="percent+label", textfont=dict(size=13, color="#1A1410"))
        fig_qat.update_layout(
            showlegend=False,
            annotations=[dict(
                text=f"<b>{pct_high_qat}%</b><br>High", x=0.5, y=0.5,
                font=dict(size=16, color="#8B2635"), showarrow=False
            )]
        )
        apply_chart_theme(fig_qat, 380)
        st.plotly_chart(fig_qat, use_container_width=True)

    st.markdown("---")

    st.markdown('<div class="section-header">🛡️ "Safe Bet" Interventions — Skills Flagged Across Multiple Scenarios</div>', unsafe_allow_html=True)
    st.caption("Skills appearing as gaps in 4–5 scenarios are robust to uncertainty. Manara should prioritise these regardless of which future materialises.")

    consensus = (
        gap_pos.groupby("skill_category")
        .agg(n_scenarios=("scenario", "nunique"), avg_gap=("gap_score", "mean"))
        .reset_index()
        .sort_values(["n_scenarios", "avg_gap"], ascending=[False, False])
        .head(20)
    )
    consensus["label"] = consensus["skill_category"].str[:40]
    fig_con = px.bar(
        consensus.sort_values("n_scenarios"),
        x="n_scenarios", y="label", orientation="h",
        color="n_scenarios",
        color_continuous_scale=[[0, "#4A7A9B"], [0.5, "#C49040"], [0.75, "#C0564A"], [1.0, "#8B2635"]],
        labels={"n_scenarios": "Scenarios flagging as gap (of 5)", "label": ""},
        hover_data={"avg_gap": ":.2f", "n_scenarios": True},
        text=consensus.sort_values("n_scenarios")["n_scenarios"].map(lambda n: f"{n}/5 scenarios"),
    )
    fig_con.update_traces(textposition="outside", textfont=dict(color="#1A1410", size=11))
    fig_con.add_vline(x=4, line_dash="dash", line_color="#9A9088", line_width=1,
                      annotation_text="4+ scenario threshold", annotation_font_color="#9A9088",
                      annotation_position="top right")
    fig_con.update_layout(
        coloraxis_showscale=False,
        yaxis=dict(autorange="reversed"),
        xaxis=dict(range=[0, 6.5], dtick=1)
    )
    apply_chart_theme(fig_con, 480)
    st.plotly_chart(fig_con, use_container_width=True)

    st.markdown("---")

    st.markdown('<div class="section-header">🎯 Top Skills to Act On — High Qatarization Priority</div>', unsafe_allow_html=True)
    st.caption("Top skills by gap score where Qatarization relevance is high. These are the clearest Manara programme design signals.")

    top5 = (
        gap_pos[gap_pos["qatarization_relevance"] == "high"]
        .sort_values("gap_score", ascending=False)
        .drop_duplicates("skill_category")
        .head(5)
    )

    if len(top5) == 0:
        st.info("No high Qatarization priority gaps found for current filters.")
    else:
        cols = st.columns(len(top5))
        for i, (_, row) in enumerate(top5.iterrows()):
            with cols[i]:
                sector_short = SECTOR_LABELS.get(row["sector"], row["sector"])
                horizon = row.get("time_horizon", "—").replace("_", " ")
                st.markdown(f'''
<div class="metric-card" style="min-height:180px;">
    <div style="font-size:0.65rem;color:#9A9088;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:6px;">#{i+1} Priority</div>
    <div style="font-size:0.95rem;font-weight:600;color:#1A1410;line-height:1.3;margin-bottom:10px;">{row["skill_category"]}</div>
    <div style="font-size:1.4rem;font-weight:700;color:#8B2635;margin-bottom:8px;">{row["gap_score"]:.2f}</div>
    <div style="font-size:0.72rem;color:#5A5248;">
        📂 {sector_short}<br>
        🏷️ {row["scenario"]} · {horizon}
    </div>
</div>''', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════
# TAB 0 — GUIDE & DEFINITIONS
# ════════════════════════════════════════════════════════════════════
with tab0:
    st.markdown("## Welcome to the Qatar 2030 Labor Market Intelligence Dashboard")
    st.markdown(
        "This dashboard helps policymakers, researchers, and programme designers "
        "understand **where Qatar's labor market is heading** and **where the gaps are** "
        "between strategic ambitions and actual hiring. Built for the "
        "**Manara programme** and aligned with **Qatar National Vision 2030**."
    )
    st.markdown("---")

    st.markdown("### 🧭 How to Use This Dashboard")
    col_h1, col_h2, col_h3 = st.columns(3)
    with col_h1:
        st.markdown(card(
            "<b style='color:#1A1410;'>Step 1 — Select Scenarios</b><br><br>"
            "<span style='color:#5A5248;'>Use the sidebar to choose which futures to analyse. Select all 5 for a complete picture, or isolate one to focus. "
            "<b>S1 Diversification</b> is the baseline QNV case and a good starting point.</span>"
        ), unsafe_allow_html=True)
    with col_h2:
        st.markdown(card(
            "<b style='color:#1A1410;'>Step 2 — Apply Filters</b><br><br>"
            "<span style='color:#5A5248;'>Narrow by sector (energy, healthcare, tech etc.) or Qatarization relevance. "
            "Select <b>High</b> to focus on skills where Qatari nationals are the explicit policy priority.</span>"
        ), unsafe_allow_html=True)
    with col_h3:
        st.markdown(card(
            "<b style='color:#1A1410;'>Step 3 — Navigate Tabs</b><br><br>"
            "<span style='color:#5A5248;'>Each tab answers a different question. Start with <b>Skill Gap Analysis</b> for headline findings, "
            "then drill into <b>Industry Matrix</b> and <b>Strategic Demand</b> for sector detail.</span>"
        ), unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📖 Key Definitions")

    st.markdown("#### 📐 Core Concepts")
    r1a, r1b, r1c = st.columns(3)
    with r1a:
        st.markdown(card(
            card_label("🔍 Skill Gap") +
            card_body("The difference between what Qatar's strategic documents predict will be needed by 2030 "
                      "and what employers are <i>actually</i> hiring for today.<br><br>"
                      "<span style='color:#8B2635;font-weight:600;'>Large positive gap</span> = strategically critical but market hasn't caught up → Manara should intervene.")
        ), unsafe_allow_html=True)
    with r1b:
        st.markdown(card(
            card_label("📊 Gap Score (±1.0 scale)") +
            card_body("<b>Gap Score</b> = Calibration Score (41 sources) minus Posting Frequency (5,067 job postings).<br><br>"
                      "<span style='color:#5A8A64;'>● Positive</span> Strategy expects more → intervene<br>"
                      "<span style='color:#9A9088;'>● Near zero</span> Market & strategy aligned<br>"
                      "<span style='color:#C0564A;'>● Negative</span> Market over-supplies this skill")
        ), unsafe_allow_html=True)
    with r1c:
        st.markdown(card(
            card_label("⚖️ Calibration Score") +
            card_body("How strongly the 41 sources signal demand for a skill <b>(0–1)</b>.<br><br>"
                      "Built from:<br>Source credibility × Scenario alignment × Signal volume<br><br>"
                      "Higher = more sources agree this skill will be needed.")
        ), unsafe_allow_html=True)

    st.markdown("<div style='margin-top:12px'></div>", unsafe_allow_html=True)

    st.markdown("#### 🎭 Scenarios & Policy")
    r2a, r2b = st.columns(2)
    with r2a:
        st.markdown(card(
            card_label("🎭 The 5 Scenarios") +
            card_body("Plausible futures for Qatar's economy by 2030:<br>"
                      "<span style='color:#C0564A;'>■</span> <b>S1</b> Diversification Acceleration — QNV on track, all sectors grow<br>"
                      "<span style='color:#C49040;'>■</span> <b>S2</b> Hydrocarbon Dominance — LNG expansion, slower diversification<br>"
                      "<span style='color:#5A8A64;'>■</span> <b>S3</b> Green Transition Pressure — Decarbonization accelerates<br>"
                      "<span style='color:#4A7A9B;'>■</span> <b>S4</b> Knowledge Economy Leap — Qatar as R&D and AI hub<br>"
                      "<span style='color:#8A6A80;'>■</span> <b>S5</b> Regional Hub — Qatar as services and diplomacy centre")
        ), unsafe_allow_html=True)
    with r2b:
        st.markdown(card(
            card_label("⛵ Qatarization Priority") +
            card_body("Qatar's policy to increase employment of Qatari nationals per <b>QNV 2030 Human Development</b> pillar.<br><br>"
                      "<span style='color:#8B2635;font-weight:600;'>High</span> = Strategic documents explicitly flag developing Qatari talent here → Most critical for Manara programme design.<br>"
                      "<span style='color:#C49040;font-weight:600;'>Medium</span> = Relevant but secondary priority.<br>"
                      "<span style='color:#4A7A9B;font-weight:600;'>Low</span> = General workforce need, not Qatari-specific.")
        ), unsafe_allow_html=True)

    st.markdown("<div style='margin-top:12px'></div>", unsafe_allow_html=True)

    st.markdown("#### 🛠️ Technical & Model")
    r3a, r3b, r3c = st.columns(3)
    with r3a:
        st.markdown(card(
            card_label("🎯 Signal Count Penalty") +
            card_body("A <b>square-root balancing factor</b> for scenarios with fewer contributing sources.<br><br>"
                      "Prevents a low-signal scenario from dominating. Ensures all 5 scenarios are fairly compared.")
        ), unsafe_allow_html=True)
    with r3b:
        st.markdown(card(
            card_label("📈 Demand Direction Arrows") +
            card_body("<span style='color:#5A8A64;'>↑↑</span> Strong increase (gap ≥ 0.6) — urgent<br>"
                      "<span style='color:#5A8A64;'>↑</span>  Moderate increase (0.2–0.6)<br>"
                      "<span style='color:#9A9088;'>→</span>  Stable / aligned (−0.2–0.2)<br>"
                      "<span style='color:#C49040;'>↓</span>  Moderate decrease<br>"
                      "<span style='color:#9A9088;'>—</span>  No signal for this combination")
        ), unsafe_allow_html=True)
    with r3c:
        st.markdown(card(
            card_label("🏭 Sector Classification") +
            card_body("Each job posting is assigned to one of <b>8 sectors</b> using a 5-layer classifier:<br><br>"
                      "Industry tags → LinkedIn industry → Job function → Job title → SOC codes<br>"
                      "Unmatched jobs → labelled <b>cross_sector</b>.")
        ), unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(f'<div style="text-align:center;color:#9A9088;font-size:0.85rem;padding:8px 0;">'
                f'Built for the <b>Qatar Foundation Manara Programme</b> · CMU Tepper MSBA Capstone 2025 · '
                f'41 authoritative sources · 5,067 Qatar job postings · 5 scenarios</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════
# TAB 1 — SKILL GAP ANALYSIS
# ════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown('<div class="section-header">Strategic Skill Gaps — Scenario vs. Market Reality</div>', unsafe_allow_html=True)
    st.info("📌 **What this tab shows:** Which skills are strategically expected by 2030 but missing from Qatar's job market. A positive gap score means Manara should intervene. Filter by scenario, sector, and Qatarization relevance using the sidebar.")
    st.caption("Gap score = strategic expectation (41 published sources) minus actual hiring frequency (Qatar job postings). Positive = under-supplied.")

    col_l, col_r = st.columns([2, 1])
    with col_l:
        top_gaps = gap_f[gap_f["gap_score"] > 0].nlargest(20, "gap_score").copy()
        top_gaps["label"] = (
            top_gaps["sector"].map(lambda x: SECTOR_LABELS.get(x, x)).str[:12]
            + " | " + top_gaps["skill_category"].str[:28]
        )
        fig = px.bar(
            top_gaps, x="gap_score", y="label", color="scenario",
            color_discrete_map=SCENARIO_COLORS, orientation="h",
            labels={"gap_score": "Gap Score", "label": "", "scenario": "Scenario"},
            title="Top 20 Strategic Skill Gaps — All 5 Scenarios",
            hover_data=["skill_category", "sector", "qatarization_relevance", "time_horizon"]
        )
        fig.update_layout(yaxis=dict(autorange="reversed"),
                          legend=dict(orientation="h", yanchor="bottom", y=1.02))
        fig.add_vline(x=0, line_dash="dash", line_color="#E0D8D0", line_width=1)
        apply_chart_theme(fig, 520)
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        qat_c = top_gaps["qatarization_relevance"].value_counts().reset_index()
        qat_c.columns = ["relevance", "count"]
        fig_d = px.pie(qat_c, values="count", names="relevance", hole=0.55,
                       color="relevance",
                       color_discrete_map={"high": "#8B2635", "medium": "#C49040", "low": "#4A7A9B"},
                       title="Qatarization Relevance")
        apply_chart_theme(fig_d, 260)
        st.plotly_chart(fig_d, use_container_width=True)

        th_c = top_gaps["time_horizon"].value_counts().reset_index()
        th_c.columns = ["horizon", "count"]
        fig_th = px.bar(th_c, x="count", y="horizon", orientation="h",
                        color="horizon", title="Time Horizon",
                        color_discrete_sequence=["#8B2635", "#C49040", "#4A7A9B"])
        fig_th.update_layout(showlegend=False)
        apply_chart_theme(fig_th, 200)
        st.plotly_chart(fig_th, use_container_width=True)

    st.markdown('<div class="section-header">Skill Gap Heatmap: Scenario × Skill Category</div>', unsafe_allow_html=True)
    pivot = gap_f.pivot_table(index="skill_category", columns="scenario",
                               values="gap_score", aggfunc="mean").fillna(0).clip(-1, 1)
    sc_order = [s for s in ALL_SCENARIOS if s in pivot.columns]
    pivot = pivot[sc_order]
    pivot = pivot.loc[pivot.abs().max(axis=1).nlargest(20).index]
    pivot.columns = [SCENARIO_LABELS.get(c, c) for c in pivot.columns]

    fig_h = px.imshow(pivot, color_continuous_scale="RdYlGn", zmin=-1, zmax=1,
                      text_auto=".2f", aspect="auto",
                      title="Skill Gap Heatmap (green=under-supplied, red=over-supplied)")
    apply_chart_theme(fig_h, 600)
    st.plotly_chart(fig_h, use_container_width=True)

    p = img_path("scenario_analysis_charts.png")
    if p:
        st.markdown('<div class="section-header">Full Dashboard Chart (from pipeline)</div>', unsafe_allow_html=True)
        st.image(str(p), use_container_width=True)

# ════════════════════════════════════════════════════════════════════
# TAB 2 — INDUSTRY MATRIX
# ════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-header">Industry × Scenario Skill Gap Matrix</div>', unsafe_allow_html=True)
    st.info("📌 **What this tab shows:** A heatmap of average skill gap per industry sector per scenario. All green = Qatar is universally under-supplied. Use this to identify which sectors are furthest behind their strategic targets.")
    st.caption("Average gap score per sector × scenario. Green = under-supplied. Red = over-supplied.")

    p = img_path("industry_scenario_skill_matrix.png")
    if p:
        st.image(str(p), use_container_width=True)

    st.markdown('<div class="section-header">Interactive Version</div>', unsafe_allow_html=True)
    pivot_ind = gap_f.pivot_table(index="sector", columns="scenario",
                                   values="gap_score", aggfunc="mean").fillna(0).clip(-1, 1)
    sc_order = [s for s in ALL_SCENARIOS if s in pivot_ind.columns]
    pivot_ind = pivot_ind[sc_order]
    pivot_ind.index   = [SECTOR_LABELS.get(i, i) for i in pivot_ind.index]
    pivot_ind.columns = [SCENARIO_LABELS.get(c, c) for c in pivot_ind.columns]
    pivot_ind = pivot_ind.loc[pivot_ind.mean(axis=1).sort_values(ascending=False).index]

    def arrow(v):
        if v >= 0.6:  return f"{v:.2f}\n↑↑"
        if v >= 0.2:  return f"{v:.2f}\n↑"
        if v > -0.2:  return "—" if abs(v) < 0.01 else f"{v:.2f}\n→"
        if v > -0.6:  return f"{v:.2f}\n↓"
        return f"{v:.2f}\n↓↓"

    annot = [[arrow(v) for v in row] for row in pivot_ind.values]
    fig_ind = go.Figure(data=go.Heatmap(
        z=pivot_ind.values, x=pivot_ind.columns.tolist(), y=pivot_ind.index.tolist(),
        text=annot, texttemplate="%{text}",
        colorscale="RdYlGn", zmin=-1, zmax=1,
        colorbar=dict(title="Gap Score"),
    ))
    apply_chart_theme(fig_ind, 480)
    st.plotly_chart(fig_ind, use_container_width=True)

    p2 = img_path("qatarization_priority_gaps.png")
    if p2:
        st.markdown('<div class="section-header">High Qatarization Priority Gaps</div>', unsafe_allow_html=True)
        st.image(str(p2), use_container_width=True)

# ════════════════════════════════════════════════════════════════════
# TAB 3 — STRATEGIC DEMAND
# ════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-header">Strategic Demand Intensity — From 41 Published Sources</div>', unsafe_allow_html=True)
    st.info("📌 **What this tab shows:** What 41 published sources predict about skill demand — with no reference to job postings. This is the pure strategy side. Compare with the Skill Gap tab to see where strategy and market diverge.")
    st.caption("Based entirely on published sources — independent of job postings data.")

    p = img_path("sector_scenario_demand.png")
    if p:
        st.image(str(p), use_container_width=True)

    st.markdown('<div class="section-header">Interactive Demand by Sector & Scenario</div>', unsafe_allow_html=True)
    pivot2 = matrix_f.pivot_table(index="sector", columns="scenario",
                                   values="normalized_score", aggfunc="mean").fillna(0).reset_index()
    pivot2["sector"] = pivot2["sector"].map(lambda x: SECTOR_LABELS.get(x, x))
    sc_cols = [s for s in ALL_SCENARIOS if s in pivot2.columns]
    pivot2_m = pivot2.melt(id_vars="sector", value_vars=sc_cols,
                            var_name="scenario", value_name="Demand Score")
    pivot2_m["Scenario"] = pivot2_m["scenario"].map(SCENARIO_LABELS)
    fig2 = px.bar(pivot2_m, x="sector", y="Demand Score", color="Scenario",
                  barmode="group",
                  color_discrete_map={SCENARIO_LABELS[s]: SCENARIO_COLORS[s] for s in ALL_SCENARIOS},
                  title="Strategic Skill Demand by Sector & Scenario")
    fig2.update_layout(xaxis_tickangle=-30,
                       legend=dict(orientation="h", yanchor="bottom", y=1.02))
    apply_chart_theme(fig2, 400)
    st.plotly_chart(fig2, use_container_width=True)

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown('<div class="section-header">Top Skills per Scenario</div>', unsafe_allow_html=True)
        sel = st.selectbox("Select scenario", ALL_SCENARIOS, format_func=lambda x: SCENARIO_LABELS[x])
        top_m = matrix_f[matrix_f["scenario"] == sel].nlargest(15, "normalized_score")
        fig3 = px.bar(top_m, x="normalized_score", y="skill_category",
                      color="sector", orientation="h",
                      color_discrete_map={k: SECTOR_COLORS.get(k, "#9A9088") for k in top_m["sector"].unique()},
                      labels={"normalized_score": "Demand Score", "skill_category": ""},
                      title=f"Top Skills — {SCENARIO_LABELS[sel]}")
        fig3.update_layout(yaxis=dict(autorange="reversed"))
        apply_chart_theme(fig3, 450)
        st.plotly_chart(fig3, use_container_width=True)

    with col_b:
        st.markdown('<div class="section-header">Qatarization Priority Gaps</div>', unsafe_allow_html=True)
        qat_g = gap_f[(gap_f["qatarization_relevance"] == "high") & (gap_f["gap_score"] > 0)].nlargest(15, "gap_score")
        qat_g["label"] = qat_g["skill_category"].str[:32]
        fig4 = px.bar(qat_g, x="gap_score", y="label", color="scenario",
                      color_discrete_map=SCENARIO_COLORS, orientation="h",
                      labels={"gap_score": "Gap Score", "label": ""},
                      title="High Qatarization Priority Gaps")
        fig4.update_layout(yaxis=dict(autorange="reversed"),
                           legend=dict(orientation="h", yanchor="bottom", y=1.02))
        apply_chart_theme(fig4, 450)
        st.plotly_chart(fig4, use_container_width=True)

# ════════════════════════════════════════════════════════════════════
# TAB 4 — SCENARIO COEFFICIENTS
# ════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-header">Scenario Coefficient Report — Model Transparency</div>', unsafe_allow_html=True)
    st.info("📌 **What this tab shows:** Model transparency. Which sources drive each scenario, how quality weights are applied, and how the signal-count penalty balances scenarios. Use to justify findings to stakeholders.")
    st.caption("Shows how each source contributes to each scenario through quality weights, scenario weights, and signal-count penalties.")

    render_live_coeff_dashboard(coeff_df)

    st.markdown('<div class="section-header">Weight Definitions</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**Demand Score**")
        st.markdown("""
- Strong increase: **+2.0**
- Moderate increase: **+1.0**
- Stable: **0.0**
- Moderate decrease: **-1.0**
- Strong decrease: **-2.0**
        """)
    with col2:
        st.markdown("**Quality Weight**")
        st.markdown("""
- High (IMF, WB, QNV, ILO): **1.5×**
- Medium (sector strategies): **1.0×**
- Low (knowledge fallback): **0.5×**
        """)
    with col3:
        st.markdown("**Signal-Count Penalty**")
        st.markdown("""
Applied after normalization:
- `sqrt(scenario_signals / max_signals)`
- Balances scenarios with fewer sources
- S1 (most signals) = **1.0×**
- S2/S4/S5 (fewer) = **< 1.0×**
        """)

    if coeff_df is not None:
        st.markdown('<div class="section-header">Source Contribution Table</div>', unsafe_allow_html=True)
        sc_sel = st.selectbox("Filter by scenario", ["All"] + ALL_SCENARIOS,
                              format_func=lambda x: "All" if x == "All" else SCENARIO_LABELS[x],
                              key="coeff_sc")
        df_show = coeff_df if sc_sel == "All" else coeff_df[coeff_df["scenario"] == sc_sel]

        fig_c = px.bar(
            df_show.nlargest(30, "total_weighted"),
            x="total_weighted", y="source_id", color="scenario",
            color_discrete_map=SCENARIO_COLORS, orientation="h",
            labels={"total_weighted": "Total Weighted Score", "source_id": "Source"},
            title="Source Contributions (top 30)"
        )
        fig_c.update_layout(yaxis=dict(autorange="reversed"),
                            legend=dict(orientation="h", yanchor="bottom", y=1.02))
        apply_chart_theme(fig_c, 500)
        st.plotly_chart(fig_c, use_container_width=True)
        st.dataframe(df_show, use_container_width=True, hide_index=True)

# ════════════════════════════════════════════════════════════════════
# TAB 5 — SKILL WEIGHTS
# ════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown('<div class="section-header">Skill Weights per Scenario</div>', unsafe_allow_html=True)
    st.info("📌 **What this tab shows:** How much strategic weight each skill carries within each scenario (0–1). Skills with high bars across all 5 scenarios are universally important — the safest Manara investment bets.")
    st.caption("Normalized adjusted weight (0–1 within each scenario). Color = industry sector. Dashed line = 0.6 high-impact threshold.")

    render_live_skill_weight_dashboard(skill_wt_df)

    if skill_wt_df is not None:
        st.markdown('<div class="section-header">Interactive Skill Weight Explorer</div>', unsafe_allow_html=True)
        col_sw1, col_sw2 = st.columns(2)
        with col_sw1:
            sc_sw = st.selectbox("Scenario", ALL_SCENARIOS,
                                 format_func=lambda x: SCENARIO_LABELS[x], key="sw_sc")
        with col_sw2:
            top_n = st.slider("Top N skills", 10, 30, 15)

        sw_data = skill_wt_df[skill_wt_df["scenario"] == sc_sw].nlargest(top_n, "normalized_weight").copy()
        sw_data["sector_label"] = sw_data["sector"].map(lambda x: SECTOR_LABELS.get(x, x))

        fig_sw = px.bar(
            sw_data.sort_values("normalized_weight"),
            x="normalized_weight", y="skill_category",
            color="sector_label", orientation="h",
            color_discrete_map={SECTOR_LABELS.get(k, k): v for k, v in SECTOR_COLORS.items()},
            labels={"normalized_weight": "Normalized Weight (0–1)", "skill_category": "", "sector_label": "Sector"},
            title=f"Skill Weights — {SCENARIO_LABELS[sc_sw]}"
        )
        fig_sw.add_vline(x=0.6, line_dash="dash", line_color="#9A9088", line_width=1)
        fig_sw.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02))
        apply_chart_theme(fig_sw, 500)
        st.plotly_chart(fig_sw, use_container_width=True)

        st.markdown('<div class="section-header">Skill × Scenario Weight Matrix</div>', unsafe_allow_html=True)
        sw_pivot = skill_wt_df.pivot_table(
            index="skill_category", columns="scenario",
            values="normalized_weight", aggfunc="mean"
        ).fillna(0).round(2)
        sc_order = [s for s in ALL_SCENARIOS if s in sw_pivot.columns]
        sw_pivot = sw_pivot[sc_order]
        sw_pivot.columns = [SCENARIO_LABELS.get(c, c) for c in sw_pivot.columns]
        sw_pivot["Max"] = sw_pivot.max(axis=1)
        sw_pivot = sw_pivot.sort_values("Max", ascending=False).drop(columns="Max").head(25)

        fig_swh = px.imshow(sw_pivot, color_continuous_scale="RdPu",
                            zmin=0, zmax=1, text_auto=".2f", aspect="auto",
                            title="Skill Weight Matrix — all 5 scenarios")
        apply_chart_theme(fig_swh, 600)
        st.plotly_chart(fig_swh, use_container_width=True)

# ════════════════════════════════════════════════════════════════════
# TAB 6 — SOURCE EVIDENCE
# ════════════════════════════════════════════════════════════════════
with tab6:
    st.markdown('<div class="section-header">Source Evidence — Full Citation Trail</div>', unsafe_allow_html=True)
    st.info("📌 **What this tab shows:** Full audit trail. Every skill signal traced back to its publication — IMF, World Bank, QNV, WEF, ILO, RAND, McKinsey, Goldman Sachs and 33 more. Use to verify or cite any finding.")

    col_s1, col_s2 = st.columns(2)
    with col_s1:
        qual_c = sources_f.groupby(["source_id", "data_quality"]).size().reset_index(name="signals")
        qual_c = qual_c.sort_values("signals", ascending=False).head(15)
        fig_q = px.bar(qual_c, x="signals", y="source_id", color="data_quality",
                       orientation="h", title="Signals per Source by Quality",
                       color_discrete_map={"high": "#5A8A64", "medium": "#C49040", "low": "#C0564A"})
        fig_q.update_layout(yaxis=dict(autorange="reversed"))
        apply_chart_theme(fig_q, 420)
        st.plotly_chart(fig_q, use_container_width=True)

    with col_s2:
        sec_sig = sources_f.groupby("sector").size().reset_index(name="signals")
        sec_sig["sector_label"] = sec_sig["sector"].map(lambda x: SECTOR_LABELS.get(x, x))
        fig_ss = px.pie(sec_sig, values="signals", names="sector_label", hole=0.4,
                        title="Signal Distribution by Sector",
                        color_discrete_sequence=list(SECTOR_COLORS.values()))
        apply_chart_theme(fig_ss, 420)
        st.plotly_chart(fig_ss, use_container_width=True)

    st.markdown('<div class="section-header">Source Detail</div>', unsafe_allow_html=True)
    src_sum = sources_df.groupby(
        ["source_id", "source_title", "source_publisher", "source_year", "data_quality"]
    ).agg(
        signals=("skill_category", "count"),
        sectors=("sector", lambda x: ", ".join(sorted(set(x)))),
        scenarios=("scenario", lambda x: ", ".join(sorted(set(x))))
    ).reset_index().sort_values("signals", ascending=False)

    st.dataframe(
        src_sum[["source_id", "source_title", "source_publisher", "source_year", "data_quality", "signals", "sectors", "scenarios"]],
        use_container_width=True, hide_index=True,
        column_config={
            "source_id":        st.column_config.TextColumn("ID", width="small"),
            "source_title":     st.column_config.TextColumn("Title", width="large"),
            "source_publisher": st.column_config.TextColumn("Publisher", width="medium"),
            "source_year":      st.column_config.NumberColumn("Year", width="small", format="%d"),
            "data_quality":     st.column_config.TextColumn("Quality", width="small"),
            "signals":          st.column_config.NumberColumn("Signals", width="small"),
            "sectors":          st.column_config.TextColumn("Sectors", width="medium"),
            "scenarios":        st.column_config.TextColumn("Scenarios", width="small"),
        }
    )

    st.markdown('<div class="section-header">Demand Direction Breakdown</div>', unsafe_allow_html=True)
    dir_c = sources_f["demand_direction"].value_counts().reset_index()
    dir_c.columns = ["direction", "count"]
    fig_dir = px.bar(dir_c, x="direction", y="count", color="direction",
                     color_discrete_map={
                         "strong_increase":   "#5A8A64",
                         "moderate_increase": "#9ABF9E",
                         "stable":            "#9A9088",
                         "moderate_decrease": "#C49040",
                         "strong_decrease":   "#C0564A"
                     }, title="Skill Signals by Demand Direction")
    fig_dir.update_layout(showlegend=False)
    apply_chart_theme(fig_dir, 320)
    st.plotly_chart(fig_dir, use_container_width=True)

# ════════════════════════════════════════════════════════════════════
# TAB 7 — DATA EXPLORER
# ════════════════════════════════════════════════════════════════════
with tab7:
    st.markdown('<div class="section-header">Data Explorer</div>', unsafe_allow_html=True)
    st.info("📌 **What this tab shows:** Search, filter, and download any underlying dataset for custom analysis or reporting. Switch between Gap Analysis, Skill Matrix, Calibration, Sources, Coefficients, and Skill Weights.")

    dataset = st.radio("Select dataset",
        ["Gap Analysis", "Skill Matrix", "Calibration", "Source Signals", "Coefficients", "Skill Weights"],
        horizontal=True)

    dataset_map = {
        "Gap Analysis":   gap_f,
        "Skill Matrix":   matrix_f,
        "Calibration":    calib_df,
        "Source Signals": sources_f,
        "Coefficients":   coeff_df,
        "Skill Weights":  skill_wt_df,
    }
    df_show = dataset_map.get(dataset)
    if df_show is None:
        st.info(f"'{dataset}' not available — run the pipeline to generate it.")
    else:
        search = st.text_input("🔍 Search", placeholder="e.g. digital, healthcare, fintech...")
        if search:
            mask = df_show.astype(str).apply(
                lambda col: col.str.contains(search, case=False, na=False)).any(axis=1)
            df_show = df_show[mask]
        st.caption(f"Showing {len(df_show):,} rows")
        st.dataframe(df_show, use_container_width=True, hide_index=True)
        csv = df_show.to_csv(index=False).encode("utf-8")
        st.download_button(f"⬇ Download {dataset} CSV", csv,
                           f"qatar_{dataset.lower().replace(' ', '_')}.csv", "text/csv")

# ── Footer ────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center;color:#9A9088;font-size:0.8rem;'>"
    "Qatar 2030 Labor Market Intelligence · CMU Tepper MSBA Capstone · "
    "5 Scenarios · 41 Sources · Claude API"
    "</div>",
    unsafe_allow_html=True
)
