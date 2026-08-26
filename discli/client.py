import asyncio
import json
import sys
from typing import Any, Awaitable, Callable

import aiohttp

API_BASE = "https://discord.com/api/v10"
GATEWAY_URL = "wss://gateway.discord.gg/?v=10&encoding=json"

class DiscordClient:
    def __init__(self, token: str):
        self.token = token
        self.session: aiohttp.ClientSession | None = None
        self.ws: aiohttp.ClientWebSocketResponse | None = None
        self.user: dict | None = None
        self.seq: int | None = None
        self.session_id: str | None = None
        self._heartbeat_task: asyncio.Task | None = None
        self._listeners: dict[str, list[Callable[[dict], Awaitable[None]]]] = {}

    # ---------- REST ----------
    async def start(self):
        self.session = aiohttp.ClientSession(
            headers={
                "Authorization": self.token,
                "Content-Type": "application/json",
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "discord/1.0 Chrome/120.0.0.0 Electron/28.0.0 Safari/537.36"
                ),
            }
        )

    async def close(self):
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
        if self.ws and not self.ws.closed:
            await self.ws.close()
        if self.session and not self.session.closed:
            await self.session.close()

    async def _get(self, path: str) -> Any:
        async with self.session.get(f"{API_BASE}{path}") as r:
            r.raise_for_status()
            return await r.json()

    async def _post(self, path: str, payload: dict) -> Any:
        async with self.session.post(f"{API_BASE}{path}", json=payload) as r:
            r.raise_for_status()
            return await r.json()

    async def get_me(self) -> dict:
        return await self._get("/users/@me")

    async def get_guilds(self) -> list[dict]:
        return await self._get("/users/@me/guilds")

    async def get_channels(self, guild_id: str) -> list[dict]:
        return await self._get(f"/guilds/{guild_id}/channels")

    async def get_dm_channels(self) -> list[dict]:
        return await self._get("/users/@me/channels")

    async def get_messages(self, channel_id: str, limit: int = 50) -> list[dict]:
        return await self._get(f"/channels/{channel_id}/messages?limit={limit}")

    async def send_message(self, channel_id: str, content: str) -> dict:
        return await self._post(
            f"/channels/{channel_id}/messages", {"content": content}
        )

    # ---------- Gateway ----------
    def on(self, event: str, handler: Callable[[dict], Awaitable[None]]):
        self._listeners.setdefault(event, []).append(handler)

    async def _dispatch(self, event: str, data: dict):
        for h in self._listeners.get(event, []):
            try:
                await h(data)
            except Exception as e:
                print(f"listener error {event}: {e}", file=sys.stderr)

    async def connect_gateway(self):
        self.ws = await self.session.ws_connect(GATEWAY_URL)
        # HELLO
        hello = await self.ws.receive_json()
        interval = hello["d"]["heartbeat_interval"] / 1000

        # IDENTIFY (user token - browser-like properties)
        await self.ws.send_json({
            "op": 2,
            "d": {
                "token": self.token,
                "capabilities": 16381,
                "properties": {
                    "os": "Mac OS X",
                    "browser": "Chrome",
                    "device": "",
                    "system_locale": "en-US",
                    "browser_user_agent": (
                        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/120.0.0.0 Safari/537.36"
                    ),
                    "browser_version": "120.0.0.0",
                    "os_version": "10.15.7",
                    "referrer": "",
                    "referring_domain": "",
                    "release_channel": "stable",
                    "client_build_number": 260292,
                },
                "presence": {
                    "status": "online",
                    "since": 0,
                    "activities": [],
                    "afk": False,
                },
                "compress": False,
            },
        })

        self._heartbeat_task = asyncio.create_task(self._heartbeat(interval))

    async def _heartbeat(self, interval: float):
        try:
            while not self.ws.closed:
                await asyncio.sleep(interval)
                await self.ws.send_json({"op": 1, "d": self.seq})
        except asyncio.CancelledError:
            pass

    async def run_gateway(self):
        async for msg in self.ws:
            if msg.type != aiohttp.WSMsgType.TEXT:
                continue
            payload = json.loads(msg.data)
            op = payload.get("op")
            if op == 0:  # DISPATCH
                self.seq = payload.get("s")
                event = payload.get("t")
                data = payload.get("d") or {}
                if event == "READY":
                    self.user = data.get("user")
                    self.session_id = data.get("session_id")
                await self._dispatch(event, data)
            elif op == 11:  # HEARTBEAT ACK
                pass
            elif op == 7:  # RECONNECT
                break
            elif op == 9:  # INVALID SESSION
                break
