import urllib.request
url = "http://127.0.0.1:8001/api/predictions/experiments"
with urllib.request.urlopen(url, timeout=20) as r:
    body = r.read().decode()
print("bytes", len(body))
print(body[:500])
