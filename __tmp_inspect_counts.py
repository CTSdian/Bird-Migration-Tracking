import json, urllib.request
u='http://localhost:8001/api/routes/aggregated'
with urllib.request.urlopen(u, timeout=30) as r:
    data=json.loads(r.read().decode('utf-8','replace'))
counts=data.get('counts',{})
print(type(counts).__name__)
if isinstance(counts, dict):
    print('COUNT_KEYS', list(counts.keys())[:10])
    for k,v in counts.items():
        print('KEY',k,'TYPE',type(v).__name__)
        if isinstance(v, dict):
            items=sorted(v.items(), key=lambda kv: kv[1], reverse=True)[:5]
            print('TOP5',items)
        elif isinstance(v, list):
            print('LIST_LEN',len(v),'FIRST',v[:2])
        break
