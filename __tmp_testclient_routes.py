import traceback
from fastapi.testclient import TestClient
from backend.main import app

print("Calling /api/clustering/routes via TestClient...")
client = TestClient(app)
try:
    resp = client.get("/api/clustering/routes")
    print("Status:", resp.status_code)
    print("Body snippet:", resp.text[:1000])
except Exception as e:
    print("EXCEPTION:", type(e).__name__, str(e))
    traceback.print_exc()
    raise
