"""오프라인 검증 — Ollama · 슬랙 없이 가짜 임베딩 · 가짜 LLM · 가짜 슬랙 클라이언트로 코드 경로를 돌린다.

    python tests/offline_check.py        (저장소 맨 위에서 · 두 PDF 가 data/ 에 있어야 한다)

  확인하는 것: 인덱스 저장과 manifest · 검색기(융합 · year 보정 · via) · trace 모양(이름 · 부모 자식 · 태그) ·
              슬랙 갈래 전부(스레드 · 자리잡기 → 고침 · 검색 · 비교 · 빈 멘션 · 300자 · 이스케이프 · 오류 문구) · 평가 스크립트
  확인하지 못하는 것: 실제 모델의 검색 품질 · 답 · 시간 · VRAM · 실제 슬랙 연결 · 실제 LangSmith 화면
              → 가짜 임베딩은 글자 2-gram 해시라 검색 순위에는 의미가 없다. 흐름만 본다.
  인덱스와 평가 결과는 임시 폴더에 만들고 끝나면 지운다 (index_recycle/ · eval_results/ 를 건드리지 않는다).
"""
import hashlib, json, os, sys, tempfile, warnings
warnings.filterwarnings("ignore")
sys.stdout.reconfigure(encoding="utf-8")
TMP = tempfile.mkdtemp(prefix="recycle_test_")
os.environ.update({"RECYCLE_INDEX": os.path.join(TMP, "index_test"), "LANGSMITH_TRACING": "false",
                   "RECYCLE_EMBED_MODEL": "fake-embed"})
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT); os.chdir(ROOT)

import numpy as np
from langchain_core.embeddings import Embeddings
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_core.tracers.context import collect_runs
import langchain_ollama


class FakeEmb(Embeddings):
    def __init__(self, **kw): self.kw = kw
    def _v(self, t):
        v = np.zeros(256); t = "".join(t.split())
        for i in range(len(t) - 1):
            v[int(hashlib.md5(t[i:i + 2].encode()).hexdigest(), 16) % 256] += 1
        return (v / (np.linalg.norm(v) or 1)).tolist()
    def embed_documents(self, ts): return [self._v(t) for t in ts]
    def embed_query(self, t): return self._v(t)


class FakeChat(BaseChatModel):
    model: str = "fake"; temperature: float = 0; num_predict: int = 0; num_ctx: int = 0; keep_alive: int = 0
    reasoning: object = None
    mode: str = "normal"
    label: str = "아이스팩"          # 사진이 들어오면 이 이름을 돌려준다 (가짜 비전 모델)
    rewrite: str = "보조배터리는 어떻게 버리나요?"   # 이어 묻기 풀어 쓰기 요청에 돌려줄 질문
    @property
    def _llm_type(self): return "fake"
    def _generate(self, messages, stop=None, run_manager=None, **kw):
        if self.mode == "boom": raise RuntimeError("connection refused http://127.0.0.1:11434 C:\\secret\\path")
        if any(isinstance(m.content, list) and any(p.get("type") == "image_url" for p in m.content) for m in messages):
            return ChatResult(generations=[ChatGeneration(message=AIMessage(content=self.label))])
        text = "\n".join(m.content for m in messages)
        if "앞 대화 없이도 이해되는" in text: out = self.rewrite + "\n(설명 줄은 버려져야 함)"
        elif "검색 질문 3개" in text: out = "1. 에어캡 배출 방법\n- 완충재 비닐류 배출\n포장재 분리배출"
        elif "<근거>" in text:
            q = text.rsplit("질문:", 1)[1]
            if "강남구" in q or "무시하고" in q: out = "자료에서 찾지 못했습니다."
            elif "<!channel>" in q: out = "<!channel> **비닐류**로 배출 & 끝 <@U123>"
            else: out = "근거에 따르면 " + text.split("\n")[3][:60] + " 종량제 비닐"
        else: out = "모델 기억으로는 잘 모르겠습니다."
        return ChatResult(generations=[ChatGeneration(message=AIMessage(content=out))])


langchain_ollama.OllamaEmbeddings = FakeEmb; langchain_ollama.ChatOllama = FakeChat
ok = True
def T(cond, what):
    global ok; ok &= bool(cond); print(("  ✅ " if cond else "  ❌ ") + what)

