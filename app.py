import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="The Great Oreo Takeover · Dashboard",
    page_icon="🍪",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .main { background-color: #0d0d0d; }
    .block-container { padding: 1.5rem 2rem; }

    /* Header banner */
    .oreo-header {
        background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
        border: 1px solid #333;
        border-radius: 16px;
        padding: 28px 36px;
        margin-bottom: 24px;
        display: flex;
        align-items: center;
        gap: 20px;
    }
    .oreo-header h1 { color: #fff; font-size: 2rem; font-weight: 800; margin: 0; }
    .oreo-header p  { color: #aaa; margin: 4px 0 0; font-size: 0.9rem; }
    .oreo-badge {
        background: #fff; color: #000;
        border-radius: 8px; padding: 6px 14px;
        font-weight: 700; font-size: 0.8rem; white-space: nowrap;
    }

    /* Metric cards */
    .metric-card {
        background: #1a1a1a;
        border: 1px solid #2a2a2a;
        border-radius: 14px;
        padding: 22px 20px;
        text-align: center;
        height: 120px;
        display: flex; flex-direction: column;
        justify-content: center;
    }
    .metric-value { font-size: 1.7rem; font-weight: 800; color: #fff; }
    .metric-label { font-size: 0.75rem; color: #888; margin-top: 4px; text-transform: uppercase; letter-spacing: 0.05em; }
    .metric-sub   { font-size: 0.7rem; color: #555; margin-top: 2px; }

    /* Section headers */
    .section-title {
        font-size: 1rem; font-weight: 700;
        color: #fff; margin-bottom: 12px;
        padding-bottom: 8px; border-bottom: 1px solid #222;
    }

    /* Status pills */
    .pill-planned  { background:#1a3a1a; color:#4CAF50; border-radius:99px; padding:3px 10px; font-size:0.72rem; font-weight:600; }
    .pill-live     { background:#3a1a00; color:#FF9800; border-radius:99px; padding:3px 10px; font-size:0.72rem; font-weight:600; }
    .pill-done     { background:#1a1a3a; color:#9B59B6; border-radius:99px; padding:3px 10px; font-size:0.72rem; font-weight:600; }
    .pill-analysis { background:#3a2800; color:#FFC107; border-radius:99px; padding:3px 10px; font-size:0.72rem; font-weight:600; }

    /* Sidebar */
    [data-testid="stSidebar"] { background: #111 !important; }
    [data-testid="stSidebar"] * { color: #ccc !important; }
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stMultiSelect label { color: #aaa !important; }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] { background: #1a1a1a; border-radius: 10px; }
    .stTabs [data-baseweb="tab"] { color: #888; }
    .stTabs [aria-selected="true"] { color: #fff !important; background: #2a2a2a !important; }

    /* Plotly charts transparent bg */
    .js-plotly-plot { background: transparent !important; }
</style>
""", unsafe_allow_html=True)


# ── Data ──────────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    # ---- Content Calendar ----
    raw = pd.read_excel("data/oreo_content_calendar.xlsx",
                        sheet_name="Content Calendar", header=None)
    header_row = 2
    df = raw.iloc[header_row + 1:].copy()
    df.columns = ["Phase", "Week", "Day", "Day_of_Week", "Platform",
                  "Format", "Content_Description", "Message_Hook",
                  "Hashtag_CTA", "Budget_Note", "KPI_Focus", "Status"]
    df = df.reset_index(drop=True)

    # Forward-fill Phase & Week
    df["Phase"] = df["Phase"].replace(r'^\s*$', pd.NA, regex=True).ffill()
    df["Week"]  = df["Week"].replace(r'^\s*$', pd.NA, regex=True).ffill()

    # Clean Phase / Week labels
    df["Phase"] = df["Phase"].astype(str).str.replace(r'\n', ' ', regex=True).str.strip()
    df["Week"]  = df["Week"].astype(str).str.replace(r'\n', ' ', regex=True).str.strip()

    df["Day"]          = pd.to_numeric(df["Day"], errors="coerce")
    df["Status"]       = df["Status"].fillna("Planned").astype(str).str.strip()
    df["Platform"]     = df["Platform"].fillna("—").astype(str).str.strip()
    df["Format"]       = df["Format"].fillna("—").astype(str).str.strip()
    df["Budget_Note"]  = df["Budget_Note"].fillna("Organic").astype(str).str.strip()
    df["KPI_Focus"]    = df["KPI_Focus"].fillna("—").astype(str).str.strip()
    df["Content_Description"] = df["Content_Description"].fillna("").astype(str).str.strip()

    # Drop fully empty rows
    df = df[df["Day"].notna()].copy()

    # Paid vs Organic flag
    df["Budget_Type"] = df["Budget_Note"].apply(
        lambda x: "Paid" if "Paid" in x or "Retarget" in x or "Boost" in x or "Creator" in x
        else "Organic"
    )

    # ---- Budget ----
    braw = pd.read_excel("data/oreo_content_calendar.xlsx",
                         sheet_name="Budget Breakdown", header=None)
    platform_rows = braw.iloc[9:13, [0, 2, 3]].copy()
    platform_rows.columns = ["Platform", "HUF", "Share"]
    platform_rows["Platform"] = platform_rows["Platform"].astype(str).str.strip()
    platform_rows["HUF"]      = pd.to_numeric(platform_rows["HUF"], errors="coerce")
    platform_rows["Share"]    = platform_rows["Share"].astype(str).str.replace("%","").str.strip()
    platform_rows["Share"]    = pd.to_numeric(platform_rows["Share"], errors="coerce")
    platform_rows = platform_rows.dropna(subset=["HUF"])

    # ---- KPI Tracker ----
    kraw = pd.read_excel("data/oreo_content_calendar.xlsx",
                         sheet_name="KPI Tracker", header=None)
    kdf = kraw.iloc[2:].copy()
    kdf.columns = ["KPI", "Target", "Week1", "Week2", "Week3", "Week4", "Week5"]
    kdf = kdf[~kdf["KPI"].isin(["KPI", "PRIMARY KPIs", "SECONDARY KPIs", None])].copy()
    kdf = kdf[kdf["KPI"].notna() & (kdf["KPI"].astype(str).str.strip() != "")]
    kdf = kdf.reset_index(drop=True)

    return df, platform_rows, kdf

df, budget_df, kpi_df = load_data()

# ── Sidebar filters ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🍪 Filters")
    st.markdown("---")

    all_phases = sorted(df["Phase"].dropna().unique().tolist())
    sel_phases = st.multiselect("Phase", all_phases, default=all_phases,
                                key="phase_filter")

    all_platforms = sorted(df["Platform"].dropna().unique().tolist())
    sel_platforms = st.multiselect("Platform", all_platforms, default=all_platforms,
                                   key="platform_filter")

    all_statuses = sorted(df["Status"].dropna().unique().tolist())
    sel_statuses = st.multiselect("Status", all_statuses, default=all_statuses,
                                  key="status_filter")

    budget_types = st.multiselect("Budget Type", ["Organic", "Paid"],
                                  default=["Organic", "Paid"], key="budget_filter")

    st.markdown("---")
    st.markdown("**Campaign Info**")
    st.markdown("🎯 Market: **Hungary**")
    st.markdown("💰 Budget: **20M HUF**")
    st.markdown("👥 Target: **14–34 yr olds**")
    st.markdown("📅 Duration: **5 Weeks**")

# Apply filters
mask = (
    df["Phase"].isin(sel_phases) &
    df["Platform"].isin(sel_platforms) &
    df["Status"].isin(sel_statuses) &
    df["Budget_Type"].isin(budget_types)
)
fdf = df[mask].copy()

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="oreo-header">
    <span style="font-size:2.8rem">🍪</span>
    <div style="flex:1">
        <h1>The Great Oreo Takeover</h1>
        <p>Content Tracking Dashboard · Hungary · Brand Awareness Campaign</p>
    </div>
    <div class="oreo-badge">🇭🇺 HU · 5 Weeks</div>
</div>
""", unsafe_allow_html=True)

# ── KPI Summary Cards ─────────────────────────────────────────────────────────
c1, c2, c3, c4, c5, c6 = st.columns(6)

total_posts   = len(fdf)
planned       = len(fdf[fdf["Status"] == "Planned"])
paid_posts    = len(fdf[fdf["Budget_Type"] == "Paid"])
organic_posts = len(fdf[fdf["Budget_Type"] == "Organic"])
platforms_n   = fdf["Platform"].nunique()
phases_n      = fdf["Phase"].nunique()

for col, val, label, sub in [
    (c1, total_posts,   "Total Posts",     f"filtered"),
    (c2, planned,       "Planned",          f"of {total_posts}"),
    (c3, paid_posts,    "Paid Activations", "boosted/creator"),
    (c4, organic_posts, "Organic Posts",    "no ad spend"),
    (c5, platforms_n,   "Platforms",        "active channels"),
    (c6, phases_n,      "Phases",           "campaign stages"),
]:
    col.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{val}</div>
        <div class="metric-label">{label}</div>
        <div class="metric-sub">{sub}</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📅 Content Calendar",
    "📊 Platform Analysis",
    "💰 Budget",
    "🎯 KPI Tracker",
    "🗂 Raw Data",
])

COLORS = {
    "TikTok":           "#69C9D0",
    "Instagram":        "#E1306C",
    "Facebook":         "#1877F2",
    "YouTube":          "#FF0000",
    "UGC/Creator":      "#F4A261",
    "Boost":            "#A8DADC",
    "—":                "#555",
    "nan":              "#555",
}
PHASE_COLORS = {
    "Phase 1 Teaser & Launch": "#4CAF50",
    "Phase 2 Scale & Amplify": "#2196F3",
    "Phase 3 Recap & Sustain": "#9C27B0",
}


# ── Tab 1 · Content Calendar ──────────────────────────────────────────────────
with tab1:
    st.markdown('<div class="section-title">📅 Content Timeline by Day</div>',
                unsafe_allow_html=True)

    if fdf.empty:
        st.info("No posts match current filters.")
    else:
        # Timeline scatter
        fig = px.scatter(
            fdf, x="Day", y="Platform", color="Phase",
            symbol="Budget_Type",
            hover_data={"Content_Description": True, "Format": True,
                        "KPI_Focus": True, "Budget_Note": True,
                        "Status": True},
            color_discrete_sequence=["#4CAF50", "#2196F3", "#9C27B0"],
            size_max=14,
        )
        fig.update_traces(marker=dict(size=14, line=dict(width=1, color="#333")))
        fig.update_layout(
            plot_bgcolor="#111", paper_bgcolor="#111",
            font_color="#ccc",
            xaxis=dict(title="Campaign Day", gridcolor="#222",
                       tickmode="linear", tick0=1, dtick=1),
            yaxis=dict(title="", gridcolor="#222"),
            legend=dict(bgcolor="#1a1a1a", bordercolor="#333",
                        font=dict(color="#ccc")),
            height=420,
            margin=dict(l=10, r=10, t=10, b=10),
        )
        st.plotly_chart(fig, use_container_width=True)

        # Posts per day bar
        st.markdown('<div class="section-title">📆 Posts Per Day</div>',
                    unsafe_allow_html=True)
        day_counts = fdf.groupby(["Day", "Platform"]).size().reset_index(name="Count")
        fig2 = px.bar(
            day_counts, x="Day", y="Count", color="Platform",
            color_discrete_map=COLORS, barmode="stack",
        )
        fig2.update_layout(
            plot_bgcolor="#111", paper_bgcolor="#111", font_color="#ccc",
            xaxis=dict(title="Day", gridcolor="#222",
                       tickmode="linear", tick0=1, dtick=1),
            yaxis=dict(title="# Posts", gridcolor="#222"),
            legend=dict(bgcolor="#1a1a1a", bordercolor="#333"),
            height=320, margin=dict(l=10, r=10, t=10, b=10),
        )
        st.plotly_chart(fig2, use_container_width=True)

        # Phase breakdown table
        st.markdown('<div class="section-title">📋 Posts by Phase & Week</div>',
                    unsafe_allow_html=True)
        phase_week = fdf.groupby(["Phase", "Week"]).size().reset_index(name="Posts")
        st.dataframe(
            phase_week,
            use_container_width=True,
            hide_index=True,
        )


# ── Tab 2 · Platform Analysis ─────────────────────────────────────────────────
with tab2:
    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown('<div class="section-title">Platform Distribution</div>',
                    unsafe_allow_html=True)
        plat_counts = fdf["Platform"].value_counts().reset_index()
        plat_counts.columns = ["Platform", "Count"]
        fig3 = px.pie(
            plat_counts, names="Platform", values="Count",
            color="Platform", color_discrete_map=COLORS, hole=0.45,
        )
        fig3.update_traces(textfont_color="#fff", textinfo="label+percent")
        fig3.update_layout(
            plot_bgcolor="#111", paper_bgcolor="#111", font_color="#ccc",
            showlegend=False, height=360,
            margin=dict(l=10, r=10, t=10, b=10),
        )
        st.plotly_chart(fig3, use_container_width=True)

    with col_r:
        st.markdown('<div class="section-title">Format Breakdown</div>',
                    unsafe_allow_html=True)
        fmt_counts = fdf["Format"].value_counts().reset_index()
        fmt_counts.columns = ["Format", "Count"]
        fig4 = px.bar(
            fmt_counts, x="Count", y="Format", orientation="h",
            color="Count", color_continuous_scale=["#1a1a1a", "#E1306C"],
        )
        fig4.update_layout(
            plot_bgcolor="#111", paper_bgcolor="#111", font_color="#ccc",
            xaxis=dict(title="# Posts", gridcolor="#222"),
            yaxis=dict(title="", gridcolor="#222"),
            coloraxis_showscale=False, height=360,
            margin=dict(l=10, r=10, t=10, b=10),
        )
        st.plotly_chart(fig4, use_container_width=True)

    # Platform × Phase heatmap
    st.markdown('<div class="section-title">Platform × Phase Heatmap</div>',
                unsafe_allow_html=True)
    heat_data = fdf.groupby(["Platform", "Phase"]).size().reset_index(name="Count")
    heat_pivot = heat_data.pivot(index="Platform", columns="Phase", values="Count").fillna(0)
    fig5 = px.imshow(
        heat_pivot, color_continuous_scale=["#111", "#E1306C"],
        aspect="auto", text_auto=True,
    )
    fig5.update_layout(
        plot_bgcolor="#111", paper_bgcolor="#111", font_color="#ccc",
        height=320, margin=dict(l=10, r=10, t=10, b=10),
    )
    st.plotly_chart(fig5, use_container_width=True)

    # KPI Focus word-style bar
    st.markdown('<div class="section-title">Top KPI Focuses (by post count)</div>',
                unsafe_allow_html=True)
    kpi_counts = fdf["KPI_Focus"].value_counts().head(12).reset_index()
    kpi_counts.columns = ["KPI", "Count"]
    fig6 = px.bar(
        kpi_counts, x="Count", y="KPI", orientation="h",
        color_discrete_sequence=["#69C9D0"],
    )
    fig6.update_layout(
        plot_bgcolor="#111", paper_bgcolor="#111", font_color="#ccc",
        xaxis=dict(gridcolor="#222"), yaxis=dict(title=""),
        height=360, margin=dict(l=10, r=10, t=10, b=10),
    )
    st.plotly_chart(fig6, use_container_width=True)


# ── Tab 3 · Budget ────────────────────────────────────────────────────────────
with tab3:
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown('<div class="section-title">💰 Platform Budget Allocation</div>',
                    unsafe_allow_html=True)
        fig7 = px.pie(
            budget_df, names="Platform", values="HUF",
            color="Platform",
            color_discrete_map={
                "TikTok":                        "#69C9D0",
                "Instagram":                     "#E1306C",
                "Facebook + YouTube":            "#1877F2",
                "Boosting / Creator Amplification": "#F4A261",
            },
            hole=0.4,
        )
        fig7.update_traces(
            texttemplate="%{label}<br>%{value:,.0f} HUF<br>(%{percent})",
            textfont_color="#fff",
        )
        fig7.update_layout(
            plot_bgcolor="#111", paper_bgcolor="#111", font_color="#ccc",
            showlegend=False, height=380,
            margin=dict(l=10, r=10, t=10, b=10),
        )
        st.plotly_chart(fig7, use_container_width=True)

    with col_b:
        st.markdown('<div class="section-title">HUF Allocation Table</div>',
                    unsafe_allow_html=True)
        display_budget = budget_df.copy()
        display_budget["HUF"] = display_budget["HUF"].apply(lambda x: f"{x:,.0f}")
        display_budget["Share"] = display_budget["Share"].apply(lambda x: f"{x:.0f}%")
        st.dataframe(display_budget, use_container_width=True, hide_index=True)

        # Funnel split
        st.markdown('<div class="section-title" style="margin-top:20px">Funnel Split</div>',
                    unsafe_allow_html=True)
        funnel_data = pd.DataFrame({
            "Type":  ["Prospecting", "Retargeting"],
            "HUF":   [18_000_000, 2_000_000],
            "Share": [90, 10],
        })
        fig8 = px.bar(
            funnel_data, x="Type", y="HUF",
            color="Type",
            color_discrete_sequence=["#4CAF50", "#E1306C"],
            text="Share",
        )
        fig8.update_traces(texttemplate="%{text}%", textposition="outside",
                           textfont_color="#fff")
        fig8.update_layout(
            plot_bgcolor="#111", paper_bgcolor="#111", font_color="#ccc",
            showlegend=False, xaxis=dict(title=""),
            yaxis=dict(title="HUF", gridcolor="#222"),
            height=280, margin=dict(l=10, r=10, t=30, b=10),
        )
        st.plotly_chart(fig8, use_container_width=True)

    # Organic vs Paid posts mix
    st.markdown('<div class="section-title">📦 Organic vs Paid Post Mix</div>',
                unsafe_allow_html=True)
    budget_mix = fdf.groupby(["Week", "Budget_Type"]).size().reset_index(name="Posts")
    fig9 = px.bar(
        budget_mix, x="Week", y="Posts", color="Budget_Type", barmode="group",
        color_discrete_map={"Organic": "#4CAF50", "Paid": "#E1306C"},
    )
    fig9.update_layout(
        plot_bgcolor="#111", paper_bgcolor="#111", font_color="#ccc",
        xaxis=dict(title=""), yaxis=dict(gridcolor="#222"),
        legend=dict(bgcolor="#1a1a1a", bordercolor="#333"),
        height=320, margin=dict(l=10, r=10, t=10, b=10),
    )
    st.plotly_chart(fig9, use_container_width=True)


# ── Tab 4 · KPI Tracker ───────────────────────────────────────────────────────
with tab4:
    st.markdown('<div class="section-title">🎯 KPI Targets & Weekly Actuals</div>',
                unsafe_allow_html=True)

    st.info("💡 Enter your weekly actuals below. Targets are locked from the campaign plan.")

    kpi_display = kpi_df.copy()
    kpi_display.columns = ["KPI", "Target", "Week 1", "Week 2", "Week 3", "Week 4", "Week 5"]

    # Editable KPI table
    edited = st.data_editor(
        kpi_display,
        use_container_width=True,
        hide_index=True,
        disabled=["KPI", "Target"],
        num_rows="fixed",
        key="kpi_editor",
    )

    st.markdown('<div class="section-title" style="margin-top:24px">Primary KPI Targets</div>',
                unsafe_allow_html=True)

    primary_kpis = [
        ("📣 Reach", "3.5M – 4.5M", "#4CAF50"),
        ("👁 Impressions", "14M – 20M", "#2196F3"),
        ("🔄 Frequency", "4 – 5×", "#FF9800"),
        ("🎬 Video Views", "5M – 7M", "#E91E63"),
        ("⏱ VTR", "20% – 30%", "#9C27B0"),
        ("💬 Engagement Rate", "3% – 5%", "#F4A261"),
        ("📌 Ad Recall Lift", "Via platform survey", "#69C9D0"),
    ]

    cols = st.columns(len(primary_kpis))
    for col, (label, target, color) in zip(cols, primary_kpis):
        col.markdown(f"""
        <div class="metric-card" style="border-color:{color}33; height:110px;">
            <div style="font-size:1.1rem; font-weight:700; color:{color}">{label}</div>
            <div style="font-size:0.8rem; color:#aaa; margin-top:6px">{target}</div>
        </div>""", unsafe_allow_html=True)


# ── Tab 5 · Raw Data ──────────────────────────────────────────────────────────
with tab5:
    st.markdown('<div class="section-title">🗂 Full Content Calendar Data</div>',
                unsafe_allow_html=True)

    search = st.text_input("🔍 Search content descriptions", placeholder="e.g. TikTok, creator, ASMR…")
    display_cols = ["Phase", "Week", "Day", "Day_of_Week", "Platform",
                    "Format", "Content_Description", "Message_Hook",
                    "Hashtag_CTA", "Budget_Note", "KPI_Focus", "Status", "Budget_Type"]

    show_df = fdf[display_cols].copy()
    if search:
        mask_search = show_df.apply(
            lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1
        )
        show_df = show_df[mask_search]

    st.markdown(f"**{len(show_df)} posts** matching filters")
    st.dataframe(show_df, use_container_width=True, hide_index=True, height=500)

    csv = show_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Download filtered data as CSV",
        data=csv, file_name="oreo_content_filtered.csv", mime="text/csv",
    )
