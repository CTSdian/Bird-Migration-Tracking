# Backend API

This backend uses FastAPI to serve bird migration route data and prediction placeholders.

## Setup

1. Create or activate a Python virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Run the API

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

## Available endpoints

- `GET /api/species` — list available bird species
- `GET /api/routes?species=<scientific_name>` — return route point records
- `GET /api/predictions?species=<scientific_name>` — return a prediction placeholder
