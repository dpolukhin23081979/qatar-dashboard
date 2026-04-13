import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import os

# ── Page config ───────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Qatar 2030 Labor Market Intelligence",
    page_icon="🇶🇦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; color: #e8e4dc; }
h1, h2, h3 { font-family: 'DM Serif Display', serif; color: #f0ece4 !important; }
.main { background-color: #0d0d14; }
.stApp { background-color: #0d0d14; }
section[data-testid="stMain"] { background-color: #0d0d14; }
div[data-testid="stTabs"] { background-color: #0d0d14; }
button[data-baseweb="tab"] { color: #a09a8e !important; }
button[data-baseweb="tab"][aria-selected="true"] { color: #f0ece4 !important; border-bottom-color: #c0392b !important; }

.metric-card {
    background: #1a1a2e; border-radius: 12px; padding: 20px 24px;
    border-left: 4px solid #c0392b; box-shadow: 0 4px 16px rgba(0,0,0,0.4);
    margin-bottom: 8px;
}
.metric-value { font-size: 2rem; font-weight: 600; color: #e8513a; line-height: 1; }
.metric-label { font-size: 0.8rem; color: #8a8070; text-transform: uppercase; letter-spacing: 0.08em; margin-top: 4px; }

.section-header {
    font-family: 'DM Serif Display', serif; font-size: 1.4rem;
    color: #f0ece4 !important; border-bottom: 2px solid #c0392b;
    padding-bottom: 8px; margin: 24px 0 16px 0;
}

div[data-testid="stSidebarContent"] { background-color: #0a0a12; color: #e8e4dc; }
div[data-testid="stSidebarContent"] label { color: #e8e4dc !important; }
div[data-testid="stSidebarContent"] p { color: #a09a8e !important; }
div[data-testid="stMarkdownContainer"] p { color: #e8e4dc; }
div[data-testid="stCaptionContainer"] p { color: #8a8070 !important; }
div[data-testid="stDownloadButton"] button { background-color: #c0392b; color: white; border: none; }
hr { border-color: #2a2a3e; }
</style>
""", unsafe_allow_html=True)

# ── Data loading ──────────────────────────────────────────────────────────
DATA_DIR = Path("data")

@st.cache_data
def load_data():
    gap      = pd.read_csv(DATA_DIR / "scenario_gap_analysis.csv")
    matrix   = pd.read_csv(DATA_DIR / "scenario_skill_matrix.csv")
    calib    = pd.read_csv(DATA_DIR / "scenario_calibration.csv")
    sources  = pd.read_csv(DATA_DIR / "scenario_sources_raw.csv")
    gap["gap_score"] = gap["gap_score"].clip(-1.0, 1.0)
    return gap, matrix, calib, sources

@st.cache_data
def load_optional(filename):
    path = DATA_DIR / filename
    if path.exists():
        return pd.read_csv(path)
    return None

gap_df, matrix_df, calib_df, sources_df = load_data()
coeff_df     = load_optional("scenario_coefficients.csv")
skill_wt_df  = load_optional("scenario_skill_weights.csv")

# ── Constants ─────────────────────────────────────────────────────────────
SCENARIO_LABELS = {
    "S1": "S1: Diversification Acceleration",
    "S2": "S2: Hydrocarbon Dominance",
    "S3": "S3: Green Transition Pressure",
    "S4": "S4: Knowledge Economy Leap",
    "S5": "S5: Regional Hub & Geopolitical Pivot",
}
SCENARIO_COLORS = {
    "S1": "#2196F3", "S2": "#FF9800",
    "S3": "#4CAF50", "S4": "#9C27B0", "S5": "#F44336"
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

ALL_SCENARIOS = ["S1", "S2", "S3", "S4", "S5"]

def img_path(filename):
    p = DATA_DIR / filename
    return p if p.exists() else None

# ── Sidebar ───────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div style="font-family:\'DM Serif Display\',serif;font-size:1.3rem;color:#f0ece4;padding:8px 0;">🇶🇦 Qatar 2030<br>Labor Market Intelligence</div>', unsafe_allow_html=True)
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
    qat_filter  = st.selectbox("Qatarization Relevance", ["All","high","medium","low"])
    time_filter = st.selectbox("Time Horizon", ["All","near_term","medium_term","both"])

    st.markdown("---")
    st.markdown("**Data sources**")
    st.markdown(f"- {sources_df['source_id'].nunique()} publications")
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
sources_f = sources_df[sources_df["scenario"].isin(selected_scenarios or ALL_SCENARIOS)]

# ── Header ────────────────────────────────────────────────────────────────
st.markdown("# Qatar 2030 Labor Market Intelligence")
st.markdown("*Strategic Skill Demand Scenarios — Evidence-based workforce gap analysis for Manara & QNV 2030*")

# ── Key Definitions ───────────────────────────────────────────────────────
with st.expander("📖 Key Definitions — Start Here", expanded=False):
    st.markdown("""
<div class="definition-box">
<b>🔍 What is a Skill Gap?</b><br>
A skill gap is the difference between what Qatar's strategic documents (QNV 2030, IMF, World Bank, WEF etc.) predict will be needed by 2030, and what employers are <i>actually</i> hiring for today. A large positive gap means a skill is strategically critical but the labor market hasn't caught up yet — this is where Manara should intervene.
</div>

<div class="definition-box">
<b>📊 What is a Gap Score?</b><br>
Gap Score = Calibration Score (from 41 published sources) minus Posting Frequency (from 5,067 Qatar job postings), scaled to ±1.0.<br>
• <b>Positive (green)</b>: Strategy expects more demand than market shows → intervention needed<br>
• <b>Near zero</b>: Market and strategy are aligned → no action needed<br>
• <b>Negative (red)</b>: Market already hires more than strategy expects → skill is market-led
</div>

<div class="definition-box">
<b>🇶🇦 What is Qatarization Priority?</b><br>
Qatarization is Qatar's national policy to increase employment of Qatari nationals in the private sector, aligned with QNV 2030's Human Development pillar. Skills marked <b>High Qatarization Relevance</b> are those where strategic documents explicitly flag the need to develop Qatari talent — not just hire expats. These are the most important for Manara programme design.
</div>

<div class="definition-box">
<b>🎭 What are Scenarios?</b><br>
Scenarios are plausible futures for Qatar's economy by 2030. Each scenario changes which skills become most important:<br>
• <b>S1 Diversification</b>: QNV succeeds — tech, health, education, finance all grow<br>
• <b>S2 Hydrocarbon</b>: LNG expansion dominates — engineering, operations, energy skills<br>
• <b>S3 Green Transition</b>: Decarbonization accelerates — clean energy, sustainability skills<br>
• <b>S4 Knowledge Leap</b>: Qatar becomes R&D/AI hub — research, innovation, deep tech<br>
• <b>S5 Regional Hub</b>: Qatar as services & diplomacy centre — finance, logistics, soft skills
</div>

<div class="definition-box">
<b>⚖️ What is a Calibration Score?</b><br>
The calibration score (0–1) reflects how strongly the 41 published sources signal demand for a skill under a given scenario. It is built from: source credibility (quality weight), scenario alignment (scenario weight), and signal volume (penalty factor). Higher = more sources agree this skill will be in demand.
</div>
""", unsafe_allow_html=True)

# ── How to Use ────────────────────────────────────────────────────────────
with st.expander("🧭 How to Use This Dashboard", expanded=False):
    st.markdown("""
<div class="how-to-box">
<b>Step 1 — Select your scenarios</b> (sidebar, top)<br>
Choose which futures you want to analyse. Select all 5 for a full picture, or isolate one scenario to see what skills matter specifically under that future. S1 is the baseline QNV case.
</div>

<div class="how-to-box">
<b>Step 2 — Filter by sector and Qatarization relevance</b> (sidebar)<br>
Narrow down to a specific industry (energy, healthcare, tech etc.) or focus on skills where Qatari nationals are the priority target. "High" Qatarization relevance = most important for Manara.
</div>

<div class="how-to-box">
<b>Step 3 — Navigate the tabs</b><br>
📊 <b>Skill Gap Analysis</b>: The main output. Which skills are strategically expected but missing from the market?<br>
🏭 <b>Industry Matrix</b>: Which sectors have the biggest gaps, broken down by scenario.<br>
🎯 <b>Strategic Demand</b>: What the 41 sources say about future skill demand — independent of job postings.<br>
🔬 <b>Scenario Coefficients</b>: How scenario scores are built — which sources drive each scenario and by how much.<br>
🧠 <b>Skill Weights</b>: Which skills carry the most weight in each scenario and across all 5.<br>
📚 <b>Source Evidence</b>: Full audit trail — every signal traced to its publication.<br>
📋 <b>Data Explorer</b>: Search and download any underlying dataset.
</div>

<div class="how-to-box">
<b>Interpreting the charts</b><br>
• <b>Green bars/cells</b>: skills Qatar needs more of — gaps to fill<br>
• <b>Red bars/cells</b>: skills the market already over-supplies<br>
• <b>— (dash)</b>: no signal from sources for that scenario × skill combination<br>
• <b>↑↑ ↑ → ↓ ↓↓</b>: demand direction arrows in the heatmap
</div>
""", unsafe_allow_html=True)

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
    st.markdown(f'<div class="metric-card"><div class="metric-value">{avg:.2f}</div><div class="metric-label">Avg Gap Score</div></div>', unsafe_allow_html=True)
with k5:
    st.markdown(f'<div class="metric-card"><div class="metric-value">{sources_df["source_id"].nunique()}</div><div class="metric-label">Sources Analysed</div></div>', unsafe_allow_html=True)

st.markdown("---")

# ════════════════════════════════════════════════════════════════════
# TABS
# ════════════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📊 Skill Gap Analysis",
    "🏭 Industry Matrix",
    "🎯 Strategic Demand",
    "⚖️ Scenario Coefficients",
    "🧠 Skill Weights",
    "📚 Source Evidence",
    "📋 Data Explorer",
])

# ════════════════════════════════════════════════════════════════════
# TAB 1 — SKILL GAP ANALYSIS
# ════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown('<div class="section-header">Strategic Skill Gaps — Scenario vs. Market Reality</div>', unsafe_allow_html=True)
    st.caption("Gap score = strategic expectation (41 published sources) minus actual hiring frequency (Qatar job postings). Positive = under-supplied.")

    col_l, col_r = st.columns([2, 1])
    with col_l:
        top_gaps = gap_f[gap_f["gap_score"] > 0].nlargest(20, "gap_score").copy()
        top_gaps["label"] = (
            top_gaps["sector"].map(lambda x: SECTOR_LABELS.get(x,x)).str[:12]
            + " | " + top_gaps["skill_category"].str[:28]
        )
        fig = px.bar(
            top_gaps, x="gap_score", y="label", color="scenario",
            color_discrete_map=SCENARIO_COLORS, orientation="h",
            labels={"gap_score":"Gap Score","label":"","scenario":"Scenario"},
            title="Top 20 Strategic Skill Gaps — All 5 Scenarios",
            hover_data=["skill_category","sector","qatarization_relevance","time_horizon"]
        )
        fig.update_layout(height=520, plot_bgcolor="#1a1a2e", paper_bgcolor="#1a1a2e",
                          font=dict(color="#e8e4dc"), yaxis=dict(autorange="reversed"),
                          legend=dict(orientation="h", yanchor="bottom", y=1.02))
        fig.add_vline(x=0, line_dash="dash", line_color="#555", line_width=1)
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        qat_c = top_gaps["qatarization_relevance"].value_counts().reset_index()
        qat_c.columns = ["relevance","count"]
        fig_d = px.pie(qat_c, values="count", names="relevance", hole=0.55,
                       color="relevance",
                       color_discrete_map={"high":"#8B0000","medium":"#D4A017","low":"#4C78A8"},
                       title="Qatarization Relevance")
        fig_d.update_layout(height=260, plot_bgcolor="#1a1a2e", paper_bgcolor="#1a1a2e",
                            font=dict(color="#e8e4dc"))
        st.plotly_chart(fig_d, use_container_width=True)

        th_c = top_gaps["time_horizon"].value_counts().reset_index()
        th_c.columns = ["horizon","count"]
        fig_th = px.bar(th_c, x="count", y="horizon", orientation="h",
                        color="horizon", title="Time Horizon",
                        color_discrete_sequence=["#8B0000","#D4A017","#4C78A8"])
        fig_th.update_layout(height=200, plot_bgcolor="#1a1a2e", paper_bgcolor="#1a1a2e",
                             font=dict(color="#e8e4dc"), showlegend=False)
        st.plotly_chart(fig_th, use_container_width=True)

    # Heatmap
    st.markdown('<div class="section-header">Skill Gap Heatmap: Scenario × Skill Category</div>', unsafe_allow_html=True)
    pivot = gap_f.pivot_table(index="skill_category", columns="scenario",
                               values="gap_score", aggfunc="mean").fillna(0).clip(-1,1)
    sc_order = [s for s in ALL_SCENARIOS if s in pivot.columns]
    pivot = pivot[sc_order]
    pivot = pivot.loc[pivot.abs().max(axis=1).nlargest(20).index]
    pivot.columns = [SCENARIO_LABELS.get(c,c) for c in pivot.columns]

    fig_h = px.imshow(pivot, color_continuous_scale="RdYlGn", zmin=-1, zmax=1,
                      text_auto=".2f", aspect="auto",
                      title="Skill Gap Heatmap (green=under-supplied, red=over-supplied)")
    fig_h.update_layout(height=600, plot_bgcolor="#1a1a2e", paper_bgcolor="#1a1a2e",
                        font=dict(color="#e8e4dc"))
    st.plotly_chart(fig_h, use_container_width=True)

    # Static chart from pipeline
    p = img_path("scenario_analysis_charts.png")
    if p:
        st.markdown('<div class="section-header">Full Dashboard Chart (from pipeline)</div>', unsafe_allow_html=True)
        st.image(str(p), use_container_width=True)

# ════════════════════════════════════════════════════════════════════
# TAB 2 — INDUSTRY MATRIX
# ════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-header">Industry × Scenario Skill Gap Matrix</div>', unsafe_allow_html=True)
    st.caption("Average gap score per sector × scenario. Green = under-supplied. Red = over-supplied.")

    # Static image from pipeline
    p = img_path("industry_scenario_skill_matrix.png")
    if p:
        st.image(str(p), use_container_width=True)

    # Interactive version
    st.markdown('<div class="section-header">Interactive Version</div>', unsafe_allow_html=True)
    pivot_ind = gap_f.pivot_table(index="sector", columns="scenario",
                                   values="gap_score", aggfunc="mean").fillna(0).clip(-1,1)
    sc_order = [s for s in ALL_SCENARIOS if s in pivot_ind.columns]
    pivot_ind = pivot_ind[sc_order]
    pivot_ind.index = [SECTOR_LABELS.get(i,i) for i in pivot_ind.index]
    pivot_ind.columns = [SCENARIO_LABELS.get(c,c) for c in pivot_ind.columns]
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
    fig_ind.update_layout(height=480, plot_bgcolor="#1a1a2e", paper_bgcolor="#1a1a2e",
                          font=dict(color="#e8e4dc", size=12))
    st.plotly_chart(fig_ind, use_container_width=True)

    # Qatarization chart
    p2 = img_path("qatarization_priority_gaps.png")
    if p2:
        st.markdown('<div class="section-header">High Qatarization Priority Gaps</div>', unsafe_allow_html=True)
        st.image(str(p2), use_container_width=True)

# ════════════════════════════════════════════════════════════════════
# TAB 3 — STRATEGIC DEMAND
# ════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-header">Strategic Demand Intensity — From 41 Published Sources</div>', unsafe_allow_html=True)
    st.caption("Based entirely on published sources — independent of job postings data.")

    p = img_path("sector_scenario_demand.png")
    if p:
        st.image(str(p), use_container_width=True)

    # Interactive sector × scenario
    st.markdown('<div class="section-header">Interactive Demand by Sector & Scenario</div>', unsafe_allow_html=True)
    pivot2 = matrix_f.pivot_table(index="sector", columns="scenario",
                                   values="normalized_score", aggfunc="mean").fillna(0).reset_index()
    pivot2["sector"] = pivot2["sector"].map(lambda x: SECTOR_LABELS.get(x,x))
    sc_cols = [s for s in ALL_SCENARIOS if s in pivot2.columns]
    pivot2_m = pivot2.melt(id_vars="sector", value_vars=sc_cols,
                            var_name="scenario", value_name="Demand Score")
    pivot2_m["Scenario"] = pivot2_m["scenario"].map(SCENARIO_LABELS)
    fig2 = px.bar(pivot2_m, x="sector", y="Demand Score", color="Scenario",
                  barmode="group",
                  color_discrete_map={SCENARIO_LABELS[s]: SCENARIO_COLORS[s] for s in ALL_SCENARIOS},
                  title="Strategic Skill Demand by Sector & Scenario")
    fig2.update_layout(height=400, plot_bgcolor="#1a1a2e", paper_bgcolor="#1a1a2e",
                       font=dict(color="#e8e4dc"), xaxis_tickangle=-30,
                       legend=dict(orientation="h", yanchor="bottom", y=1.02))
    st.plotly_chart(fig2, use_container_width=True)

    # Top skills per scenario
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown('<div class="section-header">Top Skills per Scenario</div>', unsafe_allow_html=True)
        sel = st.selectbox("Select scenario", ALL_SCENARIOS, format_func=lambda x: SCENARIO_LABELS[x])
        top_m = matrix_f[matrix_f["scenario"] == sel].nlargest(15, "normalized_score")
        fig3 = px.bar(top_m, x="normalized_score", y="skill_category",
                      color="sector", orientation="h",
                      labels={"normalized_score":"Demand Score","skill_category":""},
                      title=f"Top Skills — {SCENARIO_LABELS[sel]}")
        fig3.update_layout(height=450, plot_bgcolor="#1a1a2e", paper_bgcolor="#1a1a2e",
                           font=dict(color="#e8e4dc"), yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig3, use_container_width=True)

    with col_b:
        st.markdown('<div class="section-header">Qatarization Priority Gaps</div>', unsafe_allow_html=True)
        qat_g = gap_f[(gap_f["qatarization_relevance"]=="high") & (gap_f["gap_score"]>0)].nlargest(15,"gap_score")
        qat_g["label"] = qat_g["skill_category"].str[:32]
        fig4 = px.bar(qat_g, x="gap_score", y="label", color="scenario",
                      color_discrete_map=SCENARIO_COLORS, orientation="h",
                      labels={"gap_score":"Gap Score","label":""},
                      title="High Qatarization Priority Gaps")
        fig4.update_layout(height=450, plot_bgcolor="#1a1a2e", paper_bgcolor="#1a1a2e",
                           font=dict(color="#e8e4dc"), yaxis=dict(autorange="reversed"),
                           legend=dict(orientation="h", yanchor="bottom", y=1.02))
        st.plotly_chart(fig4, use_container_width=True)

# ════════════════════════════════════════════════════════════════════
# TAB 4 — SCENARIO COEFFICIENTS
# ════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-header">Scenario Coefficient Report — Model Transparency</div>', unsafe_allow_html=True)
    st.caption("Shows how each source contributes to each scenario through quality weights, scenario weights, and signal-count penalties.")

    # Static chart
    p = img_path("scenario_coefficient_report.png")
    if p:
        st.image(str(p), use_container_width=True)
    else:
        st.info("📊 Chart not yet generated. Run **Cell 8b** in the Qatar Scenario Pipeline notebook, then upload `scenario_coefficient_report.png` to your `data/` folder on GitHub.")

    # Weight definitions
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

    # Coefficient table
    if coeff_df is not None:
        st.markdown('<div class="section-header">Source Contribution Table</div>', unsafe_allow_html=True)
        sc_sel = st.selectbox("Filter by scenario", ["All"] + ALL_SCENARIOS,
                              format_func=lambda x: "All" if x=="All" else SCENARIO_LABELS[x],
                              key="coeff_sc")
        df_show = coeff_df if sc_sel == "All" else coeff_df[coeff_df["scenario"] == sc_sel]

        # Interactive chart
        fig_c = px.bar(
            df_show.nlargest(30, "total_weighted"),
            x="total_weighted", y="source_id", color="scenario",
            color_discrete_map=SCENARIO_COLORS, orientation="h",
            labels={"total_weighted":"Total Weighted Score","source_id":"Source"},
            title="Source Contributions (top 30)"
        )
        fig_c.update_layout(height=500, plot_bgcolor="#1a1a2e", paper_bgcolor="#1a1a2e",
                            font=dict(color="#e8e4dc"), yaxis=dict(autorange="reversed"),
                            legend=dict(orientation="h", yanchor="bottom", y=1.02))
        st.plotly_chart(fig_c, use_container_width=True)
        st.dataframe(df_show, use_container_width=True, hide_index=True)

# ════════════════════════════════════════════════════════════════════
# TAB 5 — SKILL WEIGHTS
# ════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown('<div class="section-header">Skill Weights per Scenario</div>', unsafe_allow_html=True)
    st.info("**What you're looking at:** How much strategic weight each skill carries within each scenario (0–1 normalized). The top chart shows the most important skills per scenario. The cross-scenario comparison shows which skills are universally strategic (high bars across all 5 scenarios) vs scenario-specific (only tall in one). Universal skills are the safest Manara investment bets.")
    st.caption("Normalized adjusted weight (0–1 within each scenario). Color = industry sector. Dashed line = 0.6 high-impact threshold.")

    # Static charts
    p_sw = img_path("scenario_skill_weights.png")
    if p_sw:
        st.image(str(p_sw), use_container_width=True)
    else:
        st.info("📊 Chart not yet generated. Run **Cell 8c** in the Qatar Scenario Pipeline notebook, then upload `scenario_skill_weights.png` to your `data/` folder on GitHub.")

    p_cs = img_path("scenario_cross_skill_comparison.png")
    if p_cs:
        st.markdown('<div class="section-header">Cross-Scenario Skill Comparison</div>', unsafe_allow_html=True)
        st.image(str(p_cs), use_container_width=True)

    # Interactive skill weight explorer
    if skill_wt_df is not None:
        st.markdown('<div class="section-header">Interactive Skill Weight Explorer</div>', unsafe_allow_html=True)
        col_sw1, col_sw2 = st.columns(2)
        with col_sw1:
            sc_sw = st.selectbox("Scenario", ALL_SCENARIOS,
                                 format_func=lambda x: SCENARIO_LABELS[x], key="sw_sc")
        with col_sw2:
            top_n = st.slider("Top N skills", 10, 30, 15)

        sw_data = skill_wt_df[skill_wt_df["scenario"] == sc_sw].nlargest(top_n, "normalized_weight")

        SECTOR_COLORS = {
            "technology_digital":"#1976D2","energy_lng":"#F57C00",
            "healthcare":"#388E3C","education":"#7B1FA2",
            "finance_banking":"#C62828","construction_real_estate":"#5D4037",
            "tourism_hospitality":"#00838F","cross_sector":"#757575",
        }
        sw_data["sector_label"] = sw_data["sector"].map(lambda x: SECTOR_LABELS.get(x,x))
        sw_data["color"] = sw_data["sector"].map(lambda x: SECTOR_COLORS.get(x,"#757575"))

        fig_sw = px.bar(
            sw_data.sort_values("normalized_weight"),
            x="normalized_weight", y="skill_category",
            color="sector_label", orientation="h",
            color_discrete_map={SECTOR_LABELS.get(k,k): v for k,v in SECTOR_COLORS.items()},
            labels={"normalized_weight":"Normalized Weight (0–1)","skill_category":"","sector_label":"Sector"},
            title=f"Skill Weights — {SCENARIO_LABELS[sc_sw]}"
        )
        fig_sw.add_vline(x=0.6, line_dash="dash", line_color="#aaa", line_width=1)
        fig_sw.update_layout(height=500, plot_bgcolor="#1a1a2e", paper_bgcolor="#1a1a2e",
                             font=dict(color="#e8e4dc"),
                             legend=dict(orientation="h", yanchor="bottom", y=1.02))
        st.plotly_chart(fig_sw, use_container_width=True)

        # Cross-scenario pivot
        st.markdown('<div class="section-header">Skill × Scenario Weight Matrix</div>', unsafe_allow_html=True)
        sw_pivot = skill_wt_df.pivot_table(
            index="skill_category", columns="scenario",
            values="normalized_weight", aggfunc="mean"
        ).fillna(0).round(2)
        sc_order = [s for s in ALL_SCENARIOS if s in sw_pivot.columns]
        sw_pivot = sw_pivot[sc_order]
        sw_pivot.columns = [SCENARIO_LABELS.get(c,c) for c in sw_pivot.columns]
        sw_pivot["Max"] = sw_pivot.max(axis=1)
        sw_pivot = sw_pivot.sort_values("Max", ascending=False).drop(columns="Max").head(25)

        fig_swh = px.imshow(sw_pivot, color_continuous_scale="Purples",
                            zmin=0, zmax=1, text_auto=".2f", aspect="auto",
                            title="Skill Weight Matrix — all 5 scenarios")
        fig_swh.update_layout(height=600, plot_bgcolor="#1a1a2e", paper_bgcolor="#1a1a2e",
                              font=dict(color="#e8e4dc"))
        st.plotly_chart(fig_swh, use_container_width=True)

# ════════════════════════════════════════════════════════════════════
# TAB 6 — SOURCE EVIDENCE
# ════════════════════════════════════════════════════════════════════
with tab6:
    st.markdown('<div class="section-header">Source Evidence — Full Citation Trail</div>', unsafe_allow_html=True)

    col_s1, col_s2 = st.columns(2)
    with col_s1:
        qual_c = sources_f.groupby(["source_id","data_quality"]).size().reset_index(name="signals")
        qual_c = qual_c.sort_values("signals", ascending=False).head(15)
        fig_q = px.bar(qual_c, x="signals", y="source_id", color="data_quality",
                       orientation="h", title="Signals per Source by Quality",
                       color_discrete_map={"high":"#2ecc71","medium":"#f39c12","low":"#e74c3c"})
        fig_q.update_layout(height=420, plot_bgcolor="#1a1a2e", paper_bgcolor="#1a1a2e",
                            font=dict(color="#e8e4dc"), yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig_q, use_container_width=True)

    with col_s2:
        sec_sig = sources_f.groupby("sector").size().reset_index(name="signals")
        sec_sig["sector_label"] = sec_sig["sector"].map(lambda x: SECTOR_LABELS.get(x,x))
        fig_ss = px.pie(sec_sig, values="signals", names="sector_label", hole=0.4,
                        title="Signal Distribution by Sector",
                        color_discrete_sequence=px.colors.qualitative.Set2)
        fig_ss.update_layout(height=420, plot_bgcolor="#1a1a2e", paper_bgcolor="#1a1a2e",
                             font=dict(color="#e8e4dc"))
        st.plotly_chart(fig_ss, use_container_width=True)

    # Source summary table
    st.markdown('<div class="section-header">Source Detail</div>', unsafe_allow_html=True)
    src_sum = sources_df.groupby(
        ["source_id","source_title","source_publisher","source_year","data_quality"]
    ).agg(
        signals=("skill_category","count"),
        sectors=("sector", lambda x: ", ".join(sorted(set(x)))),
        scenarios=("scenario", lambda x: ", ".join(sorted(set(x))))
    ).reset_index().sort_values("signals", ascending=False)

    st.dataframe(
        src_sum[["source_id","source_title","source_publisher","source_year","data_quality","signals","sectors","scenarios"]],
        use_container_width=True, hide_index=True,
        column_config={
            "source_id":    st.column_config.TextColumn("ID", width="small"),
            "source_title": st.column_config.TextColumn("Title", width="large"),
            "source_publisher": st.column_config.TextColumn("Publisher", width="medium"),
            "source_year":  st.column_config.NumberColumn("Year", width="small", format="%d"),
            "data_quality": st.column_config.TextColumn("Quality", width="small"),
            "signals":      st.column_config.NumberColumn("Signals", width="small"),
            "sectors":      st.column_config.TextColumn("Sectors", width="medium"),
            "scenarios":    st.column_config.TextColumn("Scenarios", width="small"),
        }
    )

    # Demand direction
    st.markdown('<div class="section-header">Demand Direction Breakdown</div>', unsafe_allow_html=True)
    dir_c = sources_f["demand_direction"].value_counts().reset_index()
    dir_c.columns = ["direction","count"]
    fig_dir = px.bar(dir_c, x="direction", y="count", color="direction",
                     color_discrete_map={
                         "strong_increase":"#2ecc71","moderate_increase":"#a8d8a8",
                         "stable":"#95a5a6","moderate_decrease":"#f39c12","strong_decrease":"#e74c3c"
                     }, title="Skill Signals by Demand Direction")
    fig_dir.update_layout(height=320, plot_bgcolor="#1a1a2e", paper_bgcolor="#1a1a2e",
                          font=dict(color="#e8e4dc"), showlegend=False)
    st.plotly_chart(fig_dir, use_container_width=True)

# ════════════════════════════════════════════════════════════════════
# TAB 7 — DATA EXPLORER
# ════════════════════════════════════════════════════════════════════
with tab7:
    st.markdown('<div class="section-header">Data Explorer</div>', unsafe_allow_html=True)

    dataset = st.radio("Select dataset",
        ["Gap Analysis","Skill Matrix","Calibration","Source Signals","Coefficients","Skill Weights"],
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
                           f"qatar_{dataset.lower().replace(' ','_')}.csv", "text/csv")

# ── Footer ────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center;color:#555;font-size:0.8rem;'>"
    "Qatar 2030 Labor Market Intelligence · CMU Tepper MSBA Capstone · "
    "5 Scenarios · 41 Sources · Claude API"
    "</div>",
    unsafe_allow_html=True
)
