# 사진으로 묻기 — 모델 검토 · 실험 계획

> 상태: **계획 · 설계** (2026-11-20 작성 · 코드 · 슬랙 앱 설정은 아직 손대지 않음). **제출은 이 저장소** — 사진 기능까지 넣어 14주차(12/4)에.
> 다음 세션 순서: **구현(클라우드 · 5-2) → 측정(사용자 PC · 6장) → 기본값 채택 → 문서 · 캡처(7장) → `main`** (2026-11-17 때와 같은 방식).
> 슬랙에 사진을 올리면 답하는 기능을 붙이기 전에 «어떤 모델로 · 어떤 구조로 · 무엇을 재서 정하나» 를 정리한 문서입니다.
> 모델 크기 · 점수는 대부분 모델 카드 · 제3자 가이드 값이고 출처끼리 엇갈리는 것이 많습니다 — **최종 판단은 6장의 실측으로** 합니다.
> 구현이 끝나면 이 문서는 결과 기록으로 바꾸거나 정리합니다(사용자 확인).

## 0. 한눈에

| 항목 | 내용 |
|---|---|
| 기능 | 슬랙에 사진 → 비전 모델이 **품목 이름**을 붙임 → 지금 RAG(문서 근거 + 출처)로 답 |
| 합격선 | 같은 조건에서 수업 기본 **`gemma3:4b` 보다 좋을 것** (2장) |
| 1순위 후보 | **`gemma4:e4b`** · **`qwen3.5:4b`** — 한 모델로 답도 하고 사진도 읽음 |
| 보험 | 지금 생성 모델 유지 + **`qwen3.5:0.8b`** 가 사진에 이름만 붙임 |
| 다음 할 일 | ① 클라우드에서 구현 (5-2 · 모델은 환경 변수로 바꿔 끼움) → ② 사용자 PC 에서 측정 (6장 · 약 1 ~ 1.5시간) → ③ 채택 · 문서 · 캡처 (7장) |

---

## 1. 목적과 범위

- 사용자는 **이름을 몰라도** 사진으로 묻는다. 이 봇의 가장 큰 숙제인 «생활 용어 ↔ 문서 용어» 간극(«뽁뽁이 ↔ 에어캡», «돌돌이 ↔ 테이프크리너»)을 이름 단계에서 없앤다.
- **원칙: 사진은 «품목 이름 붙이기» 에만 쓴다. 답은 지금처럼 문서에서 근거 + 출처로.**
  사진만 보고 배출 방법을 말하게 하지 않는다 — 출처 없는 답은 README 1번이 문제 삼은 «블로그 답» 과 같다.
- 하지 않는 것: 웹 검색으로 답 보충 · 재질 분류기 · 미세조정 (이유는 부록).

## 2. 합격선 (사용자 결정 · 2026-11-20)

| 조건 | 기준 |
|---|---|
| **필수 ①** | 같은 조건(지금 인덱스 456청크 · 같은 문항)에서 **`gemma3:4b` 보다 정답이 많고 자기모순이 적거나 같을 것** |
| **필수 ②** | **사진 입력** 가능 + **8GB 안** (KURE · 화면 몫 포함 — 3장) |
| 하지 않음 | 지금 생성 모델(A.X 4.0 Light)보다 좋을 필요 없음 · A.X 와의 비교나 «A.X 보다 낮음» 표시도 하지 않음 (문서 방침은 7-1) |

⚠️ **`gemma3:4b` 기준선이 아직 없습니다.** 있는 것은 10주차 기록뿐 — 6문항 **4/6** · 자기모순 **2회** · 답 1.0 ~ 1.6초 · GPU 4.87GB,
그것도 옛 인덱스(재귀 181청크)에서 잰 값(CONTEXT 부록 C). → 6장 1단계에서 **지금 인덱스 · 30문항으로 다시** 잽니다.
(`evaluate.py` 머리말에 `python evaluate.py answer --model gemma3:4b  # (선택) 수업 기본 모델과 비교` 가 이미 있음)

## 3. 제약 — 8GB 예산 (계산)

```
  RTX 3070 8GB
  − 화면 등 다른 프로그램        ≈ 0.6 GB   (2026-11-17 실측 5.75 ~ 6.37GB 안에 포함돼 있던 몫)
  − KURE-v1 (임베딩)            ≈ 0.38 GB  (ollama ps 380MB)
  ─────────────────────────────────────────
  = 생성(+사진) 모델 몫          ≈ 7 GB     ← 한 모델로 교체할 때의 상한
    지금 생성 모델(4.6GB)을 그대로 두면 사진 모델 몫은 ≈ 1.5 ~ 2 GB
```