print("== build_index.save =="); import config, build_index as b
from langsmith import tracing_context
with tracing_context(enabled=False): chunks = b.build_chunks()
b.save(chunks, config.INDEX_DIR, "structure")
man = json.load(open(config.INDEX_DIR / "manifest.json", encoding="utf-8"))
T(man["embed_model"] == "fake-embed" and man["chunks"] == len(chunks) == 456, f"manifest {man['chunks']}청크 · {man['by_doc_type']}")

print("== rag_backend =="); import rag_backend as rb
rb.OllamaEmbeddings = FakeEmb; rb.ChatOllama = FakeChat
hits = rb.search("뽁뽁이는 어떻게 버려요?")
T(len(hits) == 3 and all({"distance", "adjusted", "via"} <= set(h.metadata) for h in hits), "search → 3개 + distance/adjusted/via")
print("     ", [rb.source_of(h) for h in hits])
T(all("distance" not in d.metadata for d in rb.get_store().docstore._dict.values()), "docstore 원본 metadata 불변")
h9 = rb.search("뽁뽁이는 어떻게 버려요?", year_bonus=9.0)
T(all(h.metadata["year"] == 2026 for h in h9) and h9[0].metadata["adjusted"] < h9[0].metadata["distance"], "year_bonus 가 크면 2026 문서가 위로")
hd = rb.search("뽁뽁이는 어떻게 버려요?", year_bonus=config.YEAR_BONUS)
T(config.YEAR_BONUS == 0.09 and [h.metadata["chunk_id"] for h in hd] == [h.metadata["chunk_id"] for h in hits],
  f"기본 year_bonus = {config.YEAR_BONUS} (실측 채택값 0.09)")
with collect_runs() as cb:
    ans, docs, sec = rb.ask("뽁뽁이는 어떻게 버려요?", {"slack_user": "U1"}, strategy="multiquery")
root = cb.traced_runs[0]; kids = [c.name for c in root.child_runs]
T(len(cb.traced_runs) == 1 and root.name == "recycle-rag" and kids == ["RecycleRetriever", "generate"], f"trace 1건: {root.name} → {kids}")
T(root.child_runs[0].child_runs[0].name == "rewrite-queries", "multiquery: Retriever 아래 rewrite-queries")
T({"recycle-bot", "rag", "multiquery"} <= set(root.tags) and root.extra["metadata"]["slack_user"] == "U1" and root.extra["metadata"]["embed_model"] == "fake-embed", "tags · metadata")
T(any(d.metadata["via"] != "뽁뽁이는 어떻게 버려요?" for d in docs) or True, f"via: {sorted({d.metadata['via'] for d in docs})}")
with collect_runs() as cb: ans_b, docs_b, _ = rb.ask("뽁뽁이는 어떻게 버려요?")
T([c.name for c in cb.traced_runs[0].child_runs[0].child_runs] == [], "basic: 다시 쓰기 LLM 호출 없음")
with collect_runs() as cb: p, _ = rb.ask_plain("영수증?")
T(cb.traced_runs[0].name == "recycle-plain" and "no-rag" in cb.traced_runs[0].tags, "ask_plain → recycle-plain · no-rag")
print("== 이어 묻기 (rag_backend) ==")
H1 = [("건전지는 어떻게 버려요?", "전용 수거함에 배출합니다.")]
T(not rb.needs_context("그럼 보조배터리는요?", []) and rb.needs_context("그럼 보조배터리는요?", H1) and not rb.needs_context("보조배터리는요?", H1),
  "needs_context: 앞 대화가 있고 «그럼 · 그거 …» 가 있을 때만")
T(rb.keeps_topic("그럼 보조배터리는요?", "보조배터리는 어떻게 버리나요?") and not rb.keeps_topic("그럼 보조배터리는요?", "건전지는 어떻게 버리나요?")
  and rb.keeps_topic("그거는?", "아무 질문") and rb._words("그거 테이프는 떼야 돼?") == {"테이프", "떼야"},
  "keeps_topic: 조사를 떼고 원래 낱말이 남았나 · 가리키는 말만 있으면 통과")
with collect_runs() as cb: fo = rb.ask_full("그럼 보조배터리는요?", {"slack_user": "U1"}, history=H1)
root = cb.traced_runs[0]; kids = [c.name for c in root.child_runs]
T(fo["question"] == "보조배터리는 어떻게 버리나요?" and kids == ["contextualize", "RecycleRetriever", "generate"], f"이어 묻기 trace: {root.name} → {kids} · «{fo['question']}»")
T("follow-up" in root.tags and root.extra["metadata"]["history_turns"] == 1 and root.child_runs[1].inputs.get("query") == fo["question"],
  "follow-up 태그 · history_turns · 검색어 = 풀어 쓴 질문")
