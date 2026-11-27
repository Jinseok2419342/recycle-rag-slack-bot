"""[버릴지도 ④] MCP 서버 — «우리 동네 분리배출 메모» 도구 세 개 (FastMCP)

   13주차 기준 코드(slack_bot/mcp_server.py)와 같은 모양입니다.  @mcp.tool 을 붙이면 MCP 도구가 됩니다.

       도구           하는 일                                   봇 쪽 안전장치 (memo_agent.py)
       show_memos     저장된 메모 보기 (읽기)                    —
       add_memo       메모 하나 저장 (쓰기)                      —
       delete_memo    번호로 메모 하나 지우기 (되돌릴 수 없음)     질문에 «지워 · 삭제 …» 가 없으면 실행하지 않음

   ★ 왜 이 도구인가 — 분리배출 문서(RAG)에는 «우리 동네 배출 요일 · 시간 · 장소 · 수수료» 가 없습니다(지자체마다 다름).
     봇은 그런 질문에 «자료에서 찾지 못했습니다 — 구청에 확인하세요» 라고 답하고, 사용자가 확인한 내용을
     이 도구로 남겨 두었다가 다시 볼 수 있게 합니다. 문서에 있는 것은 RAG, 문서 밖의 «우리 동네» 것은 도구.

   메모는 저장소 맨 위의 memo.json 에 저장됩니다 (.gitignore · 없으면 처음 쓸 때 만들어짐).
   다른 곳에 두려면 환경 변수 RECYCLE_MEMO_FILE (tests/offline_check.py 가 임시 폴더로 바꿀 때 씀).

  ⚠️ 이 파일은 직접 실행하지 않습니다. memo_agent.py 가 자식 프로세스로 띄우고, 끝나면 종료합니다.
  ⚠️ 이 파일에서는 print() 를 쓰지 않습니다 — stdio 전송은 표준출력이 곧 통신 통로입니다 (9주차).
"""

import json
import os
from datetime import datetime
from pathlib import Path

from fastmcp import FastMCP

MEMO_FILE = Path(os.getenv("RECYCLE_MEMO_FILE") or Path(__file__).with_name("memo.json"))
MAX_TEXT = 200          # 메모 한 건 글자 수 상한 (슬랙 질문 300자 제한보다 작게)

mcp = FastMCP("recycle-memo")


def _load() -> list[dict]:
    if not MEMO_FILE.exists():
        return []
    return json.loads(MEMO_FILE.read_text(encoding="utf-8"))


def _save(memos: list[dict]) -> None:
    MEMO_FILE.parent.mkdir(parents=True, exist_ok=True)
    MEMO_FILE.write_text(json.dumps(memos, ensure_ascii=False, indent=2), encoding="utf-8")


@mcp.tool
def show_memos() -> str:
    """저장된 우리 동네 분리배출 메모(배출 요일 · 시간 · 장소 · 수수료 등)를 번호와 함께 모두 보여 준다."""
    memos = _load()
    if not memos:
        return "저장된 메모가 없습니다."
    return "\n".join(f"{m['id']}. {m['text']}  ({m['at']})" for m in memos)


@mcp.tool
def add_memo(text: str) -> str:
    """우리 동네 분리배출 메모 하나를 저장한다. text 는 사용자가 남기려는 내용 그대로다."""
    text = " ".join(str(text).split())[:MAX_TEXT]
    if not text:
        return "저장할 내용이 비어 있어 저장하지 않았습니다."
    memos = _load()
    new_id = max((m["id"] for m in memos), default=0) + 1
    memos.append({"id": new_id, "text": text, "at": datetime.now().strftime("%m-%d %H:%M")})
    _save(memos)
    return f"{new_id}번 메모를 저장했습니다: {text}"


@mcp.tool
def delete_memo(memo_id: int) -> str:
    """번호(memo_id)로 메모 하나를 지운다. 되돌릴 수 없다."""
    memos = _load()
    left = [m for m in memos if m["id"] != int(memo_id)]
    if len(left) == len(memos):
        return f"{memo_id}번 메모가 없습니다."
    _save(left)
    return f"{memo_id}번 메모를 지웠습니다."


if __name__ == "__main__":
    mcp.run(show_banner=False)
