---
name: feature-engineering
description: "Transform raw pandas DataFrame columns into model-ready features: encoding categoricals, scaling numerics, creating date features, handling interactions, binning, and target encoding. Use before training any ML model or when asked to prepare features."
---

# Feature Engineering Skill

## Required Packages
```
pip_install("pandas numpy scikit-learn category_encoders")
```

## 1. Encode Categorical Variables

### One-Hot Encoding (low cardinality, ≤ 20 unique)
```python
df = pd.get_dummies(df, columns=["color", "city"], drop_first=True, dtype=int)
```

### Ordinal Encoding (ordered categories)
```python
from sklearn.preprocessing import OrdinalEncoder

order = [["low", "medium", "high"]]
enc = OrdinalEncoder(categories=order)
df["priority_enc"] = enc.fit_transform(df[["priority"]])
```

### Label Encoding (binary or tree-based models)
```python
from sklearn.preprocessing import LabelEncoder

le = LabelEncoder()
df["status_enc"] = le.fit_transform(df["status"])
```

### Target Encoding (high cardinality)
```python
import category_encoders as ce

enc = ce.TargetEncoder(cols=["city"])
df["city_enc"] = enc.fit_transform(df["city"], df["target"])
```

### Frequency Encoding
```python
freq = df["city"].value_counts(normalize=True)
df["city_freq"] = df["city"].map(freq)
```

## 2. Scale Numeric Features

### StandardScaler (zero mean, unit variance)
```python
from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()
cols = ["age", "income", "score"]
df[cols] = scaler.fit_transform(df[cols])
```

### MinMaxScaler (0–1 range)
```python
from sklearn.preprocessing import MinMaxScaler

scaler = MinMaxScaler()
df[["x", "y"]] = scaler.fit_transform(df[["x", "y"]])
```

### RobustScaler (outlier-resistant)
```python
from sklearn.preprocessing import RobustScaler

scaler = RobustScaler()
df[["value"]] = scaler.fit_transform(df[["value"]])
```

### Log Transform (right-skewed, all positive)
```python
import numpy as np

df["revenue_log"] = np.log1p(df["revenue"])  # log1p handles zeros
```

## 3. Date / Time Features
```python
df["date"] = pd.to_datetime(df["date"])

df["year"]        = df["date"].dt.year
df["month"]       = df["date"].dt.month
df["day"]         = df["date"].dt.day
df["dayofweek"]   = df["date"].dt.dayofweek   # 0=Monday
df["is_weekend"]  = (df["date"].dt.dayofweek >= 5).astype(int)
df["quarter"]     = df["date"].dt.quarter
df["week"]        = df["date"].dt.isocalendar().week.astype(int)

# Days since reference date
ref = pd.Timestamp("2020-01-01")
df["days_since_ref"] = (df["date"] - ref).dt.days

# Cyclical encoding (for models sensitive to periodicity)
import numpy as np
df["month_sin"] = np.sin(2 * np.pi * df["month"] / 12)
df["month_cos"] = np.cos(2 * np.pi * df["month"] / 12)
```

## 4. Binning / Discretisation
```python
# Equal-width bins
df["age_bin"] = pd.cut(df["age"], bins=5, labels=False)

# Custom bins with labels
df["age_group"] = pd.cut(df["age"],
                          bins=[0, 18, 35, 60, 100],
                          labels=["child", "young", "adult", "senior"])

# Quantile bins (equal-frequency)
df["income_quartile"] = pd.qcut(df["income"], q=4, labels=["Q1","Q2","Q3","Q4"])
```

## 5. Interaction Features
```python
# Multiplication
df["x_times_y"] = df["x"] * df["y"]

# Ratio
df["price_per_sqft"] = df["price"] / (df["sqft"] + 1)

# Polynomial features (for linear models)
from sklearn.preprocessing import PolynomialFeatures
import pandas as pd

poly = PolynomialFeatures(degree=2, include_bias=False)
poly_arr = poly.fit_transform(df[["x", "y"]])
poly_df = pd.DataFrame(poly_arr, columns=poly.get_feature_names_out(["x", "y"]))
df = pd.concat([df, poly_df.drop(columns=["x", "y"])], axis=1)
```

## 6. Text Features (basic)
```python
df["text_len"]       = df["text"].str.len()
df["word_count"]     = df["text"].str.split().str.len()
df["has_keyword"]    = df["text"].str.contains("keyword", case=False).astype(int)
df["exclamation_ct"] = df["text"].str.count("!")
```

## 7. Aggregation Features (groupby-based)
```python
# Mean encoding by group
agg = df.groupby("user_id")["purchase_amount"].agg(["mean", "sum", "count"])
agg.columns = ["user_avg_purchase", "user_total_purchase", "user_purchase_count"]
df = df.merge(agg, on="user_id", how="left")
```

## 8. Feature Selection

### Correlation filter
```python
corr_with_target = df.select_dtypes("number").corr()["target"].abs()
top_features = corr_with_target[corr_with_target > 0.1].index.tolist()
print("Top correlated features:", top_features)
```

### Variance threshold
```python
from sklearn.feature_selection import VarianceThreshold

sel = VarianceThreshold(threshold=0.01)
sel.fit(df.select_dtypes("number"))
kept = df.select_dtypes("number").columns[sel.get_support()].tolist()
print("Features kept:", kept)
```

## Save / Load Transformers
```python
import joblib

# Save
joblib.dump(scaler, "scaler.pkl")
joblib.dump(enc, "encoder.pkl")

# Load
scaler = joblib.load("scaler.pkl")
```