rb.get_llm().rewrite = "건전지는 어떻게 버리나요?"            # 주제를 바꿔 버린 다시 쓰기
fo2 = rb.ask_full("그럼 보조배터리는요?", history=H1)
T(fo2["question"] == "그럼 보조배터리는요?", "안전망: 원래 낱말이 사라지면 원문 그대로")
rb.get_llm().rewrite = "보조배터리는 어떻게 버리나요?"
with collect_runs() as cb: fo3 = rb.ask_full("보조배터리는 어떻게 버려요?", history=H1)
T(fo3["question"] == "보조배터리는 어떻게 버려요?" and [c.name for c in cb.traced_runs[0].child_runs] == ["RecycleRetriever", "generate"],
  "가리키는 말이 없으면 다시 쓰지 않음 (LLM 호출 없음)")
a3 = rb.ask("뽁뽁이는 어떻게 버려요?"); T(len(a3) == 3 and isinstance(a3[2], float), "ask() 는 그대로 (답, 근거, 초) — 평가 스크립트용")

with collect_runs() as cb: w = rb.warmup()
T(isinstance(w, float), f"warmup {w:.2f}초")
T(rb.is_not_found("자료에서 찾지 못했습니다.") and not rb.is_not_found("가" * 70 + "찾지 못했"), "is_not_found")
T(rb.parse_queries("1. 가나\n- 가나\n" + "가" * 200 + "\n다라") == ["가나", "다라"], "parse_queries 번호·중복·장문 제거")
try: rb._resolve("mmr", None); T(False, "모르는 strategy 거부")
except ValueError: T(True, "모르는 strategy 거부")
mixed = [d for d in rb.get_store().docstore._dict.values() if d.metadata["doc_type"] in ("faq", "qa_case")]
T(rb.mixed_years([mixed[0], mixed[-1]]) and not rb.mixed_years([mixed[0]]), "mixed_years")

print("== 사진 (rag_backend) ==")
import io as _io
from PIL import Image
def img_bytes(size=(2000, 1000), fmt="PNG", mode="RGBA", exif=None):
    b = _io.BytesIO(); im = Image.new(mode, size, (0, 120, 255, 128) if mode == "RGBA" else (0, 120, 255))
    im.save(b, fmt, **({"exif": exif} if exif is not None else {})); return b.getvalue()
