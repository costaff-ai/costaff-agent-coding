---
name: statistical-analysis
description: "Run statistical tests and analyses on pandas DataFrames: hypothesis testing (t-test, chi-square, ANOVA), confidence intervals, regression, and non-parametric tests. Use when asked to test significance, compare groups, find relationships, or validate assumptions."
---

# Statistical Analysis Skill

## Required Packages
```
pip_install("scipy statsmodels pandas numpy")
```

## 1. Descriptive Statistics
```python
import pandas as pd
import numpy as np

# Summary
print(df["value"].describe())
print(f"Skewness: {df['value'].skew():.3f}")
print(f"Kurtosis: {df['value'].kurtosis():.3f}")

# Confidence interval for the mean
from scipy import stats
n = len(df["value"].dropna())
mean = df["value"].mean()
se = stats.sem(df["value"].dropna())
ci = stats.t.interval(0.95, df=n-1, loc=mean, scale=se)
print(f"95% CI: ({ci[0]:.3f}, {ci[1]:.3f})")
```

## 2. Normality Test
```python
from scipy import stats

stat, p = stats.shapiro(df["value"].dropna())
print(f"Shapiro-Wilk: statistic={stat:.4f}, p={p:.4f}")
print("Normal" if p > 0.05 else "Not normal (p < 0.05)")

# For large samples (n > 5000), use D'Agostino-Pearson
stat, p = stats.normaltest(df["value"].dropna())
print(f"D'Agostino: statistic={stat:.4f}, p={p:.4f}")
```

## 3. Two-Sample Comparison

### Independent t-test (parametric)
```python
from scipy import stats

group_a = df[df["group"] == "A"]["value"]
group_b = df[df["group"] == "B"]["value"]

stat, p = stats.ttest_ind(group_a, group_b)
print(f"t-test: t={stat:.4f}, p={p:.4f}")
print("Significant" if p < 0.05 else "Not significant")

# Effect size (Cohen's d)
pooled_std = np.sqrt((group_a.var() + group_b.var()) / 2)
d = (group_a.mean() - group_b.mean()) / pooled_std
print(f"Cohen's d: {d:.3f}")
```

### Mann-Whitney U (non-parametric)
```python
stat, p = stats.mannwhitneyu(group_a, group_b, alternative="two-sided")
print(f"Mann-Whitney: U={stat:.1f}, p={p:.4f}")
```

### Paired t-test
```python
stat, p = stats.ttest_rel(df["before"], df["after"])
print(f"Paired t-test: t={stat:.4f}, p={p:.4f}")
```

## 4. ANOVA (3+ groups)
```python
from scipy import stats

groups = [group["value"].values for _, group in df.groupby("category")]
f_stat, p = stats.f_oneway(*groups)
print(f"One-way ANOVA: F={f_stat:.4f}, p={p:.4f}")

# Post-hoc: Tukey HSD
from statsmodels.stats.multicomp import pairwise_tukeyhsd
result = pairwise_tukeyhsd(endog=df["value"], groups=df["category"], alpha=0.05)
print(result.summary())
```

### Kruskal-Wallis (non-parametric ANOVA)
```python
stat, p = stats.kruskal(*groups)
print(f"Kruskal-Wallis: H={stat:.4f}, p={p:.4f}")
```

## 5. Chi-Square Test (categorical association)
```python
from scipy import stats

contingency = pd.crosstab(df["col_a"], df["col_b"])
chi2, p, dof, expected = stats.chi2_contingency(contingency)
print(f"Chi-square: χ²={chi2:.4f}, p={p:.4f}, dof={dof}")

# Effect size: Cramér's V
n = contingency.sum().sum()
cramer_v = np.sqrt(chi2 / (n * (min(contingency.shape) - 1)))
print(f"Cramér's V: {cramer_v:.3f}")
```

## 6. Correlation
```python
# Pearson (linear, continuous)
r, p = stats.pearsonr(df["x"], df["y"])
print(f"Pearson r={r:.3f}, p={p:.4f}")

# Spearman (monotonic, ordinal-safe)
rho, p = stats.spearmanr(df["x"], df["y"])
print(f"Spearman ρ={rho:.3f}, p={p:.4f}")

# Full correlation matrix with p-values
from statsmodels.stats.correlation_tools import corr_nearest
numeric = df.select_dtypes("number")
corr_matrix = numeric.corr(method="spearman")
print(corr_matrix)
```

## 7. Linear Regression
```python
import statsmodels.formula.api as smf

model = smf.ols("y ~ x1 + x2 + C(category)", data=df).fit()
print(model.summary())

# Key outputs
print(f"R²: {model.rsquared:.4f}")
print(f"Adj. R²: {model.rsquared_adj:.4f}")
print(f"AIC: {model.aic:.2f}")
print(model.params)
print(model.pvalues)
```

## 8. Logistic Regression
```python
import statsmodels.formula.api as smf

model = smf.logit("binary_target ~ x1 + x2", data=df).fit()
print(model.summary())

# Odds ratios
import numpy as np
print(np.exp(model.params))
```

## 9. Summary Report Pattern
```python
results = {
    "n": len(df),
    "mean_a": group_a.mean(),
    "mean_b": group_b.mean(),
    "p_value": p,
    "significant": p < 0.05,
    "effect_size_d": d,
}
import json
print(json.dumps(results, indent=2, default=float))
```
