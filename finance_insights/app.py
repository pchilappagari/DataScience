"""Personal Finance Insights Dashboard - Streamlit App."""

import os
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from data_loader import load_all_csvs, load_csv_from_bytes, clean_transactions
from sample_data import generate_sample_data
from analysis import (
    spending_by_category,
    monthly_trend,
    category_monthly_trend,
    top_merchants,
    monthly_summary,
    daily_spending,
    category_trend,
    income_vs_expenses,
    expenses_only,
)

# --- Page config ---
st.set_page_config(
    page_title="Finance Insights",
    page_icon="$",
    layout="wide",
)

# --- Load data ---
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


@st.cache_data
def load_from_folder():
    df, files = load_all_csvs(DATA_DIR)
    if df is not None:
        return df, files
    return None, []


def load_from_uploads(uploaded_files):
    dfs = []
    names = []
    for f in uploaded_files:
        try:
            df = load_csv_from_bytes(f)
            dfs.append(df)
            names.append(f.name)
        except Exception as e:
            st.sidebar.error(f"Could not load {f.name}: {e}")
    if dfs:
        combined = pd.concat(dfs, ignore_index=True)
        return clean_transactions(combined), names
    return None, []


# --- Sidebar ---
st.sidebar.title("Finance Insights")

# CSV upload widget
uploaded_files = st.sidebar.file_uploader(
    "Upload Simplifi CSVs",
    type=["csv"],
    accept_multiple_files=True,
    help="Export CSVs from Simplifi (web app → Transactions → download) and upload here.",
)

# Determine data source: uploads > folder > sample
if uploaded_files:
    df, loaded_files = load_from_uploads(uploaded_files)
    is_sample = False
    st.sidebar.success(f"Uploaded: {', '.join(loaded_files)}")
else:
    folder_df, folder_files = load_from_folder()
    if folder_df is not None:
        df, loaded_files, is_sample = folder_df, folder_files, False
        st.sidebar.success(f"Loaded from folder: {', '.join(loaded_files)}")
    else:
        df = generate_sample_data(months=12)
        df = clean_transactions(df)
        loaded_files, is_sample = [], True
        st.sidebar.warning("Using sample data. Upload CSVs above or drop them into `data/` folder.")