모델을 안 바꾸고 VRAM 을 짜내는 방법:

| 방법 | 확보 (계산) | 비고 |
|---|---|---|
| KURE 만 CPU 로 (Ollama 옵션 `num_gpu: 0`) | ≈ 0.38 GB | 질문 하나 임베딩은 CPU 로도 짧을 것(예상 · 재 볼 것) |
| 모니터를 메인보드 출력(내장 그래픽)에 | ≈ 0.6 GB | i9-12900 (F 모델이 아니면 내장 그래픽 있음) — 사용자 PC 확인 |
| 대화 메모리(KV) 압축 `OLLAMA_KV_CACHE_TYPE=q8_0` | ≈ 0.1 GB | Qwen2.5-7B 구조 기준 4096토큰 KV 가 원래 ≈ 0.23GB 라 효과 작음 |
| `OLLAMA_NUM_PARALLEL=1` | 기본값이 1 이 아니면 수백 MB | `ollama ps` 로 확인 |

- CONTEXT «범위 밖» 표에 «사진으로 품목 판별 — 이미지 입력 · 비전 모델 → 8GB 초과» 라고 적혀 있음 → **6장 실측으로 갱신 대상** (7-2).

## 4. 후보 모델 (2026-11-20 조사)

### 4-1. 등급별

| 등급 | 모델 (Ollama 태그) | 출시 · 라이선스 | 크기 · 8GB | 장점 | 걸리는 점 |
|---|---|---|---|---|---|
| ⭐ 1군 | **`gemma4:e4b`** | 2026-04 · Apache 2.0 | 파일 6.1GB(QAT `gemma4:e4b-it-qat`) ~ 9.6GB(기본 태그) · ⚠️ | **`gemma3:4b` 의 직계 후속** → «수업 기본보다 나아졌나» 를 가장 깔끔하게 보여 줌. 텍스트 + 사진 + 오디오 | 실효 4.5B · 전체 8B(층별 임베딩 포함). VRAM 추정이 4 ~ 6.3GB(짧은 문맥) ~ 10GB 로 엇갈림. 넘치면 `gemma4:e2b`(QAT 4.3GB) |
| ⭐ 1군 | **`qwen3.5:4b`** | 2026-03 · Apache 2.0 | 3.3 ~ 4.0GB · ✅ 여유 | 사진 네이티브 · 최신 · «201개 언어» (모델 카드) | **생각(thinking) 모드가 기본으로 켜짐** — 꺼야 함(8장). 한국어 KMMLU 수치 없음. Qwen3.5 의 언어 간 정렬이 약하다는 연구 1건 |
| ⭐ 보험 | **지금 생성 모델 + `qwen3.5:0.8b`** (또는 `2b`) | 2026-03 · Apache 2.0 | 1.2GB (2b 2.7 ~ 3.1GB) · ⚠️ 경계 | 답 품질이 지금 그대로 · 실패해도 손해 없음 | 모델 2개 — 빠듯하면 Ollama 가 번갈아 올리거나(사진 질문이 느려짐) 사진 모델만 CPU 로 |
| 2군 | `qwen3-vl:4b` | 2025-10 | 3.3GB · ✅ | 검증된 사진 모델 | `qwen3.5:4b` 의 이전 세대 — 비교용 |
| 2군 | `ministral-3:3b` | 2025-12 · Apache 2.0 | 작음 · ✅ | Ollama 공식 · 사진 가능 | 한국어 근거 없음 |
| 3군 | A.X 4.0 VL Light (SKT · 8B) | 2025-07 · Apache 2.0 | 4비트 ≈ 5 ~ 6GB (계산) · ⚠️ | 한국어 사진 벤치마크 평균 79.4 (Qwen2.5-VL-32B 73.4 · 제작사 측정) | **Ollama 불가** — LLaVA-Next 기반 자체 구조(SigLIP + Qwen2 + MLP/LDP 연결부 · `a.x-4-vl` · Transformers 4.49 + `trust_remote_code`). GGUF 직접 변환이나 Transformers 4비트 실행이 필요 |
| 3군 | `qwen3.5:9b` · `qwen3-vl:8b` · `ministral-3:8b` · `minicpm-v4.5` | — | 6.0 ~ 7.6GB · ❌ ~ ⚠️ | 클수록 똑똑할 가능성 | KURE 와 같이 두면 8GB 를 넘기 쉬움 |

### 4-2. 구조 선택지

