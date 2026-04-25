---
name: data-pipeline
description: "Build ETL/ELT data pipelines in Python: extract from files or APIs, transform with pandas, load to CSV/database/Parquet, schedule with cron or APScheduler, and handle errors with retries. Use when asked to build a pipeline, automate data processing, schedule jobs, or orchestrate data workflows."
---

# Data Pipeline Skill

## Required Packages
```
pip_install("pandas requests sqlalchemy apscheduler tenacity")
pip_install("pyarrow")  # for Parquet output
```

## 1. Pipeline Structure

```python
import logging
import pandas as pd
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

def extract() -> pd.DataFrame:
    """Load raw data from source."""
    ...

def transform(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and enrich data."""
    ...

def load(df: pd.DataFrame) -> None:
    """Write to destination."""
    ...

def run_pipeline():
    log.info("Pipeline started")
    try:
        raw = extract()
        log.info(f"Extracted {len(raw)} rows")
        clean = transform(raw)
        log.info(f"Transformed → {len(clean)} rows")
        load(clean)
        log.info("Pipeline completed")
    except Exception as e:
        log.error(f"Pipeline failed: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    run_pipeline()
```

## 2. Extract Patterns

### From CSV / Excel
```python
def extract() -> pd.DataFrame:
    return pd.read_csv("data/input.csv", parse_dates=["date"])
```

### From REST API (with retry)
```python
import requests
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
def _fetch_page(url: str, params: dict) -> dict:
    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()

def extract() -> pd.DataFrame:
    records = []
    page = 1
    while True:
        data = _fetch_page("https://api.example.com/data", {"page": page, "limit": 100})
        records.extend(data["items"])
        if not data.get("has_next"):
            break
        page += 1
    return pd.DataFrame(records)
```

### From SQL
```python
from sqlalchemy import create_engine

def extract() -> pd.DataFrame:
    engine = create_engine("postgresql://user:pass@host/db")
    return pd.read_sql("SELECT * FROM orders WHERE updated_at > NOW() - INTERVAL '1 day'", engine)
```

## 3. Transform Patterns

```python
def transform(df: pd.DataFrame) -> pd.DataFrame:
    # Standardise columns
    df.columns = df.columns.str.lower().str.replace(" ", "_")

    # Parse types
    df["created_at"] = pd.to_datetime(df["created_at"], utc=True)
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")

    # Drop duplicates and nulls in key columns
    df = df.drop_duplicates(subset=["id"])
    df = df.dropna(subset=["id", "amount"])

    # Derived columns
    df["date"] = df["created_at"].dt.date
    df["amount_usd"] = df["amount"] / 100  # cents → dollars

    # Filter
    df = df[df["status"] == "completed"]

    log.info(f"Transform: {len(df)} rows after cleaning")
    return df.reset_index(drop=True)
```

## 4. Load Patterns

### To CSV
```python
def load(df: pd.DataFrame) -> None:
    out = Path("data/output") / f"result_{datetime.today().strftime('%Y%m%d')}.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    log.info(f"Saved to {out}")
```

### To Parquet
```python
def load(df: pd.DataFrame) -> None:
    out = Path("data/output/result.parquet")
    df.to_parquet(out, index=False, engine="pyarrow")
    log.info(f"Saved {len(df)} rows to {out}")
```

### To SQL (upsert pattern)
```python
from sqlalchemy import create_engine

def load(df: pd.DataFrame) -> None:
    engine = create_engine("postgresql://user:pass@host/db")
    # Replace: drop and recreate table
    df.to_sql("results", engine, if_exists="replace", index=False, chunksize=1000)

    # Append only
    # df.to_sql("results", engine, if_exists="append", index=False, chunksize=1000)
```

## 5. Incremental / Delta Load
```python
from pathlib import Path
import json

STATE_FILE = Path("pipeline_state.json")

def _load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {"last_run": "1970-01-01T00:00:00"}

def _save_state(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state))

def run_pipeline():
    state = _load_state()
    last_run = state["last_run"]

    raw = extract(since=last_run)
    if raw.empty:
        log.info("No new data")
        return

    clean = transform(raw)
    load(clean)

    state["last_run"] = datetime.utcnow().isoformat()
    _save_state(state)
```

## 6. Schedule with APScheduler
```python
from apscheduler.schedulers.blocking import BlockingScheduler

scheduler = BlockingScheduler()

@scheduler.scheduled_job("cron", hour=6, minute=0)   # every day at 06:00
def scheduled_run():
    run_pipeline()

@scheduler.scheduled_job("interval", hours=1)         # every hour
def hourly_run():
    run_pipeline()

if __name__ == "__main__":
    log.info("Scheduler started")
    scheduler.start()
```

## 7. Error Handling & Alerting
```python
import traceback

def run_pipeline():
    start = datetime.utcnow()
    try:
        raw   = extract()
        clean = transform(raw)
        load(clean)
        duration = (datetime.utcnow() - start).seconds
        log.info(f"Success: {len(clean)} rows in {duration}s")
        return {"status": "ok", "rows": len(clean), "duration_s": duration}
    except Exception as e:
        log.error(f"FAILED: {e}\n{traceback.format_exc()}")
        # Send alert here (email, Slack webhook, etc.)
        return {"status": "error", "message": str(e)}
```

## 8. Data Quality Check
```python
def validate(df: pd.DataFrame, name: str = "output") -> None:
    errors = []
    if df.empty:
        errors.append("DataFrame is empty")
    if df["id"].duplicated().any():
        errors.append(f"Duplicate IDs: {df['id'].duplicated().sum()}")
    if df["amount"].isnull().any():
        errors.append(f"Null amounts: {df['amount'].isnull().sum()}")
    if errors:
        raise ValueError(f"Validation failed for {name}: {'; '.join(errors)}")
    log.info(f"Validation passed for {name}: {len(df)} rows")
```
