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
```bash
NOW=$(date "+%A, %B %-d %Y  %H:%M")
curl -s -X POST "http://127.0.0.1:${CANVAS_PORT}/cmd" \
  -H 'Content-Type: application/json' \
  -d "{\"cmd\":\"text\",\"id\":\"_session\",\"title\":\"Session\",\"markdown\":\"**Started:** ${NOW}\"}"
```

Tell the user: "Canvas is live at `http://127.0.0.1:PORT`" — they may need to switch to that tab.

---

## Helper (use in bash commands)

```bash
CANVAS_PORT=$(cat /tmp/canvas-${CLAUDE_CODE_SESSION_ID}.port)
cx() { curl -s -X POST "http://127.0.0.1:${CANVAS_PORT}/cmd" -H 'Content-Type: application/json' -d "$1"; }
```

---

## API — POST /cmd

All calls are JSON POSTs. The `cmd` field selects the method.

### `add` / `update` — Plotly chart
```json
{
  "cmd": "add",
  "id": "my-chart",
  "spec": {
    "traces": [
      { "x": [...], "y": [...], "name": "Series A", "type": "scatter", "mode": "lines+markers" }
    ],
    "layout": {
      "title": "Chart Title",
      "yaxis": { "title": "Y label" }
    },
    "height": 360
  }
}
```
`update` replaces an existing chart in place. Dark theme applied automatically — do not set `paper_bgcolor`/`plot_bgcolor`.

### `stream` — append live data point
```json
{ "cmd": "stream", "id": "price-chart", "traceIndex": 0, "point": { "x": "14:32:05", "y": 54.44 } }
```

### `metric` — KPI card row
```json
{
  "cmd": "metric",
  "id": "kpis",
  "items": [
    { "label": "Portfolio", "value": "$283,841", "delta": "+$8,320", "trend": "up", "sub": "since inception" },
    { "label": "Cash",      "value": "$25,835",                                     "sub": "buying power" }
  ]
}
```
Key is `items`. `trend`: `"up"` | `"down"` | omit. `delta` and `sub` optional.

### `text` — markdown block
```json
{ "cmd": "text", "id": "analysis", "title": "Analysis", "markdown": "## Summary\n\n**Key finding** here." }
```
Key is `markdown`. Supports headers, bold, italic, inline code, fenced blocks, lists, hr.

### `table` — sortable data table
```json
{
  "cmd": "table",
  "id": "positions",
  "spec": {
    "title": "Positions",
    "columns": ["Symbol", "Value", "Gain %"],
    "rows": [["AAPL", "$12,400", "+42.0%"], ["MSFT", "$8,200", "-3.1%"]]
  }
}
```
Click-sortable. `+`/`▲` cells green, `-`/`▼` cells red.

### `section` — full-width divider
```json
{ "cmd": "section", "id": "s1", "label": "Portfolio Overview" }
```

### `remove` / `clear`
```json
{ "cmd": "remove", "id": "my-chart" }
{ "cmd": "clear" }
```

---

## Layout

Responsive 2-column grid. `section` and `metric` span full width. State persists to `localStorage`.

---

## Common Plotly patterns

**Time series:**
```bash
cx '{"cmd":"add","id":"perf","spec":{"traces":[{"x":["2024-01","2024-02"],"y":[0,5.2],"name":"A","type":"scatter","mode":"lines"}],"layout":{"title":"Performance","yaxis":{"title":"% Return"}}}}'
```

**Bar with color gradient:**
```bash
cx '{"cmd":"add","id":"gains","spec":{"traces":[{"x":["A","B","C"],"y":[42,-8,15],"type":"bar","marker":{"color":[42,-8,15],"colorscale":[[0,"#f87171"],[0.5,"#ffb74d"],[1,"#81c784"]],"cmin":-30,"cmax":50}}],"layout":{"title":"Returns"}}}'
```

**Donut:**
```bash
cx '{"cmd":"add","id":"alloc","spec":{"traces":[{"labels":["A","B","C"],"values":[60,25,15],"type":"pie","hole":0.55,"textinfo":"label+percent","textposition":"outside"}],"layout":{"title":"Allocation"}}}'
```

**Candlestick:**
```bash
cx '{"cmd":"add","id":"candles","spec":{"traces":[{"x":["2024-01","2024-02"],"open":[100,105],"high":[110,115],"low":[95,100],"close":[105,110],"type":"candlestick"}],"layout":{"title":"OHLC","xaxis":{"rangeslider":{"visible":false}}}}}'
```