| 안 | 구조 | 이럴 때 |
|---|---|---|
| **A. 한 모델로 교체** | `gemma4:e4b` 또는 `qwen3.5:4b` 하나가 답 + 사진 | 2장 합격선을 넘으면 — 가장 단순 |
| **B. 보험** | 지금 생성 모델 + `qwen3.5:0.8b` (사진 이름만) | A 후보가 모두 탈락하면 |
| C. 같은 집안 교체 | A.X 4.0 VL Light | A · B 모두 한국어 사진 인식이 약하고 시간이 남을 때 — 실행 경로부터 만들어야 함 |
| D. 생성 없이 고르기 | CLIP · 멀티모달 임베딩 (부록) | 사진 → 이름이 계속 틀릴 때의 대안 — 새 패키지 필요 |

## 5. 사진 흐름 · 구현 설계

### 5-1. 흐름

```
슬랙 사진 (+ 글이 있으면 같이)
  │
  ▼  ① 이름 붙이기   비전 모델 — «사진 속 물건을 한국어 품목 이름으로 짧게» (예: «파란 젤이 든 냉동팩»)
  │
  ▼  ② 검색          지금 RecycleRetriever 그대로 (KURE · year 보정) → 후보 3개 + 거리
  │
  ▼  ③ 결정          1위 거리가 충분히 가깝고 2위와 차이가 크면 → ④
  │                  애매하면 → «이 중 무엇인가요? 아이스팩 / 핫팩 / 보냉백» 되묻기 (슬랙 버튼 또는 번호)
  ▼  ④ 답            지금 RAG 로 답 + 📚 근거 + «📷 사진에서 «아이스팩» 으로 봤어요 — 틀리면 이름으로 다시 물어 주세요»
```

- **이름은 조금 틀려도 됩니다** — «파란 젤이 든 냉동팩» 이어도 검색이 품목사전 «아이스팩» 을 찾으면 됩니다. 그래서 평가 기준은 «이름이 정확한가» 가 아니라 **«정답 품목이 검색 3위 안에 오나»** 입니다.
- ③ 의 «결정(라우팅)» 은 따로 모델을 두지 않고 **검색기가 이미 계산하는 거리**를 확신도로 씁니다(눈금: 1위 ↔ 3위 거리 차 중앙값 g = 0.180 · CONTEXT 부록 D).
  확신 점수는 모델마다 실제 정답과 맞는 정도가 달라(라우팅 연구 · 출처) **기준선은 우리 사진으로 정합니다**.
- 슬랙: `files:read` 권한 + 재설치. 지금 DM 처리는 `subtype` 있는 메시지를 버리므로 사진 메시지(`file_share`)를 받게 고쳐야 함. 사진은 `url_private` 를 봇 토큰으로 내려받음.
  버튼으로 되물으려면 앱의 Interactivity 를 켬(Socket Mode 에서 공개 주소 없이 되는지 확인 필요) — 안 되면 «번호로 답해 주세요» 로.
- 사진 크기: Qwen 계열은 사진이 클수록 토큰이 늘어 VRAM · `num_ctx`(4096)를 넘길 수 있음 → 768px 안팎으로 줄여 넣음.
- 개인정보: 사진은 PC 안에서만 처리. 단 **LangSmith 추적을 켜면 사진(base64)이 trace 에 올라갈 수 있음** → 숨기거나 README 3번 보안 문장에 밝힘 (8장).

### 5-2. 구현 설계 (다음 세션 · 파일별)

**원칙: 모델을 정하기 전에 «환경 변수로 바꿔 끼울 수 있게» 먼저 짠다** → 사용자 PC 에서 같은 코드로 후보를 재고 → 판정 규칙대로 기본값을 고른다.
지금 코드의 규칙(맨 먼저 `import config` · «실행 한 번 = 설정 하나» · 예외는 콘솔에만 · 출처는 코드가 metadata 로)은 그대로 따른다.

