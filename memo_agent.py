"""[버릴지도 ④] 📝 MCP 도구 갈래 — «우리 동네 분리배출 메모» (13주차 최종 제출 기준 «MCP 도구 1개 이상» · 권장)

    @버릴지도 메모 재활용은 목요일 저녁 7시 이후 · 1층 분리수거장   → add_memo
    @버릴지도 메모 보여줘                                            → show_memos
    @버릴지도 메모 2번 지워줘                                        → delete_memo

  흐름 — 질문 1건 = LangSmith trace 1건 (recycle-memo)

    «메모 …» ─▶ ① MCP 서버 띄우기   mcp_server.py 를 자식 프로세스로 (stdio · langchain.mcp.MCPAdapter — 13주차 기준 코드와 같음)
             ─▶ ② 도구 고르기      gemma4:e4b.bind_tools(도구 3개) — 어떤 도구를 어떤 인자로 부를지 모델이 정한다
             ─▶ ③ 도구 실행        MCP 서버로 호출 → 결과 글
             ─▶ ④ 결과 알리기      도구 없는 체인(같은 gemma4:e4b)이 결과만 한두 문장으로 (목록 보기는 결과 그대로 — 모델이 목록을 빼먹어서)

  ★ 왜 «메모» 로 시작하는 질문만 이 갈래로 오나 (앞말로 가르기)
    13주차 기준 코드는 LLM 이 «학칙 / 도구 / 도움말 / 일반» 을 분류합니다. 이 봇은 지금의 «검색» · «비교» 처럼 앞말로만 가릅니다
    → 분리배출 질문이 도구 쪽으로 잘못 가는 일이 없고, RAG 경로(30문항 29/30)는 한 줄도 바뀌지 않습니다.
  ★ 도구 모델 = 생성 모델(gemma4:e4b) 그대로 — `ollama show gemma4:e4b` 에 tools ✅.
    기준 코드는 gemma3:4b 가 도구 호출을 못 해(400) llama3.2:3b 를 따로 올렸지만, 이 봇은 모델을 더 올리지 않습니다(VRAM 7.6 ~ 7.7GB 그대로).
  ★ 소형 모델 안전장치 (기준 코드 README «소형 모델 안전장치» 의 실측을 따름)
    - 도구 왕복은 1번 (MAX_TOOL_ROUNDS) — 결과를 받고도 도구를 계속 부르는 일을 처음부터 막는다
    - 질문에 «지워 · 삭제 …» 가 없는데 delete_memo 를 고르면 실행하지 않는다 — 기준 코드에서 «아무도 안 시킨 delete_note» 가 실제로 나왔음
    - 기준 코드의 «승인(interrupt)» 은 넣지 않았다 (선택 기능 · 지우기는 위 말 검사로 대신)
    - 메모 내용이 바뀌지 않게 슬랙에 쓴 원문 그대로 넘긴다 (이어 묻기 풀어 쓰기를 거치지 않음)

실행 (이 폴더에서):
    python memo_agent.py "메모 재활용은 목요일 저녁 7시 이후"
    python memo_agent.py "메모 보여줘"
"""

import config  # noqa: F401  ★ 맨 위 — load_dotenv + LangSmith 프로젝트 지정
from config import HERE, MODEL, TAG  # noqa: E402

import asyncio  # noqa: E402
import os  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
import warnings  # noqa: E402
from pathlib import Path  # noqa: E402

from langchain_core.messages import HumanMessage, SystemMessage  # noqa: E402
from langchain_core.output_parsers import StrOutputParser  # noqa: E402
from langchain_core.prompts import ChatPromptTemplate  # noqa: E402
from langchain_core.runnables import RunnableLambda  # noqa: E402

warnings.filterwarnings("ignore", message=r".*langchain\.mcp.* is in beta")
from fastmcp.client.transports import PythonStdioTransport  # noqa: E402
from langchain.mcp import MCPAdapter  # noqa: E402

import rag_backend  # noqa: E402  ← 같은 생성 모델(get_llm)을 쓴다

