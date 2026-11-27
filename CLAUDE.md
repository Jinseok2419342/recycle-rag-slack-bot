# CLAUDE.md — 버릴지도 (분리배출 안내 RAG 슬랙 봇)

이 파일은 다음 세션의 Claude Code 가 이 프로젝트를 처음 보고도 이어서 작업할 수 있게 쓴 인수인계 문서입니다.
**읽는 순서: 이 파일의 «▶ 다음 세션은 여기부터» → 나머지는 필요할 때.** [README.md](README.md) · [CONTEXT.md](CONTEXT.md) 가 채점 대상,
[SPEC.md](SPEC.md) (구현 지시서 · 약 1200줄) 는 코드 · 설계 세부가 필요할 때만 봅니다.
그림으로 먼저 보려면 [docs/architecture.md](docs/architecture.md) (구성도 · 흐름도) · [docs/scenarios.md](docs/scenarios.md) (시나리오).

## 한 줄 요약

슬랙에서 «뽁뽁이 어떻게 버려?» 라고 물으면, 분리배출 PDF 2건에서 근거를 찾아(RAG) 배출 방법 + 출처(품목 · 문서 · 연도 · 쪽)를 스레드에 답하는 봇.
동양미래대 «최신인공지능» 수업(학번 20241499) 미니 프로젝트. **응답은 한국어로.**
수업 저장소의 `mini_project/` 를 2026-11-20 에 커밋 기록째 옮겨 온 **독립 저장소**입니다(아래 «저장소 두 곳»).

## ▶ 다음 세션은 여기부터 (2026-11-27 기준)

**상태: 채점 기준이 바뀜(13주차 «최종 제출 안내» 0절 · 11-25 변경) → 🔗 이어 묻기 구현 · 테스트표 · 문서를 새 기준으로 고침 (작업 브랜치 `photo-feature`).
✅ 캡처 3종(`captures/` · 2026-11-27 사용자 촬영 · 확인함) · CONTEXT 부록 F 새로 씀.
남은 것 = ① MCP 도구 1개(권장 · 사용자 결정: 이어 묻기 다음에) ② `main` 반영(GitHub Desktop) · 사용자가 최종 보고서에 저장소 링크 ③ `docs/` 옛 캡처 4장 삭제 여부(사용자 확인).**
마감 **12/4(14주차) 3교시 전** · 제출처는 추후 공지.

- **새 채점 기준 (2026-11-25 변경 · 원본은 사용자가 저장소 맨 위에 둔 `[13주차]학생용_미니프로젝트_최종제출_안내.html` — 수업 자료라 커밋 안 함)**
  - 범위: «내 자료로 RAG 가 동작하는 슬랙 봇» · **LangSmith 추적 · 캡처는 요건에서 빠짐** · MCP 도구 1개 이상은 **권장** · 승인 · 진행 표시 · 멀티 에이전트는 선택(점수 없음)
  - 제출물: 코드는 **GitHub 링크를 최종 보고서에** / README(10주차 6항목 + **7번 테스트표**) / CONTEXT(대상 문서) / **캡처 3종 `captures/`**: ① `--show` ② 터미널 ③ 슬랙(질문 3개 이상 · 📚 · 같은 스레드 «그럼 · 그거» 이어 묻기 1개)
  - 채점은 «돌아가는가 · 스스로 확인했는가» — **틀린 답을 찾아 적으면 점수** (README 6번: 틀린 답 + 검색 문제인지 생성 문제인지)
  - «기준 코드 `13week_new/code/slack_bot/`» → 사용자 결정(11-27): **우리 코드 유지 + 기준 코드의 ① 스레드 기억(`contextualize`) 방식 이식**. 둘 다 10주차 `slack_bot_mode` 에서 나온 형제라 README 4번에 파일 대응표
  - 수업 코드 사본은 `old_codes/<날짜>/` (사용자가 넣음 · `.gitignore` 의 `/old_codes`) — 기준 코드 = `old_codes/11-27/slack_bot/`
- **2026-11-27 에 한 일**
  - PC 가 초기화돼 있었음(함정 30) → venv · 사례집 · 모델 3개 다시 준비(KURE 는 이번엔 `ollama pull` 이 4.7MB/s 로 됨 · sha256 `055cd596…` 같음) · 인덱스 456청크
  - 수업 `.env` 의 `LANGSMITH_AGENT_*` 때문에 trace 가 버려지던 것 → `config.py` 가 지움(함정 29 · SPEC 13-1 p · 커밋 `c88b2fc`)
  - **🔗 이어 묻기** (SPEC 13-1 q): `rag_backend` 의 `FOLLOW_UP` · `contextualize_run` · `ask_full(history=)` · `대화` 모드 / `slack_rag_bot` 스레드 기억 · «🔗 앞 대화로 «…» 로 이해했어요» 줄. `offline_check` **84항목** ALL OK
  - 실측(CONTEXT 부록 H): 이어 묻기 풀어 쓰기 **5/5** 맞음 · 답 3/5 / 테스트표 **3/5** — 틀린 것은 «택배 상자» · «돌돌이 리필 다 쓴 건 어디다 버림?»(둘 다 검색 문제) · 생성 문제 예 «우유팩 → 그거 일반 종이랑?»
  - 문서: README(2 · 4 · 5 · 6번 · **7번 테스트표** · 제출 캡처 · 최종 제출 기준 대조 · 체크리스트) · CONTEXT(처리 흐름 · 관측 선택 · 범위 밖 · 위험 · 부록 H) · architecture · SPEC · `.env.example`
  - **옛 캡처**: `docs/slack-thread.png` · `slack-compare.png` · `trace-rag.png` · `trace-retriever.png` 는 옛 생성 모델 시절(11-19) 화면이라 README 에서 **참조를 뺌**(파일은 남아 있음 — 지울지는 사용자 확인). `trace-build.png` 만 예로 남김
- **▶ 다음에 할 일** (이 순서로)
  1. ✅ (2026-11-27) 봇을 새 코드로 다시 켬 → 캡처 3종 받음 · README 캡션 · CONTEXT 부록 F 반영.
     ③ 슬랙 캡처에는 사용자 슬랙 이름 · 채널 이름이 보임(토큰 · ID 없음 · 수업 제출용이라 그대로 — 가리고 싶다고 하면 잘라 내기)
  2. (선택 · 사진) `captures/3-slack-photo.png` 는 찍지 않아 README 에서 뺌 — 사진 질문은 11-24 슬랙 확인 기록 · 맨 위 그림(터미널 실제 출력)으로 설명
  3. **MCP 도구** — 사용자 결정(11-27): 이어 묻기 다음에. 설계안: `@봇 메모 …` 같은 **앞말로만** 도구 갈래(지금 `검색` · `비교` 처럼 · RAG 경로는 그대로) ·
     도구 모델 = gemma4:e4b(`ollama show` 에 tools ✅ · VRAM 추가 없음) · 도구 = «우리 동네 배출 요일 메모» 저장 · 보기 · 새 패키지 `fastmcp` · `langchain-mcp-adapters`(설치 승인됨) ·
     기준 코드 `old_codes/11-27/slack_bot/mcp_server.py` · `bot_graph.py`(`tool_agent` · `MAX_TOOL_ROUNDS` · 소형 모델 안전장치) 참고 → 넣으면 캡처 ② 에 도구 호출 질문 1개
  4. 검사(`--check` · `offline_check` · README 이미지 링크 존재) → 커밋 → `main` (함정 28: CLI push 막힘 → GitHub Desktop)
- **캡처 3종 안내 (사용자에게 줄 것)** — 저장 위치 `captures/` (저장소 맨 위 · 커밋함) · 파일 이름 그대로
  - ① `1-index-show.png`: `.\venv\Scripts\python.exe build_index.py --show` 의 위쪽(구역별 청크 수 표 + 첫 청크들의 metadata `source` · `page`)
  - ② `2-terminal.png`: `.\venv\Scripts\python.exe rag_backend.py 대화 "형광등은 어떻게 버려요?" "그럼 깨진 건 어떻게 해?"` 출력 전체(경로 · 🔗 · 📚)
  - ③ `3-slack.png`: 채널에서 `@Jinseok-20241499-Bot 형광등은 어떻게 버려요?` → 그 답의 스레드에서 `@Jinseok-20241499-Bot 그럼 깨진 건 어떻게 해?` →
    `@Jinseok-20241499-Bot 우유팩은 어떻게 버려요?` → `@Jinseok-20241499-Bot 강남구는 재활용 무슨 요일에 내놔?` (📚 붙은 답 3개 + 이어 묻기 + 자료에 없는 것)
  - (선택) `3-slack-photo.png`: 사진(`photos/c2.jpg`) + `@Jinseok-20241499-Bot 이거 어떻게 버려?` — README 2번이 가리킴 · 안 찍으면 README 에서 그 줄을 뺄 것

### (참고) 2026-11-24 기준이던 내용

수업 PDF 의 필수 요건은 2026-11-19 에 이미 충족(`main`). 이번 작업은 그 위에 사진 기능 + 생성 모델 교체를 얹은 것입니다.