| 파일 | 할 일 |
|---|---|
| `config.py` | `VISION_MODEL = os.getenv("RECYCLE_VISION_MODEL", MODEL)` — 기본은 생성 모델과 같음(A 안) · 따로 주면 B 안. `RECYCLE_REASONING`(기본 off → `ChatOllama(reasoning=False)`). 사진 크기 상한 · 확신 기준선(거리 · 1위와 2위 차) 상수 — **기준선은 6장 실측으로 정하고, 정하기 전엔 «항상 답 + 다른 후보 표시»**. 기본 `MODEL` 은 채택 전까지 그대로 |
| `rag_backend.py` | ① `get_llm()` 에 `reasoning` 반영(⚠️ 생각 기능이 없는 모델에 `False` 를 보내도 되는지 첫 실행에서 확인 — 오류면 그 모델엔 `None`) ② `describe_photo(image: bytes, mime, hint)` — `HumanMessage([{"type":"text",…}, {"type":"image_url","image_url":"data:<mime>;base64,<…>"}])` 를 `VISION_MODEL` 로 (langchain-ollama 1.1.0 이 이 형식을 Ollama `images` 로 넘김 · 2026-11-20 코드 확인). 프롬프트: «사진 속 물건 하나를 분리배출 품목 이름으로 한국어로 짧게 · 물건이 아니거나 모르면 '모름'» ③ `ask_photo(image, mime, text, meta)` — `RunnableLambda(name="recycle-photo")` 한 trace 안에 `describe-photo` → `RecycleRetriever`(질문 = 이름 + 사용자 글) → 확신 판정 → (확신) 지금 `generate` / (애매) 후보 3개만 ④ 사진 base64 가 trace 입력에 그대로 남지 않게 «image: N bytes» 로 줄여 기록 (`build_index.py` 의 `_traced` 와 같은 방식) — 자식 ChatOllama run 에 남는지 확인 |
| `slack_rag_bot.py` | 사진 받기: DM `message` 중 `subtype == "file_share"` 만 새로 받음(나머지 subtype · 봇 메시지는 계속 무시) · `app_mention` 에 `files` 가 오면 같이(오는지 첫 실행에서 확인). 첫 `image/*` 하나만 · `url_private_download` 를 `Authorization: Bearer <xoxb>` 로 표준 라이브러리 `urllib.request` 로 받음(새 패키지 없음) · 크기 상한 넘으면 안내. 답: ⏳ 자리잡기 → 확신이면 «📷 사진에서 «…» 으로 봤어요 — 틀리면 이름으로 다시 물어 주세요» + 답 + 📚 근거 + 꼬리 줄 / 애매하면 «이 중 무엇인가요? 1) … 2) … 3) … — 이름으로 다시 물어 주세요». 사진과 같이 온 글은 힌트로. 슬랙 버튼은 나중(선택) |
| `evaluate.py` | `python evaluate.py photo --dir photos [--vision-model …]` — `photos/<문항id>.jpg` 마다 이름 → 검색 Top-3 에 `questions.py` 의 `gold` 가 있나 · 확신 여부 · 시간, `photos/out_*.jpg` 는 범위 밖(확신이 아니어야 정답) → `eval_results/<시각>-photo.md` · `.json`. 텍스트는 지금 `answer --model` 그대로 |
| `questions.py` | 변경 없음 — 사진 채점에 `gold` 를 그대로 씀 |
| `tests/offline_check.py` | 가짜 LLM 이 사진 메시지를 받으면 «아이스팩» 을 돌려줌 → `describe_photo` · `ask_photo`(확신 · 애매 두 갈래) · 슬랙 `file_share` 갈래(가짜 내려받기) · 크기 상한 · trace 이름과 «사진이 trace 입력에 그대로 없음» 을 검사에 추가 |
| `.gitignore` · `requirements.txt` | `photos/` 커밋 여부는 사용자 결정(개인 사진일 수 있음). 새 패키지는 넣지 않는 것이 기본 — 사진 크기 줄이기에 Pillow 가 필요하면 사용자 확인 후 (지금 venv 에 Pillow 없음 · Ollama 의 모델별 전처리가 크기를 맞추는지 6장에서 VRAM · 시간으로 확인) |
| 문서 | 코드가 SPEC 과 달라지는 곳은 SPEC 13-1 에 새 행 · CLAUDE.md 갱신 |

### 5-3. 어디서 무엇을 하나

| 클라우드 세션 (환경 «버릴지도 (분리배출 RAG 봇)») | 사용자 PC (RTX 3070 8GB · Ollama) |
|---|---|
| 코드 · `tests/offline_check.py` · `build_index.py --check` · `questions.py` · 문서 (사례집은 `curl -sS -L -o "data/분리배출_QA사례100_2026.pdf" "https://www.kwaste.or.kr/lib/fileDownload.php?save_file=attachment_202605081124500.29008db5d7c61e61718f7a154de14539.pdf&file_name=QA100.pdf"` · 68,862,868바이트) | `ollama pull` · `evaluate.py answer` · `evaluate.py photo` · 사진 찍기 · 슬랙 봇 실행 · `nvidia-smi` · 슬랙 · LangSmith 캡처 |

