from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

clients: List[WebSocket] = []


def _blank_state() -> Dict[str, Any]:
    return {
        "n1": None,         # subject picks any 4-digit number (1000–9999)
        "n2": None,         # subject picks 4-digit number (1000–8999)
        "n3": None,         # auto: 9999 - n2  (system response)
        "n4": None,         # subject picks 4-digit number (1000–8999)
        "n5": None,         # auto: 9999 - n4  (system response)
        "prediction": None, # auto: n1 + 19998
        "total": None,      # auto: n1+n2+n3+n4+n5 (equals prediction)
        "reveal": False,
    }


state: Dict[str, Any] = _blank_state()


def _parse_int(value: Any, lo: int, hi: int) -> Optional[int]:
    try:
        n = int(value)
    except (TypeError, ValueError):
        return None
    return n if lo <= n <= hi else None


def _recalculate() -> None:
    n1, n2, n4 = state["n1"], state["n2"], state["n4"]
    state["prediction"] = (n1 + 19998) if n1 is not None else None
    state["n3"] = (9999 - n2) if n2 is not None else None
    state["n5"] = (9999 - n4) if n4 is not None else None
    n3, n5 = state["n3"], state["n5"]
    if all(v is not None for v in [n1, n2, n3, n4, n5]):
        state["total"] = n1 + n2 + n3 + n4 + n5
    else:
        state["total"] = None


async def broadcast_state() -> None:
    payload = json.dumps(state)
    dead: List[WebSocket] = []
    for ws in clients:
        try:
            await ws.send_text(payload)
        except Exception:
            dead.append(ws)
    for ws in dead:
        if ws in clients:
            clients.remove(ws)


@app.get("/")
async def display_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("display.html", {"request": request})


@app.get("/control")
async def control_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("control.html", {"request": request})


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await websocket.accept()
    clients.append(websocket)
    await websocket.send_text(json.dumps(state))

    try:
        while True:
            message = await websocket.receive_text()
            data = json.loads(message)
            action = data.get("action")

            if action == "set_n1":
                n1 = _parse_int(data.get("value"), 1000, 9999)
                if n1 is not None:
                    state.update(_blank_state())
                    state["n1"] = n1
                    _recalculate()

            elif action == "set_n2":
                if state["n1"] is not None:
                    n2 = _parse_int(data.get("value"), 1000, 8999)
                    if n2 is not None:
                        state["n2"] = n2
                        state["n4"] = None
                        state["n5"] = None
                        state["total"] = None
                        _recalculate()

            elif action == "set_n4":
                if state["n2"] is not None:
                    n4 = _parse_int(data.get("value"), 1000, 8999)
                    if n4 is not None:
                        state["n4"] = n4
                        _recalculate()

            elif action == "reveal":
                if state["total"] is not None:
                    state["reveal"] = True

            elif action == "hide":
                state["reveal"] = False

            elif action == "clear":
                state.update(_blank_state())

            await broadcast_state()

    except WebSocketDisconnect:
        if websocket in clients:
            clients.remove(websocket)
