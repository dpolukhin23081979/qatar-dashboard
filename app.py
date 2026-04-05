import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path

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

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

h1, h2, h3 {
    font-family: 'DM Serif Display', serif;
}

.main { background-color: #f5f3ef; }

.stApp { background-color: #f5f3ef; }

.metric-card {
    background: white;
    border-radius: 12px;
    padding: 20px 24px;
    border-left: 4px solid #8B0000;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    margin-bottom: 8px;
}

.metric-value {
    font-size: 2rem;
    font-weight: 600;
    color: #8B0000;
    line-height: 1;
}

.metric-label {
    font-size: 0.8rem;
    color: #666;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-top: 4px;
}

.section-header {
    font-family: 'DM Serif Display', serif;
    font-size: 1.4rem;
    color: #1a1a1a;
    border-bottom: 2px solid #8B0000;
    padding-bottom: 8px;
    margin: 24px 0 16px 0;
}

.source-tag {
    display: inline-block;
    background: #f0e8e8;
    color: #8B0000;
    border-radius: 4px;
    padding: 2px 8px;
    font-size: 0.75rem;
    font-weight: 500;
    margin: 2px;
}

.scenario-s1 { color: #2196F3; font-weight: 600; }
.scenario-s2 { color: #FF9800; font-weight: 600; }
.scenario-s3 { color: #4CAF50; font-weight: 600; }

div[data-testid="stSidebarContent"] {
    background-color: #1a1a2e;
    color: white;
}

.sidebar-title {
    color: white;
    font-family: 'DM Serif Display', serif;
    font-size: 1.3rem;
    padding: 8px 0;
}
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

    # Cap gap scores
    gap["gap_score"] = gap["gap_score"].clip(-1.0, 1.0)

    return gap, matrix, calib, sources

gap_df, matrix_df, calib_df, sources_df = load_data()

# ── Constants ─────────────────────────────────────────────────────────────
SCENARIO_LABELS = {
    "S1": "S1: Diversification Acceleration",
    "S2": "S2: Hydrocarbon Dominance",
    "S3": "S3: Green Transition"
}
SCENARIO_COLORS = {"S1": "#2196F3", "S2": "#FF9800", "S3": "#4CAF50"}
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

# ── Sidebar ───────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-title">🇶🇦 Qatar 2030<br>Labor Market Intelligence</div>', unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("### Filters")

    selected_scenarios = st.multiselect(
        "Scenarios",
        options=["S1", "S2", "S3"],
        default=["S1", "S2", "S3"],
        format_func=lambda x: SCENARIO_LABELS[x]
    )

    all_sectors = sorted(gap_df["sector"].unique().tolist())
    selected_sectors = st.multiselect(
        "Sectors",
        options=all_sectors,
        default=all_sectors,
        format_func=lambda x: SECTOR_LABELS.get(x, x)
    )

    qat_filter = st.selectbox(
        "Qatarization Relevance",
        options=["All", "high", "medium", "low"],
        index=0
    )

    time_filter = st.selectbox(
        "Time Horizon",
        options=["All", "near_term", "medium_term", "both"],
        index=0
    )

    st.markdown("---")
    st.markdown("**Data sources**")
    st.markdown(f"- {sources_df['source_id'].nunique()} publications")
    st.markdown(f"- {len(sources_df)} skill signals")
    st.markdown(f"- {gap_df['skill_category'].nunique()} skill categories")
    st.markdown(f"- Horizon: 2025–2030")

# ── Filter data ───────────────────────────────────────────────────────────
def apply_filters(df):
    d = df.copy()
    if selected_scenarios:
        d = d[d["scenario"].isin(selected_scenarios)]
    if selected_sectors:
        d = d[d["sector"].isin(selected_sectors)]
    if qat_filter != "All":
        d = d[d["qatarization_relevance"] == qat_filter]
    if time_filter != "All":
        d = d[d["time_horizon"] == time_filter]
    return d

gap_filtered    = apply_filters(gap_df)
matrix_filtered = matrix_df[matrix_df["scenario"].isin(selected_scenarios or ["S1","S2","S3"])]
sources_filtered = sources_df[sources_df["scenario"].isin(selected_scenarios or ["S1","S2","S3"])]

# ── Header ────────────────────────────────────────────────────────────────
st.markdown("# Qatar 2030 Labor Market Intelligence")
st.markdown("*Strategic Skill Demand Scenarios — Evidence-based workforce gap analysis for Manara & QNV 2030*")
st.markdown("---")

# ── KPI row ───────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)

top_gap = gap_filtered[gap_filtered["gap_score"] > 0]
with k1:
    st.markdown(f'<div class="metric-card"><div class="metric-value">{len(top_gap)}</div><div class="metric-label">Skill Gaps Identified</div></div>', unsafe_allow_html=True)
with k2:
    st.markdown(f'<div class="metric-card"><div class="metric-value">{gap_filtered["sector"].nunique()}</div><div class="metric-label">Sectors Covered</div></div>', unsafe_allow_html=True)
with k3:
    high_qat = top_gap[top_gap["qatarization_relevance"] == "high"]
    st.markdown(f'<div class="metric-card"><div class="metric-value">{len(high_qat)}</div><div class="metric-label">High Qatarization Priority</div></div>', unsafe_allow_html=True)
with k4:
    avg_gap = top_gap["gap_score"].mean()
    st.markdown(f'<div class="metric-card"><div class="metric-value">{avg_gap:.2f}</div><div class="metric-label">Avg Gap Score</div></div>', unsafe_allow_html=True)
with k5:
    st.markdown(f'<div class="metric-card"><div class="metric-value">{sources_df["source_id"].nunique()}</div><div class="metric-label">Sources Analysed</div></div>', unsafe_allow_html=True)

st.markdown("---")

# ── Tabs ──────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Skill Gap Analysis",
    "🏭 Industry Matrix",
    "🎯 Strategic Demand",
    "📚 Source Evidence",
    "📋 Data Explorer"
])

# ════════════════════════════════════════════════════════════════════════
# TAB 1 — SKILL GAP ANALYSIS
# ════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown('<div class="section-header">Strategic Skill Gaps — Scenario vs. Market Reality</div>', unsafe_allow_html=True)
    st.caption("Gap score = strategic expectation (from 18 published sources) minus actual hiring frequency (from 5,067 Qatar job postings). Positive = under-supplied.")

    col_left, col_right = st.columns([2, 1])

    with col_left:
        # Top skill gaps bar chart
        top_gaps = gap_filtered[gap_filtered["gap_score"] > 0].nlargest(20, "gap_score").copy()
        top_gaps["label"] = top_gaps["sector"].map(lambda x: SECTOR_LABELS.get(x, x)).str[:12] + " | " + top_gaps["skill_category"].str[:28]
        top_gaps["scenario_label"] = top_gaps["scenario"].map(SCENARIO_LABELS)

        fig = px.bar(
            top_gaps,
            x="gap_score",
            y="label",
            color="scenario",
            color_discrete_map=SCENARIO_COLORS,
            orientation="h",
            labels={"gap_score": "Gap Score", "label": "", "scenario": "Scenario"},
            title="Top Strategic Skill Gaps",
            hover_data=["skill_category", "sector", "qatarization_relevance", "time_horizon"]
        )
        fig.update_layout(
            height=520,
            plot_bgcolor="white",
            paper_bgcolor="white",
            yaxis=dict(autorange="reversed"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
            font=dict(family="DM Sans"),
            title_font=dict(family="DM Serif Display", size=16)
        )
        fig.add_vline(x=0, line_dash="dash", line_color="gray", line_width=1)
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        # Qatarization breakdown donut
        qat_counts = top_gaps["qatarization_relevance"].value_counts().reset_index()
        qat_counts.columns = ["relevance", "count"]

        fig_donut = px.pie(
            qat_counts,
            values="count",
            names="relevance",
            hole=0.55,
            color="relevance",
            color_discrete_map={"high": "#8B0000", "medium": "#D4A017", "low": "#4C78A8"},
            title="Qatarization Relevance<br>of Top Gaps"
        )
        fig_donut.update_layout(
            height=260,
            plot_bgcolor="white",
            paper_bgcolor="white",
            showlegend=True,
            font=dict(family="DM Sans"),
            title_font=dict(family="DM Serif Display", size=14),
            margin=dict(t=60, b=20, l=20, r=20)
        )
        st.plotly_chart(fig_donut, use_container_width=True)

        # Time horizon breakdown
        th_counts = top_gaps["time_horizon"].value_counts().reset_index()
        th_counts.columns = ["horizon", "count"]
        fig_th = px.bar(
            th_counts,
            x="count",
            y="horizon",
            orientation="h",
            color="horizon",
            color_discrete_sequence=["#8B0000", "#D4A017", "#4C78A8"],
            title="Time Horizon of Gaps"
        )
        fig_th.update_layout(
            height=220,
            plot_bgcolor="white",
            paper_bgcolor="white",
            showlegend=False,
            font=dict(family="DM Sans"),
            title_font=dict(family="DM Serif Display", size=14),
            margin=dict(t=50, b=20, l=20, r=20)
        )
        st.plotly_chart(fig_th, use_container_width=True)

    # Skill gap heatmap
    st.markdown('<div class="section-header">Skill Gap Heatmap: Scenario × Skill Category</div>', unsafe_allow_html=True)

    pivot = gap_filtered.pivot_table(
        index="skill_category",
        columns="scenario",
        values="gap_score",
        aggfunc="mean"
    ).fillna(0).clip(-1, 1)

    pivot = pivot.loc[pivot.abs().max(axis=1).nlargest(20).index]
    pivot.columns = [SCENARIO_LABELS.get(c, c) for c in pivot.columns]

    fig_heat = px.imshow(
        pivot,
        color_continuous_scale="RdYlGn",
        zmin=-1, zmax=1,
        text_auto=".2f",
        aspect="auto",
        title="Skill Gap Heatmap (green = under-supplied, red = over-supplied)"
    )
    fig_heat.update_layout(
        height=600,
        font=dict(family="DM Sans"),
        title_font=dict(family="DM Serif Display", size=16),
        coloraxis_colorbar=dict(title="Gap Score")
    )
    st.plotly_chart(fig_heat, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════
# TAB 2 — INDUSTRY MATRIX
# ════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-header">Industry × Scenario Skill Gap Matrix</div>', unsafe_allow_html=True)
    st.caption("Average gap score per sector × scenario. Green = strategic demand exceeds market supply. Red = over-supplied.")

    pivot_ind = gap_filtered.pivot_table(
        index="sector",
        columns="scenario",
        values="gap_score",
        aggfunc="mean"
    ).fillna(0).clip(-1, 1)

    pivot_ind.index = [SECTOR_LABELS.get(i, i) for i in pivot_ind.index]
    pivot_ind.columns = [SCENARIO_LABELS.get(c, c) for c in pivot_ind.columns]
    pivot_ind = pivot_ind.loc[pivot_ind.mean(axis=1).sort_values(ascending=False).index]

    # Build annotation text
    def gap_arrow(v):
        if v >= 0.6:  return f"{v:.2f}\n↑↑"
        if v >= 0.2:  return f"{v:.2f}\n↑"
        if v > -0.2:  return f"{v:.2f}\n→" if v != 0 else "—"
        if v > -0.6:  return f"{v:.2f}\n↓"
        return f"{v:.2f}\n↓↓"

    annot_text = [[gap_arrow(v) for v in row] for row in pivot_ind.values]

    fig_ind = go.Figure(data=go.Heatmap(
        z=pivot_ind.values,
        x=pivot_ind.columns.tolist(),
        y=pivot_ind.index.tolist(),
        text=annot_text,
        texttemplate="%{text}",
        colorscale="RdYlGn",
        zmin=-1, zmax=1,
        colorbar=dict(title="Gap Score"),
        hoverongaps=False,
    ))
    fig_ind.update_layout(
        height=500,
        font=dict(family="DM Sans", size=13),
        title_font=dict(family="DM Serif Display", size=16),
        xaxis=dict(side="bottom"),
        plot_bgcolor="white",
        paper_bgcolor="white",
    )
    st.plotly_chart(fig_ind, use_container_width=True)

    # Sector gap ranking
    st.markdown('<div class="section-header">Sector Gap Ranking</div>', unsafe_allow_html=True)
    sector_avg = gap_filtered[gap_filtered["gap_score"] > 0].groupby("sector")["gap_score"].mean().reset_index()
    sector_avg["sector_label"] = sector_avg["sector"].map(lambda x: SECTOR_LABELS.get(x, x))
    sector_avg = sector_avg.sort_values("gap_score", ascending=False)

    fig_sector = px.bar(
        sector_avg,
        x="sector_label",
        y="gap_score",
        color="gap_score",
        color_continuous_scale="RdYlGn",
        labels={"gap_score": "Avg Gap Score", "sector_label": "Sector"},
        title="Average Strategic Skill Gap by Sector"
    )
    fig_sector.update_layout(
        height=380,
        plot_bgcolor="white",
        paper_bgcolor="white",
        showlegend=False,
        font=dict(family="DM Sans"),
        title_font=dict(family="DM Serif Display", size=16),
        xaxis_tickangle=-30,
        coloraxis_showscale=False
    )
    st.plotly_chart(fig_sector, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════
# TAB 3 — STRATEGIC DEMAND
# ════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-header">Strategic Demand Intensity — From Published Sources</div>', unsafe_allow_html=True)
    st.caption("Based entirely on 18 published sources (IMF, World Bank, QNV, WEF, ILO etc.) — independent of job postings data.")

    # Sector × Scenario demand intensity
    pivot2 = matrix_filtered.pivot_table(
        index="sector",
        columns="scenario",
        values="normalized_score",
        aggfunc="mean"
    ).fillna(0)
    pivot2.index = [SECTOR_LABELS.get(i, i) for i in pivot2.index]
    pivot2.columns = [SCENARIO_LABELS.get(c, c) for c in pivot2.columns]

    fig_demand = px.bar(
        pivot2.reset_index().melt(id_vars="sector", var_name="Scenario", value_name="Demand Score"),
        x="sector",
        y="Demand Score",
        color="Scenario",
        barmode="group",
        color_discrete_sequence=list(SCENARIO_COLORS.values()),
        title="Strategic Skill Demand Intensity by Sector & Scenario",
        labels={"sector": "Sector", "Demand Score": "Normalized Demand Score"}
    )
    fig_demand.update_layout(
        height=420,
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="DM Sans"),
        title_font=dict(family="DM Serif Display", size=16),
        xaxis_tickangle=-30,
        legend=dict(orientation="h", yanchor="bottom", y=1.02)
    )
    st.plotly_chart(fig_demand, use_container_width=True)

    col_a, col_b = st.columns(2)

    with col_a:
        # Top skills by scenario
        st.markdown('<div class="section-header">Top Skills per Scenario</div>', unsafe_allow_html=True)
        sel_scenario = st.selectbox("Select scenario", ["S1", "S2", "S3"], format_func=lambda x: SCENARIO_LABELS[x], key="scenario_sel")
        top_matrix = matrix_filtered[matrix_filtered["scenario"] == sel_scenario].nlargest(15, "normalized_score")

        fig_top = px.bar(
            top_matrix,
            x="normalized_score",
            y="skill_category",
            color="sector",
            orientation="h",
            labels={"normalized_score": "Demand Score", "skill_category": "", "sector": "Sector"},
            title=f"Top Skills — {SCENARIO_LABELS[sel_scenario]}"
        )
        fig_top.update_layout(
            height=450,
            plot_bgcolor="white",
            paper_bgcolor="white",
            yaxis=dict(autorange="reversed"),
            font=dict(family="DM Sans"),
            title_font=dict(family="DM Serif Display", size=14),
            showlegend=True
        )
        st.plotly_chart(fig_top, use_container_width=True)

    with col_b:
        # Qatarization priority gaps
        st.markdown('<div class="section-header">Qatarization Priority Gaps</div>', unsafe_allow_html=True)
        qat_gaps = gap_filtered[
            (gap_filtered["qatarization_relevance"] == "high") &
            (gap_filtered["gap_score"] > 0)
        ].nlargest(15, "gap_score").copy()
        qat_gaps["label"] = qat_gaps["skill_category"].str[:30]

        fig_qat = px.bar(
            qat_gaps,
            x="gap_score",
            y="label",
            color="scenario",
            color_discrete_map=SCENARIO_COLORS,
            orientation="h",
            labels={"gap_score": "Gap Score", "label": "", "scenario": "Scenario"},
            title="High Qatarization Priority Gaps"
        )
        fig_qat.update_layout(
            height=450,
            plot_bgcolor="white",
            paper_bgcolor="white",
            yaxis=dict(autorange="reversed"),
            font=dict(family="DM Sans"),
            title_font=dict(family="DM Serif Display", size=14),
            legend=dict(orientation="h", yanchor="bottom", y=1.02)
        )
        st.plotly_chart(fig_qat, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════
# TAB 4 — SOURCE EVIDENCE
# ════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-header">Source Evidence — Full Citation Trail</div>', unsafe_allow_html=True)
    st.caption("Every skill signal is traceable to a specific published source. All 18 sources listed below.")

    col_src1, col_src2 = st.columns(2)

    with col_src1:
        # Sources by quality
        qual_counts = sources_filtered.groupby(["source_id", "data_quality"]).size().reset_index(name="signals")
        qual_counts = qual_counts.sort_values("signals", ascending=False).head(15)
        fig_qual = px.bar(
            qual_counts,
            x="signals",
            y="source_id",
            color="data_quality",
            orientation="h",
            color_discrete_map={"high": "#2ecc71", "medium": "#f39c12", "low": "#e74c3c"},
            title="Signals per Source (by Data Quality)",
            labels={"signals": "Number of Signals", "source_id": "Source", "data_quality": "Quality"}
        )
        fig_qual.update_layout(
            height=420,
            plot_bgcolor="white",
            paper_bgcolor="white",
            yaxis=dict(autorange="reversed"),
            font=dict(family="DM Sans"),
            title_font=dict(family="DM Serif Display", size=14)
        )
        st.plotly_chart(fig_qual, use_container_width=True)

    with col_src2:
        # Signals by sector
        sec_sig = sources_filtered.groupby("sector").size().reset_index(name="signals")
        sec_sig["sector_label"] = sec_sig["sector"].map(lambda x: SECTOR_LABELS.get(x, x))
        fig_sec_sig = px.pie(
            sec_sig,
            values="signals",
            names="sector_label",
            hole=0.4,
            title="Signal Distribution by Sector",
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig_sec_sig.update_layout(
            height=420,
            font=dict(family="DM Sans"),
            title_font=dict(family="DM Serif Display", size=14)
        )
        st.plotly_chart(fig_sec_sig, use_container_width=True)

    # Source detail table
    st.markdown('<div class="section-header">Source Detail</div>', unsafe_allow_html=True)
    src_summary = sources_df.groupby(["source_id", "source_title", "source_publisher", "source_year", "data_quality"]).agg(
        signals=("skill_category", "count"),
        sectors=("sector", lambda x: ", ".join(sorted(set(x)))),
        scenarios=("scenario", lambda x: ", ".join(sorted(set(x))))
    ).reset_index().sort_values("signals", ascending=False)

    st.dataframe(
        src_summary[["source_id", "source_title", "source_publisher", "source_year", "data_quality", "signals", "sectors", "scenarios"]],
        use_container_width=True,
        hide_index=True,
        column_config={
            "source_id": st.column_config.TextColumn("ID", width="small"),
            "source_title": st.column_config.TextColumn("Title", width="large"),
            "source_publisher": st.column_config.TextColumn("Publisher", width="medium"),
            "source_year": st.column_config.NumberColumn("Year", width="small", format="%d"),
            "data_quality": st.column_config.TextColumn("Quality", width="small"),
            "signals": st.column_config.NumberColumn("Signals", width="small"),
            "sectors": st.column_config.TextColumn("Sectors", width="medium"),
            "scenarios": st.column_config.TextColumn("Scenarios", width="small"),
        }
    )

    # Demand direction breakdown
    st.markdown('<div class="section-header">Demand Direction Breakdown</div>', unsafe_allow_html=True)
    dir_counts = sources_filtered["demand_direction"].value_counts().reset_index()
    dir_counts.columns = ["direction", "count"]
    dir_color = {
        "strong_increase": "#2ecc71",
        "moderate_increase": "#a8d8a8",
        "stable": "#95a5a6",
        "moderate_decrease": "#f39c12",
        "strong_decrease": "#e74c3c"
    }
    fig_dir = px.bar(
        dir_counts,
        x="direction",
        y="count",
        color="direction",
        color_discrete_map=dir_color,
        title="Skill Signals by Demand Direction",
        labels={"direction": "Direction", "count": "Number of Signals"}
    )
    fig_dir.update_layout(
        height=340,
        plot_bgcolor="white",
        paper_bgcolor="white",
        showlegend=False,
        font=dict(family="DM Sans"),
        title_font=dict(family="DM Serif Display", size=14)
    )
    st.plotly_chart(fig_dir, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════
# TAB 5 — DATA EXPLORER
# ════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown('<div class="section-header">Data Explorer</div>', unsafe_allow_html=True)

    dataset = st.radio(
        "Select dataset",
        ["Gap Analysis", "Skill Matrix", "Calibration Table", "Source Signals"],
        horizontal=True
    )

    dataset_map = {
        "Gap Analysis": gap_filtered,
        "Skill Matrix": matrix_filtered,
        "Calibration Table": calib_df,
        "Source Signals": sources_filtered
    }

    df_show = dataset_map[dataset]

    # Search
    search = st.text_input("🔍 Search", placeholder="e.g. digital, healthcare, fintech...")
    if search:
        mask = df_show.astype(str).apply(lambda col: col.str.contains(search, case=False, na=False)).any(axis=1)
        df_show = df_show[mask]

    st.caption(f"Showing {len(df_show):,} rows")
    st.dataframe(df_show, use_container_width=True, hide_index=True)

    # Download
    csv = df_show.to_csv(index=False).encode("utf-8")
    st.download_button(
        label=f"⬇ Download {dataset} CSV",
        data=csv,
        file_name=f"qatar_{dataset.lower().replace(' ', '_')}.csv",
        mime="text/csv"
    )

# ── Footer ────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:#999; font-size:0.8rem;'>"
    "Qatar 2030 Labor Market Intelligence · CMU Tepper MSBA Capstone · "
    "Powered by Claude API + 18 authoritative sources"
    "</div>",
    unsafe_allow_html=True
)