**다음 세션 첫 답에서 사용자에게 한 번에 확인할 것**: ① 이번 세션에 GPU PC 를 쓸 수 있나 ② 6-3 판정 목표치(사진 15/20 등) 확정 ③ 테스트 사진을 저장소에 커밋할지 ④ 슬랙 앱에 `files:read` 추가 · 재설치 가능한지 ⑤ Pillow(새 패키지)를 들일지

## 6. 실험 계획 · 판정 규칙

### 6-1. 단계 (GPU PC · 저장소 맨 위에서)

| # | 할 일 | 명령 · 방법 | 비고 |
|---|---|---|---|
| 0 | 준비 | `ollama -v` (기록상 0.32.14 — gemma4 는 0.20+, qwen3.5 는 0.17.4+ 에서 지원) · `ollama pull gemma4:e4b` (또는 `gemma4:e4b-it-qat`) · `ollama pull qwen3.5:4b` · `ollama pull qwen3.5:0.8b` | 다운로드 ≈ 11GB (계산). `gemma3:4b` 는 설치돼 있음 |
| 1 | **기준선** | `python evaluate.py answer --model gemma3:4b` · `python evaluate.py answer --model gemma3:4b --ids scratch` | 코드 그대로. 결과 파일에 «생성 중 GPU 메모리» 가 자동 기록 |
| 2 | **후보 텍스트** | `python evaluate.py answer --model gemma4:e4b` · `--model qwen3.5:4b` (먼저 `--ids scratch` 로 답에 생각 글이 섞이지 않는지 확인) | 생각 모드는 5-2 의 `RECYCLE_REASONING`(기본 off)으로 끔 |
| 3 | **VRAM** | 2 를 돌리는 동안 `nvidia-smi` · `ollama ps` (PROCESSOR 가 100% GPU 인지) | 모델 사이에 `ollama stop <모델>` |
| 4 | **사진 20장 + 범위 밖 4장** | `python evaluate.py photo --dir photos --vision-model <모델>` (5-2) — 구현 전 빠른 확인은 `ollama run <모델> "이 사진 속 물건을 한국어 품목 이름으로 짧게 답해 줘 .\photos\c2.jpg"` → `python rag_backend.py 검색 "<답>"` | 후보 = `gemma4:e4b` · `qwen3.5:4b` · `qwen3.5:0.8b` · (기준점) `gemma3:4b` |
| 5 | 기록 | 1 ~ 3 은 `eval_results/` 에 자동 · 4 는 표로 정리 → CONTEXT 새 부록 | |

### 6-2. 사진 세트 — `questions.py` 의 정답 위치(gold)를 그대로 씀

문서에 정답이 있는 물건을 직접 찍습니다. 문항 id 를 파일 이름으로(`photos/c2.jpg`) 하면 **정답 위치를 새로 만들 필요가 없습니다** — `questions.py` 의 `gold` 로 채점.

| id | 물건 | id | 물건 | id | 물건 | id | 물건 |
|---|---|---|---|---|---|---|---|
| c1 | 뽁뽁이(에어캡) | c6 | 핫팩 | s4 | 먹다 남은 약 | y3 | 우유팩 |
| c2 | 아이스팩 | s1 | 탁상달력 | s5 | 나무젓가락 | y4 | 코팅 프라이팬 |
| c3 | 돌돌이 리필 | s3 | 형광등 | a1 | 송장 붙은 택배 비닐 | a2 | 마스크 |
| c4 | 선글라스 | s6 | 칫솔살균기 | y1 | 소주 페트병 | a3 | 치킨 박스 |
| c5 | 마트 영수증 | s7 | 면도날 (포장째 · 안전 주의) | y2 | 생수병 | a4 | 우산 |

- **범위 밖 사진 4장** (음식 접시 · 풍경 · 반려동물 · 빈 책상) — 엉뚱한 품목으로 답하지 않고 «찾지 못했어요 / 되묻기» 로 가야 정답.
- `y2` 생수병은 텍스트로도 검색이 못 찾는 문항(README 6번) — 사진이 이름을 «먹는 샘물 페트병» 으로 붙여 주면 풀릴 수도 있음.

### 6-3. 판정 규칙 (측정 전에 고정)

| 조건 | 기준 |
|---|---|
| 텍스트 | 30문항 정답 **> `gemma3:4b`** · 자기모순 **≤ `gemma3:4b`** · 범위 밖 **≥ `gemma3:4b`** |
| 사진 | 20장 중 **15장 이상** 정답 품목이 검색 3위 안 · 범위 밖 4장은 엉뚱한 품목 답 없음 (제안값 — 실험 전에 사용자와 확정) |
| VRAM | KURE 포함 `nvidia-smi` **< 8GB** · `ollama ps` 100% GPU |
| 고르기 | 합격한 것 중 **텍스트 정답이 가장 많은 것** → 같으면 사진 적중 → 같으면 작고 빠른 쪽 |
| 아무것도 합격 못 하면 | **B 안 (보험)** — 사진 모델은 `qwen3.5:0.8b` 와 `2b` 중 사진 적중이 높은 쪽 |