MCP_SERVER = HERE / "mcp_server.py"
MEMO_FILE = Path(os.getenv("RECYCLE_MEMO_FILE") or HERE / "memo.json")
MEMO_WORDS = ("메모", "memo")
MAX_TOOL_ROUNDS = 1                     # 도구 왕복 상한 — 한 번 고르고, 실행하고, 알린다
MAX_CALLS = 2                           # 한 번에 부를 수 있는 도구 수 상한
DELETE_WORDS = ("지워", "지우", "삭제", "없애", "빼 줘", "빼줘")

TOOL_SYSTEM = (
    "너는 분리배출 안내 봇의 메모 도구를 쓰는 조수다. 메모에는 사용자가 확인한 우리 동네의 배출 요일 · 시간 · 장소 · 수수료 같은 정보를 남긴다.\n"
    "도구 고르는 기준:\n"
    "- 메모를 보여 달라 · 목록 · 뭐 있어 · 언제였지 → show_memos\n"
    "- 메모를 남겨 달라 · 저장 · 적어 둬, 또는 '메모' 뒤에 남길 내용이 있으면 → add_memo (text 에는 '메모' 뒤의 내용을 고치지 말고 그대로)\n"
    "- N번 메모를 지워 달라 · 삭제 → delete_memo (memo_id 에는 번호)\n"
    "도구는 한 번만 고른다. 같은 도구를 같은 인자로 두 번 부르지 마라."
)
TOOL_ANSWER_PROMPT = ChatPromptTemplate.from_template(
    "사용자 요청: {q}\n도구 실행 결과:\n{r}\n\n"
    "위 결과를 사용자에게 한국어 한두 문장으로 알려라. 메모 목록이면 번호와 내용을 그대로 보여 줘라. 결과에 없는 내용은 덧붙이지 마라."
)
NO_TOOL_TEXT = ("메모 도구를 고르지 못했어요 — `메모 <남길 내용>` · `메모 보여줘` · `메모 2번 지워줘` 처럼 물어봐 주세요.")


def is_memo(text: str) -> bool:
    """«메모» 로 시작하는 질문인가 (슬랙 · 터미널 대화 모드가 갈래를 나눌 때)."""
    first = (text or "").strip().split(" ", 1)[0].lower()
    return first in MEMO_WORDS


def transport() -> PythonStdioTransport:
    """MCP 서버를 같은 파이썬(venv)으로 띄운다. 메모 파일 위치는 환경 변수로 넘긴다 (자식 프로세스는 부모의 환경을 다 받지 않는다)."""
    env = {"RECYCLE_MEMO_FILE": str(MEMO_FILE), "PYTHONUTF8": "1"}
    return PythonStdioTransport(MCP_SERVER, env=env, cwd=str(HERE), python_cmd=sys.executable)


def _tool_text(content) -> str:
    """MCP 도구 결과는 [{'type': 'text', 'text': …}] 모양일 때가 있다 → 글만."""
    if isinstance(content, list):
        return " ".join(p.get("text", "") if isinstance(p, dict) else str(p) for p in content).strip()
    return str(content).strip()


def make_llm():
    """질문마다 새 모델 객체 — 캐시한 rag_backend.get_llm() 은 첫 이벤트 루프에 묶여 두 번째 질문부터 «Event loop is closed» (함정 31)."""
    return rag_backend.new_llm()


def blocked(call: dict, text: str) -> str | None:
    """실행하지 않을 도구 호출이면 그 이유 (안전장치)."""
    if call["name"] == "delete_memo" and not any(w in text for w in DELETE_WORDS):
        return "지우라는 말이 없어 실행하지 않았습니다."
    return None


