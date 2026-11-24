"""공용 설정 — 다른 파일은 langchain · langsmith 를 import 하기 **전에** 이 파일부터 import 한다.

  ★ 이유: LangSmith 는 환경 변수를 처음 읽을 때 기억해 둔다.
     여기서 프로젝트 이름을 정한 뒤에 라이브러리가 올라와야 trace 가 «recycle-bot-20241499» 로 간다.

  모델 · 전략은 전용 키 RECYCLE_* 로만 바꾼다 (.env 의 MODEL · EMBED_MODEL 은 읽지 않는다 — 수업 저장소에서 다른 주차 실습과 .env 를 같이 쓸 때 정한 규칙).
  RECYCLE_* 는 «실행 한 번 = 설정 하나» — 인덱스와 모델을 한 번만 읽어 계속 쓰기 때문에 실행 중에는 바뀌지 않는다.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()                                   # 저장소 맨 위의 .env (이 파일의 폴더부터 위로 올라가며 찾음)
# ★ LangSmith 프로젝트는 여기서 정한다 — .env 에 넣지 않아도 되고, .env 를 다른 실습과 같이 써도 trace 가 안 섞임
os.environ["LANGSMITH_PROJECT"] = os.getenv("RECYCLE_LANGSMITH_PROJECT", "recycle-bot-20241499")

HERE = Path(__file__).resolve().parent
DATA_DIR = HERE / "data"
INDEX_DIR = HERE / os.getenv("RECYCLE_INDEX", "index_recycle")   # 평가에서 비교용 인덱스로 바꿀 때만

MODEL = os.getenv("RECYCLE_MODEL", "hf.co/mykor/A.X-4.0-Light-gguf:Q4_K_M")
EMBED_MODEL = os.getenv("RECYCLE_EMBED_MODEL", "hf.co/mykor/KURE-v1-gguf:Q8_0")

DOCS = [   # (파일, year, 출처에 쓸 짧은 이름)
    ("분리배출_가이드라인.pdf", 2018, "가이드라인"),
    ("분리배출_QA사례100_2026.pdf", 2026, "사례집"),
]
SHORT_NAME = {name: short for name, _, short in DOCS}

CHUNK_SIZE, CHUNK_OVERLAP = 400, 40
KO_SEPARATORS = ["\n\n", "\n", "다. ", ". ", " ", ""]
UNIT_MAX = 600          # 구조 단위(Q&A · FAQ · 품목)는 이 길이를 넘을 때만 재귀로 다시 자른다
MIN_BODY_CHARS = 30     # 가이드라인 **본문** 청크에만 적용 (품목사전은 평균 20자 — 걸면 대부분 사라진다)

TOP_K = 3               # 근거로 넘길 청크 수
FETCH_K = 10            # 재정렬 전에 넓게 가져올 후보 수
YEAR_RECENT = 2020      # 이 해 이후 문서를 «최신» 으로 본다
# ★ 아래 기본값은 evaluate.py 실측(2026-11-17)으로 채택한 값
#   YEAR_BONUS 0.09 = 0.5g (g = 0.180) — eval_results/20261117-153601-retrieval.md:
#     Top-3 23 → 23 (줄지 않음) · c1 ○ · 연도충돌 top-1 이 2026 2/4 → 4/4. 생성은 28/30 = 28/30 (…153652 ↔ …153846)
#   STRATEGY basic — multiquery 는 Top-3 20~21 로 오히려 낮고 5배 느림 (같은 파일)
#   PROMPT base — recent 는 27~28/30 + 자기모순 1 (…153750 · …153940)
YEAR_BONUS = float(os.getenv("RECYCLE_YEAR_BONUS", "0.09"))
STRATEGY = os.getenv("RECYCLE_STRATEGY", "basic")          # basic | multiquery
PROMPT_VARIANT = os.getenv("RECYCLE_PROMPT", "base")       # base | recent — E4 실험용 («더 최근 근거를 따른다» 한 줄)

TEMPERATURE, MAX_OUT, NUM_CTX = 0.1, 300, 4096
KEEP_ALIVE = 1800       # 초(30분) — Ollama 가 모델을 5분 만에 내리지 않게 (첫 답 20초 문제)
#                         ⚠️ 정수로 둘 것: OllamaEmbeddings 의 keep_alive 는 int 만 받는다 ("30m" 은 ValidationError)

# 생각(thinking) 모드 — qwen3.5 는 기본이 켜짐이라 답 앞에 긴 생각 글을 쓴다 → 기본은 끈다
#   off = think:false (생각 기능이 없는 gemma3:4b 도 받는다 — 2026-11-24 확인) · on = think:true · auto = 보내지 않음
REASONINGS = {"off": False, "on": True, "auto": None}
_reasoning = os.getenv("RECYCLE_REASONING", "off")
if _reasoning not in REASONINGS:
    raise SystemExit(f"RECYCLE_REASONING 은 {' | '.join(REASONINGS)} 중 하나여야 합니다 (지금: {_reasoning!r})")
REASONING = REASONINGS[_reasoning]

# ── 사진으로 묻기 — 사진은 «품목 이름 붙이기» 에만 쓰고, 답은 지금처럼 문서에서 (docs/photo-feature-plan.md) ──
VISION_MODEL = os.getenv("RECYCLE_VISION_MODEL") or MODEL   # 비우면 생성 모델이 사진도 본다 (한 모델) · 따로 주면 두 모델
PHOTO_SIDE = int(os.getenv("RECYCLE_PHOTO_SIDE", "768"))    # 긴 변을 이 픽셀까지 줄여 넣는다 (VRAM · 시간)
PHOTO_MAX_BYTES = 15 * 1024 * 1024                          # 슬랙에서 받을 사진 원본 상한
LABEL_MAX_OUT = 40                                          # 이름 붙이기는 짧게 — 토큰 상한
UNKNOWN_LABEL = "모름"                                       # 비전 모델이 «물건이 아니다 · 모르겠다» 일 때
# 확신 기준 — 1위 거리가 PHOTO_MAX_DIST 보다 멀거나, 다른 품목 후보와의 거리 차가 PHOTO_MIN_GAP 보다 작으면 «되묻기».
#   0 = 쓰지 않음 (항상 답 + 다른 후보 표시). 값은 사진 실측으로 정한다 (evaluate.py photo 의 거리 표).
PHOTO_MAX_DIST = float(os.getenv("RECYCLE_PHOTO_MAX_DIST", "0"))
PHOTO_MIN_GAP = float(os.getenv("RECYCLE_PHOTO_MIN_GAP", "0"))
NOT_FOUND = "자료에서 찾지 못했습니다"
MAX_QUESTION = 300
TAG = "recycle-bot"

STRATEGIES = ("basic", "multiquery")
if STRATEGY not in STRATEGIES:
    raise SystemExit(f"RECYCLE_STRATEGY 는 {' | '.join(STRATEGIES)} 중 하나여야 합니다 (지금: {STRATEGY!r})")


def short_model(name: str = MODEL) -> str:
    """«hf.co/mykor/A.X-4.0-Light-gguf:Q4_K_M» → «A.X-4.0-Light» · «gemma4:e4b» → «gemma4:e4b» (슬랙 꼬리 줄 · 로그용).

    Ollama 공식 모델은 태그가 크기(4b · e4b)라 남기고, hf.co/… 는 태그가 양자화 방식이라 뗀다.
    """
    base = name.rsplit("/", 1)[-1]
    if name.startswith("hf.co/") or ":" not in base:
        return base.split(":", 1)[0].removesuffix("-gguf")
    return base
