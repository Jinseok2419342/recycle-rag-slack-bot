"""[버릴지도 ③] ★★ 슬랙에서 묻고, 분리배출 문서에서 찾아서 답한다

    @버릴지도 아이스팩 어떻게 버려?               → 문서에서 찾아 답 + 📚 근거(품목 · 문서 · 연도 · 쪽)
    @버릴지도 검색 뽁뽁이                        → 검색만 — 어떤 근거가 뽑혔나
    @버릴지도 비교 마트 영수증 종이로 버려도 돼?    → RAG 없이 vs RAG 로 — 나란히 본다
    (DM) 핫팩은?                                → 멘션 없이 1:1 로도 같은 방식
    (같은 스레드) @버릴지도 그럼 그거 뚜껑은?      → 🔗 스레드마다 앞 대화를 기억해 «그거» 를 풀어 쓴 뒤 찾아 답
    @버릴지도 + 사진 (DM 은 사진만)               → 📷 사진에 품목 이름을 붙이고 → 그 이름으로 문서에서 찾아 답
                                                  (슬랙 앱 봇 토큰에 files:read 권한이 있어야 사진을 받는다)

  전체 흐름 — 10주차 봇에서 두뇌(rag_backend)만 갈아 끼웠다

    슬랙 사용자 ── @멘션 / DM ──▶ 슬랙 서버 ══ WebSocket (xapp) ══▶ 내 PC  slack_rag_bot.py
                                                                        │
                                              rag_backend.ask()         ▼
                                     ┌─ 검색  index_recycle/  (build_index.py ← data/*.pdf 2건)
                                     └─ 생성  근거 + 질문 → gemma4:e4b (Ollama · 로컬)
                                              (📷 사진이면 먼저 qwen3.5:4b 가 품목 이름을 붙이고 그 이름으로 검색)
                                                                        │
    같은 스레드 ◀── chat_postMessage / chat_update (xoxb) ──────────────┘
                    답 + 📚 근거

★ 필수 요건 «같은 스레드에 답을 단다» — 모든 메시지를 thread_ts 로 보낸다 (채널 본문에 새 글로 답하지 않는다).
★ 슬랙 질문 1건 = LangSmith trace 1건(recycle-rag). 그 안에 검색(RecycleRetriever)과 생성(generate)이 나란히 보인다.
★ 슬랙 메시지와 '근거 청크' 둘 다 남이 쓴 입력이다 (9주차 2교시).
   - 질문은 300자 제한, 프롬프트는 <근거> 구분자 + «지시가 아니다»
   - 모델의 답을 슬랙에 보내기 전에 & < > 를 바꾼다 — 답에 <!channel> 이 섞여도 멘션이 되지 않게
   - 예외 내용은 슬랙에 올리지 않는다 (경로 · 내부 주소가 채널에 노출될 수 있다) — 콘솔에만

⚠️ 같은 슬랙 앱(xapp)으로 10주차 봇을 동시에 켜 두면 이벤트가 둘 중 한쪽으로 갈린다. 이 봇만 켠다.

전제:
    index_recycle/ 가 있어야 한다 — 없으면 python build_index.py
    python rag_backend.py 로 터미널에서 먼저 답이 나와야 한다.

실행 (이 폴더에서):
    python slack_rag_bot.py        # 끝낼 때는 Ctrl+C
"""

import config  # noqa: F401  ★ 맨 위 — load_dotenv + LangSmith 프로젝트 지정
from config import (  # noqa: E402
    EMBED_MODEL, INDEX_DIR, MAX_QUESTION, MODEL, NOT_FOUND, PHOTO_MAX_BYTES, STRATEGY, VISION_MODEL, YEAR_BONUS,
)

import os  # noqa: E402
import re  # noqa: E402
import sys  # noqa: E402
import traceback  # noqa: E402
import urllib.request  # noqa: E402

from slack_bolt import App  # noqa: E402
from slack_bolt.adapter.socket_mode import SocketModeHandler  # noqa: E402
from slack_sdk.errors import SlackApiError  # noqa: E402

# ★ 두뇌 — 봇(입구 · 출구)과 RAG 가 나뉘어 있어서 이 줄만 바꾸면 다른 두뇌가 된다
from rag_backend import (  # noqa: E402
    HISTORY_TURNS, PhotoError, ask_full, ask_photo, ask_plain, is_not_found, mixed_years, other_names,
    read_manifest, search, source_of, warmup,
)
from collections import OrderedDict  # noqa: E402
from threading import Lock  # noqa: E402

