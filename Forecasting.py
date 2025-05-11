import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_percentage_error

# Load the aggregated daily summary file (assuming it's stored)
daily_summary = pd.read_csv("daily_summary.csv", parse_dates=["Date"])

print(daily_summary["Date"].duplicated().sum())  # Count duplicate dates
print(daily_summary[daily_summary["Date"].duplicated()])# Show duplicate entries

daily_summary = daily_summary.drop_duplicates(subset=["Date"])
daily_summary.set_index("Date", inplace=True)
daily_summary = daily_summary.asfreq("D")  # Explicitly set daily frequency

train_size = int(len(daily_summary) * 0.8)

# Split into train and test sets
train_data = daily_summary.iloc[:train_size]
test_data = daily_summary.iloc[train_size:]

print(f"Train set: {train_data.shape}, Test set: {test_data.shape}")

from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.statespace.sarimax import SARIMAX

# Check stationarity for Daily_Revenue
result = adfuller(daily_summary["Daily_Revenue"])
print(f"ADF Statistic: {result[0]}, p-value: {result[1]}")


import itertools
import numpy as np

p = d = q = range(0, 3)  # Try values from 0 to 2
seasonal_p = seasonal_d = seasonal_q = range(0, 2)
s = [7, 30]  # Weekly vs Monthly seasonality

# Generate all possible parameter combinations
param_combinations = list(itertools.product(p, d, q))
seasonal_combinations = list(itertools.product(seasonal_p, seasonal_d, seasonal_q, s))

# Test each combination and find the best
# best_aic = np.inf
# best_params = None

# for param in param_combinations:
#     for seasonal_param in seasonal_combinations:
#         try:
#             model = SARIMAX(daily_summary["Daily_Revenue"], order=param, seasonal_order=seasonal_param)
#             result = model.fit()
#             if result.aic < best_aic:  # Track the lowest AIC (better model fit)
#                 best_aic = result.aic
#                 best_params = (param, seasonal_param)
#         except:
#             continue  # Skip if the model fails to fit

# print(f"Best SARIMA Parameters: {best_params}, AIC: {best_aic}")

# If p-value > 0.05, apply differencing
sarima_model = SARIMAX(daily_summary["Daily_Revenue"], 
                        order=(2, 0, 2), 
                        seasonal_order=(1, 0, 1, 30), 
                        enforce_stationarity=False, 
                        enforce_invertibility=False)

sarima_result = sarima_model.fit(maxiter=1000, method="powell")
sarima_result.plot_diagnostics(figsize=(12, 8))
plt.show()

# Forecast for test period length
forecast = sarima_result.get_forecast(steps=len(test_data))

# Extract predicted values & actual test values
predicted_values = forecast.predicted_mean
actual_values = test_data["Daily_Revenue"]

# Evaluate Model Performance
rmse = np.sqrt(mean_squared_error(actual_values, predicted_values))
mape = mean_absolute_percentage_error(actual_values, predicted_values)

print(f"Model Validation:")
print(f"RMSE (Root Mean Squared Error): {rmse}")
print(f"MAPE (Mean Absolute Percentage Error): {mape * 100:.2f}%")  # Convert to percentage

forecast = sarima_result.get_forecast(steps=30)
forecast_index = pd.date_range(start=daily_summary.index[-1], periods=30, freq="D")  # Generate correct dates
forecast_series = pd.Series(forecast.predicted_mean.values, index=forecast_index)

print(forecast_series)


test_subset = test_data.iloc[:30]  # Take only the first 30 days of the test set
# plt.plot(test_subset.index, test_subset["Daily_Revenue"], label="Actual Revenue", marker="o")
# plt.plot(forecast_index, forecast.predicted_mean, label="Predicted Revenue", linestyle="dashed", color="red")


import matplotlib.pyplot as plt

# Plot actual vs predicted values
plt.figure(figsize=(12, 6))

# Actual Revenue from Test Data
plt.plot(test_subset.index, test_subset["Daily_Revenue"], label="Actual Revenue", marker="o", color="blue")

# Forecasted Revenue
plt.plot(test_subset.index, forecast.predicted_mean, label="Predicted Revenue", marker="x", linestyle="dashed", color="red")

# Add Confidence Interval
forecast_ci = forecast.conf_int()
plt.fill_between(test_subset.index, forecast_ci.iloc[:, 0], forecast_ci.iloc[:, 1], color='gray', alpha=0.2)

# Formatting
plt.legend()
plt.title("SARIMA Forecast vs Actual Revenue")
plt.xlabel("Date")
plt.ylabel("Revenue")
plt.grid()
plt.show()


from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense

# Normalize data
from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler()
scaled_data = scaler.fit_transform(daily_summary[["Daily_Revenue"]])

# Create sequences for LSTM (past 7 days → predict next day)
def create_sequences(data, seq_length=30):
    X, y = [], []
    for i in range(len(data) - seq_length):
        X.append(data[i:i+seq_length])
        y.append(data[i+seq_length])
    return np.array(X), np.array(y)

X, y = create_sequences(scaled_data)
X_train, y_train = X[:int(len(X) * 0.8)], y[:int(len(y) * 0.8)]

# Build LSTM Model
model = Sequential([
    LSTM(100, return_sequences=True, input_shape=(X_train.shape[1], X_train.shape[2])),
    LSTM(50),
    Dense(1)
])

model.compile(optimizer="adam", loss="mean_squared_error")
model.fit(X_train, y_train, epochs=20, batch_size=16)

# Forecast Next 30 Days
predictions = model.predict(X[-30:])
scaled_forecast = scaler.inverse_transform(predictions)

print(scaled_forecast)

import matplotlib.pyplot as plt

# Generate dates for the forecasted period
forecast_index = pd.date_range(start=daily_summary.index[-1], periods=30, freq="D")

# Plot historical revenue
plt.figure(figsize=(12, 6))
plt.plot(daily_summary.index[-100:], daily_summary["Daily_Revenue"].iloc[-100:], label="Historical Revenue", marker="o", color="blue")

# Plot LSTM forecasted revenue
plt.plot(forecast_index, scaled_forecast, label="LSTM Forecast", linestyle="dashed", color="red", marker="x")

# Formatting
plt.title("LSTM Forecast vs Actual Revenue")
plt.xlabel("Date")
plt.ylabel("Revenue")
plt.legend()
plt.grid()
plt.show()
