import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Define the restaurants
restaurants = ["Savory Bites", "Urban Feast", "Gourmet Haven"]

# Define the two-year period (January 1, 2023 to December 31, 2024)
start_date = datetime(2023, 1, 1)
end_date = datetime(2024, 12, 31)
n_days = (end_date - start_date).days + 1  # Total number of days in the period

data = []
transaction_counter = 1  # To ensure unique transaction IDs

# For each day in the period
for day in range(n_days):
    current_day = start_date + timedelta(days=day)
    # For each restaurant
    for restaurant in restaurants:
        # Ensure minimum of 150 transactions per day for each restaurant.
        # You can make it exactly 150, or add extra variation if desired.
        for i in range(150):
            # Generate a random time within the day (0 to 86399 seconds)
            random_seconds = np.random.randint(0, 86400)
            trans_datetime = current_day + timedelta(seconds=int(random_seconds))
            
            # Generate a random transaction amount between £10.00 and £100.00
            amount = round(random.uniform(10, 100), 2)
            
            # Choose a payment method randomly ("Card" or "Cash")
            payment_method = random.choice(["Card", "Cash"])
            
            # Set transaction status with probabilities: Completed (90%), Refunded (5%), Pending (5%)
            status = np.random.choice(["Completed", "Refunded", "Pending"], p=[0.9, 0.05, 0.05])
            
            # Create a unique transaction ID (e.g., T0000001, T0000002, ...)
            trans_id = "T" + str(transaction_counter).zfill(7)
            transaction_counter += 1
            
            # Append the transaction record
            data.append([trans_id, trans_datetime, amount, payment_method, restaurant, status])

# Create a DataFrame from the data
df = pd.DataFrame(data, columns=["Transaction_ID", "Date_Time", "Amount", "Payment_Method", "Restaurant_Name", "Status"])

# Save the DataFrame to a CSV file
df.to_csv("transactions_2yrs_min150.csv", index=False)

print("Transactions data generated and saved as 'transactions_2yrs_min150.csv'.")
