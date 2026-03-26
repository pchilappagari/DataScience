"""Spending analysis functions."""

import pandas as pd


def expenses_only(df):
    """Filter to only expense transactions (negative amounts in Simplifi)."""
    return df[df["Amount"] < 0].copy()


def spending_by_category(df):
    """Total spending per category (as positive values)."""
    exp = expenses_only(df)
    result = (
        exp.groupby("Category")["Amount"]
        .sum()
        .abs()
        .sort_values(ascending=False)
        .reset_index()
    )
    result.columns = ["Category", "Total"]
    return result


def monthly_trend(df):
    """Total spending per month over time."""
    exp = expenses_only(df)
    result = (
        exp.groupby("Month")["Amount"]
        .sum()
        .abs()
        .reset_index()
    )
    result.columns = ["Month", "Total"]
    result = result.sort_values("Month")
    return result


def category_monthly_trend(df):
    """Spending per category per month."""
    exp = expenses_only(df)
    result = (
        exp.groupby(["Month", "Category"])["Amount"]
        .sum()
        .abs()
        .reset_index()
    )
    result.columns = ["Month", "Category", "Total"]
    result = result.sort_values("Month")
    return result


def top_merchants(df, n=10):
    """Top N merchants by total spend."""
    exp = expenses_only(df)
    result = (
        exp.groupby("Payee")
        .agg(Total=("Amount", lambda x: abs(x.sum())), Transactions=("Amount", "count"))
        .sort_values("Total", ascending=False)
        .head(n)
        .reset_index()
    )
    return result


def monthly_summary(df):
    """Current month vs previous month comparison."""
    exp = expenses_only(df)
    months = sorted(exp["Month"].unique())

    if len(months) < 1:
        return {"current": 0, "previous": 0, "change_pct": 0, "current_month": "N/A"}

    current_month = months[-1]
    current_total = abs(exp[exp["Month"] == current_month]["Amount"].sum())

    if len(months) >= 2:
        prev_month = months[-2]
        prev_total = abs(exp[exp["Month"] == prev_month]["Amount"].sum())
        change_pct = ((current_total - prev_total) / prev_total * 100) if prev_total > 0 else 0
    else:
        prev_total = 0
        change_pct = 0

    return {
        "current": round(current_total, 2),
        "previous": round(prev_total, 2),
        "change_pct": round(change_pct, 1),
        "current_month": current_month,
    }


def daily_spending(df, month):
    """Daily cumulative spending for a given month."""
    exp = expenses_only(df)
    month_data = exp[exp["Month"] == month].copy()

    if month_data.empty:
        return pd.DataFrame(columns=["Day", "Daily", "Cumulative"])

    daily = (
        month_data.groupby("Day")["Amount"]
        .sum()
        .abs()
        .reset_index()
    )
    daily.columns = ["Day", "Daily"]
    daily = daily.sort_values("Day")
    daily["Cumulative"] = daily["Daily"].cumsum()
    return daily


def category_trend(df, category):
    """Single category spending over time by month."""
    exp = expenses_only(df)
    cat_data = exp[exp["Category"] == category]
    result = (
        cat_data.groupby("Month")["Amount"]
        .sum()
        .abs()
        .reset_index()
    )
    result.columns = ["Month", "Total"]
    result = result.sort_values("Month")
    return result


def income_vs_expenses(df):
    """Monthly income vs expenses."""
    income = df[df["Amount"] > 0].groupby("Month")["Amount"].sum().reset_index()
    income.columns = ["Month", "Income"]

    expenses = df[df["Amount"] < 0].groupby("Month")["Amount"].sum().abs().reset_index()
    expenses.columns = ["Month", "Expenses"]

    result = pd.merge(income, expenses, on="Month", how="outer").fillna(0)
    result["Net"] = result["Income"] - result["Expenses"]
    result = result.sort_values("Month")
    return result