SEARCH_WORDS = ("검색", "search")
COMPARE_WORDS = ("비교", "vs")
MODEL_SHORT = config.short_model()
PHOTO_MODELS = MODEL_SHORT if VISION_MODEL == MODEL else f"{config.short_model(VISION_MODEL)} → {MODEL_SHORT}"

USAGE = (
    "분리배출 방법을 물어봐 주세요 ♻️\n"
    "• `@버릴지도 아이스팩 어떻게 버려?` — 문서에서 찾아 답하고 📚 근거를 붙입니다\n"
    "• `@버릴지도 검색 뽁뽁이` — 어떤 근거가 뽑혔는지만 보여 줍니다\n"
    "• `@버릴지도 비교 마트 영수증 종이로 버려도 돼?` — 문서 없이 답한 것과 나란히\n"
    "• 📷 이름을 모르면 사진을 올리며 `@버릴지도` — 사진 속 물건 이름으로 문서에서 찾아 답합니다\n"
    "• 🔗 같은 스레드에서는 `@버릴지도 그럼 그거 뚜껑은?` 처럼 이어서 물어도 앞 대화로 알아듣습니다\n"
    "• DM 으로는 멘션 없이 `핫팩은?` 처럼 바로 묻거나 사진만 보내도 됩니다"
)
HOLDER = "⏳ 분리배출 문서에서 찾는 중…"
PHOTO_HOLDER = "📷 사진을 보고 문서에서 찾는 중…"
PHOTO_UNKNOWN = ("📷 사진에서 버릴 물건을 알아보지 못했어요 — 물건 이름으로 물어봐 주세요. "
                 "(예: `@버릴지도 아이스팩 어떻게 버려?`)")
NOT_FOUND_TEXT = (f"{NOT_FOUND} — 지역별 배출 요일 · 수수료처럼 지자체마다 다른 내용은 "
                  "거주지 구청(주민센터)에 확인하세요.")
MIXED_NOTE = ("ℹ️ 2018 가이드라인과 2026 사례집이 함께 근거로 쓰였습니다 — "
              "내용이 다르면 최신인 사례집(2026)을 따르세요.")
FAIL_TEXT = "⚠️ 답을 만들지 못했습니다. 잠시 뒤 다시 물어봐 주세요."


# ── 0. 스레드마다 기억 — 같은 스레드의 «그럼 · 그거» 를 앞 대화로 풀어 답한다 ★ ────────
#   키 = «채널-스레드ts» (13주차 기준 코드 slack_bot 의 thread_id 와 같은 모양).
#   기억은 이 프로그램 안에만 둔다 — 봇을 껐다 켜면 사라진다(기준 코드의 InMemorySaver 와 같음). 슬랙 권한을 더 받지 않는다.
#   질문은 풀어 쓴 질문으로 적어 둔다 — 다음 이어 묻기가 «그거» 의 «그거» 를 다시 풀 필요가 없게.
MAX_THREADS = 500                       # 오래된 스레드부터 잊는다 (메모리가 끝없이 늘지 않게)
_memory: "OrderedDict[str, list[tuple[str, str]]]" = OrderedDict()
_memory_lock = Lock()


def thread_key(channel: str, thread: str) -> str:
    return f"{channel}-{thread}"


def history_of(key: str) -> list[tuple[str, str]]:
    with _memory_lock:
        return list(_memory.get(key, []))


def remember(key: str, question: str, answer: str) -> None:
    with _memory_lock:
        turns = _memory.pop(key, [])
        _memory[key] = (turns + [(question, answer)])[-HISTORY_TURNS:]
        while len(_memory) > MAX_THREADS:
            _memory.popitem(last=False)


def follow_line(asked: str, understood: str) -> str:
    """이어 묻기로 질문을 풀어 썼으면 무엇으로 알아들었는지 한 줄 — 틀렸으면 사용자가 바로 알 수 있게."""
    return f"🔗 앞 대화로 *«{escape(understood)}»* 로 이해했어요\n" if understood != asked else ""


# ── 1. 메시지 → (모드, 질문) ─────────────────────────────────────
def parse(text: str) -> tuple[str, str]:
    text = re.sub(r"<@[A-Z0-9]+>\s*", "", text or "").strip()      # 앞의 <@U07ABCDEF> 를 떼어 낸다
    first, _, rest = text.partition(" ")
    if first.lower() in SEARCH_WORDS:
        return "search", rest.strip()
    if first.lower() in COMPARE_WORDS:
        return "compare", rest.strip()
    return "rag", text


