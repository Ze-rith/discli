import asyncio
from datetime import datetime

from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout

from .client import DiscordClient
from .config import load_token


def ts(iso: str) -> str:
    try:
        return datetime.fromisoformat(iso.replace("Z", "+00:00")).strftime("%H:%M")
    except Exception:
        return "--:--"


HELP = """\
명령어:
  :g              서버 목록 보기
  :c <번호>       해당 서버의 채널 목록 (번호는 :g 에서 나온 숫자)
  :dm             DM 목록 보기
  :o <번호>       채널 열기 (번호는 :c 또는 :dm 에서 나온 숫자)
  :r              현재 채널 다시 불러오기 (최근 50개)
  :h              도움말
  :q              종료
그 외 아무 텍스트나 입력하면 현재 열린 채널로 전송됩니다.
"""


class Repl:
    def __init__(self):
        self.client = DiscordClient(load_token())
        self.guilds: list[dict] = []
        self.channels: list[dict] = []
        self.current: dict | None = None
        self.session = PromptSession()

    async def run(self):
        await self.client.start()
        me = await self.client.get_me()
        print(f"connected as {me.get('username')}  (type :h for help)")
        self.client.on("MESSAGE_CREATE", self._on_msg)
        await self.client.connect_gateway()
        asyncio.create_task(self.client.run_gateway())

        with patch_stdout():
            while True:
                try:
                    line = await self.session.prompt_async("> ")
                except (EOFError, KeyboardInterrupt):
                    break
                if not line.strip():
                    continue
                try:
                    if not await self._handle(line):
                        break
                except Exception as e:
                    print(f"err: {e}")

        await self.client.close()

    async def _handle(self, line: str) -> bool:
        if not line.startswith(":"):
            if not self.current:
                print("no channel open. use :g then :c <n> then :o <n>")
                return True
            await self.client.send_message(self.current["id"], line)
            return True

        parts = line[1:].split()
        cmd = parts[0] if parts else ""
        args = parts[1:]

        if cmd in ("q", "quit", "exit"):
            return False
        if cmd in ("h", "help", "?"):
            print(HELP)
        elif cmd == "g":
            self.guilds = await self.client.get_guilds()
            for i, g in enumerate(self.guilds, 1):
                print(f"  {i:>3}  {g['name']}")
        elif cmd == "c":
            if not args or not args[0].isdigit():
                print("usage: :c <n>")
                return True
            i = int(args[0]) - 1
            if not (0 <= i < len(self.guilds)):
                print("out of range")
                return True
            g = self.guilds[i]
            chs = await self.client.get_channels(g["id"])
            chs = [c for c in chs if c.get("type") in (0, 5)]
            chs.sort(key=lambda c: (c.get("position", 0), c.get("name") or ""))
            self.channels = chs
            for j, c in enumerate(chs, 1):
                print(f"  {j:>3}  #{c.get('name')}")
        elif cmd == "dm":
            chs = await self.client.get_dm_channels()
            self.channels = chs
            for j, c in enumerate(chs, 1):
                if c.get("type") in (1, 3):
                    names = ", ".join(
                        r.get("username", "?") for r in c.get("recipients") or []
                    )
                    print(f"  {j:>3}  @{names}")
                else:
                    print(f"  {j:>3}  #{c.get('name')}")
        elif cmd == "o":
            if not args or not args[0].isdigit():
                print("usage: :o <n>")
                return True
            i = int(args[0]) - 1
            if not (0 <= i < len(self.channels)):
                print("out of range")
                return True
            self.current = self.channels[i]
            await self._reload()
        elif cmd == "r":
            if self.current:
                await self._reload()
        else:
            print(f"unknown: :{cmd}  (try :h)")
        return True

    async def _reload(self):
        msgs = await self.client.get_messages(self.current["id"], limit=50)
        for m in reversed(msgs):
            self._print_msg(m)

    def _print_msg(self, m: dict):
        author = (m.get("author") or {}).get("username", "?")
        content = m.get("content", "") or ""
        # replace newlines so it stays log-like
        content = content.replace("\n", " ⏎ ")
        print(f"{ts(m.get('timestamp',''))} {author}: {content}")

    async def _on_msg(self, data: dict):
        if self.current and data.get("channel_id") == self.current["id"]:
            self._print_msg(data)


def main():
    try:
        asyncio.run(Repl().run())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
