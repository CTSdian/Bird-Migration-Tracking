import subprocess, sys, time, urllib.request, urllib.error
from pathlib import Path

root = Path.cwd()
py = root / '.venv' / 'Scripts' / 'python.exe'
cmd = [str(py), '-m', 'uvicorn', 'backend.main:app', '--host', '127.0.0.1', '--port', '8001', '--log-level', 'debug']
proc = subprocess.Popen(cmd, cwd=str(root), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
logs = []
started = False
start_deadline = time.time() + 25

while time.time() < start_deadline:
    line = proc.stdout.readline()
    if not line:
        if proc.poll() is not None:
            break
        continue
    logs.append(line.rstrip('\n'))
    if 'Uvicorn running on' in line or 'Application startup complete' in line:
        started = True
        break

status = None
body = ''
err = None
url = 'http://127.0.0.1:8001/api/routes'
if started and proc.poll() is None:
    try:
        with urllib.request.urlopen(url, timeout=20) as r:
            status = r.getcode()
            body = r.read().decode('utf-8', errors='replace')
    except urllib.error.HTTPError as e:
        status = e.code
        body = e.read().decode('utf-8', errors='replace')
    except Exception as e:
        err = repr(e)
else:
    err = 'Server failed to start'

# allow log flush
time_limit = time.time() + 5
while time.time() < time_limit:
    if proc.poll() is not None:
        break
    line = proc.stdout.readline()
    if not line:
        continue
    logs.append(line.rstrip('\n'))

if proc.poll() is None:
    proc.terminate()
    try:
        rest, _ = proc.communicate(timeout=10)
    except Exception:
        proc.kill()
        rest, _ = proc.communicate()
else:
    rest, _ = proc.communicate()

if rest:
    logs.extend(rest.splitlines())

print(f'STATUS={status if status is not None else "N/A"}')
print('BODY_START')
print(body)
print('BODY_END')
if err:
    print(f'ERROR={err}')

# Extract key traceback lines
trace_idx = -1
for i, ln in enumerate(logs):
    if 'Traceback (most recent call last):' in ln:
        trace_idx = i

print('TRACE_START')
if trace_idx >= 0:
    excerpt = logs[trace_idx:trace_idx+40]
    for ln in excerpt:
        print(ln)
else:
    # fallback: print error-ish lines
    key = [ln for ln in logs if any(k in ln for k in ['ERROR', 'Exception', 'Traceback', 'ValueError', 'TypeError'])]
    for ln in key[-30:]:
        print(ln)
print('TRACE_END')