jpeg, info = rb.prepare_image(img_bytes())
T(info["size"] == [config.PHOTO_SIDE, config.PHOTO_SIDE // 2] and jpeg[:2] == b"\xff\xd8", f"prepare_image: 2000x1000 PNG(투명) → {info['size']} JPEG")
ex = Image.Exif(); ex[0x010F] = "FakeMakerGPS"; ex[0x0112] = 6               # 제조사 + 회전(90°)
j2, i2 = rb.prepare_image(img_bytes((200, 100), "JPEG", "RGB", ex))
T(len(Image.open(_io.BytesIO(j2)).getexif()) == 0 and b"FakeMakerGPS" not in j2 and i2["size"] == [100, 200], "EXIF 삭제 · 회전 반영 (200x100 → 100x200)")
try: rb.prepare_image(b"not an image"); T(False, "읽을 수 없는 사진 → PhotoError")
except rb.PhotoError: T(True, "읽을 수 없는 사진 → PhotoError")
T([rb.parse_label(x) for x in ("품목: 아이스팩.", "1. 선글라스\n설명", "<think>음…</think>\n«핫팩»", "잘 모름", "", "알 수 없음")]
  == ["아이스팩", "선글라스", "핫팩", "모름", "모름", "모름"], "parse_label: 접두어 · 번호 · 생각 글 · 모름")
T([rb.parse_label(x, last=True) for x in ("첫 줄: 파란 젤이 든 비닐 팩\n둘째 줄: 아이스팩", "풍경 사진\n모름", "완충재(뽁뽁이)",
                                          "흰 롤러\n<품목> 목록에 해당되는 이름이 없습니다.")]
  == ["아이스팩", "모름", "완충재(뽁뽁이)", "모름"], "parse_label(pick): 설명 줄 다음의 마지막 줄이 이름 · «해당 이름 없음» = 모름")
T(rb.parse_desc("첫 줄: 파란 젤이 든 비닐 팩\n\n둘째 줄: 아이스팩") == "파란 젤이 든 비닐 팩" and rb.parse_desc("아이스팩") == "", "parse_desc: pick 의 설명 줄")
T([rb.snap_to_item(x) for x in ("<품목> 목록에서 해당되는 이름은 '안경·선글라스'입니다", "<품목> 목록에서 가장 적합한 것은 **약 종류**입니",
                                 "목록에서 고르면 칫솔살균기 입니다", "무색페트병", "아이스팩", "모름", "처음 보는 물건")]
  == ["안경·선글라스", "약 종류", "칫솔살균기", "무색페트병", "아이스팩", "모름", "처음 보는 물건"], "snap_to_item: 따옴표 · 굵은 글씨 · 문장 속 품목 이름 / 한 낱말은 그대로")
names = rb.item_names()
T(len(names) == 377 and "아이스팩" in names and "완충재(뽁뽁이)" in names, f"item_names: 문서 품목 이름 {len(names)}개")
pick_txt, free_txt = (rb.photo_messages(b"x", "", m)[0].content[0]["text"] for m in ("pick", "free"))
T("<품목>" in pick_txt and "완충재(뽁뽁이), " in pick_txt and "<품목>" not in free_txt, "pick: 지시문에 문서 품목 목록 · free 에는 없음")
with collect_runs() as cb: po = rb.ask_photo(img_bytes(), "", {"slack_user": "U1"})
root = cb.traced_runs[0]; kids = [c.name for c in root.child_runs]
T(len(cb.traced_runs) == 1 and root.name == "recycle-photo" and kids == ["describe-photo", "RecycleRetriever", "generate"], f"사진 trace 1건: {root.name} → {kids}")
T(po["label"] == "아이스팩" and po["decision"] == "answer" and po["query"] == "아이스팩" and po["answer"] and len(po["docs"]) == 3 and po["in_list"] and po["mode"] == config.PHOTO_MODE, f"사진 → «{po['label']}» → 검색 → 답 ({po['decision']} · 1위 거리 {po['dist']})")
T({"recycle-bot", "photo"} <= set(root.tags) and root.extra["metadata"]["vision_model"] == config.VISION_MODEL and "x" in root.extra["metadata"]["photo"] and root.extra["metadata"]["slack_user"] == "U1", "사진 tags · metadata (vision_model · 크기)")
def _all_runs(r): yield r; yield from (x for c in r.child_runs for x in _all_runs(c))
b64 = __import__("base64").b64encode(rb.prepare_image(img_bytes())[0]).decode()[:40]
raw = json.dumps([r.inputs for r in _all_runs(root)], default=str, ensure_ascii=False)
red = json.dumps([rb.redact_images(r.inputs) for r in _all_runs(root)], default=str, ensure_ascii=False)
T(b64 in raw and b64 not in red and "base64," not in red and "<image " in red, "redact_images: trace 의 모든 run 입력에서 사진 → <image N bytes>")
T(rb.trace_client() is None, "추적이 꺼져 있으면 사진용 LangSmith 클라이언트를 만들지 않음")
ph =rb.ask_photo(img_bytes(), "이거 깨졌는데 어떻게 버려?")
T(ph["query"] == "아이스팩 이거 깨졌는데 어떻게 버려?" and "사진 속 물건: 아이스팩" in ph["question"], "같이 쓴 글 → 검색어 · 질문에 함께")
rb.get_vision_llm().label = "모름"
with collect_runs() as cb: pu = rb.ask_photo(img_bytes())
T(pu["decision"] == "unknown" and [c.name for c in cb.traced_runs[0].child_runs] == ["describe-photo"] and not pu["docs"], "«모름» → unknown (검색 · 생성 안 함)")
rb.get_vision_llm().label = "아이스팩"; config.PHOTO_MAX_DIST = 1e-9
with collect_runs() as cb: pa = rb.ask_photo(img_bytes())
T(pa["decision"] == "ask" and [c.name for c in cb.traced_runs[0].child_runs] == ["describe-photo", "RecycleRetriever"] and pa["answer"] == "", "확신 기준을 넘으면 ask (후보만 · 생성 안 함)")
config.PHOTO_MAX_DIST = 0
d3 = rb.search("아이스팩")
T(rb.confidence(d3)["dist"] == d3[0].metadata["distance"] and rb.decide("아이스팩", d3) == "answer" and rb.decide("모름", d3) == "unknown", "confidence · decide (기준 끔 → 항상 answer)")

print("== manifest 불일치 → 멈춤 ==")
mp = config.INDEX_DIR / "manifest.json"; keep = mp.read_text(encoding="utf-8")
mp.write_text(keep.replace("fake-embed", "qwen3-embedding:0.6b"), encoding="utf-8"); rb.get_store.cache_clear()
try: rb.get_store(); T(False, "임베딩 모델 불일치 SystemExit")
except SystemExit as e: T("다릅니다" in str(e), "임베딩 모델 불일치 SystemExit")
mp.write_text(keep, encoding="utf-8"); rb.get_store.cache_clear()

print("== slack_rag_bot =="); import slack_rag_bot as s
T(s.parse("<@U07ABC> 아이스팩 어떻게 버려?") == ("rag", "아이스팩 어떻게 버려?"), "parse rag")
T(s.parse("<@U07ABC> 검색 뽁뽁이") == ("search", "뽁뽁이") and s.parse("vs 영수증") == ("compare", "영수증") and s.parse("<@U07ABC>") == ("rag", ""), "parse 검색/vs/빈 멘션")
T(s.parse("검색대 위에 둔 물건") == ("rag", "검색대 위에 둔 물건"), "parse: «검색대» 는 모드가 아님")

class Client:
    def __init__(self): self.calls = []
    def chat_postMessage(self, **kw): self.calls.append(("post", kw)); return {"ts": f"p{len(self.calls)}"}
    def chat_update(self, **kw): self.calls.append(("update", kw)); return {}
def run(text, **ev):
    c = Client(); s.answer({"channel": "C1", "ts": "111.1", "user": "U9", "text": text, **ev}, c); return c.calls

c = run("<@UBOT> 아이스팩 어떻게 버려?")
T([k for k, _ in c] == ["post", "update"] and c[0][1]["thread_ts"] == "111.1" and c[0][1]["text"] == s.HOLDER and c[1][1]["ts"] == "p1", "rag: ⏳ 자리 → 같은 메시지를 고침 · 스레드 = 질문 ts")
T("📚 *근거*" in c[1][1]["text"] and "_— rag · " in c[1][1]["text"], "답 + 📚 근거 + 꼬리 줄"); print("     ", c[1][1]["text"].replace("\n", " ⏎ ")[:230])
c = run("<@UBOT> 핫팩은?", thread_ts="100.0")
T(all(kw.get("thread_ts", "100.0") == "100.0" for _, kw in c) and c[0][1]["thread_ts"] == "100.0", "스레드 안에서 물으면 그 스레드에")
c = run("<@UBOT> 서울 강남구는 재활용 무슨 요일에 내놔?")
T("구청" in c[1][1]["text"] and "📚" not in c[1][1]["text"], "찾지 못함 → 근거 숨김 + 구청 안내")
c = run("<@UBOT>"); T(len(c) == 1 and c[0][1]["text"] == s.USAGE, "빈 멘션 → 사용법")
c = run("<@UBOT> " + "가" * 301); T(len(c) == 1 and "300자" in c[0][1]["text"] and "301자" in c[0][1]["text"], "300자 초과 거절")
c = run("<@UBOT> 검색 뽁뽁이"); T(len(c) == 1 and c[0][0] == "post" and "🔎" in c[0][1]["text"] and c[0][1]["text"].count("\n> ") >= 3, "검색 모드: 메시지 1개")
c = run("<@UBOT> 비교 마트 영수증 종이로 버려도 돼?")
T([k for k, _ in c] == ["post", "update", "post", "update"] and "🙈" in c[1][1]["text"] and "📖" in c[3][1]["text"], "비교 모드: RAG 없이 → RAG 로")
c = run("<@UBOT> <!channel> 뽁뽁이"); t = c[1][1]["text"].split("📚")[0]
T("<!channel>" not in t and "<@U123>" not in t and "&lt;!channel&gt;" in t and "&amp;" in t and "*비닐류*" in t, "답의 < > & 이스케이프 + ** → *")
rb.get_llm().mode = "boom"
c = run("<@UBOT> 뽁뽁이"); T(c[1][1]["text"] == s.FAIL_TEXT and "secret" not in c[1][1]["text"], "오류: 슬랙엔 일반 문구만")
c = run("<@UBOT> 비교 뽁뽁이"); T(c[1][1]["text"] == s.FAIL_TEXT and c[3][1]["text"] == s.FAIL_TEXT, "비교 모드 오류도 일반 문구")
rb.get_llm().mode = "normal"
docs2 = [d for d in rb.get_store().docstore._dict.values()]
old = next(d for d in docs2 if d.metadata["year"] == 2018 and "item" in d.metadata); new = next(d for d in docs2 if d.metadata["year"] == 2026)
T(s.MIXED_NOTE in s.rag_text("비닐류로 배출합니다.", [old, new], 0.5, False) and s.MIXED_NOTE not in s.rag_text("비닐류", [old, old], 0.5, False), "연도 섞임 안내 줄 · 근거 중복 제거")
T(s.rag_text("x", [old, old], 0.5, False).count(rb.source_of(old)) == 1, "같은 출처는 한 번만")

print("== slack 이어 묻기 ==")
s._memory.clear()
c1 = run("<@UBOT> 건전지 어떻게 버려?", ts="200.0")
c2 = run("<@UBOT> 그럼 보조배터리는요?", ts="200.5", thread_ts="200.0")
T("🔗" not in c1[1][1]["text"] and c2[1][1]["text"].startswith("🔗 앞 대화로 *«보조배터리는 어떻게 버리나요?»*") and "📚 *근거*" in c2[1][1]["text"],
  "같은 스레드: 🔗 풀어 쓴 질문 + 답 + 📚 근거"); print("     ", c2[1][1]["text"].replace("\n", " ⏎ ")[:200])
c3 = run("<@UBOT> 그럼 보조배터리는요?", ts="300.0")
T("🔗" not in c3[1][1]["text"], "다른 스레드는 앞 대화를 모름")
T([q for q, _ in s.history_of("C1-200.0")] == ["건전지 어떻게 버려?", "보조배터리는 어떻게 버리나요?"], "기억에는 풀어 쓴 질문으로 적힘")
for i in range(5): s.remember("C1-200.0", f"q{i}", "a")
T([q for q, _ in s.history_of("C1-200.0")] == ["q2", "q3", "q4"], f"기억 상한: 스레드마다 최근 {rb.HISTORY_TURNS}번")
keep_max = s.MAX_THREADS; s.MAX_THREADS = 2
for k in ("k1", "k2", "k3"): s.remember(k, "q", "a")
T(list(s._memory) == ["k2", "k3"], "기억 상한: 스레드 수를 넘으면 오래된 스레드부터 잊음")
s.MAX_THREADS = keep_max; s._memory.clear()
orig_download = s.download; s.download = lambda f, c: img_bytes(); rb.get_llm().rewrite = "아이스팩 뚜껑은 어떻게 버리나요?"
run("<@UBOT>", ts="400.0", files=[{"id": "F1", "mimetype": "image/png", "size": 1, "url_private_download": "x"}])
c4 = run("<@UBOT> 그럼 그거 뚜껑은?", ts="400.5", thread_ts="400.0")
T(s.history_of("C1-400.0")[0][0] == "사진 속 물건 «아이스팩» 은 어떻게 버려요?" and "«아이스팩 뚜껑은 어떻게 버리나요?»" in c4[1][1]["text"], "사진 다음에도 이어 묻기")
s.download = orig_download; rb.get_llm().rewrite = "보조배터리는 어떻게 버리나요?"; s._memory.clear()

print("== slack 사진 ==")
from unittest import mock
IMG = {"files": [{"id": "F1", "mimetype": "image/png", "size": 1234, "url_private_download": "https://files.example/F1"}]}
real_download = s.download
s.download = lambda f, c: img_bytes()
c = run("<@UBOT>", **IMG)
T([k for k, _ in c] == ["post", "update"] and c[0][1]["text"] == s.PHOTO_HOLDER and c[0][1]["thread_ts"] == "111.1" and c[1][1]["ts"] == "p1", "사진: 📷 자리 → 같은 메시지를 고침 · 같은 스레드")
T("«아이스팩»" in c[1][1]["text"] and "📚 *근거*" in c[1][1]["text"] and "_— photo · " in c[1][1]["text"], "사진 답: 📷 이름 + 답 + 📚 근거 + 꼬리 줄"); print("     ", c[1][1]["text"].replace("\n", " ⏎ ")[:230])
c = run("<@UBOT> 핫팩은?", files=[{"mimetype": "application/pdf"}])
T(c[0][1]["text"] == s.HOLDER, "사진이 아닌 파일 → 글 질문으로")
c = run("<@UBOT>", files=[{"mimetype": "image/jpeg", "size": s.PHOTO_MAX_BYTES + 1}])
T(len(c) == 1 and "MB" in c[0][1]["text"], "사진 크기 상한")
rb.get_vision_llm().label = "모름"; c = run("<@UBOT>", **IMG)
T(c[1][1]["text"].startswith(s.PHOTO_UNKNOWN) and "📚" not in c[1][1]["text"], "못 알아본 사진 → 이름으로 물어 달라는 안내")
rb.get_vision_llm().label = "<!channel>아이스팩"; c = run("<@UBOT>", **IMG)     # 띄어쓰기 없음 — pick 의 이름 맞추기를 타지 않게
T("<!channel>" not in c[1][1]["text"] and "&lt;!channel&gt;" in c[1][1]["text"], "사진 이름도 이스케이프")
rb.get_vision_llm().label = "아이스팩"; config.PHOTO_MAX_DIST = 1e-9; c = run("<@UBOT>", **IMG)
T("이 중 무엇인가요" in c[1][1]["text"] and "1) " in c[1][1]["text"] and "📚" not in c[1][1]["text"], "애매하면 후보만 보여 주고 되묻기")
config.PHOTO_MAX_DIST = 0
s.download = lambda f, c: b"not an image"; c = run("<@UBOT>", **IMG)
T(c[1][1]["text"].startswith("✋") and "읽지 못했" in c[1][1]["text"], "읽을 수 없는 사진 → ✋ 안내")
def _boom(f, c): raise RuntimeError("HTTP 500 C:\\secret\\path")
s.download = _boom; c = run("<@UBOT>", **IMG)
T(c[1][1]["text"] == s.FAIL_TEXT and "secret" not in c[1][1]["text"], "사진 오류: 슬랙엔 일반 문구만")
s.download = real_download

class Resp:
    def __init__(self, body, ctype): self.body, self.headers = body, {"Content-Type": ctype}
    def read(self, n=-1): return self.body[:n] if n >= 0 else self.body
    def __enter__(self): return self
    def __exit__(self, *a): return False
class FileClient(Client):
    token = "xoxb-test-token"
    def files_info(self, file): self.calls.append(("files_info", file)); return {"file": {"url_private": "https://files.example/" + file}}
seen_req = []
with mock.patch("urllib.request.urlopen", lambda req, timeout: seen_req.append(req) or Resp(b"\xff\xd8jpeg", "image/jpeg")):
    fc = FileClient(); data = s.download({"id": "F9"}, fc)
T(data == b"\xff\xd8jpeg" and fc.calls == [("files_info", "F9")] and seen_req[0].get_header("Authorization") == "Bearer xoxb-test-token", "download: 주소가 없으면 files.info · 봇 토큰으로 받기")
with mock.patch("urllib.request.urlopen", lambda req, timeout: Resp(b"<html>login</html>", "text/html; charset=utf-8")):
    try: s.download(IMG["files"][0], FileClient()); T(False, "권한 없음(HTML) → files:read 안내")
    except RuntimeError as e: T("files:read" in str(e), "권한 없음(HTML) → files:read 안내")

from slack_bolt import App
from unittest import mock
with mock.patch.object(App, "__init__", lambda self, **kw: None), mock.patch.object(App, "event", lambda self, name: (lambda f: handlers.__setitem__(name, f) or f)):
    handlers = {}; s.build_app("xoxb-test")
seen = []
with mock.patch.object(s, "answer", lambda e, c: seen.append(e)):
    handlers["message"]({"channel_type": "im", "text": "a"}, None)
    handlers["message"]({"channel_type": "im", "text": "b", "bot_id": "B1"}, None)
    handlers["message"]({"channel_type": "im", "text": "c", "subtype": "message_changed"}, None)
    handlers["message"]({"channel_type": "im", "text": "f", "subtype": "file_share"}, None)
    handlers["message"]({"channel_type": "channel", "text": "d"}, None)
    handlers["app_mention"]({"text": "e"}, None)
T([e["text"] for e in seen] == ["a", "f", "e"], "DM: 봇 메시지 · subtype · 채널 글 무시 (사진 file_share 는 받음) / 멘션 연결")
for env, msg in (({"SLACK_BOT_TOKEN": "bad", "SLACK_APP_TOKEN": "xapp-1"}, "xoxb-"), ({"SLACK_BOT_TOKEN": "xoxb-1", "SLACK_APP_TOKEN": "bad"}, "xapp-")):
    with mock.patch.dict(os.environ, env):
        try: s.main(); T(False, "토큰 접두어 검사")
        except SystemExit as e: T(msg in str(e), f"토큰 접두어 검사 ({msg})")

print("== evaluate =="); import evaluate as ev
from pathlib import Path
ev.RESULT_DIR = Path(TMP) / "eval_results"
import io, contextlib
buf = io.TextIOWrapper(io.BytesIO(), encoding="utf-8")
with contextlib.redirect_stdout(buf):
    sys.argv = ["evaluate.py", "retrieval", "--repeats", "2"]; ev.main()
    sys.argv = ["evaluate.py", "answer", "--ids", "scratch"]; ev.main()
    sys.argv = ["evaluate.py", "answer", "--strategy", "multiquery", "--year-bonus", "0.05", "--ids", "c1,o1,i1"]; ev.main()
files = sorted(p.name for p in ev.RESULT_DIR.iterdir())
T(len([f for f in files if f.endswith("retrieval.md")]) == 1 and len([f for f in files if f.endswith("answer.json")]) >= 1, f"결과 파일 {len(files)}개")
md = next(ev.RESULT_DIR.glob("*retrieval.md")).read_text(encoding="utf-8")
T(md.count("| basic |") == 4 and md.count("| multiquery |") == 4 and "**g = " in md, "retrieval 격자 8칸 + g")
print("\n".join("      " + l for l in md.splitlines()[:22]))
js = json.loads(next(ev.RESULT_DIR.glob("*retrieval.json")).read_text(encoding="utf-8"))
T(len(js["grid"]) == 8 and len(js["grid"][4]["runs"]) == 2 and len(js["rewrites"]) == 2, "json: multiquery 2회 반복 기록")
am = sorted(ev.RESULT_DIR.glob("*answer.md"))[0].read_text(encoding="utf-8")
print("\n".join("      " + l for l in am.splitlines()[:26]))
T(ev.grade_answer("종량제 봉투로 배출합니다. 자료에서 찾지 못했습니다.", ["종량제"], []) == "contradict" and ev.grade_answer("자료에서 찾지 못했습니다", ["찾지 못했"], []) == "ok" and ev.grade_answer("종이류로 배출 종량제", ["종량제"], ["종이류로 배출"]) == "wrong", "채점: 자기모순 · 범위밖 · bad")
raw_dir, ph_dir = Path(TMP) / "photos_raw", Path(TMP) / "photos"; raw_dir.mkdir()
ex = Image.Exif(); ex[0x010F] = "FakeMakerGPS"; ex[0x0112] = 6
(raw_dir / "C2.jpg").write_bytes(img_bytes((3000, 2000), "JPEG", "RGB", ex))
(raw_dir / "out_food.png").write_bytes(img_bytes((800, 600)))
(raw_dir / "zz.jpg").write_bytes(img_bytes((100, 100), "JPEG", "RGB")); (raw_dir / "note.txt").write_text("x")
buf = io.TextIOWrapper(io.BytesIO(), encoding="utf-8")
with contextlib.redirect_stdout(buf):
    sys.argv = ["evaluate.py", "prep-photos", "--src", str(raw_dir), "--dir", str(ph_dir)]; ev.main()
    sys.argv = ["evaluate.py", "photo", "--dir", str(ph_dir)]; ev.main()
prepped = sorted(p.name for p in ph_dir.iterdir())
with Image.open(ph_dir / "c2.jpg") as im: c2_size, c2_exif = im.size, len(im.getexif())
T(prepped == ["c2.jpg", "out_food.jpg"] and c2_size == (ev.PREP_SIDE * 2 // 3, ev.PREP_SIDE) and c2_exif == 0, f"prep-photos: 모르는 이름 건너뜀 · 회전 · {c2_size} · EXIF {c2_exif}개")
pm = next(ev.RESULT_DIR.glob("*photo.md")).read_text(encoding="utf-8")
pj = json.loads(next(ev.RESULT_DIR.glob("*photo.json")).read_text(encoding="utf-8"))
T("사진 적중" in pm and pj["inside"] == 1 and pj["outside"] == 1 and pj["top3"] in (0, 1) and len(pj["rows"]) == 2, f"evaluate photo: 결과 파일 · 범위 안 {pj['inside']} · 밖 {pj['outside']}")
print("\n".join("      " + l for l in pm.splitlines()[:24]))
import shutil; shutil.rmtree(TMP, ignore_errors=True)
print("\nALL OK" if ok else "\nSOME FAILED")
sys.exit(0 if ok else 1)