def escape(text: str) -> str:
    """슬랙 제어 문자를 바꾼다 — 모델 답 · 문서 조각에 <!channel> · <@U…> 가 섞여도 멘션이 되지 않게."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def to_mrkdwn(answer: str) -> str:
    """먼저 escape, 그다음 굵게 표기 변환 (LLM 은 **굵게**, 슬랙은 *굵게*)."""
    return escape(answer.strip()).replace("**", "*")


def sources_block(docs) -> str:
    """📚 근거 — metadata 가 여기서 쓰인다 ★  (같은 출처가 겹치면 한 번만)"""
    seen = list(dict.fromkeys(escape(source_of(d)) for d in docs))
    return "📚 *근거*  " + "  /  ".join(seen)


def tail(mode: str, sec: float) -> str:
    return f"_— {mode} · {MODEL_SHORT} · {sec:.1f}초_"


def rag_text(ans: str, docs, sec: float, compare: bool) -> str:
    head = "📖 *RAG 로* (문서에서 찾아서)\n" if compare else ""
    if is_not_found(ans):
        # 관련 없는 근거를 보여 주면 오해를 산다 — 근거를 숨기고 갈 곳을 알려 준다
        return f"{head}{NOT_FOUND_TEXT}\n{tail('rag', sec)}"
    note = f"\n{MIXED_NOTE}" if mixed_years(docs) else ""
    return f"{head}{to_mrkdwn(ans)}\n\n{sources_block(docs)}{note}\n{tail('rag', sec)}"


def search_text(question: str, meta: dict) -> str:
    hits = search(question, config={"run_name": "recycle-search", "tags": [config.TAG, "search", STRATEGY],
                                    "metadata": meta})
    lines = [f"🔎 *검색 결과* — 거리(작을수록 가깝다) · {STRATEGY} · year_bonus {YEAR_BONUS}"]
    for i, doc in enumerate(hits, 1):
        m = doc.metadata
        preview = escape(doc.page_content[:80].replace("\n", " "))
        via = f"\n> ↳ 검색 질문: {escape(m['via'])}" if m["via"] != question else ""
        lines.append(f"{i}. `{m['distance']:.3f}` *{escape(source_of(doc))}*\n> {preview}…{via}")
    return "\n".join(lines)


def log_fail(where: str, e: Exception) -> None:
    """원인은 콘솔에만 — 슬랙에는 일반 문구만 올린다."""
    print(f"  실패 → {where} {type(e).__name__}: {e}")
    traceback.print_exc()


# ── 1-2. 사진 ─────────────────────────────────────────────────────
def first_image(event: dict) -> dict | None:
    """메시지에 붙은 파일 중 첫 사진 하나 (여러 장이면 첫 장만 본다)."""
    return next((f for f in event.get("files") or [] if str(f.get("mimetype", "")).startswith("image/")), None)


def download(file: dict, client) -> bytes:
    """슬랙 사진을 봇 토큰으로 받는다 — 봇 토큰에 files:read 권한이 있어야 한다. 새 패키지 없이 표준 라이브러리로."""
    url = file.get("url_private_download") or file.get("url_private")
    if not url and file.get("id"):          # 이벤트에 주소가 안 실려 올 때가 있다 (file_access: check_file_info)
        file = client.files_info(file=file["id"])["file"]
        url = file.get("url_private_download") or file.get("url_private")
    if not url:
        raise RuntimeError("사진 주소(url_private)가 이벤트에 없습니다")
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {client.token}"})
    with urllib.request.urlopen(req, timeout=30) as r:
        ctype = r.headers.get("Content-Type", "")
        data = r.read(PHOTO_MAX_BYTES + 1)
    if ctype.startswith("text/html"):       # 권한이 없으면 사진 대신 슬랙 로그인 화면(HTML)이 온다
        raise RuntimeError("사진 대신 HTML 이 왔습니다 — 봇 토큰 scope 에 files:read 가 있는지, Reinstall 했는지 확인")
    if len(data) > PHOTO_MAX_BYTES:
        raise PhotoError(f"사진은 {PHOTO_MAX_BYTES // 2**20}MB 이하로 부탁드립니다")
    return data


def photo_text(out: dict) -> str:
    """📷 무엇으로 봤는지 → 답 + 📚 근거 + 다른 후보 / 애매하면 후보만 / 못 알아보면 이름으로 물어 달라고."""
    tail_ = f"_— photo · {PHOTO_MODELS} · {out['sec']:.1f}초_"
    if out["decision"] == "unknown":
        return f"{PHOTO_UNKNOWN}\n{tail_}"
    label = escape(out["label"])
    names = [escape(n) for n in other_names(out["docs"])]
    if out["decision"] == "ask":
        choices = "\n".join(f"{i}) {n}" for i, n in enumerate(names, 1))
        return (f"📷 사진에서 «{label}» 으로 봤는데, 문서의 어느 품목인지 확신이 없어요. 이 중 무엇인가요?\n{choices}\n"
                f"→ 물건 이름으로 다시 물어 주세요\n{tail_}")
    seen = f"📷 사진에서 *«{label}»* 으로 봤어요 — 틀리면 이름으로 다시 물어 주세요"
    if is_not_found(out["answer"]):
        return f"{seen}\n{NOT_FOUND_TEXT}\n{tail_}"
    note = f"\n{MIXED_NOTE}" if mixed_years(out["docs"]) else ""
    others = f"\n🔁 다른 후보: {' · '.join(names[1:])}" if len(names) > 1 else ""
    return f"{seen}\n\n{to_mrkdwn(out['answer'])}\n\n{sources_block(out['docs'])}{note}{others}\n{tail_}"


# ── 2. 답하기 — 자리부터 잡고, 답이 오면 고친다 ───────────────────
def answer(event: dict, client) -> None:
    channel = event["channel"]
    thread = event.get("thread_ts") or event["ts"]          # ★ 같은 스레드에 — 스레드 안이면 그 스레드, 아니면 그 메시지 아래
    user = event.get("user", "")
    mode, question = parse(event.get("text", ""))
    image = first_image(event)
    print(f"받음 ← user={user} {'photo' if image else mode} {question!r}")

    def post(text: str):
        return client.chat_postMessage(channel=channel, thread_ts=thread, text=text)

    meta = {"slack_user": user, "slack_channel": channel, "source": "slack"}
    key = thread_key(channel, thread)

    # ── 사진 — 같이 쓴 글은 힌트로 (검색 · 비교 모드는 글 질문에서만) ──
    if image:
        hint = re.sub(r"<@[A-Z0-9]+>\s*", "", event.get("text") or "").strip()
        if len(hint) > MAX_QUESTION:
            post(f"✋ 사진과 같이 쓰는 글은 {MAX_QUESTION}자 이내로 부탁드립니다. (지금 {len(hint)}자)")
            return
        if (image.get("size") or 0) > PHOTO_MAX_BYTES:
            post(f"✋ 사진은 {PHOTO_MAX_BYTES // 2**20}MB 이하로 부탁드립니다.")
            return
        holder = post(PHOTO_HOLDER)
        try:
            out = ask_photo(download(image, client), hint, meta)
            text = photo_text(out)
            if out["decision"] == "answer":          # 사진 다음의 «그럼 그거 뚜껑은?» 도 풀 수 있게
                remember(key, f"사진 속 물건 «{out['label']}» 은 어떻게 버려요?", out["answer"].strip())
            print(f"  답함 → {out['sec']:.1f}초  이름 «{out['label']}» · {out['decision']} · "
                  f"근거 chunk_id={[d.metadata.get('chunk_id') for d in out['docs']]}")
        except PhotoError as e:
            text = f"✋ {e}"
        except Exception as e:
            log_fail("photo", e)
            text = FAIL_TEXT
        client.chat_update(channel=channel, ts=holder["ts"], text=text)
        return

    if not question:
        post(USAGE)
        return
    if len(question) > MAX_QUESTION:
        post(f"✋ 질문은 {MAX_QUESTION}자 이내로 부탁드립니다. (지금 {len(question)}자)")
        return

    # ── 검색만 ──
    if mode == "search":
        try:
            text = search_text(question, meta)
        except Exception as e:
            log_fail("search", e)
            text = FAIL_TEXT
        post(text)
        return

    # ── 비교 — 먼저 RAG 없이 ──
    if mode == "compare":
        holder = post(f"⏳ [RAG 없이] {MODEL_SHORT} 가 생각 중입니다…")
        try:
            ans, sec = ask_plain(question, meta)
            text = f"🙈 *RAG 없이* (모델 기억만)\n{to_mrkdwn(ans)}\n\n{tail('no-rag', sec)}"
        except Exception as e:
            log_fail("no-rag", e)
            text = FAIL_TEXT
        client.chat_update(channel=channel, ts=holder["ts"], text=text)

    # ── RAG — ① 자리 잡기 → ② 찾아서 답하기 → ③ 자리를 답으로 ★ ──
    holder = post(HOLDER)
    try:
        out = ask_full(question, meta, history=history_of(key))     # ★ 같은 스레드의 앞 대화를 함께
        ans, docs, sec = out["answer"], out["docs"], out["sec"]
        text = follow_line(question, out["question"]) + rag_text(ans, docs, sec, compare=(mode == "compare"))
        remember(key, out["question"], ans.strip())
        if out["question"] != question:
            print(f"  이어 묻기 → {out['question']!r}")
        print(f"  답함 → {sec:.1f}초  근거 chunk_id={[d.metadata.get('chunk_id') for d in docs]}")
    except Exception as e:
        log_fail("rag", e)
        text = FAIL_TEXT
    client.chat_update(channel=channel, ts=holder["ts"], text=text)


def build_app(bot_token: str) -> App:
    app = App(token=bot_token)

    @app.event("app_mention")
    def on_mention(event, client):
        answer(event, client)

    @app.event("message")
    def on_dm(event, client):
        # 봇에게 1:1 DM 으로 물을 때 — message.im 이벤트를 구독해야 온다
        # subtype(수정 · 삭제 알림)과 봇이 쓴 메시지는 무시한다 — 자기 답에 다시 답하지 않게
        # 단 file_share(사진을 올린 메시지)는 받는다 — 📷 사진으로 묻기
        if (event.get("channel_type") == "im" and event.get("subtype") in (None, "file_share")
                and not event.get("bot_id")):
            answer(event, client)

    return app


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    bot_token = os.environ.get("SLACK_BOT_TOKEN", "")
    app_token = os.environ.get("SLACK_APP_TOKEN", "")
    if not bot_token.startswith("xoxb-"):
        raise SystemExit("SLACK_BOT_TOKEN 은 xoxb- 로 시작해야 합니다. (루트 .env)")
    if not app_token.startswith("xapp-"):
        raise SystemExit("SLACK_APP_TOKEN 은 xapp- 로 시작해야 합니다. (루트 .env)")

    tracing = os.environ.get("LANGSMITH_TRACING", "").lower() == "true"
    manifest = read_manifest()
    print("=" * 60)
    print(f"인덱스    : {INDEX_DIR}  ({manifest.get('chunks', '?')}청크 · {manifest.get('mode', '?')})")
    print(f"임베딩    : {EMBED_MODEL}")
    print(f"생성 모델 : {MODEL}")
    print(f"사진 모델 : {VISION_MODEL}" + ("  (생성 모델과 같음 — 한 모델)" if VISION_MODEL == MODEL else "")
          + f"  · 이름 붙이기 {config.PHOTO_MODE}")
    print(f"검색      : {STRATEGY} · year_bonus {YEAR_BONUS}")
    print(f"LangSmith : {os.environ['LANGSMITH_PROJECT']}  (추적 {'켜짐 ✅' if tracing else '꺼짐'})")
    if not tracing:
        print("ℹ️ LANGSMITH_TRACING 이 true 가 아닙니다 — 추적을 보려면 루트 .env 에 LANGSMITH_TRACING=true (11-25 부터 요건 아님 · 선택).")

    # ★ 켜기 전에 두 모델을 올린다 — 첫 답 20초(모델 로딩)를 여기서 미리 치르고, 설정도 확인된다
    print("모델 올리는 중… (처음엔 20초쯤)")
    try:
        sec = warmup()
    except SystemExit:
        raise                                              # 인덱스 없음 · 임베딩 모델 불일치 — 안내 문구 그대로
    except Exception as e:
        raise SystemExit(
            f"워밍업 실패 — {type(e).__name__}: {e}\n"
            "  점검 순서:  ① ollama serve 가 떠 있나  ② ollama list 에 두 모델이 있나 (없으면 ollama pull)\n"
            "              ③ python rag_backend.py 검색 \"뽁뽁이\" 가 되나"
        )
    print(f"워밍업 ✅ {sec:.1f}초")

    app = build_app(bot_token)
    print("슬랙에서 @버릴지도 질문 / 검색 질문 / 비교 질문 / 📷 사진.  끝낼 때는 Ctrl+C")
    print("=" * 60)
    try:
        SocketModeHandler(app, app_token).start()
    except SlackApiError as e:
        raise SystemExit(f"앱 토큰으로 연결하지 못했습니다: {e.response['error']}  → .env 의 SLACK_APP_TOKEN · 슬랙 앱 Socket Mode 설정부터 확인 (README 5-2 ⑤)")


if __name__ == "__main__":
    main()
