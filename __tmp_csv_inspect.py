import csv
from pathlib import Path
from collections import Counter
R=Path('Bird_Tracking_Data'); I=[2,3,4,22,23]; L={2:'C',3:'D',4:'E',22:'W',23:'X'}
B=[(b'\xff\xfe\x00\x00','UTF-32 LE BOM'),(b'\x00\x00\xfe\xff','UTF-32 BE BOM'),(b'\xef\xbb\xbf','UTF-8 BOM'),(b'\xff\xfe','UTF-16 LE BOM'),(b'\xfe\xff','UTF-16 BE BOM')]
def bom(raw):
    for s,n in B:
        if raw.startswith(s): return n
    return 'none'
def enc(raw):
    for e in ['utf-8-sig','utf-8','utf-16','utf-16-le','utf-16-be']:
        try: raw.decode(e); return e,False
        except: pass
    for e in ['cp1252','latin-1']:
        try: raw.decode(e); return e,True
        except: pass
    return 'unknown',True
def delim(txt):
    s='\n'.join([x for x in txt.splitlines() if x.strip()][:20])
    try: d=csv.Sniffer().sniff(s,delimiters=',\t;|').delimiter
    except: d=max([',','\t',';','|'],key=s.count) if s else 'unknown'
    return '\\t' if d=='\t' else d
def rows(txt,d):
    return [r for r in csv.reader(txt.splitlines(),delimiter=('\t' if d=='\\t' else d)) if any(c.strip() for c in r)]
def g(r,i): return r[i] if r and i<len(r) else '<missing>'
def n(x): return ' '.join(x.strip().lower().replace('_',' ').replace('-',' ').split())
files=sorted(R.rglob('*.csv')); dc=Counter(); ec=Counter(); bc=Counter(); issues=[]; ts=Counter(); lon=Counter(); lat=Counter(); ident=Counter()
for p in files:
    raw=p.read_bytes(); b=bom(raw); e,loss=enc(raw)
    try: txt=raw.decode(e,errors=('replace' if loss else 'strict'))
    except: txt=raw.decode('latin-1',errors='replace'); e='latin-1'; loss=True
    d=delim(txt); rr=rows(txt,d); h1=rr[0] if rr else None; h2=rr[1] if len(rr)>1 else None; data=rr[1] if len(rr)>1 else rr[0] if rr else None
    print('\nFILE',p.as_posix()); print('COLS',len(h1) if h1 else 0); print('ENC',e,'BOM',b,'LOSSY',loss,'DELIM',d)
    print('H1',h1 if h1 else '<none>'); print('H2',h2 if h2 else '<none>')
    print('HEADIDX',{L[i]:g(h1,i) for i in I}); print('DATAIDX',{L[i]:g(data,i) for i in I})
    dc[d]+=1; ec[e]+=1; bc[b]+=1
    if loss or b!='none': issues.append((p.as_posix(),b,e,loss))
    if h1:
        for x in h1:
            y=n(x)
            if not y: continue
            if any(k in y for k in ['time','date','timestamp','datetime']): ts[y]+=1
            if 'lon' in y or 'longitude' in y or y in {'x','location long'}: lon[y]+=1
            if 'lat' in y or 'latitude' in y or y in {'y','location lat'}: lat[y]+=1
            if any(k in y for k in ['id','identifier','tag','individual','bird','animal','name']) and y not in {'latitude','longitude'}: ident[y]+=1
print('\nSUMMARY')
print('FILES',len(files)); print('DELIMS',dict(dc)); print('ENCS',dict(ec)); print('BOMS',dict(bc)); print('ISSUES',issues if issues else 'none')
print('TS',ts.most_common(12)); print('LON',lon.most_common(12)); print('LAT',lat.most_common(12)); print('ID',ident.most_common(16))
