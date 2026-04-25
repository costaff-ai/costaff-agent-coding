---
name: data-loading
description: "Load data from CSV, Excel, JSON, Parquet, or SQL databases into pandas DataFrames. Use when reading files, importing datasets, connecting to databases, or handling encoding and schema issues."
---

# Data Loading Skill

## Required Packages
```
pip_install("pandas openpyxl sqlalchemy")
pip_install("pyarrow")   # for Parquet
```

## Loading by Format

### CSV
```python
import pandas as pd

# Basic
df = pd.read_csv("data.csv")

# Common options
df = pd.read_csv(
    "data.csv",
    encoding="utf-8",          # try "utf-8-sig" for Excel-exported CSVs
    sep=",",                   # or "\t" for TSV
    header=0,                  # row index of column names (None if no header)
    usecols=["col_a", "col_b"],# only load needed columns
    dtype={"id": str},         # force specific types
    parse_dates=["date_col"],  # auto-parse date columns
    na_values=["N/A", "-", ""],# custom NA strings
)
```

### Excel
```python
df = pd.read_excel("data.xlsx", sheet_name="Sheet1")

# All sheets as dict
sheets = pd.read_excel("data.xlsx", sheet_name=None)
df = sheets["Sales"]
```

### JSON
```python
# Records format: [{"a":1}, {"a":2}]
df = pd.read_json("data.json")

# Nested: use json_normalize
import json
with open("data.json") as f:
    raw = json.load(f)
df = pd.json_normalize(raw, record_path="items", meta=["id", "name"])
```

### Parquet
```python
df = pd.read_parquet("data.parquet")
df = pd.read_parquet("data.parquet", columns=["col_a", "col_b"])
```

### SQL
```python
from sqlalchemy import create_engine

engine = create_engine("sqlite:///database.db")
df = pd.read_sql("SELECT * FROM users WHERE active = 1", engine)
df = pd.read_sql_table("users", engine)
```

## Handling Large Files
```python
# Read in chunks to avoid OOM
chunks = []
for chunk in pd.read_csv("large.csv", chunksize=100_000):
    # filter or aggregate before collecting
    chunks.append(chunk[chunk["status"] == "active"])
df = pd.concat(chunks, ignore_index=True)
```

## Encoding Diagnosis
```python
# When encoding is unknown, detect it
import chardet
with open("data.csv", "rb") as f:
    result = chardet.detect(f.read(50_000))
print(result["encoding"])   # then pass to read_csv(encoding=...)
```
Install if needed: `pip_install("chardet")`

## Post-Load Checklist
After loading, always run:
```python
print(df.shape)         # rows × columns
print(df.dtypes)        # check type inference
print(df.head())        # sanity check
print(df.isnull().sum())# missing value count
```
