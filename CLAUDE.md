# Canvas

Browser-based visualization workbook for Claude Code sessions. Serves a Plotly-powered canvas page over HTTP+WebSocket. CC pushes widgets (charts, tables, metrics, text) via `POST /cmd`; the browser updates in real-time.

## Requirements

- `uv` — Python package manager ([install](https://docs.astral.sh/uv/getting-started/installation/))
- A browser

## Install

```bash
./install.sh
```

This copies the skill and command files into `~/.claude/` and prints a one-liner to add to `~/.claude/CLAUDE.md`.

## Usage

After installing, type `/canvas:startup` in any CC session to start the server and open the browser tab.

## How it works

- `server.py` — aiohttp HTTP+WebSocket server, random port, auto-opens browser
- `www/index.html` — Plotly canvas page with dark theme and `window.canvas` API
- Port and PID written to `/tmp/canvas-{CLAUDE_CODE_SESSION_ID}.{port,pid}`
- Server auto-opens a browser tab on startup
- Killed automatically when the CC session ends
