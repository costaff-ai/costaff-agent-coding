---
name: time-series-analysis
description: "Analyse and forecast time series data: resampling, rolling statistics, trend/seasonality decomposition, stationarity testing, ARIMA/SARIMA forecasting, and anomaly detection. Use when asked to analyse trends over time, forecast, detect seasonality, or work with date-indexed data."
---

# Time Series Analysis Skill

## Required Packages
```
pip_install("pandas numpy matplotlib statsmodels")
pip_install("prophet")   # optional: Meta Prophet for flexible forecasting
```

## 1. Prepare the Time Series
```python
import pandas as pd

# Parse dates and set index
df["date"] = pd.to_datetime(df["date"])
df = df.sort_values("date").set_index("date")
ts = df["value"]  # Series with DatetimeIndex

# Check for gaps
expected_freq = "D"  # "H" hourly, "W" weekly, "M" monthly
ts = ts.asfreq(expected_freq)          # inserts NaT for missing dates
missing = ts.isnull().sum()
print(f"Missing after asfreq: {missing}")

# Fill gaps
ts = ts.ffill()   # forward fill — or ts.interpolate(method="time")
```

## 2. Resample (change granularity)
```python
# Aggregate to weekly / monthly
weekly = ts.resample("W").sum()
monthly = ts.resample("ME").mean()

# Multiple aggregations
monthly_agg = ts.resample("ME").agg(["mean", "min", "max", "sum"])
print(monthly_agg.head())
```

## 3. Rolling Statistics
```python
import matplotlib.pyplot as plt

window = 7  # rolling window size

rolling_mean = ts.rolling(window=window).mean()
rolling_std  = ts.rolling(window=window).std()

fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(ts, label="Original", alpha=0.5)
ax.plot(rolling_mean, label=f"{window}-day Mean", linewidth=2)
ax.fill_between(ts.index,
                rolling_mean - 2 * rolling_std,
                rolling_mean + 2 * rolling_std,
                alpha=0.2, label="±2σ band")
ax.legend()
ax.set_title("Rolling Statistics")
plt.tight_layout()
plt.savefig("rolling_stats.png", dpi=150)
plt.close()
```

## 4. Decomposition (trend + seasonality + residual)
```python
from statsmodels.tsa.seasonal import seasonal_decompose
import matplotlib.pyplot as plt

# model="additive" (constant variance) or "multiplicative" (growing variance)
result = seasonal_decompose(ts.dropna(), model="additive", period=7)

fig = result.plot()
fig.set_size_inches(12, 10)
plt.tight_layout()
plt.savefig("decomposition.png", dpi=150)
plt.close()

print(f"Trend range: {result.trend.dropna().min():.2f} – {result.trend.dropna().max():.2f}")
```

## 5. Stationarity Test
```python
from statsmodels.tsa.stattools import adfuller

result = adfuller(ts.dropna())
print(f"ADF Statistic : {result[0]:.4f}")
print(f"p-value       : {result[1]:.4f}")
print(f"Stationary    : {result[1] < 0.05}")

# Make stationary if needed
ts_diff = ts.diff().dropna()       # first difference
ts_log_diff = ts.apply("log").diff().dropna()  # log + diff (for multiplicative)
```

## 6. ARIMA Forecasting
```python
from statsmodels.tsa.arima.model import ARIMA

# Fit ARIMA(p, d, q)
# p = autoregressive order, d = differencing, q = moving average
model = ARIMA(ts.dropna(), order=(2, 1, 2))
result = model.fit()
print(result.summary())

# Forecast
n_forecast = 30
forecast = result.forecast(steps=n_forecast)
forecast_df = pd.DataFrame({
    "forecast": forecast,
    "date": pd.date_range(ts.index[-1], periods=n_forecast + 1, freq=ts.index.freq)[1:]
}).set_index("date")

import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(ts[-90:], label="History")
ax.plot(forecast_df, label="Forecast", linestyle="--")
ax.legend()
ax.set_title("ARIMA Forecast")
plt.tight_layout()
plt.savefig("forecast.png", dpi=150)
plt.close()
```

## 7. Auto-Select ARIMA Order (auto_arima)
```python
# pip_install("pmdarima")
from pmdarima import auto_arima

auto_model = auto_arima(ts.dropna(), seasonal=True, m=7,  # m=period
                        stepwise=True, suppress_warnings=True, information_criterion="aic")
print(auto_model.summary())
forecast = auto_model.predict(n_periods=30)
```

## 8. Prophet Forecasting (flexible, handles holidays)
```python
from prophet import Prophet
import pandas as pd

# Prophet requires columns: ds (datetime) and y (value)
prophet_df = ts.reset_index()
prophet_df.columns = ["ds", "y"]

m = Prophet(yearly_seasonality=True, weekly_seasonality=True, daily_seasonality=False)
m.fit(prophet_df)

future = m.make_future_dataframe(periods=30)
forecast = m.predict(future)

fig = m.plot(forecast)
fig.savefig("prophet_forecast.png", dpi=150)

fig2 = m.plot_components(forecast)
fig2.savefig("prophet_components.png", dpi=150)

print(forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].tail(30))
```

## 9. Anomaly Detection
```python
import numpy as np

# Z-score method on rolling window
rolling_mean = ts.rolling(window=30).mean()
rolling_std  = ts.rolling(window=30).std()
z_score = (ts - rolling_mean) / rolling_std
anomalies = ts[z_score.abs() > 3]
print(f"Anomalies found: {len(anomalies)}")
print(anomalies)

import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(ts, label="Series", alpha=0.7)
ax.scatter(anomalies.index, anomalies, color="red", s=50, label="Anomaly", zorder=5)
ax.legend()
ax.set_title("Anomaly Detection")
plt.tight_layout()
plt.savefig("anomalies.png", dpi=150)
plt.close()
```

## 10. Summary
```python
import json

summary = {
    "start": str(ts.index.min().date()),
    "end": str(ts.index.max().date()),
    "n_points": int(len(ts)),
    "mean": float(ts.mean()),
    "std": float(ts.std()),
    "trend": "upward" if ts.iloc[-1] > ts.iloc[0] else "downward",
    "stationary": bool(adfuller(ts.dropna())[1] < 0.05),
}
print(json.dumps(summary, indent=2))
```
