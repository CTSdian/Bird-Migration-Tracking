# Bird Migration Web Application

This project is a bird migration visualization and prediction web app.

## Structure

- `backend/` — Python FastAPI backend serving migration route and prediction APIs.
- `frontend/` — React + Vite application for interactive route visualization.
- `data.csv` — migration dataset in CSV format.

## Getting started

### Quick Start (Both Servers)

Run the PowerShell script to start both backend and frontend:

```powershell
.\start.ps1
```

This starts the backend on port 8001 and frontend on port 5173.

### Manual Start

#### Backend

1. Create or activate a Python virtual environment in the project root.
2. Install backend dependencies:

```bash
pip install -r backend/requirements.txt
```

3. Run the backend API:

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8001
```

#### Frontend

1. Install Node dependencies in `frontend`:

```bash
cd frontend
npm install
```

2. Start the Vite development server:

```bash
npm run dev
```

3. Open the browser at `http://localhost:5173`.

## Notes

- The frontend proxies `/api` calls to `http://localhost:8001`.
- The backend currently loads `data.csv` from the project root.
- The polygon choropleth maps fetch Natural Earth country and admin-1 GeoJSON layers at runtime, so an internet connection is required for full boundary rendering in development.
- Route prediction is scaffolded as a placeholder and can be extended with sequence mining or ML models.
