---
name: data-cleaning
description: "Clean a pandas DataFrame: handle missing values, remove duplicates, fix data types, detect and treat outliers. Use before any analysis, modelling, or visualisation task."
---

# Data Cleaning Skill

## Step 1 — Assess the Damage
```python
print(df.shape)
print(df.dtypes)
print(df.isnull().sum().sort_values(ascending=False))
print(df.duplicated().sum())
df.describe(include="all")
```

## Step 2 — Handle Missing Values

### Drop rows / columns
```python
df.dropna(inplace=True)                        # drop rows with ANY missing
df.dropna(subset=["critical_col"], inplace=True)  # drop only if key col is missing
df.dropna(thresh=int(len(df.columns) * 0.5), inplace=True)  # drop if >50% cols missing
df.drop(columns=["col_with_90pct_missing"], inplace=True)
```

### Fill missing values
```python
df["age"].fillna(df["age"].median(), inplace=True)      # numeric → median
df["city"].fillna(df["city"].mode()[0], inplace=True)   # categorical → mode
df["notes"].fillna("", inplace=True)                    # text → empty string
df["price"].fillna(method="ffill", inplace=True)        # time series → forward fill
```

## Step 3 — Remove Duplicates
```python
df.drop_duplicates(inplace=True)                        # exact duplicates
df.drop_duplicates(subset=["user_id", "date"], keep="last", inplace=True)
```

## Step 4 — Fix Data Types
```python
df["id"] = df["id"].astype(str)
df["revenue"] = pd.to_numeric(df["revenue"], errors="coerce")  # non-numeric → NaN
df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d", errors="coerce")
df["category"] = df["category"].astype("category")
```

### Clean string columns
```python
df["name"] = df["name"].str.strip().str.lower()
df["phone"] = df["phone"].str.replace(r"[^\d]", "", regex=True)
```

## Step 5 — Detect and Treat Outliers

### IQR method (recommended)
```python
Q1 = df["value"].quantile(0.25)
Q3 = df["value"].quantile(0.75)
IQR = Q3 - Q1
lower = Q1 - 1.5 * IQR
upper = Q3 + 1.5 * IQR

# Option A: remove outliers
df = df[(df["value"] >= lower) & (df["value"] <= upper)]

# Option B: cap (Winsorize)
df["value"] = df["value"].clip(lower=lower, upper=upper)
```

### Z-score method
```python
from scipy import stats
import numpy as np
z_scores = np.abs(stats.zscore(df["value"].dropna()))
df = df[z_scores < 3]
```

## Step 6 — Validate
```python
assert df.isnull().sum().sum() == 0, "Still has missing values"
assert df.duplicated().sum() == 0, "Still has duplicates"
print(f"Clean shape: {df.shape}")
df.to_csv("data_clean.csv", index=False)
```
