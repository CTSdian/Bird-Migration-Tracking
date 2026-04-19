import json, urllib.request, urllib.parse, urllib.error

base = 'http://localhost:8001'


def get_json(path):
    url = base + path
    req = urllib.request.Request(url, headers={'Accept': 'application/json'})
    status = None
    body = ''
    data = None
    error = None
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            status = r.getcode()
            body = r.read().decode('utf-8', errors='replace')
    except urllib.error.HTTPError as e:
        status = e.code
        body = e.read().decode('utf-8', errors='replace')
        error = f'HTTPError {e.code}'
    except Exception as e:
        error = repr(e)
    if body:
        try:
            data = json.loads(body)
        except Exception:
            data = None
    return status, body, data, error

results = {}

s_status, s_body, s_data, s_err = get_json('/api/species')
results['species'] = {'status': s_status, 'error': s_err}
first_species = None
species_count = None
if isinstance(s_data, list):
    species_count = len(s_data)
    if s_data:
        first_species = s_data[0] if isinstance(s_data[0], str) else str(s_data[0])
elif isinstance(s_data, dict):
    for k in ['species', 'items', 'data']:
        if isinstance(s_data.get(k), list):
            arr = s_data[k]
            species_count = len(arr)
            if arr:
                first_species = arr[0] if isinstance(arr[0], str) else str(arr[0])
            break
results['species']['count'] = species_count
results['species']['first_species'] = first_species

all_status, all_body, all_data, all_err = get_json('/api/routes/aggregated')
results['aggregated_all'] = {'status': all_status, 'error': all_err}
summary = {'node_count': None, 'country_count': None, 'state_count': None}
count_entries = []
if isinstance(all_data, dict):
    sm = all_data.get('summary')
    if isinstance(sm, dict):
        for k in summary.keys():
            summary[k] = sm.get(k)

    if isinstance(all_data.get('counts'), dict):
        pairs = sorted(all_data['counts'].items(), key=lambda kv: kv[1], reverse=True)
        count_entries = [{'name': k, 'count': v} for k, v in pairs[:5]]
    elif isinstance(all_data.get('routes'), list):
        rows = [r for r in all_data['routes'] if isinstance(r, dict) and isinstance(r.get('count'), (int,float))]
        rows = sorted(rows, key=lambda x: x['count'], reverse=True)[:5]
        for r in rows:
            count_entries.append({'name': r.get('name') or r.get('species') or r.get('id'), 'count': r.get('count')})

results['aggregated_all']['summary'] = summary
results['aggregated_all']['top5'] = count_entries
results['aggregated_all']['keys'] = list(all_data.keys()) if isinstance(all_data, dict) else None

if first_species:
    q = urllib.parse.quote(first_species, safe='')
    fs_status, fs_body, fs_data, fs_err = get_json('/api/routes/aggregated?species=' + q)
    results['aggregated_first_species'] = {
        'status': fs_status,
        'species': first_species,
        'error': fs_err,
        'keys': list(fs_data.keys()) if isinstance(fs_data, dict) else None,
    }
    if isinstance(fs_data, dict) and isinstance(fs_data.get('summary'), dict):
        results['aggregated_first_species']['summary'] = fs_data['summary']
else:
    results['aggregated_first_species'] = {'status': None, 'species': None, 'error': 'Could not determine first species'}

print(json.dumps(results, indent=2))
