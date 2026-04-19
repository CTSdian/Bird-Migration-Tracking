import json, urllib.request
u='http://localhost:8001/api/routes/aggregated'
with urllib.request.urlopen(u, timeout=30) as r:
    data=json.loads(r.read().decode('utf-8','replace'))
counts=data.get('counts')
print('TYPE',type(counts).__name__)
if isinstance(counts,list):
    print('LEN',len(counts))
    for i,item in enumerate(counts[:5]):
        print(i,type(item).__name__,item)
