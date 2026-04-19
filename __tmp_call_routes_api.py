import traceback
import urllib.request
import urllib.error
url = "http://localhost:8000/api/clustering/routes"
print(f"GET {url}")
try:
    with urllib.request.urlopen(url, timeout=20) as r:
        status = r.getcode()
        body = r.read().decode("utf-8", errors="replace")
        print("Status:", status)
        print("Body snippet:", body[:1000])
except urllib.error.HTTPError as e:
    body = e.read().decode("utf-8", errors="replace")
    print("Status:", e.code)
    print("Body snippet:", body[:1000])
    traceback.print_exc()
    raise
except Exception as e:
    print("EXCEPTION:", type(e).__name__, str(e))
    traceback.print_exc()
    raise
