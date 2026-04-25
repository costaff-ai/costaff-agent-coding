---
name: data_tools
description: "Work with structured data: read and query JSON/YAML files, manage .env configuration variables, compare file versions with diff, and process CSV/tabular data. Use for config management, data inspection, environment setup, or output comparison."
---

# Data Tools Skill

## JSON / YAML

### Read and query with dot-notation
```python
query_json("config.json")                        # pretty-print entire file
query_json("config.json", "database.host")       # nested key
query_json("config.json", "servers.0.port")      # list index (as string)
query_json("settings.yaml", "app.debug")         # YAML supported
```
If YAML support is needed: `pip_install("pyyaml")`

### Error handling
- Key not found → tool returns available keys — use those to refine the expression
- JSON parse error → check file with `read_file()` first for syntax issues

## .env File Management

```python
dotenv_list(".env")                              # show all key=value pairs
dotenv_get("DATABASE_URL")                       # read a single value
dotenv_set("API_KEY", "sk-...")                  # add or update
dotenv_delete("OLD_KEY")                         # remove a key
```

Default path is `.env` in workspace root. For project-specific files:
```python
dotenv_set("PORT", "8080", path="myproject/.env")
```

**Never hardcode secrets in source files** — use `dotenv_set()` to write them to `.env` and read via `os.getenv()` at runtime.

## File Comparison

```python
diff_files("v1/main.py", "v2/main.py")
```
Returns a unified diff, or "Files are identical" if no differences. Useful for:
- Comparing before/after a refactor
- Verifying a patch was applied correctly
- Comparing expected vs actual output files

## CSV / Tabular Data
For analysis and transformation, use `run_python_code()` with pandas:

```python
run_python_code("""
import pandas as pd
df = pd.read_csv('data.csv')
print(df.shape)
print(df.dtypes)
print(df.describe())
print(df.head(10))
""")
```
Install if needed: `pip_install("pandas")`

For large files, read with `head()` or `read_lines()` first to understand structure before loading the whole file.
