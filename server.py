# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "aiohttp>=3.9",
# ]
# ///

import asyncio
import json
import os
import signal
import socket
import webbrowser
from pathlib import Path

from aiohttp import web, WSMsgType

SESSION_ID = os.environ.get("CLAUDE_CODE_SESSION_ID", "default")
PORT_FILE = Path(f"/tmp/canvas-{SESSION_ID}.port")
PID_FILE = Path(f"/tmp/canvas-{SESSION_ID}.pid")

WWW_DIR = Path(__file__).parent / "www"

_clients: set[web.WebSocketResponse] = set()


async def handle_ws(request: web.Request) -> web.WebSocketResponse:
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    _clients.add(ws)
    try:
        async for msg in ws:
            if msg.type in (WSMsgType.CLOSE, WSMsgType.ERROR):
                break
    finally:
        _clients.discard(ws)
    return ws


async def handle_cmd(request: web.Request) -> web.Response:
    try:
        data = await request.json()
    except Exception:
        return web.Response(status=400, text="invalid JSON")

    payload = json.dumps(data)
    dead: set[web.WebSocketResponse] = set()
    for ws in list(_clients):
        try:
            await ws.send_str(payload)
        except Exception:
            dead.add(ws)
    _clients.difference_update(dead)

    return web.json_response({"ok": True, "clients": len(_clients)})


async def handle_static(request: web.Request) -> web.Response:
    rel = request.match_info.get("path", "index.html") or "index.html"
    target = (WWW_DIR / rel).resolve()
    try:
        target.relative_to(WWW_DIR.resolve())
    except ValueError:
        raise web.HTTPForbidden()
    if not target.exists():
        raise web.HTTPNotFound()
    return web.FileResponse(target)


def _pick_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _cleanup() -> None:
    PORT_FILE.unlink(missing_ok=True)
    PID_FILE.unlink(missing_ok=True)


async def main() -> None:
    os.setsid()
    port = _pick_port()

    PORT_FILE.write_text(str(port))
    PID_FILE.write_text(str(os.getpid()))

    app = web.Application()
    app.router.add_get("/ws", handle_ws)
    app.router.add_post("/cmd", handle_cmd)
    app.router.add_get("/", handle_static)
    app.router.add_get("/{path:.+}", handle_static)

    runner = web.AppRunner(app, access_log=None)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", port)
    await site.start()

    url = f"http://127.0.0.1:{port}"
    print(f"Canvas ready at {url}", flush=True)
    webbrowser.open(url)

    loop = asyncio.get_running_loop()
    stop = loop.create_future()

    def _handle_signal() -> None:
        _cleanup()
        if not stop.done():
            stop.set_result(None)

    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, _handle_signal)

    try:
        await stop
    finally:
        await runner.cleanup()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    finally:
        _cleanup()
