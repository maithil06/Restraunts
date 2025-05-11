import pandas as pd
import random
from datetime import datetime, timedelta

# Define the three restaurants and the inventory items
restaurants = ["Savory Bites", "Urban Feast", "Gourmet Haven"]
inventory_items = ["Coffee Powder", "Veggies", "Consumables"]

# Define the two-year period for generating data
start_date = datetime(2023, 1, 1)
end_date = datetime(2024, 12, 31)

data = []
order_id_counter = 1

# Generate inventory orders every week during the period
current_date = start_date
while current_date <= end_date:
    for restaurant in restaurants:
        for item in inventory_items:
            order_date = current_date.strftime("%Y-%m-%d")
            # Simulate the delivery date as the order date plus 0 to 2 days
            delivery_delta = random.randint(0, 2)
            delivery_date = (current_date + timedelta(days=delivery_delta)).strftime("%Y-%m-%d")
            # Random quantity of items ordered
            quantity_ordered = random.randint(50, 300)
            # Simulate the current stock level (a random fallback level)
            current_stock = random.randint(20, 150)
            # Reorder level is set randomly within a certain threshold
            reorder_level = random.randint(30, 70)
            # Set a unit price based on the item type (with some variability)
            if item == "Coffee Powder":
                unit_price = round(random.uniform(0.5, 1.0), 2)
            elif item == "Veggies":
                unit_price = round(random.uniform(1.0, 2.0), 2)
            elif item == "Consumables":
                unit_price = round(random.uniform(2.0, 4.0), 2)
            # Total cost of the order
            total_cost = round(quantity_ordered * unit_price, 2)
            # Last updated timestamp (order date with a random hour offset)
            last_updated = (current_date + timedelta(hours=random.randint(0, 23))).strftime("%Y-%m-%d %H:%M")
            
            inventory_id = "I" + str(order_id_counter).zfill(6)
            order_id_counter += 1
            
            data.append([
                inventory_id,
                restaurant,
                item,
                order_date,
                delivery_date,
                quantity_ordered,
                current_stock,
                reorder_level,
                unit_price,
                total_cost,
                last_updated
            ])
    # Advance to the next week
    current_date += timedelta(days=7)

# Define the DataFrame columns
columns = [
    "Inventory_ID",
    "Restaurant_Name",
    "Item_Name",
    "Order_Date",
    "Delivery_Date",
    "Quantity_Ordered",
    "Current_Stock",
    "Reorder_Level",
    "Unit_Price",
    "Total_Cost",
    "Last_Updated"
]

# Create a DataFrame and export it to CSV
df_inventory = pd.DataFrame(data, columns=columns)
df_inventory.to_csv("inventory_stock_2yrs.csv", index=False)

print("Inventory stock data generated and saved as 'inventory_stock_2yrs.csv'.")
