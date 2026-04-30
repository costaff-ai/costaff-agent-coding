---
name: data-visualization
description: "Create charts and visualisations from pandas DataFrames using matplotlib and seaborn: line charts, bar charts, scatter plots, heatmaps, pie charts, and multi-panel dashboards. Use when asked to plot, chart, visualise, or generate figures."
---

# Data Visualisation Skill

## Required Packages
```
pip_install("matplotlib seaborn pandas")
```

## Chart Patterns

### Line Chart
```python
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(df["date"], df["value"], marker="o", linewidth=2, label="Series A")
ax.set_title("Value Over Time")
ax.set_xlabel("Date")
ax.set_ylabel("Value")
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("line_chart.png", dpi=150)
plt.close()
```

### Bar Chart
```python
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.bar(df["category"], df["value"], color="steelblue", edgecolor="white")

# Add value labels on bars
for bar in bars:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width() / 2., height,
            f"{height:,.0f}", ha="center", va="bottom")

ax.set_title("Value by Category")
ax.set_xlabel("Category")
ax.set_ylabel("Value")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig("bar_chart.png", dpi=150)
plt.close()
```

### Horizontal Bar Chart (many categories)
```python
fig, ax = plt.subplots(figsize=(10, 8))
df_sorted = df.sort_values("value", ascending=True)
ax.barh(df_sorted["category"], df_sorted["value"], color="steelblue")
ax.set_title("Value by Category")
plt.tight_layout()
plt.savefig("barh_chart.png", dpi=150)
plt.close()
```

### Scatter Plot
```python
import seaborn as sns

fig, ax = plt.subplots(figsize=(8, 6))
scatter = ax.scatter(df["x"], df["y"], c=df["color_col"], cmap="viridis",
                     alpha=0.7, s=50)
plt.colorbar(scatter, ax=ax, label="Color Column")
ax.set_title("X vs Y")
ax.set_xlabel("X")
ax.set_ylabel("Y")
plt.tight_layout()
plt.savefig("scatter.png", dpi=150)
plt.close()
```

### Heatmap (correlation or pivot table)
```python
import seaborn as sns

# Correlation heatmap
corr = df.select_dtypes("number").corr()
fig, ax = plt.subplots(figsize=(10, 8))
sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm",
            vmin=-1, vmax=1, square=True, ax=ax)
ax.set_title("Correlation Matrix")
plt.tight_layout()
plt.savefig("heatmap.png", dpi=150)
plt.close()

# Pivot heatmap
pivot = df.pivot_table(values="value", index="row_col", columns="col_col", aggfunc="mean")
fig, ax = plt.subplots(figsize=(12, 8))
sns.heatmap(pivot, annot=True, fmt=".1f", cmap="YlOrRd", ax=ax)
plt.tight_layout()
plt.savefig("pivot_heatmap.png", dpi=150)
plt.close()
```

### Histogram + KDE
```python
fig, ax = plt.subplots(figsize=(8, 5))
ax.hist(df["value"], bins=30, density=True, alpha=0.6, color="steelblue", edgecolor="white")
df["value"].plot.kde(ax=ax, color="red", linewidth=2)
ax.set_title("Distribution of Value")
ax.set_xlabel("Value")
plt.tight_layout()
plt.savefig("histogram.png", dpi=150)
plt.close()
```

### Box Plot
```python
fig, ax = plt.subplots(figsize=(10, 6))
df.boxplot(column="value", by="group", ax=ax, grid=False)
ax.set_title("Value by Group")
plt.suptitle("")  # suppress default title
plt.tight_layout()
plt.savefig("boxplot.png", dpi=150)
plt.close()
```

### Pie Chart
```python
fig, ax = plt.subplots(figsize=(8, 8))
ax.pie(df["value"], labels=df["label"], autopct="%1.1f%%",
       startangle=90, counterclock=False)
ax.set_title("Distribution")
plt.tight_layout()
plt.savefig("pie_chart.png", dpi=150)
plt.close()
```

### Multi-Panel Dashboard
```python
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle("Dashboard", fontsize=16, fontweight="bold")

axes[0, 0].plot(df["date"], df["metric1"])
axes[0, 0].set_title("Metric 1 Over Time")

axes[0, 1].bar(df["category"], df["metric2"])
axes[0, 1].set_title("Metric 2 by Category")

axes[1, 0].scatter(df["x"], df["y"], alpha=0.5)
axes[1, 0].set_title("X vs Y")

axes[1, 1].hist(df["metric3"], bins=20)
axes[1, 1].set_title("Metric 3 Distribution")

plt.tight_layout()
plt.savefig("dashboard.png", dpi=150)
plt.close()
```

## Style Defaults
```python
# Apply at top of script for consistent styling
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid", palette="muted", font_scale=1.1)
plt.rcParams["figure.dpi"] = 150
plt.rcParams["savefig.bbox"] = "tight"
```

## Output
- Always call `plt.savefig("filename.png", dpi=150)` then `plt.close()`
- Save to the shared output directory when delivering to users
- Use descriptive filenames: `sales_by_region.png`, not `chart1.png`