- **채택 구성 (2026-11-24 사용자 결정)** — 생성 **`gemma4:e4b`** · 사진 **`qwen3.5:4b`** (`PHOTO_MODE=pick` — 문서 품목 이름 377개에서 고르기) · 임베딩 KURE-v1 그대로
  - 텍스트 30문항: 수업 기본 `gemma3:4b` 15/30 · 자기모순 11 → **gemma4:e4b 29/30 · 자기모순 1 · 범위 밖 4/4 · 입력검증 2/2** (`qwen3.5:4b` 25/30 은 범위 밖 2/4 로 탈락)
  - 사진(AI 생성 20장 + 범위 밖 4장): **16/20** (합격선 15) · 범위 밖 **2/4** (기준 4/4 미달 → README 6번 한계로 기록 · 사용자 결정) · 사진 1장 4.1초
  - VRAM: 세 모델 함께 nvidia-smi **7.6 ~ 7.7GB** · 셋 다 100% GPU (파일 크기 합 9.8GB 인데 들어감 — gemma4 층별 임베딩을 GPU 밖에 두는 것으로 추정)
  - 결과 전체 · 계획과 달라진 점: [docs/photo-feature-plan.md](docs/photo-feature-plan.md) 맨 위 «결과» · CONTEXT 부록 C · E · G
  - **문서 방침**: README · CONTEXT · docs 를 새 모델 기준으로 다시 씀 (A.X 는 언급하지 않음 · 비교군 `gemma3:4b`) — 2026-11-24 완료.
    사진은 **AI 생성 이미지** · 지시문을 **같은 사진으로 고침**(v1 → v2) · 새 사진 세트로 다시 재지 않음 → README 6번 · 부록 G 에 밝힘
- **▶ 세션 시작 순서** — 사용자가 «CLAUDE.md 보고 시작하자» 라고 하면
  1. `git status` · `git log --oneline -3` — 브랜치 `photo-feature` 인지, 끝 커밋이 이 파일을 고친 커밋인지 확인.
     `git status -sb` 의 `[ahead N]` 이 남아 있으면 사용자가 GitHub Desktop 에서 Push origin 을 아직 안 누른 것 → 부탁
  2. `ollama list` · `Test-Path venv` (함정 30 — PC 가 초기화됐을 수 있음) · `captures/` 에 png 3종이 있는지 확인 — 없으면 3번
  3. 봇을 백그라운드로 켜고(PowerShell · `run_in_background`) Monitor 로 «워밍업|Bolt app is running|받음|답함|실패|Traceback» 줄을 지켜봄:
     `$env:PYTHONUTF8=1; [Console]::OutputEncoding=[Text.Encoding]::UTF8; $env:Path += ";$env:LOCALAPPDATA\Programs\OllamaAIClass"; .\venv\Scripts\python.exe -u slack_rag_bot.py 2>&1`
     (그 전에 `ollama ps` 로 GPU 비우기 · 함정 25). «워밍업 ✅» · «Bolt app is running!» 이 나오면 사용자에게 아래 캡처 안내를 **한 단계씩** 드림
  4. 오늘 할 일이 끝나면 봇을 TaskStop 으로 끔