## 7. 채택하면 바꿀 곳

### 7-1. 문서 방침 (사용자 결정 · 2026-11-20 · 아직 제출 전)

- README · CONTEXT · docs 는 **새 모델 기준으로 처음부터** 씁니다. 지금 생성 모델(A.X 4.0 Light)은 언급하지 않아도 되고, **비교군은 `gemma3:4b`** 입니다
  (README 3번의 틀 «수업 기본 → 같은 조건에서 비교해 고른 모델» 은 그대로).
- 단, **숫자 · 캡처는 전부 새 모델로 다시 재고 다시 찍습니다** — 옛 숫자를 새 모델 이름으로 옮겨 적지 않습니다(실측 원칙).
- 임베딩(KURE-v1) · 분할 · 검색 쪽 실측(CONTEXT 부록 A · B · D)은 생성 모델과 무관해 그대로 유효합니다.

### 7-2. 체크리스트

| 구분 | 고칠 곳 |
|---|---|
| 코드 | `config.py` 기본 `MODEL` · `rag_backend.py` (사진 입력 · 생각 모드 끄기 · `warmup`) · `slack_rag_bot.py` (사진 이벤트 · 내려받기 · 크기 줄이기 · 📷 줄 · 되묻기) · `.env.example` 주석 · `questions.py` / `evaluate.py` (사진 문항) · `tests/offline_check.py` (가짜 비전 모델로 새 갈래 확인) |
| 재실행 | `scratch_eval.py gemma3:4b` ↔ `scratch_eval.py <새 모델>` (CONTEXT 부록 C 의 10주차 비교를 새 모델로) · `evaluate.py answer` (부록 E) · 사진 실험 (새 부록) |
| 슬랙 앱 | `files:read` 권한 → Reinstall to Workspace · (버튼을 쓰면) Interactivity |
| README | 맨 위 그림 · 2번(사진 기능 · 화면) · 3번(모델 선택 근거 · VRAM) · 4번(스택 · 캡처) · 5번(`ollama pull` · 확인된 환경) · 6번(한계) · 필수 요건 대조 |
| CONTEXT | «범위 밖» 의 사진 줄 → 범위 안으로 · 처리 흐름 · 하드웨어 확인 · 위험과 대응 · 부록 C · E · **사진 실측 부록 추가** |
| docs · SPEC | `docs/architecture.md` · `docs/scenarios.md` (사진 시나리오) · SPEC 13-1 에 새 행 · CLAUDE.md |
| 캡처 | **다시 찍음**: `trace-rag.png`(생성 모델 이름) · `trace-retriever.png`(왼쪽 트리에 생성 모델 이름이 보임) · `slack-thread.png` · `slack-compare.png`(답 꼬리 줄에 모델 이름) / **그대로**: `trace-build.png`(모델 이름 없음 · 2026-11-20 확인) / **새로**: 슬랙 사진 질문 · 사진이 든 trace |
| 옛 실측 파일 | `eval_results/` 의 2026-11-17 파일 중 생성 모델로 잰 6개(`…-answer` 5개 · `…153601-retrieval`) — 삭제는 사용자 확인 뒤. README · CONTEXT 는 새 실측 파일을 가리키게 |

(참고 · 2026-11-20 기준 «A.X» 가 나오는 곳: README 10줄 · CONTEXT 12 · `docs/scenarios.md` 9 · CLAUDE.md 6 · SPEC 4 · `docs/architecture.md` 3 · `config.py` 2 · `.env.example` 1 · `slack_rag_bot.py` 1 · `scratch_eval.py` 1)

### 7-3. 새 기능이라 새로 써야 할 것 · 새 캡처

모델을 바꾸는 것(7-2)과 별개로, **기능이 하나 늘었으니 README 가 그 기능을 보여 줘야** 합니다 — README 가 곧 점수이고 LangSmith 캡처는 필수 제출물입니다.

