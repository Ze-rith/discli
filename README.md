# discli

터미널에서 `discli` 

## 설치 (pipx)

```bash
brew install pipx
pipx ensurepath              # 최초 1회, PATH 잡아줌 → 새 터미널 열기
pipx install discord-cli
```

## 실행

어디서든:

```bash
discli
```

첫 실행 시 토큰을 물어봅니다. 붙여넣기(입력은 표시 안 됨) → `~/.discord_cli_token` 에 자동 저장 → 다음부터는 바로 로그인. 토큰이 만료되면 자동으로 다시 물어봄.

## 토큰 얻는 법 (북마클릿)

브라우저 북마크바에 아무 페이지나 북마크 추가 → 편집 → **URL** 자리에 아래를 통째로 붙여넣기:

```
javascript:(()=>{const o=XMLHttpRequest.prototype.setRequestHeader;XMLHttpRequest.prototype.setRequestHeader=function(k,v){if(k.toLowerCase()==='authorization'&&v&&v.length>50){navigator.clipboard.writeText(v);alert('token copied: '+v.slice(0,15)+'...');XMLHttpRequest.prototype.setRequestHeader=o}return o.apply(this,arguments)}})();
```

이름은 아무거나 (예: `d`).

**사용**: discord.com 열어놓고 그 북마크 클릭 → 아무 채널 클릭 → `token copied` 알림 → 클립보드에 복사됨 → 터미널 `token:` 프롬프트에 `Cmd+V`.

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