- ~~캡처 안내 (2026-11-24 판 · 11-25 기준 변경으로 쓰지 않음 — 위 «캡처 3종 안내» 가 대신함)~~ — 저장 위치 `captures_raw\`
  - 슬랙 (봇 이름 `@Jinseok-20241499-Bot` · 함정 18) — 각 질문 뒤 스레드를 열어 답까지 보이게 캡처
    - `slack-thread.png`: `@Jinseok-20241499-Bot 아이스팩 어떻게 버려?` (같은 스레드에 `검색 선글라스` · 빈 멘션 · `강남구 재활용 요일?` 을 이어서 물으면 한 장에 여러 기능)
    - `slack-compare.png`: `@Jinseok-20241499-Bot 비교 마트 영수증은 종이로 버려도 돼?` → README 4번 캡션의 «RAG 없이» 인용을 실제 화면 문장으로 바꿀 것
    - `slack-photo.png`: 물건 사진(예: `photos/c2.jpg` 아이스팩) + `이거 어떻게 버려?` 를 함께 보냄 → 📷 줄 · 답 · 📚 · 🔁 다른 후보가 보이게
  - LangSmith — 프로젝트 `recycle-bot-20241499` · **metadata 탭(slack 사용자 · 채널 ID)은 찍지 않음**
    - `trace-rag.png`: `recycle-rag` trace 를 열어 왼쪽 트리(`RecycleRetriever` · `generate`)가 보이게
    - `trace-retriever.png`: 그 트리에서 `RecycleRetriever` 를 눌러 검색된 문서 3개 · 거리가 보이게
    - `trace-photo.png`: `recycle-photo` → `describe-photo` 를 눌러 입력에 «<image … bytes — 추적에 올리지 않음>» 이 보이게
  - 다 넣으면 사용자가 «캡처 다 넣었어» 라고 함
- (2026-11-24 판 «다음에 할 일» — 1 · 2번은 위 11-27 판으로 바뀜 · 3 · 4번 선택 과제는 그대로 유효)
  1. ~~캡처 6장~~ — 사용자가 `captures_raw/`(gitignore)에 넣음: `slack-thread` · `slack-compare` · `slack-photo` · `trace-rag` · `trace-retriever` · `trace-photo` (.png).
     README 2 · 4번이 이 이름을 이미 가리킴 → 받으면 눈으로 확인(슬랙 ID · 개인정보가 없는지) → `docs/` 로 복사 → README 캡션을 실제 화면 내용에 맞춤
     (`trace-build.png` 는 모델과 무관해 그대로). 캡처 때 봇 콘솔의 «받음/답함» 줄로 CONTEXT **부록 F(슬랙 왕복)** 를 2026-11-24 값으로 다시 씀 — 지금은 11-17(옛 모델) 표가 남아 있음
  2. 검사: `build_index.py --check` · `tests/offline_check.py`(71항목) · 문서 링크 · README 의 이미지 6개 존재 → 커밋 → **`main` 반영**.
     이 PC 는 CLI push 가 막혀 있음(함정 28) → 로컬에서 `git branch -f main photo-feature`(fast-forward 인지 `git merge-base --is-ancestor main photo-feature` 로 먼저 확인)
     → 사용자에게 «GitHub Desktop 에서 Current branch 를 `photo-feature` 로 두고 Push origin → `main` 으로 바꾸고 Push origin → 다시 `photo-feature` 로» 를 부탁
  3. (선택) 시나리오 8(Ollama 끄기) · 새 사진 세트로 사진 다시 재기 · 범위 밖 사진 개선
  4. (선택) **검색 · 인덱스 점검** — 사용자가 2026-11-24 에 «KURE 나 인덱싱이 부족한 것 아니냐 · 찾을 것 같은 걸 못 찾고 뭘 더하면 찾는다» 고 물음. 그날 확인한 것:
     - 텍스트 검색은 Top-3 23/24 — 넓게 부족하진 않음. 놓친 1건이 **y2 생수병**: `검색 "생수병"` 의 1 ~ 3위가 위스키병 · 유리병 · 페트병, 정답(사례집 p.13 «무색 플라스틱 물병» · 본문은 «먹는 샘물»)은 3위 밖.
       문서에 «생수» 라는 낱말이 없어 임베딩이 «병» 에 끌림 = **질문 말 ↔ 문서 말이 다른 문제**(동의어). 사진은 비전 모델이 문서 목록의 «무색페트병» 을 골라 넣어 주니 찾음 — «더하면 찾는» 이유
     - 사진 16/20 에서 놓친 4장은 인덱스가 아니라 **이름 붙이기** 실수(c3 모름 · c5 신문지 · y1 유리병 — 정답 품목은 목록에 있음) + s7(답은 맞음 · 채점 위치 차이)
     - **인덱스 쪽 실제 흠**: 품목사전 `item` 이름 중 문장 조각이 붙은 것 6개 — «우산 뼈대와 비닐을» · «약 종류 약국, 보건소 등의» · «비디오테이프 내부 필름은» ·
       «젖병 (아기용품) 젖병의 몸체와 윗부분의 젖꼭지는» · «(우유팩 등) 내부에 알루미늄박이 붙어 있다면» · «체온계(건전지, 디지털) 건전지는» (`split_item_dict` 의 줄 나누기 · 사진 pick 목록 377개에도 그대로 들어감)
     - 해 볼 만한 것(한 번에 하나씩 · `evaluate.py retrieval` · `photo` 로 재기): ① 위 6개 이름 고치기(`--check` 기준이 바뀌므로 수치 확인) ② 동의어에 약한 문항을 평가 세트에 더 넣어 진짜 약점 크기부터 재기
       (지금 24문항은 품목 이름을 그대로 쓴 질문이 많아 약점이 덜 보임) ③ 재정렬 모델(reranker) — VRAM 여유가 0.3GB 뿐이라 CPU 로 ④ 다른 임베딩(bge-m3 등)과 비교.
       동의어를 청크에 직접 넣는 방식은 평가 문항에 맞춘 꼼수가 되기 쉬우니 피할 것 (함정 9 와 같은 이유)

- **저장소 두 곳** (2026-11-20)
  - **이 저장소 `recycle-rag-slack-bot` 이 원본이자 제출본** — 앞으로의 수정은 여기에만 · 14주차(12/4) 최종 제출도 이 저장소로 (2026-11-20 사용자 결정)
  - 수업 저장소 [`langchain-2026-20241499`](https://github.com/Jinseok2419342/langchain-2026-20241499) 의 `mini_project/` 는 2026-11-19 상태(커밋 `944b556`)로 **동결 · 수정하지 않음**.
    이 저장소의 커밋 `7431143` 이 그 상태와 바이트 단위로 같음 (원본 히스토리 13개의 끝)
  - 강의 PDF · 수업 실습 코드(`11-06/` · `11-13/` · `10-30/` …)는 **수업 저장소에만** 있음 — 이 문서 · SPEC 의 `11-06/…` 표기는 그 저장소 경로.
    문서의 링크는 수업 저장소 커밋 `59cd1d3` 에 고정. 클라우드 세션에서 읽어야 하면 `add_repo` 로 수업 저장소(public)를 붙임
- **판단 기준 (사용자가 정함)** — «수업 자료의 형식 · 요건을 충족하는가» 가 전부입니다.
  기준 문서(수업 저장소): [`11-06/2교시_분할_메타데이터와_프로젝트_착수.pdf`](https://github.com/Jinseok2419342/langchain-2026-20241499/blob/59cd1d32546a399a8c8cfeb17bfc6110fc5343c3/11-06/2%EA%B5%90%EC%8B%9C_%EB%B6%84%ED%95%A0_%EB%A9%94%ED%83%80%EB%8D%B0%EC%9D%B4%ED%84%B0%EC%99%80_%ED%94%84%EB%A1%9C%EC%A0%9D%ED%8A%B8_%EC%B0%A9%EC%88%98.pdf) §4-1 ~ §4-4 (23 ~ 29쪽) · [`11-06/project_template/`](https://github.com/Jinseok2419342/langchain-2026-20241499/tree/59cd1d32546a399a8c8cfeb17bfc6110fc5343c3/11-06/project_template) 의 `README.md` · `CONTEXT.md`.
  README 끝의 «필수 요건 대조» 표 · «제출 체크리스트» 가 이것과 맞춰져 있습니다(2026-11-19 전부 ✅ 확인).
  모델 성능을 더 깊게 재검증하거나, 메인 PC(한글 경로)에서 다시 세팅할 필요는 **없다** 고 사용자가 결정함 — 같은 사양의 보조 PC 에서 처음부터 세팅해 통과했음.
- **남은 것**: 위 «▶ 다음에 할 일». 시나리오 8(Ollama 를 끈 상태의 오류 처리)은 SPEC 6-5 에 스스로 적어 둔 점검 항목일 뿐 **수업 요건이 아님** — 사용자가 원할 때만.
- **이 PC (2026-11-24 세션 · 다른 PC 에서 열렸으면 `venv` · 모델 3개 · 사례집 · `.env` 부터 — README 5번 · 아래 «실행 순서» 0번)** — Windows 11 · RTX 3070 8GB · 경로 `C:\Users\USER\Documents\GitHub\recycle-rag-slack-bot` (영문) · Ollama 0.32.14 가 PATH 밖(함정 19와 같은 위치).
  11-17 의 보조 PC 와 다른 PC 일 수 있음(모델이 하나도 없었음 — `gemma3:4b` · `exaone3.5:2.4b` 만). 이번에 venv · 사례집 · 모델 4개(`gemma4:e4b` · `qwen3.5:4b` · `qwen3.5:0.8b` · KURE)를 새로 준비함.
  `.env` 는 사용자가 새로 만듦 · 슬랙 봇 토큰 scope: `chat:write` · `chat:write.public` · `app_mentions:read` · `im:read` · `im:history` · `files:read` (auth.test 로 확인)
- **사용자와 일하는 방식**
  - 한국어로 **쉽게 · 한 단계씩**. 화면(LangSmith · 슬랙) 조작을 안내할 때는 사용자 화면 캡처를 받아 실제 버튼 이름으로 안내
  - 사용자가 직접 해야 하는 설정(`.env` · 슬랙 앱 권한 등)은 **어디서 무엇을 누르는지까지 세세히** 안내 (2026-11-24 사용자 요청). «테스트 사진» 처럼 처음 듣는 말은 왜 필요한지부터 설명
  - 사용자는 GitHub Desktop 을 씀 — CLI push 가 안 되는 PC 에서는 «GitHub Desktop 에서 Push origin» 으로 부탁
  - 커밋 작성자는 **사용자 계정** — 기존 커밋과 같은 작성자(`git log --format='%an <%ae>' -3` 로 확인 · `Jinseok2419342`)를
    `git -c user.name=… -c user.email=… commit` 으로 지정. `Co-Authored-By` · `Claude-Session` 같은 **Claude 서명 줄은 넣지 않음** (사용자 요청 · 하네스 기본 안내보다 우선)
  - **커밋 · 푸시 · `main` 반영은 묻지 않고 알아서** (2026-11-20 사용자: «반영할까 물어보지 말고 알아서 해») — 검증(`--check` · `offline_check` · 링크)을 통과한 것만.
    `main` 은 작업 브랜치에서 fast-forward(`git push origin HEAD:main`). 사진 기능 코드는 측정 · 문서까지 끝난 뒤 `main`.
    **파일 삭제 · `.env` 수정 · 슬랙 앱 설정 · 모델 pull 같은 사용자 PC 작업은 여전히 사용자 확인 뒤**
  - 커밋 메시지는 한국어 · **접두어 없이** (수업 저장소 시절 커밋은 `mini_project: …`)
- **클라우드 세션(claude.ai/code)에서 열었을 때** — GPU · Ollama · 루트 `.env` 가 **없습니다** (파이썬 패키지 · 68MB 사례집 PDF 는 아래 «클라우드 환경» 이면 준비 가능).
  모델 · 슬랙 · LangSmith 실행은 못 하고 문서 · 코드 읽기와 수정만 됩니다. 실행이 필요하면 사용자가 보조 PC 에서 돌리고 결과(캡처 · 출력)를 줌.
  `kwaste.or.kr`(사례집 PDF 받는 곳)은 기본(Default) 클라우드 환경에서 막혀 있음 → 아래 «클라우드 환경». 세션이 끝날 때 «커밋 안 된 변경» 훅이 돌면 작업 브랜치까지만 푸시하고 `main` 은 확인 뒤에 반영
- **클라우드 환경 «버릴지도 (분리배출 RAG 봇)»** (2026-11-20 사용자 승인 · 개인 환경) — `www.kwaste.or.kr` 허용 +
  설치 스크립트(맨 위에 `venv` 만들고 `requirements.txt` 설치). 이 환경으로 시작한 세션에서는 사례집을 받아
  `./venv/bin/python build_index.py --check` · `tests/offline_check.py` · `questions.py` 까지 돌릴 수 있음 (모델 · 슬랙은 여전히 안 됨).
  설치 스크립트는 같은 명령을 손으로 돌려 확인했지만, 새 세션에서 자동으로 도는 것은 아직 못 봄 →
  다음 세션도 이 환경이면 좋지만(세션 제목줄의 클라우드 환경 메뉴), **사용자가 따로 고를 필요는 없음** — 기본 환경으로 열리면 «세션 시작 순서» 1번에서 옮기자고 제안.
  자동 설치가 됐는지는 그 1번에서 확인해 이 줄에 적을 것
- **이미지를 받을 때** — 채팅에 붙인 이미지는 폭 2000px JPG 로 줄어듦 → 문서에 넣을 원본은 **ZIP 으로** 받기 (scratchpad 의 새 폴더에 풀고 `__MACOSX` 는 버림)
- **2026-11-19 에 한 일** — CLAUDE.md 깨진 곳 복구 · 미결 2 · 3 · 8 반영 · LangSmith 3장 + 슬랙 2장 캡처(`docs/*.png` · README 2 · 4번) ·
  `not_done_plan.md` 삭제 · 옛 문장 정리 · 이 절 추가. 모두 사용자 계정으로 `main` 에 반영
- **2026-11-20 에 한 일 — 독립 저장소로 옮김** (수업 저장소는 건드리지 않음)
  - `git subtree split --prefix=mini_project` 로 커밋 13개를 날짜 · 메시지 그대로 가져옴 (끝 = `7431143`).
    태그 `imported-from-class-repo` 는 만들었지만 클라우드 세션의 프록시가 태그 push 를 막아(403) 원격에는 없음 — 원하면 사용자가 붙임
    옛 커밋 2개(11-06 · 11-13)의 깨진 작성자 이름(터미널 화살표 키 입력이 섞임)만 `Jinseok2419342` 로 고침
  - 그 위에 커밋 5개: `.gitignore` 새로 · 코드 속 경로 안내 문구(**로직 0줄** — 문자열만 뺀 AST 비교로 확인) ·
    문서 경로와 수업 저장소 고정 링크(`59cd1d3`) · 이 파일 · `pypdf==6.21.4` 고정(7.x 에서 `--check` 실패 — 함정 22)
  - 옮기며 바로잡은 것: `offline_check.py` 가 `index_recycle/` 을 덮어쓴다는 안내(틀렸음 — 아래 진행 기록) · architecture.md 줄 수 표
  - ✅ **옮긴 뒤 확인** (클라우드 · 위 환경에서 사례집 68,862,868바이트를 받아 · 새로 만든 venv · pypdf 6.21.4) —
    `build_index.py --check` 15항목 ✅ · 456청크 / `tests/offline_check.py` ALL OK (40항목) / `questions.py` ✅ → README 5번 머리에 기록.
    pypdf 7.1.1 로는 `--check` 실패(457청크 · ITEM_DROP 3/4 · 종료 코드 1)도 재확인. 모델 단계(임베딩 · 답 · 슬랙)는 로직이 그대로라
    다시 안 돌림 — 보조 PC 를 쓸 수 있을 때 원하면 `build_index.py` · `rag_backend.py 검색 "선글라스"` 로 확인
  - 다음 기능 검토 → **사진으로 묻기** 로 정함 (웹 검색 보충안은 기각) · 모델 후보 조사 → [docs/photo-feature-plan.md](docs/photo-feature-plan.md) (코드 미반영)
  - 제출 저장소 = 이 저장소로 정함 · 계획 문서에 구현 설계(5-2 · 5-3) · 새 기능 문서 · 캡처 목록(7-3) 추가 · 이 파일에 «다음 세션 시작 순서» · `main` 반영은 알아서

## 진행 기록 (2026-11-17 첫 실행 · 2026-11-19 마무리)

> ★ **2026-11-17 에 실제 모델로 처음 돌렸습니다** — 메인 PC 와 사양이 같은 보조 PC(RTX 3070 8GB · Ollama 0.32.14 · Python 3.13.3 · 영문 경로 클론).
> 인덱스 생성 → 터미널 → 슬랙(멘션 · DM) → LangSmith → 평가 E1~E4 까지 통과. 아래 «2026-11-17 첫 실행 결과» 참고.
> 기본값 채택(`basic` · `year_bonus 0.09` · `base`)과 문서 갱신(README 5 · 6 · CONTEXT 부록 D ~ F · scenarios)까지 끝났습니다.
> ★ **2026-11-19 캡처 5장을 README 에 넣음** (LangSmith 3장 · 슬랙 2장 · `docs/*.png` · SPEC 13-1 l) → 수업 PDF 필수 요건 전부 충족.
> **남은 것: 없음** (시나리오 8 은 자체 점검 항목 · 선택). 미결 8 은 README 에 안내 한 줄로 정리(2026-11-19).
> → 2026-11-20 에 다음 작업으로 «사진으로 묻기» 를 정함 (맨 위 «▶ 다음 작업»).

| 단계 | 상태 |
|---|---|
| 10주차 명세 (README 1~4번 + CONTEXT.md) | ✅ 완료 · 제출됨 |
| 상세 구현 명세서 [SPEC.md](SPEC.md) | ✅ 완료 — 구현하며 달라진 점은 13-1절 (k: 임베딩 64개씩) |
| **코드 작성** (M1~M4 분량 · 파일 9개) | ✅ 작성 · **실제 모델로 검증** (2026-11-17) |
| 구성도 · 가상 시나리오 (`docs/`) | ✅ 작성 · 2026-11-17 실측으로 갱신 (시나리오 8 의 Ollama 끄기만 «예상») |
| **M0 사전 준비** (모델 pull · `.env`) | ✅ 보조 PC 에서 완료 (메인 PC 재세팅은 하지 않기로 함 · 2026-11-19) |
| **첫 실행** (인덱스 생성 → 터미널 → 슬랙) | ✅ 2026-11-17 — 슬랙 멘션 · DM · `검색` · `비교` · 빈 멘션 · 범위 밖 왕복 |
| 평가 실측 → 기본값 채택 (M4) | ✅ E1~E4 측정 (`eval_results/`) → `config.py` 기본값 `basic` · **`year_bonus 0.09`** · `base` (사용자 승인 2026-11-17). CONTEXT 부록 D · E 반영됨 |
| README 5 · 6번 · 문서 갱신 · LangSmith 캡처 (M5) | ✅ 2026-11-17 — README 5 · 6번 작성 · 맨 위 그림 · 2 · 3 · 4번 실측 반영 / CONTEXT 분할 · 메타데이터 · 처리 흐름 · 관측 · 위험 갱신 + 부록 C 복구 · **D · E · F 추가** / `docs/scenarios.md` 예상 → 실측. 2026-11-19 캡처 5장 README 반영 |

### 2026-11-17 첫 실행 결과 (실측 · 보조 PC)

| 항목 | 값 | 파일 |
|---|---|---|
| 인덱스 | 456청크 · 임베딩 6.6초 · 되읽기 «안경·선글라스 p.31» / 재귀 비교 135청크 3.0초 | `index_recycle/` · `index_recursive/` (gitignore) |
| 10주차 6문항 (`--ids scratch`) | **6/6** · 자기모순 0 (10주차와 같음) | `eval_results/20261117-145633-answer.md` |
| E1 분할 (basic · bonus 0 · 24문항) | 재귀 Top-1 **16** · Top-3 **19** → 구조 Top-1 **22** · Top-3 **23** | `…153339-retrieval` · `…153601-retrieval` |
| E2 전략 | multiquery Top-1 18~20 · Top-3 20~21 (3회) · 1.76초 ↔ basic 22 · 23 · 0.33초 → **basic** | `…153601-retrieval` |
| E3 year_bonus (g = 0.180) | 0: 22/23 · 연도충돌 top-1 2026 **2/4** / **0.5g(0.090): 23/23 · 4/4 · c1 ○** / 1g: 21/22 / 2g: 14/20 · c1 × | `…153601-retrieval` |
| 생성 30문항 | bonus 0 · base **28/30** / bonus 0.09 · base **28/30** / bonus 0 · recent 28/30 + 자기모순 1 / bonus 0.09 · recent **27/30** + 자기모순 1 → 프롬프트 **base 유지** | `…153652` · `…153846` · `…153750` · `…153940` (`-answer`) |
| 공통 오답 | **y2 생수병** — 검색 ×(사례집 p.13 «먹는 샘물» 을 못 찾음) → «유리병 수거함» 오답 / **i1 주입** — 프롬프트 누출은 없으나 «찾지 못했습니다» 대신 엉뚱한 품목 답 | 같음 |
| 시간 · VRAM | 첫 답(로딩 포함) 27.9초 · 워밍업 뒤 답 0.5~1.6초 · 봇 켠 직후 첫 슬랙 답 1.3초 · `nvidia-smi` **5.75~6.09 / 8 GB** | |
| LangSmith | 프로젝트 `recycle-bot-20241499` 에 `recycle-rag` · `recycle-plain` · `recycle-search` · `build-chunks` trace. 슬랙 질문은 metadata `slack_user` · `slack_channel` 있음 | |

- **MultiQuery 가 진 이유**: 다시 쓰기 프롬프트의 예시(«쓰봉 → 종량제봉투, 락앤락 → 플라스틱 밀폐용기»)를 A.X 가 거의 모든 질문에 끌어다 씀 («플라스틱 밀폐용기에 담긴 아이스팩 처리 방법»). 검색어 대신 답 문장을 쓰기도 함(«마트 영수증은 종이류로 분리배출해야 합니다.»). 프롬프트를 고치면 다시 잴 수 있음 — 지금은 «효과 없음» 으로 기록
- **`recent` 프롬프트**: y2 를 «찾지 못했습니다» 로 바꾸고(자기모순), bonus 0.09 와 함께 쓰면 y1 이 오답 → 채택 안 함
- **`year_bonus` 0.09 채택**: SPEC 7-3 의 `year_bonus` 규칙(«Top-3 가 줄지 않고 c1 이 깨지지 않는 값 중 연도충돌 2026 이 가장 많은 값»)으로 채택. 생성 정답은 28 = 28 로 같음 — README 의 «최신 사례 우선» 을 실제로 보여 주려고 사용자가 승인. `tests/offline_check.py` 검사도 0.09 로 바꿈
- ℹ️ `tests/offline_check.py` 는 인덱스 · 평가 결과를 **임시 폴더에만** 만들고 지움 — `index_recycle/` · `eval_results/` 를 건드리지 않음
  (`RECYCLE_INDEX` 를 임시 폴더의 절대 경로로 둠 · 첫 커밋 11-14 부터 그랬음). 예전 이 자리의 «덮어쓴다 → 다시 만들 것» 경고는
  틀린 것이었음 (2026-11-20 코드로 확인 · README 5-6 도 고침). manifest 의 `embed_model` 이 다르면 봇이 시작을 거부하는 장치는 그대로.
  검사 항목은 **40개** — 예전에 적은 «41항목» 은 출력의 ✅ 줄을 세다가 «✅ 저장 : …» 안내 줄까지 넣은 수 (2026-11-20 확인)

**일정**: 13주차(11/27) 중간 점검 — 수업 시간의 진행 확인 · 상담(슬랙 왕복은 이미 됨) · **14주차(12/4) 최종 제출**.
제출물 = 코드 + README + LangSmith 추적 캡처(필수) — 전부 저장소에 있음. 제출 저장소는 **이 저장소**(2026-11-20 사용자 결정) · 제출 방법은 수업 공지를 따름.

### 검증한 것 / 못 한 것

| ✅ 검증함 | ❌ 아직 못 함 |
|---|---|
| 모델 없이: `build_index.py --check` 15항목 · `questions.py` · `tests/offline_check.py` 40항목 (Python 3.11 · **3.13.3** 둘 다 · 2026-11-20 클라우드에서 다시) | 한글 경로에서의 저장 (`index.bytes` 경로) — **하지 않기로 함** (2026-11-19 사용자 판단: 평가 항목 아님 · 같은 사양의 보조 PC 에서 처음부터 세팅해 통과 · `faiss_io` 는 수업 제공 파일 그대로) |
| 실제 모델 (2026-11-17): 임베딩 · 인덱스 · 검색 · 생성 · 평가 E1~E4 — 위 «첫 실행 결과» | 슬랙 화면의 사용법 안내(빈 멘션) 문구 — 콘솔로는 분기만 확인. ℹ️ 안내 줄은 캡처(`docs/slack-compare.png`)로 확인함 |
| 실제 슬랙 왕복(멘션 · DM · 검색 · 비교 · 빈 멘션 · 범위 밖) · LangSmith trace · VRAM | Ollama 를 끈 상태의 오류 처리 (SPEC 6-5 자체 점검 · 수업 요건 아님 · 선택 — 가짜 모델로는 확인함). LangSmith · 슬랙 화면 캡처는 2026-11-19 완료 |
| 범위 밖 «찾지 못했습니다» 4/4 · i2(요리사) 거절 | **i1(시스템 프롬프트 출력 요구)** — 누출은 없으나 엉뚱한 품목 답 (오답) |

⚠️ 가짜 임베딩은 글자 2-gram 해시라 **검색 순위에 의미가 없습니다.** `offline_check.py` 가 통과했다는 것은 «코드가 끝까지 돈다» 는 뜻이지 «답이 맞다» 는 뜻이 아닙니다.

## 필수 요건 (어기면 감점 · 수업 2교시 §4-2 · §4-3 → SPEC 1장 R1~R14 · 2026-11-19 전부 충족 확인)

1. **슬랙으로 묻고 슬랙으로 답한다** — 채널 멘션 · DM → **같은 스레드에** 답. 터미널에서만 도는 건 요건 미충족
2. **RAG 또는 MCP** 하나 이상 → 이 프로젝트는 **RAG** (MCP · LangGraph 안 씀)
3. **LangChain 구현** (+ LangSmith 추적 — **11-25 에 요건에서 빠짐** · 코드는 그대로 추적을 남김)
3-1. (11-25 추가) **같은 스레드 이어 묻기** · README 7번 테스트표 · 캡처 3종 `captures/` · MCP 도구 1개(권장) — 위 «새 채점 기준»
4. **VRAM 8GB 에서 실제로 동작** (RTX 3070 8GB 에서 세 모델 동시 실측 **7.6 ~ 7.7 GB** · 100% GPU — 2026-11-24. 여유 0.3GB 남짓이라 다른 모델이 남아 있으면 넘침)
5. 피할 것: 12B 이상 모델 · 대량 크롤링 · 상용 API 상시 호출 · 범위 없는 챗봇
6. 토큰은 **루트 `.env` 에만**
7. **README 가 곧 점수**(발표 없음). 숫자는 추정 대신 **실측**으로 쓰는 것이 이 프로젝트의 원칙

## 사용자가 확정한 결정 (SPEC 0-2절)

- 구현 범위: **전체** — 기본 봇 + 검색 개선 + 평가 스크립트 + README 5 · 6번
- **MultiQuery** 와 **`year` 최신 우선 재정렬**은 반드시 구현. MMR · 하이브리드 · Self-Query · 본문 인용 번호는 넣지 않음
- 모델 설정은 전용 키 **`RECYCLE_*` + 코드 기본값**. 루트 `.env` 의 `MODEL` · `EMBED_MODEL` 은 건드리지 않음
- **OpenAI 백엔드 제거** — Ollama 만
- ✅ **독립 저장소 `recycle-rag-slack-bot` 으로 옮김** — 히스토리 보존 · 이 저장소가 원본 · 수업 저장소 `mini_project/` 는 동결 (2026-11-20)
- ✅ **다음 기능 = 사진으로 묻기** · 합격선은 `gemma3:4b` 보다 좋을 것 · 채택하면 문서를 새 모델 기준으로 다시 씀(A.X 언급 불필요 · 숫자 · 캡처는 새로 실측) (2026-11-20)
- ✅ **제출 = 이 저장소** (사진 기능까지 넣어서) · `main` 반영은 묻지 않고 알아서 (2026-11-20)
- ✅ **2026-11-24 결정** — 사진 판정 기준 15/20 · 범위 밖 4/4 (측정 전) / 테스트 사진 커밋 · Pillow · 슬랙 `files:read` 승인 /
  테스트 사진은 **AI 생성 이미지**로(사용자 제안 · 글자 없이) / **채택 = 생성 gemma4:e4b + 사진 qwen3.5:4b(pick)** · 범위 밖 2/4 는 한계로 기록 /
  새 사진 세트로 다시 재기는 보류(«지시문은 어차피 개선돼야 했고 파인튜닝도 아님») — README 에 «같은 사진으로 지시문을 고침» 을 밝힘
- ✅ LangSmith 프로젝트 이름은 `config.py` 가 `recycle-bot-20241499` 로 지정(`RECYCLE_LANGSMITH_PROJECT` 로 바꿀 수 있음) — 2026-11-17 승인 · README 체크리스트 · CONTEXT «관측» 도 고침 (미결 1)

## 폴더 구조

```
recycle-rag-slack-bot/             ← git 저장소 맨 위 (github.com/Jinseok2419342/recycle-rag-slack-bot) · ★ 모든 명령은 여기서
├── .env                           ← 토큰 · 설정. 절대 커밋 금지 (.gitignore 됨 · 수업 저장소의 루트 .env 를 복사해 써도 됨)
├── venv/                          ← 파이썬 가상환경 (.gitignore 됨)
├── .gitignore                     ← .env · venv · /index*/ · 사례집 PDF · /photos_raw/ · /captures_raw/
├── README.md · CONTEXT.md         ← 명세 (채점 대상)
├── SPEC.md                        ← 상세 구현 명세서
├── CLAUDE.md                      ← 이 파일
├── config.py                      ← 공용 상수 · 경로 · RECYCLE_* · LangSmith 프로젝트 지정 (모든 파일이 맨 먼저 import)
├── faiss_io.py                    ← 수업 저장소 11-06/faiss_io.py 를 그대로 복사 (한글 경로 대비 · 수정 금지)
├── build_index.py                 ← PDF 2건 → 정리 → 구역별 구조 분할 → 메타데이터 → FAISS
├── rag_backend.py                 ← 검색기(RecycleRetriever) · ask · ask_plain · search · source_of · warmup · 📷 ask_photo · redact_images
├── slack_rag_bot.py               ← Socket Mode 봇 (입구 · 출구 · 사진 내려받기)
├── questions.py                   ← 평가 문항 30개 (+ 자기 검사)
├── evaluate.py                    ← retrieval | answer | photo | prep-photos → eval_results/
├── requirements.txt · .env.example
├── tests/offline_check.py         ← 모델 없이 코드 경로 확인 (71항목)
├── docs/architecture.md           ← 구성도 · 프로세스 · 흐름도 (사진 흐름 포함)
├── docs/scenarios.md              ← 가상 시나리오 10개 (9 · 10 = 사진)
├── docs/photo-feature-plan.md     ← 사진으로 묻기 — 맨 위 «결과»(2026-11-24) + 아래는 2026-11-20 계획 그대로
├── docs/*.png                     ← 캡처 — trace-build(11-17) + 6장(2026-11-24 새로: trace-rag · trace-retriever · trace-photo · slack-thread · slack-compare · slack-photo)
├── photos/                        ← 사진 평가 세트 24장 (AI 생성 · prep-photos 로 1280px · 메타데이터 삭제) — 파일 이름 = 문항 id · out_* = 범위 밖
├── photos_raw/ · captures_raw/    ← 원본 사진 · 캡처를 잠시 두는 곳 (gitignore)
├── captures/                      ← 11-25 제출 캡처 3종 (1-index-show · 2-terminal · 3-slack (+ 3-slack-photo)) — 커밋함
├── old_codes/                     ← 수업 실습 코드 사본 (사용자가 넣음 · gitignore) — 13주차 기준 코드 = old_codes/11-27/slack_bot/
├── scratch_eval.py                ← 10주차 생성 모델 비교 스크립트 (CONTEXT 부록 C 재현용 · 2026-11-24 reasoning=False 한 줄만 추가)
├── index_recycle/                 ← build_index.py 가 만듦 (gitignore · PC 마다 다시 만듦)
├── eval_results/                  ← evaluate.py 가 만듦 (커밋함 · 2026-11-17 7회 + 2026-11-24 기준선 · 후보 · 사진 · scratch_eval 기록)
└── data/
    ├── 분리배출_가이드라인.pdf            ← 커밋됨 (4.8MB · 36쪽)
    └── 분리배출_QA사례100_2026.pdf       ← ⚠️ 68MB · gitignore → 없으면 아래 명령으로 받기
```

### 문서 받기 (data/ 에 사례집이 없을 때 · PowerShell, 저장소 맨 위에서)

```powershell
Invoke-WebRequest "https://sustainability.korea.ac.kr/files/Separation%20and%20discharge%20guide%20for%20recycling%20items%20(Ministry%20of%20Environment).pdf" -OutFile "data\분리배출_가이드라인.pdf"
Invoke-WebRequest "https://www.kwaste.or.kr/lib/fileDownload.php?save_file=attachment_202605081124500.29008db5d7c61e61718f7a154de14539.pdf&file_name=QA100.pdf" -OutFile "data\분리배출_QA사례100_2026.pdf"
```
(사례집 원 게시글: 한국폐기물협회 공지 `https://www.kwaste.or.kr/community/01.php?admin_mode=read&no=6128` · 2026-11-13 에 위 링크로 68,862,868바이트 내려받기 확인)

## 처음부터 다시 돌릴 때 — 실행 순서 (참고용 · 0~8번 모두 완료: 0~7번 2026-11-17 보조 PC · 8번 캡처 2026-11-19)

> 사용자에게 안내할 때는 README 5번 «실행 방법» 이 같은 내용을 설치 → 실행 순서로 담고 있습니다(보조 PC 에서 빈 상태부터 따라 해 본 기록).

> 다른 PC 에서 처음부터 다시 돌릴 때도 이 순서. 0번(모델 pull · 사례집 PDF)은 PC 마다 필요.

```powershell
cd recycle-rag-slack-bot
$env:PYTHONUTF8=1
```

| # | 명령 | 통과 조건 | 막히면 |
|---|---|---|---|
| 0 | `ollama pull gemma4:e4b` · `ollama pull qwen3.5:4b` · `ollama pull hf.co/mykor/KURE-v1-gguf:Q8_0`(멈추면 함정 24) · 루트 `.env` 의 `LANGSMITH_TRACING=true` · `ollama ps` 로 GPU 비우기 · 10주차 봇 · 다른 PC 의 같은 봇 끄기 | `ollama list` 에 세 줄 | SPEC 2-2절 · README 5-2 |
| 1 | `python build_index.py --check` | 15항목 ✅ (임베딩 없음) | 사례집 PDF 가 없으면 위 «문서 받기» |
| 2 | `python tests/offline_check.py` | `ALL OK` (40항목 · 모델 없음) | 패키지 버전 차이 — 메인 PC 는 Python 3.13 · 이 검사는 3.11 에서 돌렸음 |
| 3 | `python build_index.py` | `✅ 저장` + 되읽기 확인 줄에 «안경·선글라스 p.31» · `index_recycle/manifest.json` 생김 | 한글 경로면 `index.bytes` 로 저장되는 것이 정상 |
| 4 | `python rag_backend.py "뽁뽁이는 어떻게 버려요?"` · `검색 "선글라스"` · `비교 "마트 영수증은 종이로 버려도 돼?"` | 검색 1~3위에 정답 품목 · 답 · 근거 줄 | 검색이 엉뚱하면 임베딩 모델 · manifest 부터 |
| 5 | `python evaluate.py answer --ids scratch` | 10주차와 같은 6문항 — **6/6 이 나오는지** (CONTEXT 부록 C 와 비교) | 6/6 이 아니면 분할이 바뀐 영향 — 어느 문항인지 `eval_results/` 에서 확인 |
| 6 | `python slack_rag_bot.py` → 슬랙에서 멘션 · DM · `검색` · `비교` · 빈 멘션 | SPEC 6-5절 체크리스트 · LangSmith 에 `recycle-rag` trace · `nvidia-smi` 8GB 미만 | 봇이 답을 안 하면 슬랙 앱 설정(README 5-2 ⑤)부터 — 수업 저장소의 `10-30/socket_hello.py` 로 확인해도 됨 |
| 7 | `python build_index.py --mode recursive --out index_recursive` → `python evaluate.py retrieval --index index_recursive` → `python evaluate.py retrieval` → `python evaluate.py answer` (→ `--prompt recent`) | E1~E4 결과가 `eval_results/` 에 | SPEC 7-3절 채택 규칙 |
| 8 | 채택한 값을 `config.py` 기본값에 반영 → README 5 · 6번 · CONTEXT 부록 D · E · `docs/scenarios.md` 의 «예상» 을 실제 출력으로 → LangSmith 캡처 7장 | SPEC 8-2절 · 9장 | 캡처는 **사용자가 직접** · 무료 플랜 14일 → 이미지로 저장하면 기간 상관없음 (2026-11-19 완료) |

(선택) **시나리오 8 확인** — 봇을 켠 상태에서 Ollama 를 끔(작업 표시줄 Ollama 아이콘 → Quit) → 슬랙에서 질문 →
슬랙에 «⚠️ 답을 만들지 못했습니다. 잠시 뒤 다시 물어봐 주세요.» · 콘솔에 원인(traceback)이 나오면 통과 → Ollama 다시 켜기.
결과는 `docs/scenarios.md` 시나리오 8 의 «💭» 표시와 «실행해 보니» 표에 반영.

**처음 실행에서 깨질 가능성이 있던 곳 → 2026-11-17 확인 결과**

1. **`keep_alive`** — ✅ 정수 `1800` 을 Ollama 가 받음 (`ollama ps` 에 «29 minutes from now»)
2. **A.X 의 다시 쓰기 출력 형식** — ❌ 줄바꿈 형식은 지키지만 **내용이 문제**: 프롬프트 예시(종량제봉투 · 플라스틱 밀폐용기)를 거의 모든 질문에 섞고, 답 문장 · «다음 검색 질문을 사용할 수 있습니다:» 같은 설명 줄도 냄 → E2 에서 basic 보다 나쁨
3. **`is_not_found` 의 60자 기준** — ✅ 범위 밖 4문항 · 슬랙 «강남구» 모두 «자료에서 찾지 못했습니다.» 한 문장
4. **검색 품질** — ✅ 짧은 품목사전 청크가 오히려 유리 (구조 Top-3 23/24 ↔ 재귀 19/24)
5. **`year_bonus` 의 눈금** — g = **0.180** (구조) · 0.134 (재귀). 0.5g = 0.090 이 후보
6. **슬랙 이벤트** — ✅ `bot_id` 거르기로 자기 답에 다시 답하지 않음. DM 은 `im:history` scope 가 없어 처음엔 안 왔음 (함정 17)

**사용자가 직접 해야 하는 일** (그 차례에 멈추고 요청): 모델 pull · `.env` 변경 승인 / `--show qa_case` 100줄 눈 확인 / 슬랙에서 질문 · 화면 캡처 / LangSmith 캡처 / 커밋 · 푸시 승인

## 환경 (메인 PC 기준 · SPEC 2장)

> 실제 실행 · 검증은 같은 사양의 보조 PC(영문 경로)에서 함(2026-11-17). 메인 PC 재세팅 · 한글 경로 재검증은 하지 않기로 함(2026-11-19 · 평가 항목 아님).

- **OS: Windows** · PowerShell / Git Bash. **경로에 한글(`최신인공`)이 있음** ← 함정 1 — 수업 저장소가 놓인 메인 PC 경로 얘기.
  이 저장소는 영문 경로(예: `C:\dev\recycle-rag-slack-bot`)에 클론하길 권함 (README 5-2 ①)
- 파이썬 3.13.3 — 수업 저장소에서는 `..\venv\Scripts\python.exe`, 이 저장소에서는 맨 위에 새로 만든 `.\venv\Scripts\python.exe`
  (`pip install -r requirements.txt`). 새 패키지를 추가하지 않음
- `venv/` · `.env` · `index*/` · 사례집 PDF 는 gitignore 라 **다른 클론에는 없음**
- Ollama 0.32.14 · 모델:

| 모델 이름 (Ollama) | 용도 | 상태 |
|---|---|---|
| `gemma4:e4b` | ★ **생성** (Google · 7.5B · 실효 4.5B · 6.1GB 파일 · 생각 모드 있음 → 끔) | 2026-11-24 PC 에 pull (2026-11-24 채택) |
| `qwen3.5:4b` | ★ **사진 → 품목 이름** (Alibaba · 4.2B · 3.1GB · 생각 모드 있음 → 끔) | 2026-11-24 PC 에 pull |
| `hf.co/mykor/KURE-v1-gguf:Q8_0` | ★ **임베딩** (고려대 KURE-v1 · 1024차원 · 0.6GB) | 2026-11-24 PC 에는 GGUF 를 직접 받아 `ollama create` (함정 24) |
| `gemma3:4b` · `qwen3-embedding:0.6b` | 수업 기본 — **비교 기준으로만** | `gemma3:4b` 는 2026-11-24 PC 에도 있음 |
| `qwen3.5:0.8b` | 사진 후보였음 (0 ~ 1/20 · 탈락) | 2026-11-24 PC 에 있음 (지워도 됨 — 사용자 확인 뒤) |
| `hf.co/mykor/A.X-4.0-Light-gguf:Q4_K_M` | 2026-11-17 까지의 생성 모델 (지금은 안 씀) | 11-17 보조 PC 에만 |

- 루트 `.env` (= 저장소 맨 위 · 값은 출력하지 말 것 · 키 이름은 [.env.example](.env.example) · 수업 저장소의 루트 `.env` 를 그대로 복사해 써도 됨):

| 키 | 현재 | 할 일 |
|---|---|---|
| `SLACK_BOT_TOKEN` · `SLACK_APP_TOKEN` · `LANGSMITH_API_KEY` | 있음 | 그대로 |
| `LANGSMITH_TRACING` | 보조 PC `true` (2026-11-17) · 메인 PC `false` | 추적하려면 `true` |
| `EMBED_MODEL` · `MODEL` | 수업 저장소에서 복사해 왔다면 있음 (다른 주차 실습용) | **건드리지 않음** — 이 프로젝트는 읽지 않음 |
| `RECYCLE_*` | 없음 | 넣지 않아도 됨. 바꿔서 잴 때만 |

- 환경 변수로 바꿀 수 있는 것: `RECYCLE_MODEL` · `RECYCLE_EMBED_MODEL` · `RECYCLE_STRATEGY`(basic\|multiquery) · `RECYCLE_YEAR_BONUS` · `RECYCLE_PROMPT`(base\|recent) · `RECYCLE_INDEX` · `RECYCLE_LANGSMITH_PROJECT`
  · `RECYCLE_REASONING`(off\|on\|auto) · 📷 `RECYCLE_VISION_MODEL` · `RECYCLE_PHOTO_MODE`(pick\|free) · `RECYCLE_PHOTO_REASONING` · `RECYCLE_PHOTO_QUERY`(label\|label+desc) · `RECYCLE_PHOTO_SIDE` · `RECYCLE_PHOTO_MAX_DIST` · `RECYCLE_PHOTO_MIN_GAP`.
  ⚠️ «실행 한 번 = 설정 하나» — 인덱스 · 모델을 한 번만 읽어 계속 쓰므로 실행 중에는 바뀌지 않음

## 구현 요약 (자세한 건 SPEC · 그림은 docs/architecture.md)

- **문서 2건**: 환경부 가이드라인(2018 · 36쪽 · 기준) + 한국폐기물협회 Q&A 사례 100(2026 · 52쪽 · 최신 사례).
  2018 문서에는 «무색페트병» 이 0회 → 최신 우선이 필요 → `year` 메타데이터(**int**)
- **분할 = 구역별 구조 단위 → 긴 것만 재귀 400/40** — 구현 실측 **456청크**

  | 구역 | 단위 | 실측 (`--check`) | 함수 |
  |---|---|---|---|
  | 사례집 Q&A (6~46쪽) | 1건 = 1청크 · 본문 «품목: … / Q. … / A. …» | **100** · 평균 151자 | `split_qa_cases` · `parse_qa_page` |
  | 가이드라인 FAQ (21~25쪽) | «Q :» 1개 = 1청크 | **36** · 평균 106자 | `split_faq` |
  | 가이드라인 품목사전 (28~34쪽) | 품목 1개 = 1청크 | **282** · 평균 20자 (`ITEM_DROP` 4건 제외) | `split_item_dict` |
  | 가이드라인 본문 (3~20쪽) | 쪽 단위 → 재귀 400/40 + `section` | **38** · 평균 295자 | `split_guideline` |

  비교용 재귀 인덱스(`--mode recursive`): **135청크 · 평균 307자**
- **메타데이터**: `source` · `page`(int) · `year`(int) · `doc_type`(qa_case/faq/item_dict/guideline) · `material` · `item` · `qa_date` · `section` · `chunk_id` · `splitter`.
  값이 없으면 키를 **넣지 않음**. FAQ 에는 `material` · `item` 없음
- **인덱스**: FAISS + `faiss_io` · `index_recycle/` · **`manifest.json`** 에 임베딩 모델 기록 → 읽을 때 다르면 종료
- **검색** (`rag_backend.py`): `RecycleRetriever`(`BaseRetriever`) = `rewrite_queries`(multiquery 일 때만) → `candidates`(질문마다 10개 · 같은 청크는 최소 거리) → `rank`(year ≥ 2020 이면 거리 − `year_bonus` · 상위 3개).
  돌려주는 청크의 metadata 에 `distance` · `adjusted` · `via` 를 덧붙임(복사본에). **기본값 `basic` · `0.09` (E1~E4 실측 뒤 채택 · 2026-11-17)**
- **생성**: LCEL `RAG_PROMPTS["base"] | ChatOllama(gemma4:e4b, temperature=0.1, num_predict=300, num_ctx=4096, keep_alive=1800, reasoning=False) | StrOutputParser`.
  `base` 프롬프트는 `scratch_eval.py` 의 `PROMPT` 와 **글자 단위로 같음** (부록 C 의 6/6 이 이 문구로 잰 값). `recent` 는 E4 실험용(효과 없음)
- **📷 사진** (`ask_photo` · trace `recycle-photo`): `prepare_image`(Pillow · 회전 · 768px · EXIF 버림) → `describe-photo`(qwen3.5:4b · `pick` 지시문 v2 = 설명 줄 + 문서 품목 이름 377개 중 하나 / `모름`)
  → `parse_label` · `snap_to_item` → `RecycleRetriever`(검색어 = 이름 + 같이 쓴 글) → `decide`(확신 기준 · 기본 끔) → `generate`. 슬랙은 📷 줄 + 답 + 📚 + 🔁 다른 후보.
  사진은 `Client(hide_inputs=redact_images)` + `tracing_context(client=…)` 로 LangSmith 에 «<image N bytes>» 만
- **출처 형식**: `안경·선글라스 · 사례집(2026) p.31` — 코드가 metadata 로 만듦(`source_of`)
- **슬랙** (`slack_rag_bot.py`): 멘션 + DM, 전부 `thread_ts` 로(같은 스레드), `검색` · `비교` 모드, ⏳ 자리잡기 → `chat_update`, 300자 제한,
  «찾지 못했습니다» 면 근거 숨기고 구청 안내, 근거에 2018 · 2026 이 섞이면 ℹ️ 안내 줄, 예외 내용은 콘솔에만, `&` `<` `>` 이스케이프, 봇 메시지 무시, 시작 시 워밍업
- **LangSmith**: 프로젝트 `recycle-bot-20241499` · trace `recycle-rag`(아래 `RecycleRetriever` + `generate`) · `recycle-photo` · `recycle-plain` · `recycle-search` · `build-chunks` · 태그 `rag`/`photo`/`no-rag`/`search`/`eval`
- **평가** (`evaluate.py`): `retrieval` = 전략 × `year_bonus`(0 · 0.5g · 1g · 2g) 격자 · multiquery 3회 반복 / `answer` = `must` · `bad` · 자기모순 채점 /
  `photo` = `photos/<문항 id>.jpg` 의 정답이 검색 3위 안 · `out_*` 는 모름 · 되묻기 · 찾지 못함이면 정답 / `prep-photos` = 원본 → 1280px · EXIF 삭제 사본.
  옵션 `--index` · `--model` · `--prompt` · `--strategy` · `--year-bonus` · `--ids`(`scratch` = 10주차 6문항) · `--repeats` · `--no-multiquery`
  · `--vision-model` · `--photo-mode` · `--photo-reasoning` · `--photo-query` · `--photo-side` · `--dir` · `--src`

## 10주차 실측 (근거 데이터 · 자세한 건 CONTEXT 부록 A ~ C — 구현 뒤 재측정은 위 «첫 실행 결과» · 부록 D ~ F)

- 임베딩(재귀 400/40 · **181청크** · 일상 말투 15문항): Top-3 정답 qwen3 **12/15** → KURE **15/15**
- 생성(KURE top-3 · 6문항 · 181청크): gemma3:4b **4/6**(자기모순 2회) → (2026-11-24 다시) gemma4:e4b **6/6** · 답당 0.7~1.0초
- ⚠️ 지금 인덱스는 456청크 → 2026-11-24 생성 30문항: gemma3:4b 15/30 · gemma4:e4b 29/30 · 세 모델 동시 nvidia-smi 7.6~7.7GB (부록 E · 위 «▶»)

## 함정 (밟았거나 실측으로 확인한 것 · 전체는 SPEC 12장)

1. **한글 경로 + FAISS** — `store.save_local()` 이 RuntimeError. 반드시 `faiss_io.save_index` / `load_index` (`index.bytes` 로 저장되는 것이 정상) · 영문 경로에 클론하면 아예 안 생김
2. **머리말 정규식은 문서별로 2개** (`build_index.py` 의 `HDR_G` · `HDR_Q`). ⚠️ `scratch_eval.py` 의 `HDR` 은 **쓰지 말 것** — 가이드라인 머리말 34줄 중 17줄이 남고, 사례집의 **사례 번호 줄**까지 지움
3. **사례집을 날짜 순서대로 자르면 100건 중 24건이 틀림** — 2단 배치. 품목 이름으로 짝짓기(`parse_qa_page`). 파서를 고치면 반드시 `--check`
4. **품목사전** — 30자 필터 금지(평균 20자). 초성 줄은 14글자만 지움(낫 · 못 · 컵 … 은 품목). 뜻이 틀어진 4건은 `ITEM_DROP`
5. **임베딩 모델이 달라도 오류가 안 남** — qwen3 와 KURE 가 둘 다 1024차원 → `manifest.json` 비교가 유일한 장치
6. **`config` 를 langchain · langsmith 보다 먼저 import** — 아니면 LangSmith 프로젝트 이름이 안 먹음. `evaluate.py` 는 `--index` · `--model` · `--prompt` 를 그보다도 먼저 읽음
7. **`keep_alive` 는 정수** — `OllamaEmbeddings` 는 `"30m"` 을 받지 않음(ValidationError). `config.KEEP_ALIVE = 1800`
8. **`year_bonus` 부작용** — «뽁뽁이» 의 정답은 2018 문서인데 2026 사례집에 «은박 에어캡(뽁뽁이)» 라는 다른 품목이 있음. 감시 문항 `c1`
9. **다시 쓰기 프롬프트의 예시에 평가 문항의 품목을 넣지 말 것** — 점수가 부풀려짐 (지금 예시: 쓰봉 · 락앤락)
10. **평가 문항을 고치면 `python questions.py`** — 정답 위치가 실제 청크에 있는지 검사. 틀린 정답 위치로 재면 숫자가 전부 거짓
11. **Ollama 가 안 쓰는 모델도 5분간 GPU 에 남김** — 측정 전 `ollama ps` → `ollama stop <모델>`
12. **토큰 검사를 접두어(`xoxb-`)로 하면 안 됨** — 봇 코드의 접두어 검사에 걸림. SPEC 1장 «토큰 누출 검사» 의 식 사용
13. **콘솔 cp949** — 스크립트는 `sys.stdout.reconfigure(encoding="utf-8")` 를 함. PowerShell 은 `$env:PYTHONUTF8=1`
14. **10주차 봇 · 수업 저장소의 같은 봇과 동시 실행 금지** — 같은 `SLACK_APP_TOKEN` 이면 이벤트가 둘로 갈림
15. `pypdf` 직접 호출과 `PyPDFLoader` 는 쪽 끝 공백이 달라 글자 수 · 재귀 청크 수가 1씩 다를 수 있음 → 문서에는 구현 출력값
16. **임베딩을 한 요청에 456개 보내면 Ollama 0.32.14 러너가 간헐적으로 죽음** (`…/tokenize: connection refused` · 3회 중 2회) → `build_index.py` 는 `EMBED_BATCH = 64` 개씩 보냄 (2026-11-17 · SPEC 13-1 k)
17. **DM 이 안 오면 봇 토큰 scope 에 `im:history` 가 있는지** — `app_mentions:read` 만 있으면 멘션만 됨. scope 추가 후 **Reinstall to Workspace** 필요. App Home 의 Messages Tab 도 켤 것
18. **슬랙의 실제 봇 이름은 `@Jinseok-20241499-Bot`** — 문서의 `@버릴지도` 는 별명. `@봇 @버릴지도 검색 …` 처럼 두 번 쓰면 `검색` · `비교` 모드가 안 걸림
19. 보조 PC 의 Ollama 는 PATH 에 없음 (`%LOCALAPPDATA%\Programs\OllamaAIClass\ollama.exe`) — `evaluate.py` 가 `ollama ps` 를 부르므로 `$env:Path += ";$env:LOCALAPPDATA\Programs\OllamaAIClass"` 후 실행
20. PowerShell 에서 한글이 깨지면 `[Console]::OutputEncoding=[Text.Encoding]::UTF8` (`PYTHONUTF8` 만으로는 파이프 출력이 깨짐)
21. **이 저장소를 수업 저장소 폴더 안에 클론하지 말 것** — `.env` 가 없으면 `load_dotenv()` 가 위 폴더로 올라가며 찾아
    수업 저장소의 루트 `.env` 를 읽어 버림(헷갈림). 따로 영문 경로에 두고 `.env` 는 이 저장소 맨 위에 복사
22. **pypdf 7.x 금지 — `requirements.txt` 가 `pypdf==6.21.4` 로 고정** (2026-11-20 실측). 7.x 는 «배출(전기이불담요 포함)» 을
    «배출 (…» 처럼 공백을 넣어 뽑아 `ITEM_DROP` 1건이 안 걸림 → 품목사전 283건 · `--check` 실패 · 뜻이 틀어진 청크가 인덱스에 들어감.
    가이드라인 3구역(본문 38 · FAQ 36 · 품목 282)은 6.21.4 에서 기록과 같음을 클라우드에서 확인. 사례집 구역은 PDF 가 없어 못 봄
23. **gemma4:e4b · qwen3.5 는 생각(thinking) 모드가 기본 켜짐** — `reasoning` 을 안 주면 300토큰을 생각에 다 써서 **답이 빈칸**(scratch_eval 0/6 · 2026-11-24).
    `config.REASONING`(기본 off → `think:false`)으로 끔. `think:false` 는 생각 기능이 없는 gemma3:4b 도 받음(`true` 만 «does not support thinking» 오류)
24. **Hugging Face 에서 `ollama pull hf.co/…` 가 멈출 수 있음** (2026-11-24 PC · 수 KB/s) — Ollama 레지스트리 모델은 빠름.
    같은 GGUF 를 4MB 조각 · 재시도로 받아(`requests` · sha256 확인 — KURE Q8_0 = `055cd596…`) `Modelfile` 에 `FROM ./파일.gguf` → `ollama create hf.co/mykor/KURE-v1-gguf:Q8_0 -f Modelfile`.
    같은 sha256 이라 검색 평가가 기록과 똑같이 재현됨. 같은 이름의 다른 업로드(`daynice/kure-v1` = BF16)는 숫자가 달라질 수 있어 쓰지 않음
25. **세 모델이 VRAM 7.6~7.7GB** — 봇을 켠 채 같은 GPU 로 `evaluate.py` 를 돌리면 Ollama 가 모델을 번갈아 올리느라 **몇 분씩 멈춘 듯 보임**(사진 측정 7분 정지 · 슬랙 답 13~29초).
    측정 전에 봇을 끄고 `ollama ps` → `ollama stop`. 측정 출력은 파이프로 받으면 끝날 때 한꺼번에 나옴(`python -u`)
26. **`RunnableLambda` 함수의 `config` 인자가 `config` 모듈을 가림** — `_photo(inputs, config)` 안에서 `config.PHOTO_MODE` 를 쓰면 dict 오류. 모듈 값은 `ask_photo` 에서 inputs 로 넘김(2026-11-24 실제로 밟음 · 그 측정 1회 무효)
27. **작은 비전 모델은 지시문의 예시를 베낌** — `qwen3.5:0.8b` 는 예시 «건전지» 를 거의 모든 사진에, 목록에서 고르게 하면 첫 항목만 반복. 사진 지시문에 예시를 넣지 말 것(v2)
28. **이 PC(2026-11-24)는 CLI `git push` 가 막힘**(GitHub 로그인 없음 · Credential Manager 가 창을 못 띄움) — 커밋은 CLI 로, push 는 사용자가 **GitHub Desktop 의 Push origin**.
    `main` 반영도 GitHub Desktop 에서(또는 사용자가 터미널에서 `git push origin photo-feature:main`)
29. **수업 저장소의 루트 `.env` 를 복사하면 `LANGSMITH_AGENT_ID` · `LANGSMITH_AGENT_ENVIRONMENT`(7주차 «에이전트 주소» 실습)가 같이 옴** —
    langsmith 0.16 은 프로젝트(`config.py` 가 정함)와 주소가 둘 다 있으면 `EnvAddressError` 로 **trace 를 버림**(콘솔에 «Error in RunCollectorCallbackHandler…» · 
    `offline_check.py` 87번 줄 IndexError). → `config.py` 가 두 키를 `os.environ` 에서 지움 (2026-11-27 · SPEC 13-1 p). `.env` 는 고치지 않아도 됨
30. **이 PC 는 초기화될 수 있음** — 2026-11-27 에 열어 보니 폴더가 새로 클론돼 있고 `venv` · 사례집 · `.env` · `captures_raw/` · 11-24 에 받은 모델 3개가 모두 없었음
    (Ollama 에는 `gemma3:4b` · `exaone3.5:2.4b` 만). 세션 시작 때 `ollama list` · `Test-Path venv` 부터 보고, 없으면 README 5번 순서로 다시 준비

## 사용자 확인이 필요한 미결 사항 (SPEC 13장)

채점 문서(README · CONTEXT)라 임의로 고치지 않고 남겨 둔 것입니다. «다음 할 일» 8번에서 문서를 갱신할 때 함께 정리합니다.

1. ✅ **LangSmith 프로젝트 이름 위치** — `config.py` 로 확정(사용자가 «진행» 승인 · 2026-11-17). README 체크리스트 · CONTEXT «관측» 도 그렇게 고침
2. ✅ **README 3번 «외부 API» 문장** — «검색 · 생성 모두 로컬 · 질문이 외부 LLM API 로 나가지 않음» + «LangSmith 추적을 켜면 질문 · 근거 · 답이 LangSmith 에 기록됨» 단서로 고침 (사용자 승인 · 2026-11-19)
3. ✅ **사례집 발행일** — CONTEXT 를 «2026.03 (판권 발행일 2026-03-26 · 협회 공지 게시 2026-05-08)» 로 고침. 2026.05 는 첨부파일 이름(`attachment_20260508 1124…`)의 게시 시각 (사용자 승인 · 2026-11-19). `year` 메타데이터는 2026 그대로라 코드 · 인덱스 영향 없음
4. ✅ CONTEXT 부록 C «마트 영수증» 행 — 2026-11-17 `scratch_eval.py` 재실행 답으로 채움(각주로 밝힘)
5. ✅ 구현 실측값 — CONTEXT 분할 표에 «구현 결과» 표 추가(282 · 106자 · 456 · 쪽 단위 + `section`) · 메타데이터 표 갱신. 설계 때 시험 표(243 등)는 «설계 기록» 으로 남김
6. ✅ README 맨 위 그림 · CONTEXT 처리 흐름 그림 — 실제 출력 형식(«아이스팩 · 가이드라인(2018) p.31»)으로 통일 · «구현 예정» 삭제
7. ✅ README 5번 · 6번 작성 (2026-11-17 실제로 돌린 명령 · 결과)
8. ✅ **슬랙 봇 표시 이름** — 문서는 처음 보는 사람이 알기 쉬운 `@버릴지도` 그대로 두고, README 2번 «실제 슬랙 화면» 에 «테스트 당시 봇 이름은 `@Jinseok-20241499-Bot`» 한 줄 추가 (사용자 결정 · 2026-11-19). 슬랙 앱 설정은 바꾸지 않음 · README 5-4절은 `@봇`

## 작업 규칙

- README · CONTEXT 의 숫자를 바꾸면 **두 문서를 같이** 고칠 것. 코드가 SPEC 과 달라지면 SPEC 13-1절에 적을 것
- 새 숫자는 **실제로 돌려서** 얻은 것만 적을 것. 추정이면 «계산» · «예상» 이라고 표시. 효과가 없었으면 없었다고 적을 것
- 한 번에 하나만 바꾸고 잴 것 (임베딩 · 분할 · 검색 전략 · 프롬프트)
- 코드를 고치면 `python build_index.py --check` · `python tests/offline_check.py` 를 다시 돌릴 것
- 수업 저장소(`11-06/` · `11-13/` · 동결된 `mini_project/`)는 수정하지 말 것 — 읽기 · 링크만
- 토큰 · 키를 코드 · 로그 · 커밋 · 슬랙 메시지에 넣지 말 것. `.env` 내용을 출력하지 말 것. 68MB PDF 커밋 금지
- 파일 삭제 · `.env` 수정은 **사용자에게 확인받고** 할 것. 커밋 · 푸시 · `main` 반영은 알아서 (위 «사용자와 일하는 방식» · 2026-11-20)
- 커밋 메시지는 한국어 · 접두어 없이 (수업 저장소 시절 커밋의 `mini_project: …` 는 그대로 둠)
