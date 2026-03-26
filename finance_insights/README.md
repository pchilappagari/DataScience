# Personal Finance Insights Dashboard

A Streamlit dashboard for analyzing your spending from Simplifi by Quicken.

## Features

- **Spending Overview** - Monthly totals, category breakdown (pie chart), income vs expenses
- **Category Analysis** - Drill into each category with trend lines over time
- **Top Merchants** - See where you spend the most
- **Daily Tracker** - Cumulative daily spending for any month

## Quick Start

```bash
cd finance_insights
pip install -r requirements.txt
streamlit run app.py
```

The dashboard launches with sample data by default.

## Using Your Real Data

1. Log into [Simplifi](https://app.simplifi.quicken.com)
2. Go to **Transactions**
3. Select an account (or all)
4. Click the **download** icon and choose **CSV**
5. Save the CSV file(s) into the `finance_insights/data/` folder
6. Restart the dashboard — it auto-detects your files

You can export multiple accounts as separate CSVs. The dashboard merges them automatically.

## Expected CSV Format

The dashboard expects columns like those from Simplifi exports:

| Column   | Required | Description               |
|----------|----------|---------------------------|
| Date     | Yes      | Transaction date          |
| Amount   | Yes      | Negative = expense        |
| Payee    | No       | Merchant/description      |
| Category | No       | Spending category         |
| Account  | No       | Account name              |
| Tags     | No       | Tags from Simplifi        |
| Memo     | No       | Notes                     |

Column names are matched flexibly (e.g., "Description" maps to "Payee").
