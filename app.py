import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Oreo Dashboard",
    page_icon="🍪",
    layout="wide"
)

st.title("🍪 Oreo Campaign Dashboard")
st.caption("The Great Oreo Takeover")

# Load Excel File
df = pd.read_excel("data/oreo_content_calendar.xlsx")

# Show Raw Data
st.subheader("📄 Campaign Data")
st.dataframe(df, use_container_width=True)

# Sidebar Filters
st.sidebar.title("Filters")

if "Platform" in df.columns:
    platform_options = df["Platform"].dropna().unique()
    selected_platform = st.sidebar.selectbox(
        "Select Platform",
        platform_options
    )

    filtered_df = df[df["Platform"] == selected_platform]

    st.subheader(f"📱 Content for {selected_platform}")
    st.dataframe(filtered_df, use_container_width=True)

# KPI Cards
st.subheader("📊 KPI Overview")

col1, col2, col3 = st.columns(3)

col1.metric("Total Posts", len(df))

if "Platform" in df.columns:
    col2.metric("Platforms", df["Platform"].nunique())

if "Status" in df.columns:
    completed = len(df[df["Status"] == "Published"])
    col3.metric("Published", completed)

# Charts
if "Platform" in df.columns:

    chart_data = (
        df["Platform"]
        .value_counts()
        .reset_index()
    )

    chart_data.columns = ["Platform", "Count"]

    st.subheader("📈 Platform Distribution")

    fig = px.bar(
        chart_data,
        x="Platform",
        y="Count",
        title="Posts by Platform"
    )

    st.plotly_chart(fig, use_container_width=True)

if "Status" in df.columns:

    status_data = (
        df["Status"]
        .value_counts()
        .reset_index()
    )

    status_data.columns = ["Status", "Count"]

    st.subheader("✅ Content Status")

    fig2 = px.pie(
        status_data,
        names="Status",
        values="Count",
        title="Campaign Status Overview"
    )

    st.plotly_chart(fig2, use_container_width=True)
