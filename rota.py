import random
import pandas as pd

# Define roles and employees with initial availability/unavailability
roles = {
    "Kitchen Staff": ["John", "Alice", "Mark", "Emma", "Jake"],
    "Servers": ["Sarah", "Max", "Lily"],
    "Managers": ["Tom", "Emma", "Lily"],
    "Cleaners": ["Jane", "Jake", "Max"]
}

# Define the shifts
shifts = ["Morning", "Afternoon", "Evening"]

# Define the number of days in the month
month_days = 30

# Generate availability data for the month
schedule_data = []
for day in range(1, month_days + 1):
    for shift in shifts:
        for role, employees in roles.items():
            # Randomize availability/unavailability
            available_employees = random.sample(employees, k=min(len(employees), 2))
            unavailable_employees = list(set(employees) - set(available_employees))
            
            # Add to the schedule data
            schedule_data.append({
                "Day": day,
                "Shift": shift,
                "Role": role,
                "Available Employees": ", ".join(available_employees),
                "Unavailable Employees": ", ".join(unavailable_employees)
            })

# Convert the schedule data to a DataFrame
schedule_df = pd.DataFrame(schedule_data)

# Save the schedule to a CSV file
csv_file_path = "monthly_availability_schedule.csv"
schedule_df.to_csv(csv_file_path, index=False)

print(f"Monthly availability schedule saved to {csv_file_path}")
