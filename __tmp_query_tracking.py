import json
import urllib.request
from urllib.parse import quote

base = 'http://127.0.0.1:8001'
urls = {
    'species': f'{base}/api/tracking/species',
    'points': f"{base}/api/tracking/points?species={quote('American bittern')}"
}

results = {}
for key, url in urls.items():
    with urllib.request.urlopen(url, timeout=30) as r:
        body = r.read().decode('utf-8')
        results[key] = {'status': r.getcode(), 'data': json.loads(body)}

species_data = results['species']['data']
points_data = results['points']['data']

species_count = len(species_data) if isinstance(species_data, list) else None
point_count = points_data.get('point_count') if isinstance(points_data, dict) else None
individual_count = points_data.get('individual_count') if isinstance(points_data, dict) else None
points = points_data.get('points', []) if isinstance(points_data, dict) else []
first_three = []
for item in points[:3]:
    if isinstance(item, dict):
        first_three.append(item.get('timestamp'))

print('SPECIES_STATUS=' + str(results['species']['status']))
print('POINTS_STATUS=' + str(results['points']['status']))
print('SPECIES_COUNT=' + str(species_count))
print('POINT_COUNT=' + str(point_count))
print('INDIVIDUAL_COUNT=' + str(individual_count))
print('FIRST_3_TIMESTAMPS=' + json.dumps(first_three))
