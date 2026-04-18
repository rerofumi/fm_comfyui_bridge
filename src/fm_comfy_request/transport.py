from __future__ import annotations

import asyncio
import json
from typing import Any, Callable

import httpx
import websockets

from .models import ProgressEvent


class Transport:
    def __init__(self, server_url: str, timeout: float = 120.0):
        self.server_url = server_url if server_url.endswith("/") else server_url + "/"
        self.timeout = timeout

    def free(self) -> dict[str, Any]:
        response = httpx.post(
            f"{self.server_url}free",
            json={"unload_models": True, "free_memory": True},
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()

    def list_models(self, folder: str) -> list[Any]:
        response = httpx.get(f"{self.server_url}models/{folder}", timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    def upload_image(self, upload_name: str, image_bytes: bytes) -> dict[str, Any]:
        files = {"image": (upload_name, image_bytes, "image/png"), "overwrite": "true"}
        response = httpx.post(f"{self.server_url}upload/image", files=files, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    def submit_prompt(self, workflow: dict[str, Any], client_id: str) -> str:
        response = httpx.post(
            f"{self.server_url}prompt",
            json={"prompt": workflow, "client_id": client_id},
            timeout=self.timeout,
        )
        response.raise_for_status()
        payload = response.json()
        return str(payload["prompt_id"])

    def history(self, prompt_id: str) -> dict[str, Any]:
        response = httpx.get(f"{self.server_url}history/{prompt_id}", timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    def view(self, subfolder: str, filename: str) -> bytes:
        response = httpx.get(
            f"{self.server_url}view",
            params={"subfolder": subfolder, "filename": filename},
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.content

    async def awatch(
        self,
        client_id: str,
        prompt_id: str,
        callback: Callable[[ProgressEvent], Any] | None = None,
        timeout: float | None = None,
    ) -> None:
        base = self.server_url.replace("http://", "ws://").replace("https://", "wss://")
        async with websockets.connect(f"{base}ws?clientId={client_id}", open_timeout=timeout or self.timeout) as ws:
            while True:
                message = await asyncio.wait_for(ws.recv(), timeout=timeout or self.timeout)
                data = json.loads(message)
                payload = data.get("data") if isinstance(data.get("data"), dict) else {}
                event_prompt_id = payload.get("prompt_id") or data.get("prompt_id")
                if event_prompt_id not in (None, prompt_id):
                    continue
                event = ProgressEvent(
                    prompt_id=prompt_id,
                    event_type=str(data.get("type", "message")),
                    node_id=data.get("node") or payload.get("node"),
                    value=data.get("value") or payload.get("value"),
                    max_value=data.get("max") or payload.get("max"),
                    message=data.get("message"),
                    raw_event=data,
                )
                if callback is not None:
                    result = callback(event)
                    if asyncio.iscoroutine(result):
                        await result
                if data.get("type") == "executing" and payload.get("node") is None:
                    return

    def watch(
        self,
        client_id: str,
        prompt_id: str,
        callback: Callable[[ProgressEvent], Any] | None = None,
        timeout: float | None = None,
    ) -> None:
        asyncio.run(self.awatch(client_id, prompt_id, callback=callback, timeout=timeout))
