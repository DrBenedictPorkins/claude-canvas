# Canvas — Browser Data Visualization

Renders interactive charts, tables, metrics, and text in a persistent browser workbook via a local HTTP+WebSocket server.

**Server location:** `{{CANVAS_DIR}}`

---

## Startup ("startup canvas" / "use canvas")

When the user asks to start or use canvas, run this sequence:

### 1. Check if already running
```bash
PID_FILE="/tmp/canvas-${CLAUDE_CODE_SESSION_ID}.pid"
PORT_FILE="/tmp/canvas-${CLAUDE_CODE_SESSION_ID}.port"
if [[ -f "$PID_FILE" ]] && kill -0 "$(cat $PID_FILE)" 2>/dev/null; then
  echo "already running on port $(cat $PORT_FILE)"
fi
```

### 2. Start if not running
```bash
nohup uv run {{CANVAS_DIR}}/server.py > /tmp/canvas-${CLAUDE_CODE_SESSION_ID}.log 2>&1 &
```
Server prints `Canvas ready at http://127.0.0.1:PORT` and auto-opens the browser tab.

Wait for port file (poll up to 10s):
```bash
for i in $(seq 1 20); do
  [[ -f "$PORT_FILE" ]] && break
  sleep 0.5
done
CANVAS_PORT=$(cat "$PORT_FILE")
```

### 3. Preflight: post session header
```python
import urllib.request, json, os, subprocess
port = open(f"/tmp/canvas-{os.environ['CLAUDE_CODE_SESSION_ID']}.port").read().strip()
now = subprocess.check_output(['date', '+%A, %B %-d %Y  %H:%M']).decode().strip()
cx(port, {"cmd": "text", "id": "_session", "title": "Session", "markdown": f"**Started:** {now}"})
```

Tell the user: "Canvas is live at `http://127.0.0.1:PORT`" — they may need to switch to that tab.

---

## Helper

Define `cx()` once per session, then call it for every widget:

```python
import urllib.request, json, os

CANVAS_PORT = open(f"/tmp/canvas-{os.environ['CLAUDE_CODE_SESSION_ID']}.port").read().strip()

def cx(payload: dict) -> dict:
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        f"http://127.0.0.1:{CANVAS_PORT}/cmd",
        data=data,
        headers={"Content-Type": "application/json"},
    )
    return json.loads(urllib.request.urlopen(req).read())
```

Run via Bash with `uv run python3 -c "..."` or inline in a script. No extra dependencies — stdlib only.

---

## API — POST /cmd

All calls are JSON POSTs. The `cmd` field selects the method.

### `add` / `update` — Plotly chart
```python
cx({
    "cmd": "add",
    "id": "my-chart",
    "spec": {
        "traces": [
            {"x": [...], "y": [...], "name": "Series A", "type": "scatter", "mode": "lines+markers"}
        ],
        "layout": {"title": "Chart Title", "yaxis": {"title": "Y label"}},
        "height": 360,
    }
})
```
`update` replaces an existing chart in place. Dark theme applied automatically — do not set `paper_bgcolor`/`plot_bgcolor`.

### `stream` — append live data point
```python
cx({"cmd": "stream", "id": "price-chart", "traceIndex": 0, "point": {"x": "14:32:05", "y": 54.44}})
```

### `metric` — KPI card row
```python
cx({
    "cmd": "metric",
    "id": "kpis",
    "items": [
        {"label": "Portfolio", "value": "$283,841", "delta": "+$8,320", "trend": "up", "sub": "since inception"},
        {"label": "Cash",      "value": "$25,835",                                      "sub": "buying power"},
    ]
})
```
`trend`: `"up"` | `"down"` | omit. `delta` and `sub` optional.

### `text` — markdown block
```python
cx({"cmd": "text", "id": "analysis", "title": "Analysis", "markdown": "## Summary\n\n**Key finding** here."})
```
Supports headers, bold, italic, inline code, fenced blocks, lists, hr.

### `table` — sortable data table
```python
cx({
    "cmd": "table",
    "id": "positions",
    "spec": {
        "title": "Positions",
        "columns": ["Symbol", "Value", "Gain %"],
        "rows": [
            ["AAPL", "$12,400", "+42.0%"],
            ["MSFT", "$8,200",  "-3.1%"],
        ],
    }
})
```
Click-sortable. `+`/`▲` cells green, `-`/`▼` cells red.

### `section` — full-width divider
```python
cx({"cmd": "section", "id": "s1", "label": "Portfolio Overview"})
```

### `remove` / `clear`
```python
cx({"cmd": "remove", "id": "my-chart"})
cx({"cmd": "clear"})
```

---

## Layout

Responsive 2-column grid. `section` and `metric` span full width. State persists to `localStorage`.

---

## Common Plotly patterns

**Time series:**
```python
cx({"cmd": "add", "id": "perf", "spec": {
    "traces": [{"x": ["2024-01", "2024-02"], "y": [0, 5.2], "name": "A", "type": "scatter", "mode": "lines"}],
    "layout": {"title": "Performance", "yaxis": {"title": "% Return"}},
}})
```

**Bar with color gradient:**
```python
cx({"cmd": "add", "id": "gains", "spec": {
    "traces": [{"x": ["A", "B", "C"], "y": [42, -8, 15], "type": "bar",
                "marker": {"color": [42, -8, 15],
                           "colorscale": [[0, "#f87171"], [0.5, "#ffb74d"], [1, "#81c784"]],
                           "cmin": -30, "cmax": 50}}],
    "layout": {"title": "Returns"},
}})
```

**Donut:**
```python
cx({"cmd": "add", "id": "alloc", "spec": {
    "traces": [{"labels": ["A", "B", "C"], "values": [60, 25, 15], "type": "pie",
                "hole": 0.55, "textinfo": "label+percent", "textposition": "outside"}],
    "layout": {"title": "Allocation"},
}})
```

**Candlestick:**
```python
cx({"cmd": "add", "id": "candles", "spec": {
    "traces": [{"x": ["2024-01", "2024-02"], "open": [100, 105], "high": [110, 115],
                "low": [95, 100], "close": [105, 110], "type": "candlestick"}],
    "layout": {"title": "OHLC", "xaxis": {"rangeslider": {"visible": False}}},
}})
```
