import json
import re
import urllib.request
from urllib.parse import quote

base = 'http://127.0.0.1:8001'
with urllib.request.urlopen(f'{base}/api/tracking/species', timeout=30) as r:
    species = json.loads(r.read().decode('utf-8'))

matches = [s for s in species if isinstance(s, str) and 'osprey' in s.lower()]
chosen = matches[0] if matches else 'Osprey'

with urllib.request.urlopen(f"{base}/api/tracking/points?species={quote(chosen)}", timeout=60) as r:
    data = json.loads(r.read().decode('utf-8'))

points = data.get('points', []) if isinstance(data, dict) else []
ids = []
seen = set()
for p in points:
    if not isinstance(p, dict):
        continue
    ident = p.get('identifier')
    if ident is None:
        ident = p.get('individual_id')
    if ident is None:
        ident = p.get('id')
    if ident is None:
        continue
    ident = str(ident)
    if ident not in seen:
        seen.add(ident)
        ids.append(ident)

has_year_suffix = any(re.search(r'\(\d{4}\)$', x) for x in ids)

print('CHOSEN_SPECIES=' + chosen)
print('INDIVIDUAL_COUNT=' + str(data.get('individual_count')))
print('UNIQUE_IDENTIFIER_COUNT=' + str(len(ids)))
print('FIRST_10_UNIQUE_IDENTIFIERS=' + json.dumps(ids[:10]))
print('HAS_YEAR_SUFFIX=' + ('yes' if has_year_suffix else 'no'))