| 문서 | 새로 들어갈 내용 |
|---|---|
| README 1번 목적 | «이름을 몰라도 사진으로 묻는다» 한 줄 |
| README 2번 기능 | 기능 표에 사진 행(멘션 · DM 에 사진) · 📷 줄 · 애매할 때 되묻기 · **슬랙 사진 화면 캡처** |
| README 3번 모델 | `gemma3:4b` 대비 텍스트 실측 + **사진 → 품목 실측**(20장 적중 · 범위 밖) · 새 VRAM 계산 · 실측 |
| README 4번 스택 · LangSmith | 비전 단계(`describe-photo`)가 든 처리 표 · **`recycle-photo` trace 캡처** · 사진은 trace 에 어떻게 남는지 |
| README 5번 실행 | `ollama pull` 새 모델 · 슬랙 앱 `files:read` · `evaluate.py photo` · 자주 막히는 곳(사진이 안 옴 = 권한 · 재설치) |
| README 6번 한계 | 사진 쪽에서 실제로 본 것(오인식 · 물건 여러 개 · 어두운 사진 등 — 6장 실측으로) |
| README 필수 요건 대조 · 제출 체크리스트 | VRAM 실측 갱신 · 사진 기능 · 새 캡처 항목 |
| CONTEXT | «범위 밖» 의 사진 줄 → 범위 안(대신 «물건 여러 개 · 사람 얼굴 사진» 같은 새 범위 밖) · 처리 흐름에 사진 갈래 · 관측(사진 trace) · 하드웨어 · 위험(오인식 → 되묻기) · **사진 실측 부록** |
| `docs/architecture.md` · `docs/scenarios.md` | 사진 흐름 Mermaid · 사진 시나리오(확신 · 애매 · 범위 밖) |

| 캡처 (사용자가 찍어 ZIP 으로) | 파일 (제안) | 들어갈 곳 |
|---|---|---|
| 슬랙에 사진 → 📷 + 답 + 📚 근거 | `docs/slack-photo.png` | README 2번 |
| 애매할 때 되묻기 | `docs/slack-photo-ask.png` | README 2번 (선택) |
| LangSmith `recycle-photo` — `describe-photo` → `RecycleRetriever` → `generate` | `docs/trace-photo.png` | README 4번 |
| 다시 찍기 — 새 모델로 텍스트 질문 · 비교 | `trace-rag.png` · `trace-retriever.png` · `slack-thread.png` · `slack-compare.png` | README 2 · 4번 (7-2) |

## 8. 위험 · 열린 질문

| 위험 | 대응 |
|---|---|
| Qwen3.5 는 생각 모드가 기본 ON · 4B 가 간단한 질문에도 오래 생각한다는 보고 · `reasoning=False` 로 확실히 꺼지는 검증 사례를 못 찾음 | 6-1 의 2단계에서 `--ids scratch` 로 먼저 확인 |
| Gemma 4 E4B 의 실제 VRAM 이 출처마다 엇갈림 | 6-1 의 3단계 실측 · 넘치면 QAT 태그 → `e2b` |
| 한국어 «품목 이름 붙이기» 실력은 어느 후보도 공식 근거가 없음 | 6-2 사진 세트로 실측 |
| 사진이 LangSmith trace 에 올라감 (base64 · 용량 · 개인정보) | 사진 입력은 trace 에서 숨기거나 README 3번 «보안» 에 밝힘 — 구현 때 결정 |
| Ollama 버전 — 지원 버전은 릴리스 모음 사이트 기준 | 6-1 의 0단계에서 `ollama pull` 로 확인 |
| 일정 — 13주차(11/27) 중간 점검 · **14주차(12/4) 최종 제출 · 제출은 이 저장소** | 구현 → 측정 → 채택 → 문서 · 캡처 순. 사진 코드는 작업 브랜치에서, `main` 반영은 측정 · 문서까지 끝난 뒤 |

## 부록 — 검토했지만 고르지 않은 것 (2026-11-20)

