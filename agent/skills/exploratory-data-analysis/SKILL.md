---
name: exploratory-data-analysis
description: >
  Perform systematic exploratory data analysis (EDA) on a pandas DataFrame: shape,
  dtypes, missing values, distributions, correlations, value counts, and outlier
  detection. Use as the first step whenever you receive a new dataset, are asked to
  explore or understand data, need to profile columns before modelling, or the user
  says "show me what's in this data".
---

# Exploratory Data Analysis Skill

## EDA Workflow

### 1. Dataset Overview
```python
print("Shape:", df.shape)
print("\nDtypes:\n", df.dtypes)
print("\nMissing:\n", df.isnull().sum())
print("\nDuplicates:", df.duplicated().sum())
df.head(5)
```

### 2. Descriptive Statistics
```python
# Numeric columns
print(df.describe())

# Categorical columns
print(df.describe(include=["object", "category"]))

# Per-column: skewness and kurtosis
print(df.select_dtypes("number").skew())
print(df.select_dtypes("number").kurtosis())
```

### 3. Distributions
```python
import matplotlib.pyplot as plt
import seaborn as sns

numeric_cols = df.select_dtypes("number").columns

# Histogram grid
df[numeric_cols].hist(bins=30, figsize=(12, 8))
plt.tight_layout()
plt.savefig("distributions.png", dpi=150)
plt.close()

# Box plots (shows outliers)
fig, axes = plt.subplots(1, len(numeric_cols), figsize=(4 * len(numeric_cols), 4))
for ax, col in zip(axes, numeric_cols):
    sns.boxplot(y=df[col], ax=ax)
    ax.set_title(col)
plt.tight_layout()
plt.savefig("boxplots.png", dpi=150)
plt.close()
```

### 4. Categorical Value Counts
```python
cat_cols = df.select_dtypes(["object", "category"]).columns
for col in cat_cols:
    print(f"\n── {col} ──")
    print(df[col].value_counts().head(10))
    print(f"Unique: {df[col].nunique()}")
```

### 5. Correlation Analysis
```python
import matplotlib.pyplot as plt
import seaborn as sns

corr = df.select_dtypes("number").corr()

plt.figure(figsize=(10, 8))
sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm",
            vmin=-1, vmax=1, square=True)
plt.title("Correlation Matrix")
plt.tight_layout()
plt.savefig("correlation.png", dpi=150)
plt.close()

# Top correlated pairs
import numpy as np
pairs = (
    corr.where(np.triu(np.ones(corr.shape), k=1).astype(bool))
    .stack()
    .reset_index()
)
pairs.columns = ["col_a", "col_b", "correlation"]
print(pairs.sort_values("correlation", key=abs, ascending=False).head(10))
```

### 6. Target Variable Analysis (if applicable)
```python
target = "target_column"

# Distribution of target
print(df[target].value_counts(normalize=True))  # classification
print(df[target].describe())                    # regression

# Relationship with other features
for col in df.select_dtypes("number").columns:
    if col != target:
        corr_val = df[col].corr(df[target])
        print(f"{col}: {corr_val:.3f}")
```

### 7. Summary Report
```python
summary = {
    "rows": len(df),
    "columns": len(df.columns),
    "missing_pct": (df.isnull().sum().sum() / df.size * 100).round(2),
    "duplicates": df.duplicated().sum(),
    "numeric_cols": df.select_dtypes("number").columns.tolist(),
    "categorical_cols": df.select_dtypes(["object","category"]).columns.tolist(),
}
import json
print(json.dumps(summary, indent=2))
```
