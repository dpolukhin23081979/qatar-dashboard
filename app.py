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

gap_f     = apply_filters(gap_df)
matrix_f  = matrix_df[matrix_df["scenario"].isin(selected_scenarios or ALL_SCENARIOS)]
sources_f = sources_df[sources_df["scenario"].isin(selected_scenarios or ALL_SCENARIOS)]

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
    st.markdown(f'<div class="metric-card"><div class="metric-value">{avg:.2f}</div><div class="metric-label">Avg Gap Score</div><div style="font-size:0.72rem;color:#6a6458;margin-top:6px;">(0 = aligned · 1 = fully under-supplied)</div></div>', unsafe_allow_html=True)
with k5:
    st.markdown(f'<div class="metric-card"><div class="metric-value">{sources_df["source_id"].nunique()}</div><div class="metric-label">Sources Analysed</div></div>', unsafe_allow_html=True)

st.markdown("---")

# ════════════════════════════════════════════════════════════════════
# TABS
# ════════════════════════════════════════════════════════════════════
tab0, tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
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
        st.markdown('''<div class="metric-card">
<b>Step 1 — Select Scenarios</b><br><br>
Use the sidebar to choose which futures to analyse. Select all 5 for a complete picture, or isolate one to focus.
<b>S1 Diversification</b> is the baseline QNV case and a good starting point.
</div>''', unsafe_allow_html=True)
    with col_h2:
        st.markdown('''<div class="metric-card">
<b>Step 2 — Apply Filters</b><br><br>
Narrow by sector (energy, healthcare, tech etc.) or Qatarization relevance.
Select <b>High</b> to focus on skills where Qatari nationals are the explicit policy priority.
</div>''', unsafe_allow_html=True)
    with col_h3:
        st.markdown('''<div class="metric-card">
<b>Step 3 — Navigate Tabs</b><br><br>
Each tab answers a different question. Start with <b>Skill Gap Analysis</b> for headline findings,
then drill into <b>Industry Matrix</b> and <b>Strategic Demand</b> for sector detail.
</div>''', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📖 Key Definitions")

    # Row 1 — Core Concepts
    st.markdown("#### 📐 Core Concepts")
    r1a, r1b, r1c = st.columns(3)
    with r1a:
        st.markdown('''<div class="metric-card">
            <div style="font-size:0.7rem;color:#8a8070;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:8px;">🔍 Skill Gap</div>
            <div style="font-size:0.9rem;color:#e8e4dc;line-height:1.6;">
            The difference between what Qatar's strategic documents predict will be needed by 2030
            and what employers are <i>actually</i> hiring for today.<br><br>
            <span style="color:#e8513a;font-weight:600;">Large positive gap</span> = strategically critical but market hasn't caught up → Manara should intervene.
            </div>
        </div>''', unsafe_allow_html=True)
    with r1b:
        st.markdown('''<div class="metric-card">
            <div style="font-size:0.7rem;color:#8a8070;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:8px;">📊 Gap Score (±1.0 scale)</div>
            <div style="font-size:0.9rem;color:#e8e4dc;line-height:1.6;">
            <b>Gap Score</b> = Calibration Score (41 sources) minus Posting Frequency (5,067 job postings).<br><br>
            <span style="color:#4CAF50;">● Positive</span> Strategy expects more → intervene<br>
            <span style="color:#aaa;">● Near zero</span> Market & strategy aligned<br>
            <span style="color:#e8513a;">● Negative</span> Market over-supplies this skill
            </div>
        </div>''', unsafe_allow_html=True)
    with r1c:
        st.markdown('''<div class="metric-card">
            <div style="font-size:0.7rem;color:#8a8070;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:8px;">⚖️ Calibration Score</div>
            <div style="font-size:0.9rem;color:#e8e4dc;line-height:1.6;">
            How strongly the 41 sources signal demand for a skill <b>(0–1)</b>.<br><br>
            Built from:<br>
            Source credibility × Scenario alignment × Signal volume<br><br>
            Higher = more sources agree this skill will be needed.
            </div>
        </div>''', unsafe_allow_html=True)

    st.markdown("<div style='margin-top:12px'></div>", unsafe_allow_html=True)

    # Row 2 — Scenarios & Policy
    st.markdown("#### 🎭 Scenarios & Policy")
    r2a, r2b = st.columns(2)
    with r2a:
        st.markdown('''<div class="metric-card">
            <div style="font-size:0.7rem;color:#8a8070;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:8px;">🎭 The 5 Scenarios</div>
            <div style="font-size:0.9rem;color:#e8e4dc;line-height:1.8;">
            Plausible futures for Qatar's economy by 2030:<br>
            <span style="color:#2196F3;">■</span> <b>S1</b> Diversification Acceleration — QNV on track, all sectors grow<br>
            <span style="color:#FF9800;">■</span> <b>S2</b> Hydrocarbon Dominance — LNG expansion, slower diversification<br>
            <span style="color:#4CAF50;">■</span> <b>S3</b> Green Transition Pressure — Decarbonization accelerates<br>
            <span style="color:#9C27B0;">■</span> <b>S4</b> Knowledge Economy Leap — Qatar as R&D and AI hub<br>
            <span style="color:#F44336;">■</span> <b>S5</b> Regional Hub — Qatar as services and diplomacy centre
            </div>
        </div>''', unsafe_allow_html=True)
    with r2b:
        st.markdown('''<div class="metric-card">
            <div style="font-size:0.7rem;color:#8a8070;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:8px;">🇶🇦 Qatarization Priority</div>
            <div style="font-size:0.9rem;color:#e8e4dc;line-height:1.6;">
            Qatar's policy to increase employment of Qatari nationals per <b>QNV 2030 Human Development</b> pillar.<br><br>
            <span style="color:#e8513a;font-weight:600;">High</span> = Strategic documents explicitly flag developing Qatari talent here → Most critical for Manara programme design.<br><br>
            <span style="color:#D4A017;font-weight:600;">Medium</span> = Relevant but secondary priority.<br>
            <span style="color:#4C78A8;font-weight:600;">Low</span> = General workforce need, not Qatari-specific.
            </div>
        </div>''', unsafe_allow_html=True)

    st.markdown("<div style='margin-top:12px'></div>", unsafe_allow_html=True)

    # Row 3 — Technical / Model
    st.markdown("#### 🛠️ Technical & Model")
    r3a, r3b, r3c = st.columns(3)
    with r3a:
        st.markdown('''<div class="metric-card">
            <div style="font-size:0.7rem;color:#8a8070;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:8px;">🎯 Signal Count Penalty</div>
            <div style="font-size:0.9rem;color:#e8e4dc;line-height:1.6;">
            A <b>square-root balancing factor</b> for scenarios with fewer contributing sources.<br><br>
            Prevents a low-signal scenario from dominating. Ensures all 5 scenarios are fairly compared.
            </div>
        </div>''', unsafe_allow_html=True)
    with r3b:
        st.markdown('''<div class="metric-card">
            <div style="font-size:0.7rem;color:#8a8070;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:8px;">📈 Demand Direction Arrows</div>
            <div style="font-size:0.9rem;color:#e8e4dc;line-height:1.8;">
            <span style="color:#4CAF50;">↑↑</span> Strong increase (gap ≥ 0.6) — urgent<br>
            <span style="color:#8BC34A;">↑</span>  Moderate increase (0.2–0.6)<br>
            <span style="color:#aaa;">→</span>  Stable / aligned (−0.2–0.2)<br>
            <span style="color:#FF9800;">↓</span>  Moderate decrease<br>
            <span style="color:#aaa;">—</span>  No signal for this combination
            </div>
        </div>''', unsafe_allow_html=True)
    with r3c:
        st.markdown('''<div class="metric-card">
            <div style="font-size:0.7rem;color:#8a8070;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:8px;">🏭 Sector Classification</div>
            <div style="font-size:0.9rem;color:#e8e4dc;line-height:1.6;">
            Each job posting is assigned to one of <b>8 sectors</b> using a 5-layer classifier:<br><br>
            Industry tags → LinkedIn industry → Job function → Job title → SOC codes<br><br>
            Unmatched jobs → labelled <b>cross_sector</b>.
            </div>
        </div>''', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('''<div style="text-align:center;color:#888;font-size:0.85rem;padding:8px 0;">
Built for the <b>Qatar Foundation Manara Programme</b> · CMU Tepper MSBA Capstone 2025 ·
41 authoritative sources · 5,067 Qatar job postings · 5 scenarios
</div>''', unsafe_allow_html=True)

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
    st.info("📌 **What this tab shows:** Model transparency. Which sources drive each scenario, how quality weights are applied, and how the signal-count penalty balances scenarios. Use to justify findings to stakeholders.")

    # ── Weight definitions ────────────────────────────────────────────────
    st.markdown('<div class="section-header">How Scores Are Built</div>', unsafe_allow_html=True)
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

    if coeff_df is None:
        st.warning("scenario_coefficients.csv not found — upload it to the data/ folder on GitHub.")
    else:
        import math

        # ── Signal count & penalty charts ────────────────────────────────
        st.markdown('<div class="section-header">Signal Count & Penalty per Scenario</div>', unsafe_allow_html=True)

        sc_counts = coeff_df.groupby("scenario")["signal_count"].sum().reset_index()
        sc_counts["scenario_label"] = sc_counts["scenario"].map(SCENARIO_LABELS)
        max_sig = sc_counts["signal_count"].max()
        sc_counts["penalty"] = sc_counts["signal_count"].apply(
            lambda x: round(math.sqrt(x / max_sig), 3))

        col_s1, col_s2 = st.columns(2)
        with col_s1:
            fig_sig = px.bar(
                sc_counts.sort_values("signal_count", ascending=False),
                x="scenario_label", y="signal_count",
                color="scenario", color_discrete_map=SCENARIO_COLORS,
                text="signal_count",
                title="Signal Count per Scenario",
                labels={"scenario_label": "Scenario", "signal_count": "Number of Signals"}
            )
            fig_sig.update_traces(textposition="outside")
            fig_sig.update_layout(
                height=350, showlegend=False,
                plot_bgcolor="white", paper_bgcolor="white",
                font=dict(size=12), title_font_size=13, xaxis_tickangle=-15
            )
            st.plotly_chart(fig_sig, use_container_width=True)

        with col_s2:
            fig_pen = px.bar(
                sc_counts.sort_values("penalty", ascending=False),
                x="scenario_label", y="penalty",
                color="scenario", color_discrete_map=SCENARIO_COLORS,
                text="penalty",
                title="Signal-Count Penalty Factor (√ ratio)",
                labels={"scenario_label": "Scenario", "penalty": "Penalty (0–1)"}
            )
            fig_pen.update_traces(textposition="outside")
            fig_pen.add_hline(y=1.0, line_dash="dash", line_color="gray",
                              annotation_text="max (S1)")
            fig_pen.update_layout(
                height=350, showlegend=False,
                plot_bgcolor="white", paper_bgcolor="white",
                font=dict(size=12), title_font_size=13, xaxis_tickangle=-15
            )
            st.plotly_chart(fig_pen, use_container_width=True)

        # ── Source contributions ──────────────────────────────────────────
        st.markdown('<div class="section-header">Source Contributions per Scenario</div>', unsafe_allow_html=True)
        st.caption("Bar = adjusted weighted score (weighted_score × penalty). Color = source data quality.")

        sc_sel = st.selectbox(
            "Filter by scenario", ["All"] + ALL_SCENARIOS,
            format_func=lambda x: "All" if x == "All" else SCENARIO_LABELS[x],
            key="coeff_sc"
        )
        df_show = coeff_df if sc_sel == "All" else coeff_df[coeff_df["scenario"] == sc_sel]

        # Apply penalty
        pen_map = sc_counts.set_index("scenario")["penalty"].to_dict()
        df_plot = df_show.copy()
        df_plot["adj_weight"] = df_plot.apply(
            lambda r: r["total_weighted"] * pen_map.get(r["scenario"], 1.0), axis=1)
        df_plot = df_plot.nlargest(25, "adj_weight").sort_values("adj_weight")
        df_plot["scenario_label"] = df_plot["scenario"].map(SCENARIO_LABELS)

        QUALITY_COLORS = {"high": "#2ecc71", "medium": "#f39c12", "low": "#e74c3c"}
        fig_contrib = px.bar(
            df_plot,
            x="adj_weight", y="source_id",
            color="data_quality",
            color_discrete_map=QUALITY_COLORS,
            orientation="h",
            hover_data=["scenario_label", "publisher", "signal_count", "avg_scenario_w"],
            text=df_plot["adj_weight"].round(2),
            title=f"Source Contributions — {'All Scenarios' if sc_sel == 'All' else SCENARIO_LABELS[sc_sel]}",
            labels={"adj_weight": "Adjusted Weight", "source_id": "Source",
                    "data_quality": "Source Quality"}
        )
        fig_contrib.update_traces(textposition="outside", textfont_size=10)
        fig_contrib.update_layout(
            height=max(400, len(df_plot) * 30),
            plot_bgcolor="white", paper_bgcolor="white",
            font=dict(size=12), title_font_size=13,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, title="Source Quality")
        )
        st.plotly_chart(fig_contrib, use_container_width=True)

        # ── Source × Scenario weight matrix ──────────────────────────────
        st.markdown('<div class="section-header">Source × Scenario Weight Matrix</div>', unsafe_allow_html=True)
        st.caption("Average scenario_weight (0–1) extracted by Claude per source × scenario pair.")

        pivot_w = coeff_df.pivot_table(
            index="source_id", columns="scenario",
            values="avg_scenario_w", aggfunc="mean"
        ).fillna(0).round(2)
        sc_order_w = [s for s in ALL_SCENARIOS if s in pivot_w.columns]
        pivot_w = pivot_w[sc_order_w]
        pivot_w.columns = [SCENARIO_LABELS.get(c, c) for c in pivot_w.columns]
        pivot_w["Total"] = pivot_w.sum(axis=1)
        pivot_w = pivot_w.sort_values("Total", ascending=False).drop(columns="Total")

        fig_wmat = px.imshow(
            pivot_w, color_continuous_scale="Blues",
            zmin=0, zmax=1, text_auto=".2f", aspect="auto",
            title="Source × Scenario Weight Matrix"
        )
        fig_wmat.update_layout(
            height=max(400, len(pivot_w) * 22),
            font=dict(size=10), title_font_size=13,
            coloraxis_colorbar=dict(title="Weight")
        )
        st.plotly_chart(fig_wmat, use_container_width=True)

        with st.expander("📥 Download coefficient data"):
            csv_c = coeff_df.to_csv(index=False).encode("utf-8")
            st.download_button("⬇ Download CSV", data=csv_c,
                               file_name="scenario_coefficients.csv", mime="text/csv")

# ════════════════════════════════════════════════════════════════════
# TAB 5 — SKILL WEIGHTS
# ════════════════════════════════════════════════════════════════════

with tab5:
    st.markdown('<div class="section-header">Skill Weights per Scenario</div>', unsafe_allow_html=True)
    st.info("📌 **What this tab shows:** How much strategic weight each skill carries within each scenario (0–1). Skills with high bars across all 5 scenarios are universally important — the safest Manara investment bets.")
    st.caption("Normalized adjusted weight (0–1 within each scenario). Color = industry sector. Dashed line = 0.6 high-impact threshold.")

    if skill_wt_df is None:
        st.warning("scenario_skill_weights.csv not found — upload it to the data/ folder on GitHub.")
    else:
        SECTOR_COLORS_SW = {
            "technology_digital": "#1976D2", "energy_lng": "#F57C00",
            "healthcare": "#388E3C", "education": "#7B1FA2",
            "finance_banking": "#C62828", "construction_real_estate": "#5D4037",
            "tourism_hospitality": "#00838F", "cross_sector": "#757575",
        }

        # ── Top skills per scenario — interactive ─────────────────────────
        st.markdown('<div class="section-header">Top Skills — Select Scenario</div>', unsafe_allow_html=True)
        col_sw1, col_sw2 = st.columns([2, 1])
        with col_sw1:
            sc_sw = st.selectbox(
                "Scenario", ALL_SCENARIOS,
                format_func=lambda x: SCENARIO_LABELS[x], key="sw_sc"
            )
        with col_sw2:
            top_n = st.slider("Top N skills", 10, 30, 15)

        sw_data = (
            skill_wt_df[skill_wt_df["scenario"] == sc_sw]
            .nlargest(top_n, "normalized_weight")
            .sort_values("normalized_weight")
        )
        sw_data["sector_label"] = sw_data["sector"].map(
            lambda x: SECTOR_LABELS.get(x, x.replace("_", " ").title()))

        fig_sw = px.bar(
            sw_data,
            x="normalized_weight", y="skill_category",
            color="sector_label",
            color_discrete_map={
                SECTOR_LABELS.get(k, k.replace("_", " ").title()): v
                for k, v in SECTOR_COLORS_SW.items()
            },
            orientation="h",
            text=sw_data["normalized_weight"].round(2),
            hover_data=["signal_count", "sources"] if "sources" in skill_wt_df.columns else ["signal_count"],
            title=f"Skill Weights — {SCENARIO_LABELS[sc_sw]}",
            labels={"normalized_weight": "Normalized Weight (0–1)",
                    "skill_category": "", "sector_label": "Sector"}
        )
        fig_sw.add_vline(x=0.6, line_dash="dash", line_color="#999", line_width=1.5,
                         annotation_text="high impact", annotation_position="top right",
                         annotation_font_size=10)
        fig_sw.update_traces(textposition="outside", textfont_size=10)
        fig_sw.update_layout(
            height=max(420, top_n * 28),
            plot_bgcolor="white", paper_bgcolor="white",
            font=dict(size=12), title_font_size=13,
            xaxis=dict(range=[0, 1.3]),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, title="Sector")
        )
        st.plotly_chart(fig_sw, use_container_width=True)

        # ── All 5 scenarios — facet chart ────────────────────────────────
        st.markdown('<div class="section-header">All 5 Scenarios — Top 10 Skills Each</div>', unsafe_allow_html=True)
        st.caption("Compare priorities across all scenarios at a glance.")

        top10_all = (
            skill_wt_df.groupby("scenario", group_keys=False)
            .apply(lambda g: g.nlargest(10, "normalized_weight"))
            .reset_index(drop=True)
        )
        top10_all["scenario_label"] = top10_all["scenario"].map(SCENARIO_LABELS)
        top10_all["sector_label"] = top10_all["sector"].map(
            lambda x: SECTOR_LABELS.get(x, x.replace("_", " ").title()))

        fig_all = px.bar(
            top10_all.sort_values(["scenario", "normalized_weight"]),
            x="normalized_weight", y="skill_category",
            color="sector_label",
            color_discrete_map={
                SECTOR_LABELS.get(k, k.replace("_", " ").title()): v
                for k, v in SECTOR_COLORS_SW.items()
            },
            facet_col="scenario_label", facet_col_wrap=3,
            orientation="h",
            labels={"normalized_weight": "Weight", "skill_category": "",
                    "sector_label": "Sector"},
            title="Top 10 Skills per Scenario"
        )
        fig_all.add_vline(x=0.6, line_dash="dash", line_color="#ccc", line_width=1)
        fig_all.update_layout(
            height=600, plot_bgcolor="white", paper_bgcolor="white",
            font=dict(size=10), title_font_size=13,
            legend=dict(orientation="h", yanchor="bottom", y=-0.18, title="Sector")
        )
        fig_all.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
        st.plotly_chart(fig_all, use_container_width=True)

        # ── Cross-scenario comparison ─────────────────────────────────────
        st.markdown('<div class="section-header">Cross-Scenario Skill Comparison</div>', unsafe_allow_html=True)
        st.caption("Skills in 2+ scenarios. Universal skills (high across all) = safest Manara investment.")

        pivot_sw = skill_wt_df.pivot_table(
            index="skill_category", columns="scenario",
            values="normalized_weight", aggfunc="mean"
        ).fillna(0)
        sc_order_sw = [s for s in ALL_SCENARIOS if s in pivot_sw.columns]
        pivot_sw = pivot_sw[sc_order_sw]
        pivot_sw["scenario_count"] = (pivot_sw > 0.1).sum(axis=1)
        pivot_sw["max_weight"] = pivot_sw.drop(columns="scenario_count").max(axis=1)
        cross = (
            pivot_sw[pivot_sw["scenario_count"] >= 2]
            .sort_values("max_weight", ascending=False)
            .head(20)
            .drop(columns=["scenario_count", "max_weight"])
            .reset_index()
        )
        cross_melted = cross.melt(
            id_vars="skill_category", var_name="scenario", value_name="weight")
        cross_melted["scenario_label"] = cross_melted["scenario"].map(SCENARIO_LABELS)

        fig_cross = px.bar(
            cross_melted,
            x="skill_category", y="weight",
            color="scenario_label", barmode="group",
            color_discrete_map={v: SCENARIO_COLORS[k] for k, v in SCENARIO_LABELS.items()},
            text=cross_melted["weight"].round(2),
            labels={"skill_category": "Skill", "weight": "Normalized Weight (0–1)",
                    "scenario_label": "Scenario"},
            title="Cross-Scenario Skill Weights — Skills in 2+ Scenarios"
        )
        fig_cross.add_hline(y=0.6, line_dash="dash", line_color="#999",
                            annotation_text="high impact threshold",
                            annotation_position="top right", annotation_font_size=10)
        fig_cross.update_traces(textposition="outside", textfont_size=8)
        fig_cross.update_layout(
            height=500, plot_bgcolor="white", paper_bgcolor="white",
            font=dict(size=11), title_font_size=13,
            xaxis_tickangle=-35,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, title="Scenario")
        )
        st.plotly_chart(fig_cross, use_container_width=True)

        # ── Full skill × scenario heatmap ─────────────────────────────────
        st.markdown('<div class="section-header">Skill × Scenario Weight Matrix</div>', unsafe_allow_html=True)

        sw_pivot = skill_wt_df.pivot_table(
            index="skill_category", columns="scenario",
            values="normalized_weight", aggfunc="mean"
        ).fillna(0).round(2)
        sc_order_p = [s for s in ALL_SCENARIOS if s in sw_pivot.columns]
        sw_pivot = sw_pivot[sc_order_p]
        sw_pivot.columns = [SCENARIO_LABELS.get(c, c) for c in sw_pivot.columns]
        sw_pivot["Max"] = sw_pivot.max(axis=1)
        sw_pivot = sw_pivot.sort_values("Max", ascending=False).drop(columns="Max").head(30)

        fig_swh = px.imshow(
            sw_pivot, color_continuous_scale="Purples",
            zmin=0, zmax=1, text_auto=".2f", aspect="auto",
            title="Skill Weight Matrix — all 5 scenarios"
        )
        fig_swh.update_layout(
            height=max(500, len(sw_pivot) * 22),
            font=dict(size=10), title_font_size=13,
            coloraxis_colorbar=dict(title="Weight (0–1)")
        )
        st.plotly_chart(fig_swh, use_container_width=True)

        with st.expander("📥 Download skill weights data"):
            csv_sw = skill_wt_df.to_csv(index=False).encode("utf-8")
            st.download_button("⬇ Download CSV", data=csv_sw,
                               file_name="scenario_skill_weights.csv", mime="text/csv")

with tab6:
    st.markdown('<div class="section-header">Source Evidence — Full Citation Trail</div>', unsafe_allow_html=True)
    st.info("📌 **What this tab shows:** Full audit trail. Every skill signal traced back to its publication — IMF, World Bank, QNV, WEF, ILO, RAND, McKinsey, Goldman Sachs and 33 more. Use to verify or cite any finding.")

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
    st.info("📌 **What this tab shows:** Search, filter, and download any underlying dataset for custom analysis or reporting. Switch between Gap Analysis, Skill Matrix, Calibration, Sources, Coefficients, and Skill Weights.")

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