# Date range filter
min_date = df["Date"].min().date()
max_date = df["Date"].max().date()
date_range = st.sidebar.date_input(
    "Date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

# Account filter
accounts = sorted(df["Account"].unique())
selected_accounts = st.sidebar.multiselect("Accounts", accounts, default=accounts)

# Category filter
all_categories = sorted(df["Category"].unique())
expense_categories = [c for c in all_categories if c != "Income"]
selected_categories = st.sidebar.multiselect(
    "Categories", all_categories, default=all_categories
)

# Apply filters
filtered = df.copy()
if len(date_range) == 2:
    filtered = filtered[
        (filtered["Date"].dt.date >= date_range[0])
        & (filtered["Date"].dt.date <= date_range[1])
    ]
filtered = filtered[filtered["Account"].isin(selected_accounts)]
filtered = filtered[filtered["Category"].isin(selected_categories)]

# --- Navigation ---
page = st.sidebar.radio("Navigate", ["Overview", "Categories", "Merchants", "Daily Tracker"])

# --- Color palette ---
COLORS = px.colors.qualitative.Set2


# ===========================
# OVERVIEW PAGE
# ===========================
if page == "Overview":
    st.title("Spending Overview")

    summary = monthly_summary(filtered)
    exp = expenses_only(filtered)

    # KPI cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("This Month", f"${summary['current']:,.2f}")
    with col2:
        delta = f"{summary['change_pct']:+.1f}%"
        st.metric("vs Last Month", f"${summary['previous']:,.2f}", delta=delta, delta_color="inverse")
    with col3:
        cat_data = spending_by_category(filtered)
        top_cat = cat_data.iloc[0]["Category"] if not cat_data.empty else "N/A"
        top_cat_amt = cat_data.iloc[0]["Total"] if not cat_data.empty else 0
        st.metric("Top Category", top_cat, f"${top_cat_amt:,.2f}")
    with col4:
        st.metric("Transactions", f"{len(exp):,}")

    st.divider()

    # Charts row
    chart_col1, chart_col2 = st.columns([3, 2])

    with chart_col1:
        st.subheader("Monthly Spending Trend")
        trend = monthly_trend(filtered)
        if not trend.empty:
            fig = px.bar(
                trend,
                x="Month",
                y="Total",
                color_discrete_sequence=["#4CAF50"],
            )
            fig.update_layout(
                xaxis_title="",
                yaxis_title="Spending ($)",
                yaxis_tickprefix="$",
                showlegend=False,
                height=400,
            )
            st.plotly_chart(fig, use_container_width=True)

    with chart_col2:
        st.subheader("Spending by Category")
        cat_data = spending_by_category(filtered)
        if not cat_data.empty:
            fig = px.pie(
                cat_data,
                values="Total",
                names="Category",
                hole=0.4,
                color_discrete_sequence=COLORS,
            )
            fig.update_traces(textposition="inside", textinfo="percent+label")
            fig.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

    # Income vs Expenses
    st.subheader("Income vs Expenses")
    ive = income_vs_expenses(filtered)
    if not ive.empty:
        fig = go.Figure()
        fig.add_trace(go.Bar(x=ive["Month"], y=ive["Income"], name="Income", marker_color="#4CAF50"))
        fig.add_trace(go.Bar(x=ive["Month"], y=ive["Expenses"], name="Expenses", marker_color="#f44336"))
        fig.add_trace(go.Scatter(x=ive["Month"], y=ive["Net"], name="Net", line=dict(color="#2196F3", width=2)))
        fig.update_layout(
            barmode="group",
            xaxis_title="",
            yaxis_title="Amount ($)",
            yaxis_tickprefix="$",
            height=350,
        )
        st.plotly_chart(fig, use_container_width=True)


# ===========================
# CATEGORIES PAGE
# ===========================
elif page == "Categories":
    st.title("Category Breakdown")

    cat_data = spending_by_category(filtered)

    if not cat_data.empty:
        # Summary table
        cat_data["Pct"] = (cat_data["Total"] / cat_data["Total"].sum() * 100).round(1)
        cat_data["Total"] = cat_data["Total"].round(2)

        col1, col2 = st.columns([2, 3])

        with col1:
            st.subheader("By Category")
            display_df = cat_data.copy()
            display_df["Total"] = display_df["Total"].apply(lambda x: f"${x:,.2f}")
            display_df["Pct"] = display_df["Pct"].apply(lambda x: f"{x}%")
            st.dataframe(display_df, use_container_width=True, hide_index=True)

        with col2:
            st.subheader("Category Trends Over Time")
            cat_monthly = category_monthly_trend(filtered)
            if not cat_monthly.empty:
                selected_cat = st.selectbox(
                    "Select category", expense_categories
                )
                cat_trend = category_trend(filtered, selected_cat)
                if not cat_trend.empty:
                    fig = px.line(
                        cat_trend,
                        x="Month",
                        y="Total",
                        markers=True,
                        color_discrete_sequence=["#2196F3"],
                    )
                    fig.update_layout(
                        xaxis_title="",
                        yaxis_title=f"{selected_cat} Spending ($)",
                        yaxis_tickprefix="$",
                        height=400,
                    )
                    st.plotly_chart(fig, use_container_width=True)

        # Stacked area chart
        st.subheader("All Categories Over Time")
        cat_monthly = category_monthly_trend(filtered)
        # Exclude income for the area chart
        cat_monthly_exp = cat_monthly[cat_monthly["Category"] != "Income"]
        if not cat_monthly_exp.empty:
            fig = px.area(
                cat_monthly_exp,
                x="Month",
                y="Total",
                color="Category",
                color_discrete_sequence=COLORS,
            )
            fig.update_layout(
                xaxis_title="",
                yaxis_title="Spending ($)",
                yaxis_tickprefix="$",
                height=450,
            )
            st.plotly_chart(fig, use_container_width=True)


# ===========================
# MERCHANTS PAGE
# ===========================
elif page == "Merchants":
    st.title("Top Merchants")

    n = st.slider("Number of merchants", 5, 25, 10)
    merchants = top_merchants(filtered, n=n)

    if not merchants.empty:
        col1, col2 = st.columns([3, 2])

        with col1:
            fig = px.bar(
                merchants,
                x="Total",
                y="Payee",
                orientation="h",
                color="Total",
                color_continuous_scale="Greens",
            )
            fig.update_layout(
                yaxis=dict(autorange="reversed"),
                xaxis_title="Total Spent ($)",
                yaxis_title="",
                xaxis_tickprefix="$",
                showlegend=False,
                coloraxis_showscale=False,
                height=max(400, n * 35),
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("Details")
            display = merchants.copy()
            display["Total"] = display["Total"].apply(lambda x: f"${x:,.2f}")
            st.dataframe(display, use_container_width=True, hide_index=True)


# ===========================
# DAILY TRACKER PAGE
# ===========================
elif page == "Daily Tracker":
    st.title("Daily Spending Tracker")

    months_available = sorted(filtered["Month"].unique(), reverse=True)

    if months_available:
        selected_month = st.selectbox("Select month", months_available)
        daily = daily_spending(filtered, selected_month)

        if not daily.empty:
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Daily Spending")
                fig = px.bar(
                    daily,
                    x="Day",
                    y="Daily",
                    color_discrete_sequence=["#FF9800"],
                )
                fig.update_layout(
                    xaxis_title="Day of Month",
                    yaxis_title="Amount ($)",
                    yaxis_tickprefix="$",
                    height=400,
                )
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.subheader("Cumulative Spending")
                fig = px.area(
                    daily,
                    x="Day",
                    y="Cumulative",
                    color_discrete_sequence=["#f44336"],
                )
                fig.update_layout(
                    xaxis_title="Day of Month",
                    yaxis_title="Cumulative ($)",
                    yaxis_tickprefix="$",
                    height=400,
                )
                st.plotly_chart(fig, use_container_width=True)

            st.subheader(f"Total for {selected_month}: ${daily['Cumulative'].iloc[-1]:,.2f}")
    else:
        st.info("No data available for the selected filters.")


# --- Footer ---
st.sidebar.divider()
st.sidebar.caption("Drop Simplifi CSV exports into `finance_insights/data/` to use real data.")
