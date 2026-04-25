---
name: server-development
description: "Build REST API servers with FastAPI or Flask, including CRUD endpoints, Pydantic models, and integration tests. Use for any web server, API, HTTP endpoint, or CRUD task."
---

# Server Development Skill

## Required Packages
```
pip_install("fastapi uvicorn[standard] httpx pytest")
```

## Recommended Project Structure

```
{project_name}/
  src/{name}/
    __init__.py
    main.py           # FastAPI app + router registration
    models.py         # Pydantic models
    routes/
      __init__.py
      {resource}.py   # one file per resource (items, users, etc.)
  tests/
    test_api.py
  requirements.txt
```

## FastAPI CRUD Template

### main.py
```python
from fastapi import FastAPI
from .routes import items

app = FastAPI(title="My API")
app.include_router(items.router, prefix="/items", tags=["items"])
```

### models.py
```python
from pydantic import BaseModel

class Item(BaseModel):
    id: int
    name: str
    description: str = ""
```

### routes/{resource}.py
```python
from fastapi import APIRouter, HTTPException
from ..models import Item

router = APIRouter()
_db: dict[int, Item] = {}

@router.get("/", response_model=list[Item])
def list_items():
    return list(_db.values())

@router.post("/", response_model=Item, status_code=201)
def create_item(item: Item):
    _db[item.id] = item
    return item

@router.get("/{item_id}", response_model=Item)
def get_item(item_id: int):
    if item_id not in _db:
        raise HTTPException(status_code=404, detail="Not found")
    return _db[item_id]

@router.put("/{item_id}", response_model=Item)
def update_item(item_id: int, item: Item):
    if item_id not in _db:
        raise HTTPException(status_code=404, detail="Not found")
    _db[item_id] = item
    return item

@router.delete("/{item_id}", status_code=204)
def delete_item(item_id: int):
    if item_id not in _db:
        raise HTTPException(status_code=404, detail="Not found")
    del _db[item_id]
```

## Testing Strategy

### Unit tests with TestClient (preferred)
```python
from fastapi.testclient import TestClient
from src.{name}.main import app

client = TestClient(app)

def test_create_and_get():
    r = client.post("/items/", json={"id": 1, "name": "test"})
    assert r.status_code == 201
    r = client.get("/items/1")
    assert r.status_code == 200
    assert r.json()["name"] == "test"

def test_update():
    client.post("/items/", json={"id": 2, "name": "old"})
    r = client.put("/items/2", json={"id": 2, "name": "new"})
    assert r.status_code == 200

def test_delete():
    client.post("/items/", json={"id": 3, "name": "to-delete"})
    r = client.delete("/items/3")
    assert r.status_code == 204

def test_not_found():
    r = client.get("/items/9999")
    assert r.status_code == 404
```

### Integration test with live uvicorn (when testing real server behaviour)
```python
start_process(
    "python3 -m uvicorn src.{name}.main:app --host 0.0.0.0 --port 18200",
    "api_server"
)
wait_for_port(18200, timeout=15)
# run shell-level curl or httpx tests here
stop_process("api_server")
```
