import getpass
import os
import stat
from pathlib import Path

TOKEN_FILE = Path.home() / ".discord_cli_token"


def clear_token() -> None:
    if TOKEN_FILE.exists():
        TOKEN_FILE.unlink()


def prompt_and_save() -> str:
    print("디스코드 토큰이 필요합니다. (README 참고)")
    print("(입력은 화면에 표시되지 않습니다)")
    while True:
        token = getpass.getpass("token: ").strip()
        if token:
            break
        print("빈 값입니다. 다시 입력하세요.")
    TOKEN_FILE.write_text(token)
    try:
        TOKEN_FILE.chmod(stat.S_IRUSR | stat.S_IWUSR)  # 0600
    except Exception:
        pass
    print(f"저장됨: {TOKEN_FILE}")
    return token


def load_token() -> str:
    token = os.environ.get("DISCORD_TOKEN")
    if token:
        return token.strip()
    if TOKEN_FILE.exists():
        val = TOKEN_FILE.read_text().strip()
        if val:
            return val
    return prompt_and_save()
