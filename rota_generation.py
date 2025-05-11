import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Define the restaurants with 12 employees each.
restaurant_employees = {
    "Savory Bites": [
         {"name": n, "employee_id": f"SB_E{str(i+1).zfill(3)}", "hourly_pay": round(random.uniform(12.0, 14.0), 2)}
         for i, n in enumerate(["Alice", "Bob", "Carol", "Dave", "Eva", "Frank", "Grace", "Henry", "Irene", "Jack", "Karen", "Leo"])
    ],
    "Urban Feast": [
         {"name": n, "employee_id": f"UF_E{str(i+1).zfill(3)}", "hourly_pay": round(random.uniform(13.0, 15.0), 2)}
         for i, n in enumerate(["Mike", "Nina", "Oscar", "Pam", "Quincy", "Rose", "Steve", "Tara", "Umar", "Violet", "Will", "Xena"])
    ],
    "Gourmet Haven": [
         {"name": n, "employee_id": f"GH_E{str(i+1).zfill(3)}", "hourly_pay": round(random.uniform(14.0, 16.0), 2)}
         for i, n in enumerate(["Yvonne", "Zack", "Aaron", "Bella", "Carl", "Daisy", "Ethan", "Fiona", "Gordon", "Hanna", "Isaac", "Julia"])
    ]
}

# Define the two-year period
start_date = datetime(2023, 1, 1)
end_date = datetime(2024, 12, 31)
n_days = (end_date - start_date).days + 1  # Total number of days

# Define fixed base start times and labels for the two shifts.
shift_base = {
    0: {"base_start": "08:00", "rota_slot": "Morning"},
    1: {"base_start": "16:00", "rota_slot": "Evening"}
}

# Define possible working hours for a shift.
possible_hours = [4, 6, 8, 10]

data = []

# Generate rota records for each day, for each restaurant, and for each shift
for day in range(n_days):
    shift_date = start_date + timedelta(days=day)
    shift_date_str = shift_date.strftime("%Y-%m-%d")
    
    for restaurant, employees in restaurant_employees.items():
        for shift_index in [0, 1]:
            # Randomly select a primary employee for the shift.
            primary_employee = random.choice(employees)
            # Select a backup employee ensuring it is not the same as the primary.
            backup_candidates = [emp for emp in employees if emp["employee_id"] != primary_employee["employee_id"]]
            backup_employee = random.choice(backup_candidates)
            
            # Retrieve the base start time and rota label.
            base_start_time = shift_base[shift_index]["base_start"]
            rota_slot = shift_base[shift_index]["rota_slot"]
            
            # Combine the shift date with the base start time to get a shift start datetime.
            start_dt = datetime.strptime(shift_date_str + " " + base_start_time, "%Y-%m-%d %H:%M")
            
            # Randomly choose a number of hours for this shift from the possible_hours list.
            total_hours = np.random.choice(possible_hours)
            
            # Cast total_hours to a Python int so that timedelta accepts it.
            end_dt = start_dt + timedelta(hours=int(total_hours))
            # Format the end time as "HH:MM"
            end_time = end_dt.strftime("%H:%M")
            
            # Append the record, including total working hours.
            data.append([
                primary_employee["employee_id"],
                primary_employee["name"],
                restaurant,
                shift_date_str,
                base_start_time,
                end_time,
                primary_employee["hourly_pay"],
                backup_employee["name"],
                rota_slot,
                total_hours
            ])

# Define column names for the rota schedule data.
columns = [
    "Employee_ID",    # Primary employee's ID
    "Employee_Name",  # Primary employee's Name
    "Restaurant_Name",
    "Shift_Date",
    "Start_Time",
    "End_Time",
    "Hourly_Pay",
    "Backup",         # Backup employee name
    "Rota_Slot",
    "Total_Hours"     # Discrete total hours worked for the shift (could be 4, 6, 8, or 10)
]

# Create a DataFrame and save the data as CSV.
rota_df = pd.DataFrame(data, columns=columns)
rota_df.to_csv("rota_schedule_2yrs_12employees_randomHours.csv", index=False)

print("Rota scheduling data with random hours generated and saved as 'rota_schedule_2yrs_12employees_randomHours.csv'.")
