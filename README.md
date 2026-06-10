# claude-canvas

A browser-based visualization workbook for [Claude Code](https://claude.ai/code) sessions. Runs a local HTTP+WebSocket server; Claude pushes widgets via `POST /cmd` and the browser updates in real-time.

![dark theme canvas with charts, metrics, and tables](.github/preview.png)

## What it does

- **Charts** — any Plotly chart type (line, bar, scatter, candlestick, pie, etc.)
- **Metric cards** — KPI row with value, delta, and trend indicator
- **Tables** — sortable data tables with positive/negative cell coloring
- **Text** — markdown blocks (headers, bold, code, lists)
- **Sections** — full-width dividers to organize the canvas
- **Live streaming** — append data points to an existing chart in real-time

State persists to `localStorage` so widgets survive page refresh. Dark theme applied automatically — no styling required.

## Requirements

- [uv](https://docs.astral.sh/uv/getting-started/installation/) — Python package manager
- A browser
- Claude Code

## Install

```bash
git clone https://github.com/DrBenedictPorkins/claude-canvas
cd claude-canvas
./install.sh
```

Then add the following to `~/.claude/CLAUDE.md`:

```
## Canvas — Browser Visualization
Use `/canvas` skill to render charts, tables, metrics, and analysis text in the browser.
The canvas server lives at `~/path/to/claude-canvas/` — invoke the skill for startup instructions, API details, and Plotly patterns.
```

## Usage

In any Claude Code session, invoke the startup skill:

```
/canvas:startup
```

This checks if the server is running, starts it if not, opens a browser tab, and posts a session header. From there, Claude can push widgets via `curl` to `POST /cmd`.

## API

All calls are JSON POSTs to `http://127.0.0.1:{PORT}/cmd`.

### Chart (Plotly)

```json
{
  "cmd": "add",
  "id": "my-chart",
  "spec": {
    "traces": [
      { "x": ["Jan", "Feb", "Mar"], "y": [10, 25, 18], "type": "scatter", "mode": "lines+markers", "name": "Revenue" }
    ],
    "layout": { "title": "Monthly Revenue", "yaxis": { "title": "$K" } },
    "height": 360
  }
}
```

Use `"cmd": "update"` to replace an existing chart in place. Dark theme is applied automatically — do not set `paper_bgcolor` or `plot_bgcolor`.

### Live streaming

```json
{ "cmd": "stream", "id": "my-chart", "traceIndex": 0, "point": { "x": "14:32:05", "y": 54.44 } }
```

### Metric cards

```json
{
  "cmd": "metric",
  "id": "kpis",
  "items": [
    { "label": "Revenue", "value": "$284K", "delta": "+12%", "trend": "up", "sub": "vs last month" },
    { "label": "Churn",   "value": "2.4%",  "delta": "-0.3%", "trend": "down" }
  ]
}
```

`trend`: `"up"` | `"down"` | omit. `delta` and `sub` are optional.

### Text (markdown)

```json
{ "cmd": "text", "id": "summary", "title": "Analysis", "markdown": "## Key Finding\n\n**Revenue is up** across all segments." }
```

### Table

```json
{
  "cmd": "table",
  "id": "positions",
  "spec": {
    "title": "Positions",
    "columns": ["Symbol", "Value", "Gain %"],
    "rows": [
      ["AAPL", "$12,400", "+42.0%"],
      ["MSFT", "$8,200",  "-3.1%"]
    ]
  }
}
```

Click any column header to sort. Cells starting with `+`/`▲` are green; `-`/`▼` are red.

### Section divider

```json
{ "cmd": "section", "id": "s1", "label": "Portfolio Overview" }
```

### Remove / clear

```json
{ "cmd": "remove", "id": "my-chart" }
{ "cmd": "clear" }
```

## How it works

- `server.py` — aiohttp HTTP+WebSocket server on a random port
- `www/index.html` — self-contained Plotly canvas page (no build step)
- Port and PID written to `/tmp/canvas-{SESSION_ID}.{port,pid}` — one server per CC session
- Browser auto-opened on startup; WebSocket reconnects automatically on disconnect
- Plotly vendored locally (`www/plotly.min.js`) — no CDN required

## License

MIT
