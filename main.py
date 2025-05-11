import pandas as pd
import numpy as np

# -----------------------------
# 1. Load the datasets
# -----------------------------
# Transactions data from your synthetic transactions file.
transactions_df = pd.read_csv("transactions_2yrs_min150.csv", parse_dates=["Date_Time"])
# Inventory orders data
inventory_df = pd.read_csv("inventory_stock_2yrs.csv", parse_dates=["Order_Date"])
# Labor/rota data
rota_df = pd.read_csv("rota_schedule_2yrs_12employees_randomHours.csv")

# -----------------------------
# 2. Prepare the data – Extract Date from time stamps
# -----------------------------
# For transactions: filter to "Completed" transactions and extract the date part.
completed_transactions = transactions_df[transactions_df["Status"] == "Completed"].copy()
completed_transactions["Date"] = completed_transactions["Date_Time"].dt.date

# For inventory: Convert Order_Date to date (you can do the same for Delivery_Date if needed)
inventory_df["Date"] = pd.to_datetime(inventory_df["Order_Date"]).dt.date

# For labor: Convert Shift_Date to date and compute Labor_Cost if not already computed.
rota_df["Date"] = pd.to_datetime(rota_df["Shift_Date"]).dt.date
# Ensure Labor_Cost exists (if using previous scripts, you may have already computed it).
if "Labor_Cost" not in rota_df.columns:
    rota_df["Labor_Cost"] = rota_df["Total_Hours"] * rota_df["Hourly_Pay"]

# -----------------------------
# 3. Aggregate Metrics by Day and Restaurant
# -----------------------------

# Revenue aggregation:
daily_revenue = (
    completed_transactions
    .groupby(["Restaurant_Name", "Date"])["Amount"]
    .sum()
    .reset_index(name="Daily_Revenue")
)

# Inventory cost aggregation:
daily_inventory_cost = (
    inventory_df
    .groupby(["Restaurant_Name", "Date"])["Total_Cost"]
    .sum()
    .reset_index(name="Daily_Inventory_Cost")
)

# Labor cost aggregation:
daily_labor_cost = (
    rota_df
    .groupby(["Restaurant_Name", "Date"])["Labor_Cost"]
    .sum()
    .reset_index(name="Daily_Labor_Cost")
)

# -----------------------------
# 4. Merge the Aggregated Data and Calculate Profit
# -----------------------------
# Outer merge so that if one dataset is missing for a day, we still capture the others.
daily_summary = (
    daily_revenue
    .merge(daily_inventory_cost, on=["Restaurant_Name", "Date"], how="outer")
    .merge(daily_labor_cost, on=["Restaurant_Name", "Date"], how="outer")
)

# Fill any missing values with 0 (e.g., if there were no inventory orders on a day).
daily_summary.fillna(0, inplace=True)

# Calculate Profit for each day per restaurant.
daily_summary["Profit"] = daily_summary["Daily_Revenue"] - (daily_summary["Daily_Inventory_Cost"] + daily_summary["Daily_Labor_Cost"])

# -----------------------------
# 5. (Optional) Aggregate by Week or Month
# -----------------------------
# If you prefer weekly data, you can convert the Date column to datetime first and group using pd.Grouper:
daily_summary["Date"] = pd.to_datetime(daily_summary["Date"])
weekly_summary = (
    daily_summary
    .set_index("Date")
    .groupby(["Restaurant_Name", pd.Grouper(freq="W")])
    .sum()
    .reset_index()
)
# Similarly, for monthly data, use freq="M" instead of "W".

# -----------------------------
# 6. Display Results
# -----------------------------
print("=== Daily Summary (First 10 rows) ===")
print(daily_summary.head(10))

print("\n=== Weekly Summary (First 10 rows) ===")
print(weekly_summary.head(10))

# Save the aggregated daily summary to a CSV file
daily_summary.to_csv("daily_summary.csv", index=False)

print("Daily summary data saved as 'daily_summary.csv'.")
