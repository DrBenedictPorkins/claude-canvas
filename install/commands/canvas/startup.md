# Canvas Startup

Start the canvas server for this session and post a preflight header widget.

## Steps

### 1. Check if already running
```bash
PORT_FILE="/tmp/canvas-${CLAUDE_CODE_SESSION_ID}.port"
```
If `$PORT_FILE` exists and the server responds, skip to step 3. Otherwise delete the stale port file and continue.

### 2. Start the server
Use the Bash tool with **`run_in_background: true`**:
```bash
uv run {{CANVAS_DIR}}/server.py
```
Save the returned task ID. Then wait for the port file:
```bash
for i in $(seq 1 20); do [[ -f "$PORT_FILE" ]] && break; sleep 0.5; done
CANVAS_PORT=$(cat "$PORT_FILE")
```

### 3. Post preflight header
```bash
uv run python3 - <<'EOF'
import urllib.request, json, os, subprocess
port = open(f"/tmp/canvas-{os.environ['CLAUDE_CODE_SESSION_ID']}.port").read().strip()
now = subprocess.check_output(['date', '+%A, %B %-d %Y  %H:%M']).decode().strip()
payload = {"cmd": "text", "id": "_session", "title": "Session", "markdown": f"**Started:** {now}"}
req = urllib.request.Request(f"http://127.0.0.1:{port}/cmd", json.dumps(payload).encode(), {"Content-Type": "application/json"})
urllib.request.urlopen(req)
EOF
```

### 4. Report to user
Tell the user the canvas URL: `http://127.0.0.1:PORT` and the background task ID — they may need to switch to that browser tab.
