import json, urllib.request, urllib.parse, urllib.error

base='http://localhost:8001'

def fetch(path):
    req=urllib.request.Request(base+path, headers={'Accept':'application/json'})
    status=None; body=''; data=None; err=None
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            status=r.getcode(); body=r.read().decode('utf-8','replace')
    except urllib.error.HTTPError as e:
        status=e.code; body=e.read().decode('utf-8','replace'); err=f'HTTPError {e.code}'
    except Exception as e:
        err=repr(e)
    if body:
        try:data=json.loads(body)
        except Exception:data=None
    return status,data,err

out={}

st_species,data_species,err_species=fetch('/api/species')
first_species=None
species_count=None
if isinstance(data_species,list):
    species_count=len(data_species)
    if data_species:
        first=data_species[0]
        if isinstance(first,str):
            first_species=first
        elif isinstance(first,dict):
            first_species=first.get('species') or first.get('name') or first.get('common_name')

out['species']={'status':st_species,'error':err_species,'count':species_count,'first_species':first_species}

st_all,data_all,err_all=fetch('/api/routes/aggregated')
summary={'node_count':None,'country_count':None,'state_count':None}
top5=[]
if isinstance(data_all,dict):
    sm=data_all.get('summary')
    if isinstance(sm,dict):
        for k in summary.keys(): summary[k]=sm.get(k)
    counts=data_all.get('counts')
    if isinstance(counts,list):
        rows=[r for r in counts if isinstance(r,dict) and isinstance(r.get('count'),(int,float))]
        rows=sorted(rows,key=lambda r:r['count'],reverse=True)[:5]
        for r in rows:
            top5.append({'country':r.get('country'),'province':r.get('province'),'count':r.get('count')})
out['aggregated_all']={'status':st_all,'error':err_all,'summary':summary,'top5':top5}

if first_species:
    q=urllib.parse.quote(first_species,safe='')
    st_fs,data_fs,err_fs=fetch('/api/routes/aggregated?species='+q)
else:
    st_fs,data_fs,err_fs=None,None,'No first species'
out['aggregated_first_species']={'status':st_fs,'error':err_fs,'species':first_species}

print(json.dumps(out,indent=2,ensure_ascii=False))
