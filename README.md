# discli

터미널에서 `discli` 한 방으로 실행되는 디스코드 REPL. 색깔 없음.

**경고**: user token 사용은 디스코드 ToS 위반. 자기 책임.

## 설치 (pipx)

```bash
brew install pipx
pipx ensurepath              # 최초 1회, PATH 잡아줌 → 새 터미널 열기
pipx install /Users/zerith/Documents/GitHub/javareal/discord-cli
```

## 실행

어디서든:

```bash
discli
```

첫 실행 시 토큰을 물어봅니다. 붙여넣기(입력은 표시 안 됨) → `~/.discord_cli_token` 에 자동 저장 → 다음부터는 바로 로그인.

## 명령어

```
:g              서버 목록
:c <n>          서버 n의 채널 목록
:dm             DM 목록
:o <n>          채널 n 열기 (실시간 수신 시작)
:r              현재 채널 다시 로드
:h              도움말
:q              종료
```

명령어 아닌 텍스트 = 현재 채널로 전송.

## 업데이트

코드 고친 뒤:

```bash
pipx reinstall discli
```

## 삭제

```bash
pipx uninstall discli
rm ~/.discord_cli_token
```
