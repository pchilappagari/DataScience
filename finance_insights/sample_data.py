"""Generate realistic sample transaction data for demo purposes."""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def generate_sample_data(months=12):
    """Generate realistic fake transactions across common spending categories.

    Returns a DataFrame with columns matching Simplifi CSV export format:
    Date, Payee, Amount, Category, Account, Tags, Memo
    """
    np.random.seed(42)
    end_date = datetime.now().replace(day=1) - timedelta(days=1)
    start_date = end_date - timedelta(days=months * 30)

    # Category definitions: (category, [(payee, avg_amount, std)], frequency_per_month)
    categories = {
        "Groceries": {
            "payees": [
                ("Walmart", 85, 30),
                ("Kroger", 65, 20),
                ("Whole Foods", 95, 35),
                ("Trader Joe's", 55, 15),
                ("Costco", 150, 50),
            ],
            "frequency": 8,
        },
        "Dining Out": {
            "payees": [
                ("Chipotle", 14, 4),
                ("Starbucks", 7, 3),
                ("Olive Garden", 45, 15),
                ("McDonald's", 12, 5),
                ("DoorDash", 35, 12),
                ("Uber Eats", 30, 10),
            ],
            "frequency": 10,
        },
        "Gas & Fuel": {
            "payees": [
                ("Shell", 55, 15),
                ("Chevron", 50, 12),
                ("ExxonMobil", 52, 14),
            ],
            "frequency": 4,
        },
        "Utilities": {
            "payees": [
                ("Electric Company", 120, 40),
                ("Water Utility", 45, 10),
                ("Internet - Xfinity", 80, 5),
                ("Gas Company", 60, 25),
            ],
            "frequency": 4,
        },
        "Rent/Mortgage": {
            "payees": [("Rent Payment", 1800, 0)],
            "frequency": 1,
        },
        "Shopping": {
            "payees": [
                ("Amazon", 45, 30),
                ("Target", 55, 25),
                ("Best Buy", 120, 80),
                ("Nike", 85, 40),
                ("TJ Maxx", 40, 20),
            ],
            "frequency": 5,
        },
        "Entertainment": {
            "payees": [
                ("Netflix", 15.49, 0),
                ("Spotify", 10.99, 0),
                ("AMC Theatres", 25, 10),
                ("Steam", 30, 20),
                ("Disney+", 13.99, 0),
            ],
            "frequency": 3,
        },
        "Healthcare": {
            "payees": [
                ("CVS Pharmacy", 25, 15),
                ("Dr. Smith Office", 50, 20),
                ("Urgent Care", 150, 50),
            ],
            "frequency": 1.5,
        },
        "Insurance": {
            "payees": [
                ("Auto Insurance", 140, 10),
                ("Health Insurance", 350, 0),
            ],
            "frequency": 2,
        },
        "Subscriptions": {
            "payees": [
                ("iCloud Storage", 2.99, 0),
                ("YouTube Premium", 13.99, 0),
                ("Gym Membership", 49.99, 0),
                ("Adobe Creative", 54.99, 0),
            ],
            "frequency": 2,
        },
        "Transportation": {
            "payees": [
                ("Uber", 22, 10),
                ("Lyft", 18, 8),
                ("Parking", 10, 5),
            ],
            "frequency": 3,
        },
    }

    accounts = [
        "Chase Sapphire",
        "Amex Gold",
        "Checking Account",
        "Discover It",
    ]

    transactions = []

    current = start_date
    while current <= end_date:
        month_start = current.replace(day=1)
        if current.month == 12:
            month_end = current.replace(year=current.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            month_end = current.replace(month=current.month + 1, day=1) - timedelta(days=1)

        for category, info in categories.items():
            n_transactions = max(1, int(np.random.poisson(info["frequency"])))
            for _ in range(n_transactions):
                payee_name, avg_amt, std_amt = info["payees"][
                    np.random.randint(len(info["payees"]))
                ]
                amount = round(max(1.0, np.random.normal(avg_amt, std_amt)), 2)
                day = np.random.randint(1, month_end.day + 1)
                date = month_start.replace(day=day)
                account = np.random.choice(accounts)

                transactions.append(
                    {
                        "Date": date,
                        "Payee": payee_name,
                        "Amount": -amount,  # Expenses are negative in Simplifi
                        "Category": category,
                        "Account": account,
                        "Tags": "",
                        "Memo": "",
                    }
                )

        # Add some income
        payroll_date = month_start.replace(day=min(15, month_end.day))
        transactions.append(
            {
                "Date": payroll_date,
                "Payee": "Employer Direct Deposit",
                "Amount": 5500.00,
                "Category": "Income",
                "Account": "Checking Account",
                "Tags": "",
                "Memo": "Bi-weekly payroll",
            }
        )
        payroll_date2 = month_start.replace(day=min(30, month_end.day))
        transactions.append(
            {
                "Date": payroll_date2,
                "Payee": "Employer Direct Deposit",
                "Amount": 5500.00,
                "Category": "Income",
                "Account": "Checking Account",
                "Tags": "",
                "Memo": "Bi-weekly payroll",
            }
        )

        # Move to next month
        if current.month == 12:
            current = current.replace(year=current.year + 1, month=1, day=1)
        else:
            current = current.replace(month=current.month + 1, day=1)

    df = pd.DataFrame(transactions)
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date").reset_index(drop=True)
    return df