async def _memo(inputs: dict, config) -> dict:
    """⚠️ 인자 이름이 꼭 config 여야 RunnableLambda 가 실행 설정(같은 trace)을 넘겨준다 — 이 안에서는 config 모듈을 쓰지 않는다 (함정 26)."""
    text = inputs["text"]
    async with MCPAdapter(transport()) as adapter:                                             # ①
        tools = await adapter.list_tools()
        by_name = {t.name: t for t in tools}
        llm = make_llm()
        picker = llm.bind_tools(tools)
        ai = await picker.ainvoke([SystemMessage(TOOL_SYSTEM), HumanMessage(text)],
                                  config={**config, "run_name": "pick-tool"})                  # ②
        calls = []
        for call in (ai.tool_calls or [])[:MAX_CALLS]:                                         # ③ 왕복 1번
            reason = blocked(call, text)
            if reason is None and call["name"] not in by_name:
                reason = f"모르는 도구 {call['name']!r} 라 실행하지 않았습니다."
            if reason is None:
                msg = await by_name[call["name"]].ainvoke(call, config=config)
                result = _tool_text(getattr(msg, "content", msg))
            else:
                result = reason
            calls.append({"name": call["name"], "args": dict(call.get("args") or {}), "result": result,
                          "ran": reason is None})
    if not calls:
        return {"answer": NO_TOOL_TEXT, "calls": [], "tools": sorted(by_name)}
    if all(c["name"] == "show_memos" and c["ran"] for c in calls):
        # 목록 보기는 결과를 그대로 — 결과를 알리는 모델에게 맡겼더니 «메모 목록입니다.» 로만 답하고 목록을 빼먹음 (2026-11-27 실측)
        return {"answer": "📋 저장된 메모\n" + calls[-1]["result"], "calls": calls, "tools": sorted(by_name)}
    results = "\n".join(f"- {c['name']}: {c['result']}" for c in calls)
    chain = (TOOL_ANSWER_PROMPT | llm | StrOutputParser()).with_config(run_name="tool-answer")
    answer = (await chain.ainvoke({"q": text, "r": results}, config=config)).strip()                # ④
    return {"answer": answer or results, "calls": calls, "tools": sorted(by_name)}


memo_run = RunnableLambda(_memo, name="recycle-memo")


def ask_memo(text: str, meta: dict | None = None, tags: list[str] | None = None) -> dict:
    """«메모 …» 질문 하나 → {answer, calls[{name, args, result, ran}], tools, sec}. 슬랙 · 터미널이 함께 쓴다."""
    text = " ".join((text or "").split())
    if not is_memo(text):
        text = "메모 " + text
    start = time.perf_counter()
    out = asyncio.run(memo_run.ainvoke(
        {"text": text},
        config={"run_name": "recycle-memo", "tags": [TAG, "mcp", *(tags or [])],
                "metadata": {"model": MODEL, "mcp_server": MCP_SERVER.name, **(meta or {})}},
    ))
    return {**out, "sec": time.perf_counter() - start}


def list_tools() -> list[str]:
    """봇 시작 때 확인용 — MCP 서버를 띄워 도구 이름만 받아 온다 (모델 호출 없음)."""
    async def _names():
        async with MCPAdapter(transport()) as adapter:
            return sorted(t.name for t in await adapter.list_tools())
    return asyncio.run(_names())


def call_line(call: dict) -> str:
    """«add_memo(text='…') → 1번 메모를 저장했습니다» — 슬랙 · 터미널에 도구 호출을 보여 줄 한 줄."""
    args = ", ".join(f"{k}={v!r}" for k, v in call["args"].items())
    mark = "" if call["ran"] else " (실행 안 함)"
    return f"{call['name']}({args}){mark} → {call['result']}"


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    text = " ".join(sys.argv[1:]) or "메모 보여줘"
    print(f"MCP 서버 : {MCP_SERVER.name}  · 메모 파일 {MEMO_FILE}  · 도구 고르는 모델 {MODEL}")
    out = ask_memo(text, {"source": "terminal"})
    print(f"질문     : {text}")
    print(f"도구     : {', '.join(out['tools'])}")
    for c in out["calls"]:
        print(f"🔧 호출  : {call_line(c)}")
    print(f"답       : {out['answer']}  ({out['sec']:.1f}초)")
    rag_backend.flush_traces()


if __name__ == "__main__":
    main()
