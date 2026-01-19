# todo_backend (FastAPI)

This container runs a simple in-memory To-Do REST API using FastAPI.

## Entry point

- Module: `src.api.main`
- FastAPI instance: `app`
- Recommended uvicorn target: `src.api.main:app`

## Local run

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Run the server (bind to port 3001):

```bash
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 3001
```

Health check:

- `GET /` should return `{"message":"Healthy"}`

## Notes

If you see `ModuleNotFoundError: No module named 'fastapi'`, it means the container environment has not installed `requirements.txt` yet.