| 대안 | 고르지 않은 이유 |
|---|---|
| **RAG 에 없으면 웹 검색** | 출처 없는 블로그 답을 다시 끌어옴(README 1번과 충돌) · 외부 검색 API 키 · «질문이 외부로 안 나감»(README 3번)이 깨짐 · 웹페이지 간접 주입 위험 · «자신 있게 틀린» 답(생수병)에는 켜지지도 않음 |
| AI 허브 분리배출 데이터 + YOLO 분류기 | **재질 수준**(종이 · 비닐 · 페트병 …) — «영수증 = 종이» 처럼 품목별 예외를 틀리게 만듦 · 직접 학습 필요 |
| HyperCLOVA X SEED Vision 3B · Omni 8B (네이버) | Ollama 비전 미지원 · 네이버 자체 라이선스 · Omni 는 자체 서빙 엔진 |
| VARCO-VISION-2.0-1.7B (NCSOFT) | 한국어 사진 벤치마크는 좋으나(K-MMBench 77.9) KMMLU 10.4 로 글 답에 약함 · Ollama 미확인 · 라이선스 출처 엇갈림 |
| EXAONE 4.5 (LG · 33B) · Moondream 3 (9B MoE) | 8GB 에 안 맞음 / 자체 엔진 |
| Kanana-2 비전 인코더 426M · 98M (카카오 · 2026-10) | 인코더만 — 혼자서는 답을 못 함. CLIP 처럼 쓸 수 있는지 미확인 |
| CLIP 계열 zero-shot (MetaCLIP 2 · SigLIP 2 · jina-clip-v2) | **보류** — «문서 품목 이름 약 380개 중 고르기» 라 지어낼 수 없고 CPU 로도 됨. 단 PyTorch 계열 새 패키지 필요 · 한국어 세밀 구분 근거 없음 · jina 는 비상업 라이선스 |
| 멀티모달 임베딩 (Qwen3-VL-Embedding-2B · Apache 2.0 · 30개 이상 언어 · MMEB-V2 약 73) | **보류** — 사진으로 바로 검색할 수 있어 깔끔하지만 두 번째 인덱스 · Ollama 불가(이미지 경로는 수정판 llama.cpp 또는 Transformers) |

## 출처

- 모델: [Ollama qwen3.5](https://ollama.com/library/qwen3.5) · [Qwen/Qwen3.5-4B](https://huggingface.co/Qwen/Qwen3.5-4B) · [gemma4:e4b (Ollama)](https://ollama.com/library/gemma4:e4b/blobs/4c27e0f5b5ad) · [Gemma 4 Quickstart](https://ai.google.dev/gemma/docs/get_started) · [Gemma 4 E4B 하드웨어 요구](https://www.llamabuilds.ai/models/gemma-4-e4b) · [Ollama ministral-3](https://ollama.com/library/ministral-3:8b) · [Ollama minicpm-v4.5](https://ollama.com/library/minicpm-v4.5) · [Qwen 3 VL 로컬 설정](https://localaimaster.com/blog/qwen-3-vl-local-setup)
- 한국어 모델: [skt/A.X-4.0-VL-Light](https://huggingface.co/skt/A.X-4.0-VL-Light) · [configuration_ax4vl.py](https://huggingface.co/skt/A.X-4.0-VL-Light/blob/main/configuration_ax4vl.py) · [HyperCLOVAX-SEED-Vision-Instruct-3B](https://huggingface.co/naver-hyperclovax/HyperCLOVAX-SEED-Vision-Instruct-3B) · [HyperCLOVAX-SEED-Omni-8B](https://huggingface.co/naver-hyperclovax/HyperCLOVAX-SEED-Omni-8B) · [VARCO-VISION-2.0-1.7B](https://huggingface.co/NCSOFT/VARCO-VISION-2.0-1.7B) · [EXAONE 4.5](https://huggingface.co/LGAI-EXAONE/EXAONE-4.5-33B) · [카카오 Kanana-2 비전 인코더 보도](https://www.digitaltoday.co.kr/en/view/117407/kakao-releases-two-kanana-2-vision-encoder-models-as-open-source)
- 운영: [Ollama Thinking 문서](https://docs.ollama.com/capabilities/thinking.md) · [ChatOllama `reasoning`](https://reference.langchain.com/python/langchain-ollama/chat_models/ChatOllama/reasoning) · [Qwen3.5 4B 과잉 생각 보고](https://aiproductivity.ai/news/qwen35-4b-overthinking-simple-prompts/) · [Ollama FAQ (KV 캐시 압축)](https://docs.ollama.com/faq) · [Ollama 릴리스 기록](https://releases.sh/ollama) · [Ollama 이슈 #14730 (직접 가져온 비전 GGUF)](https://github.com/ollama/ollama/issues/14730)
- 방법: [불확실성 기반 라우팅 (Confident or Seek Stronger)](https://arxiv.org/abs/2502.04428) · [WasteAssistant (규정 기반 분리배출 사진 질의응답)](https://arxiv.org/abs/2607.10610) · [W2R 2단계 인식-검색](https://www.sciencedirect.com/science/article/abs/pii/S0921344921001506) · [MetaCLIP 2](https://huggingface.co/papers/2507.22062) · [Qwen3-VL-Embedding-2B](https://huggingface.co/Qwen/Qwen3-VL-Embedding-2B) · [AI허브 생활 폐기물 이미지](https://aihub.or.kr/aidata/27708)
