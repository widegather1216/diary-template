# Diary Template Generator - 상세 아키텍처 가이드

본 문서는 사용자의 입력을 받아 AI가 다이어리/플래너 PDF를 동적으로 생성하는 **Diary Template Generator**의 구조와 각 컴포넌트의 동작 원리를 개발자 수준에서 상세하게 기술한 가이드입니다.

---

## 1. 시스템 아키텍처 개요

이 시스템은 클라이언트의 요청이 Flask 백엔드를 거쳐 Gemini AI 모델로 전달되고, 생성된 결과물이 자체 렌더링 엔진(매크로/테마/스냅 보정)을 거쳐 최종 PDF로 변환되는 선형적인 파이프라인을 가집니다.

### 1.1. 시스템 다이어그램

```mermaid
flowchart TD
    Client[Web Client (Browser)]
    API[Flask API / app.py]
    Gen[Generator Engine / core/generator.py]
    Gemini[Google Gemini AI]
    Prompts[Prompts Package / core/prompts/]
    Renderer[Renderer / core/renderer.py]
    Themes[Themes / core/themes.py]
    Macros[Macros / core/macros.py]
    PDFMgr[PDF Manager / core/pdf_manager.py]
    WeasyPrint[WeasyPrint PDF Engine]
    
    Client -- "POST /api/generate-pdf\n(Title, Size, Mode)" --> API
    API -- "Request Layout" --> Gen
    
    Gen -- "Extract Rules & Templates" --> Prompts
    Gen -- "1. Pass 1: Initial Prompt" --> Gemini
    Gemini -- "Raw HTML/CSS" --> Gen
    Gen -- "2. Pass 2: Self-Reflection Prompt" --> Gemini
    Gemini -- "Corrected HTML/CSS" --> Gen
    
    Gen -- "Parsed HTML/CSS" --> Renderer
    Renderer -- "1. apply_theme_aesthetics()" --> Themes
    Renderer -- "2. process_repeat_macros()\n3. snap_css_to_grid()" --> Macros
    Renderer -- "Master HTML" --> PDFMgr
    
    PDFMgr -- "HTML String" --> WeasyPrint
    WeasyPrint -- "Binary PDF" --> PDFMgr
    PDFMgr -- "Return file_id" --> API
    Gen -- "Progress Updates (layout_complete, etc.)" --> API
    API -- "SSE Task Stream (status, message)" --> Client
    API -- "JSON Response {file_id} (when fully success)" --> Client
    
    Client -- "GET /api/download-pdf/{id}" --> API
    API -- "Return PDF File" --> Client
```

### 1.2. 디렉토리 구조도 (Directory Structure)

전체 프로젝트의 모듈 구조와 레이아웃은 아래와 같이 체계적으로 구조화되어 있습니다.

```text
diary-template/
├── app.py                      # Flask 애플리케이션 진입점 및 API 라우터
├── architecture.md             # 본 아키텍처 문서
├── Dockerfile                  # WeasyPrint 설치 및 컨테이너 환경 명세
├── docker-compose.yml          # 로컬 개발 및 컨테이너 오케스트레이션 설정
├── requirements.txt            # Python 라이브러리 의존성 명세 (google-genai, WeasyPrint 등)
├── core/                       # 핵심 백엔드 패키지
│   ├── __init__.py
│   ├── config.py               # [NEW] 중앙 집중식 설정 및 상수 관리 모듈
│   ├── generator.py            # 2-Pass Gemini 생성 및 자가검증 엔진
│   ├── macros.py               # repeat 매크로 파서 및 그리드 스냅 엔진
│   ├── model_config.py         # Gemini 클라이언트 및 API 설정 관리
│   ├── pdf_manager.py          # WeasyPrint PDF 렌더러 및 임시 파일 가비지 컬렉터
│   ├── renderer.py             # 페이지 치수 설정 및 Master HTML 조립기
│   ├── task_manager.py         # [NEW] 스레드-세이프 인메모리 태스크 관리자
│   ├── themes.py               # Minimal/Cute/Editorial CSS 테마 인젝터
│   └── prompts/                # LLM 프롬프트 및 가이드 지침 패키지
│       ├── __init__.py         # 프롬프트 바인딩 및 매칭 함수 노출
│       ├── base_templates.py   # 시스템 프롬프트(System, Guide) 뼈대 템플릿
│       ├── layout_hints.py     # 27개 플래너 가이드 텍스트 및 키워드 사전
│       └── review_templates.py  # Self-Reflection 검증 디자인 룰
├── static/                     # 프론트엔드 정적 파일
│   ├── script.js               # SPA 프론트엔드 비동기 API 제어 로직
│   ├── style.css               # 프론트엔드 UI/UX CSS 명세
│   ├── editor.js               # [NEW] 멀티페이지 다이어리 편집기 인터랙션 로직
│   └── editor.css              # [NEW] 멀티페이지 다이어리 편집기 전용 레이아웃/인쇄 CSS 명세
├── templates/
│   ├── index.html              # 메인 입력 및 설정 UI 대시보드
│   └── editor.html             # [NEW] 멀티페이지 다이어리 빌더 UI 템플릿
└── tests/                      # 테스트 스위트
    ├── test_all.py             # 종합 통합 테스트
    ├── test_macro.py           # 매크로 치환 수식 유닛 테스트
    ├── test_prompts.py         # 프롬프트 키워드 동적 매칭 유닛 테스트
    └── output/                 # 테스트 실행 시 생성된 HTML/PDF 파일 보관소
```

### 1.3. 주요 소스 코드 파일별 역할 요약 (Module Role Summary)

| 파일 경로 | 주요 역할 및 개발 책임 범위 |
| :--- | :--- |
| **`app.py`** | 클라이언트의 웹 요청을 접수하고 비동기 PDF 생성, SSE(Server-Sent Events)를 통한 실시간 상태 진행 스트리밍, 임시 파일 생성 및 다운로드 게이트웨이 역할을 수행하며 라이프사이클을 전담 제어. 비동기 백그라운드 태스크들(`bg_generate_task`, `bg_generate_html_task`)의 공통된 파싱 및 AI 호출 로직을 `_parse_and_generate_html()` 공통 헬퍼로 통합·모듈화하여 코드 중복 제거. 다운로드 시 UUID 형식 정합성(32자 및 16진수 포맷)을 엄격히 검증해 DoS 방지. |
| **`core/config.py`** | 프로젝트 전역에 흩어져 있던 magic number, 디렉토리 경로, 모델 명, 레이아웃 힌트 Baseline 키, 해상도 상수 등을 일괄 집중화하여 단일 진실 공급원(Single Source of Truth) 역할 수행. |
| **`core/generator.py`** | 1차 초안 생성(`_request_initial_layout`)과 2차 자가검증(`_request_self_reflection`)을 병렬 체이닝하여 AI 생성물의 규칙 준수를 강제하는 오케스트레이터. 재시도 가드 처리를 내재화하여 일시적 API 503 오류 발생 시 복구 수행. |
| **`core/prompts/`** | 템플릿과 스타일 가이드라인을 격리하여, LLM 호출 시 필요한 최적의 컨텍스트(Few-shot baseline + 동적 layout_hints)를 선별 및 조립해 주는 프롬프트 데이터베이스. |
| **`core/renderer.py`** | 용지 포맷(A4, A5 등)에 따른 최적 픽셀 치수를 설정하고, 테마 및 매크로가 후처리 완료된 CSS/HTML을 Master HTML 포맷으로 패키징하는 템플릿 어셈블러. |
| **`core/macros.py`** | AI의 출력 토큰 낭비를 예방하기 위해 반복 태그(`<repeat>`)를 팽창하고, 도안 모드의 그리드 일치를 위해 CSS 치수를 수학적으로 20px 배수로 스냅하는 후처리 엔진. 정규식 컴파일을 사전 수행하여 런타임 렌더링 성능 향상. |
| **`core/themes.py`** | 사용자가 선택한 스타일에 부합하는 Web Font(Google Fonts)를 정의하고 테마별 스타일 데코레이터 CSS를 주입하는 비주얼 에스테틱 관리자. fonts `<style>` 래핑을 분리 구조화. |
| **`core/task_manager.py`** | 디스크 I/O 없이 메모리 상에서 비동기 태스크들의 진행 상황을 저장하고 스레드 안전성(`threading.Lock`)을 보장하는 인메모리 데이터 스토어. |
| **`core/pdf_manager.py`** | 조립 완료된 Master HTML을 WeasyPrint 엔진으로 렌더링하고, 디스크 용량 누수를 방지하기 위해 생성 1시간이 지난 임시 PDF 파일을 청소하는 GC 시스템. 폰트/CSS 등의 웹 자원을 다운로드하고 디스크에 임시 캐싱하는 3계층 프록시 캐시 파이프라인 내장. |
| **`templates/editor.html`** | 멀티페이지 다이어리 편집기의 레이아웃을 정의하는 메인 마크업 템플릿. 좌측 페이지 리스트(드래그 오버 & 인라인 이름 수정), 중앙 캔버스(Iframe 미리보기 & 하이퍼링크 연결 모드), 우측 글로벌 다이어리 설정창 제공. |
| **`static/editor.js`** | 멀티페이지 빌더의 프론트엔드 비동기 통신 및 드래그 앤 드롭 정렬 알고리즘, 인라인 이름 수정 이벤트(Enter/Escape/Blur), 그리고 인쇄 시 스타일 간섭 방지를 위한 브라우저 CSSOM 파서 기반 스코핑(Scoping) 렌더링을 관장. |
| **`static/editor.css`** | 멀티페이지 편집기 전용 레이아웃, 인라인 수정 필드, 드래그 드롭 타겟 가이드라인(퍼플 글로우 상/하 삽입 라인) 및 브라우저 강제 배경 인쇄 속성(`print-color-adjust`) 정의. |

---

## 2. 모듈별 상세 기술 분석

### 2.1. 프론트엔드 및 진입점 (`static/`, `templates/`, `app.py`)

- **`templates/index.html` & `static/script.js`**:
  - 단일 페이지 애플리케이션(SPA) 형태로 사용자가 단일 플래너를 생성하고 미리보는 대시보드입니다. 중복 하드코딩된 동의어 객체(`categoryMappings`)를 완전히 제거하고 초기 구동 시 `/api/config`를 호출해 서버의 단일 진실 공급원(`LAYOUT_HINTS`) 설정을 가져오도록 단순화했습니다.
- **`templates/editor.html` & `static/editor.js` & `static/editor.css` (멀티페이지 다이어리 빌더)**:
  - 다중 페이지 다이어리를 생성, 복제, 삭제하고 드래그 정렬 및 페이지 이동 하이퍼링크를 연결할 수 있는 빌더 엔진입니다.
  - **글로벌 테마 설정 통합**: 페이지 생성 모달 내의 불필요한 중복 스타일 선택기를 삭제하고, 우측 글로벌 패널의 디자인 스타일 설정값(`editorStyleTheme.value`)으로 생성을 통일화해 디자인 일관성을 높였습니다.
  - **드래그 앤 드롭 정렬**: HTML5 Drag and Drop API를 연동하고, 드래그 오버 시 상단/하단 50% 지점을 수학적으로 감지하여 보라색 발광 가이드라인(`.drag-over-above`, `.drag-over-below`)을 표시해 주는 렉트 감지 UX를 탑재했습니다. 정렬 시 내부 `pages` 배열을 정밀하게 재배치합니다.
  - **인라인 이름 수정**: 페이지명을 더블클릭하거나 연필 모양 버튼 클릭 시, 텍스트 스팬이 입력 필드(`<input class="page-item-title-input">`)로 대체되며 텍스트 전체 자동 선택 및 포커싱이 제공됩니다. 엔터(`Enter`)나 영역 이탈(`blur`) 시 자동 저장, `Escape` 시 복구되는 반응형 UX를 구현했습니다.
  - **인쇄 시 스타일 간섭 방지 (CSS Scoping Engine)**:
    - 브라우저 인쇄 모드(`window.print()`) 시 모든 페이지가 하나의 DOM에 쏟아져 나오므로 스타일 시트 충돌이 발생합니다.
    - 이를 막기 위해 `DOMParser`로 개별 페이지 HTML을 분석하고, 브라우저 native CSSOM 파서를 사용해 모든 CSS 룰 셀렉터 앞에 해당 페이지 ID(예: `#page-123`)를 강제 접두사로 접합하는 `scopeCSS`와 `scopeRule` 로직을 내장하여 스타일 오염을 완벽 차단했습니다.
    - Google Fonts `<link>` 태그들을 검출해 메인 문서 헤더로 이식함으로써 폰트 미출력 버그를 수정했습니다.
  - **배경 인쇄 보장**:
    - 인쇄 스타일시트 내에 `-webkit-print-color-adjust: exact !important; print-color-adjust: exact !important;`를 전역 부여하여 줄노트, 모눈 격자, 테마 배경색이 출력되지 않는 브라우저 기본 동작을 우회하였습니다.
- **`app.py`**:
  - Flask 앱의 진입점으로 핵심 REST API를 정의합니다.
  - `/api/generate-pdf`: 폼 데이터를 JSON으로 받아 백그라운드 태스크로 `generate_process`를 실행하고 템플릿을 생성합니다.
  - `/api/task-stream/<task_id>`: SSE(Server-Sent Events) 프로토콜을 사용하여 클라이언트에게 실시간 생성 진행 상태(상태 텍스트, AI 자가수정 여부 등)를 지속적으로 스트리밍합니다.
  - `/api/download-pdf/<file_id>`: 로컬에 임시 생성된 PDF 파일을 클라이언트에게 첨부(attachment) 방식으로 다운로드 제공.
  - `/api/cleanup-pdf`: 서버 디스크 공간 절약을 위해 클라이언트가 이탈하거나 명시적으로 파일 파기 요청 시 즉각 PDF를 삭제합니다.

---

### 2.2. 상태 관리 및 SSE Race Condition 방어

비동기 통신 중 발생할 수 있는 엣지 케이스 및 보안적 결함을 방어하기 위한 로직이 구현되어 있습니다.

- **스레드-세이프 인메모리 태스크 스토어 (`core/task_manager.py`)**:
  - 기존의 로컬 파일 디렉토리 I/O 방식에서 전면 메모리 저장 객체 구조로 리팩토링되었습니다.
  - 모든 태스크 상태 조작(`create_task`, `update_task`, `get_task`)에 Python `threading.Lock()`을 바인딩하여 동시성 레이스 컨디션을 완벽히 제어합니다.
  - 백그라운드 가비지 컬렉션(GC) 스레드를 실행하여, 600초가 경과한 태스크나 성공/실패 후 120초가 지난 완료된 태스크를 자동으로 소거해 메모리 누수를 원천 차단합니다.
- **Race Condition 방지**:
  - AI 레이아웃 생성이 끝난 직후 `status='success'`를 방출할 경우, PDF 생성이 끝나기도 전에 프론트엔드가 다운로드 링크를 조립하여 `undefined_undefined.pdf` 버그를 일으킵니다. 이를 막기 위해 `core/generator.py`는 완료 시 `layout_complete`라는 중간 상태만을 방출하며, 오직 `app.py`에서 PDF 변환 및 파일명 저장이 완벽히 종료된 마지막 단계에서만 최종 `success` 상태를 방출하도록 상태 코드를 분리(Decoupling)했습니다.
- **UUID 정합성 검증 및 입력 값 가드 (`app.py`)**:
  - PDF 다운로드 시 전달받는 `file_id`에 대해 단순 16진수 캐스팅(`int(file_id, 16)`)을 행하기 전, 글자 수가 정확히 **32자**인지 가드 로직을 거칩니다.
  - 이를 통해 비정상적으로 길거나 악의적으로 포맷팅된 인자를 사전 차단함으로써 대용량 정수 캐스팅 연산으로 인한 CPU DoS(Denial of Service) 공격 가능성을 배제하였습니다.

---

### 2.3. 생성 엔진 (`core/generator.py` & `core/prompts/` 패키지)

Gemini AI 모델이 단순히 "웹 페이지"를 만드는 것이 아니라 "출력용 픽셀 퍼펙트 문서"를 만들도록 하기 위해 특수한 프롬프트 엔지니어링과 **2-Pass (Self-Reflection) 기법**을 적용합니다.

#### A. `core/prompts/` 패키지
코드 유지보수성과 가독성을 위해 단일 프롬프트 파일 구조를 기능 단위로 쪼개어 패키지화했습니다.

1. **`layout_hints.py`**:
   - 27개 이상의 다채로운 플래너 양식(만다라트, 먼슬리, 가계부, 해빗트래커 등)의 핵심 가이드 텍스트와 검색 키워드 사전(`LAYOUT_HINTS`)을 정의합니다.
2. **`base_templates.py`**:
   - 기본 및 핸드 드로잉 가이드 모드의 `SYSTEM_PROMPT` 뼈대를 관리하며, 템플릿 포맷팅 시 혼선을 주지 않도록 매크로용 중괄호를 `{{i}}`로 안전하게 이스케이프 처리했습니다.
3. **`review_templates.py`**:
   - 2차 자가검증에 쓰일 엄격한 테두리 및 레이아웃 관련 디자인 룰(`REVIEW_PROMPT_TEMPLATE`)을 관리합니다.
4. **`__init__.py`**:
   - 모듈 간 결합을 총괄하고 외부 진입점인 `get_system_prompts()`와 `get_review_prompt()` 함수를 제공합니다.

#### 💡 동적 힌트 매칭 및 Baseline Few-shot 메커니즘 (`__init__.py`)
LLM이 레이아웃을 무너지지 않게 렌더링하도록 유도하기 위해 다음 두 가지 방식을 융합하여 프롬프트를 구성합니다.
* **Baseline Few-shot 탑재**: 사용자의 입력값과 상관없이 가장 복잡하고 정교한 규칙을 가진 **5가지 양식(Mandalart, Monthly, Weekly, Daily, Cornell)**의 레이아웃 가이드를 항상 기본 프롬프트에 포함합니다. 이는 모델에게 코딩 지침서(Few-shot Context) 역할을 합니다.
* **공백 무시 및 오타(Typo) 방어 키워드 매칭**: 사용자가 입력한 제목과 설명을 소문자화 및 공백을 모두 제거한 상태로 변환한 뒤, `layout_hints.py`에 등록된 확장 키워드 사전("플래너", "플레너", "다이얼리" 등 오타 포함)과 대조하여 정확한 가이드를 동적으로 매칭합니다. 이로 인해 사소한 맞춤법 오류에도 레이아웃이 붕괴되지 않는 견고한 파싱이 가능합니다.

#### B. `core/generator.py` (2-Pass 자가 교정 및 제어 흐름 분할)
복잡했던 LLM 호출 및 검증 흐름을 독립된 서브 함수로 세분화했습니다.

* **`_request_initial_layout(...)`** (초안 생성):
  - `base_templates`를 참조하여 API를 호출하고 HTML/CSS 초안을 생성하며 안전성/유사성 필터 예외 처리를 수행합니다.
* **`_request_self_reflection(...)`** (자가 검증):
  - 1차 초안을 아래의 엄격한 디자인 규칙(`review_templates`)과 동적 보정 룰을 입혀 Gemini에 재전송함으로써, 레이아웃의 완성도를 높이고 버그가 없는 최종 수정본을 확보합니다.
* **`generate_layout_html(...)`**:
  - 위 단계적 함수들을 체이닝하여 전체적인 초안 생성부터 자가 검증, 마스터 HTML 결합까지의 생성 라이프사이클을 조율합니다.

#### 2차 검증(Pass 2)의 8대 핵심 디자인 룰
| 규칙 번호 | 규칙 명칭 | 상세 설명 |
| :--- | :--- | :--- |
| **1** | 외곽 패딩 제거 | 최외곽 wrapper의 패딩은 반드시 `padding: 0;`으로 설정하여 여백 유실 방지 |
| **2** | 안내 지시문 제거 | `(여기에 작성)` 등 사용자가 인쇄용으로 쓰지 않는 괄호 지시어 완전 제거 |
| **3** | 수직 정렬 강제 | 모든 입력 칸 내의 텍스트는 Flexbox 수직 정렬(`align-items: center`) 적용 |
| **4** | 문자 밑줄 금지 및 보존 | 문자 `_______`를 사용하는 방식 금지. Flexbox 컨테이너의 하단 테두리(`border-bottom`)를 활용하되, 임의로 `border-bottom: none;`을 적용하여 렌더링을 파괴하는 행위를 절대 금지 |
| **5** | 넘침 방지 및 줄 바꿈 | 모든 셀에 `overflow: hidden` 강제 적용 및 긴 제목에 `word-break: keep-all` 부여 |
| **6** | 라벨 높이 정렬 | 텍스트 라벨과 공백 밑줄 라인은 하단 정렬(`align-items: flex-end`) 및 너비 하드코딩 금지 |
| **7 (7a~7g)** | 테두리 폐쇄 및 2px 방지 | 부모는 상/좌만, 자식은 하/우 테두리만 주어 2px 겹침을 방지하되 외곽선은 빈틈없이 닫음 |
| **7h** | 메모 영역 붕괴 및 배경오염 방지 | 메모 영역(`.lined-bg`)이 빈 태그로 렌더링되어 붕괴되지 않도록 공백 문자(`&nbsp;`)를 강제 삽입하며, AI가 임의로 커스텀 그라디언트 CSS 배경을 덮어씌우는 것을 엄격히 차단 |
| **7j** | 다단 컬럼 분리선 강제 | 데일리 플래너 등 2-column 다단 레이아웃 생성 시, 좌우 컬럼의 시각적 분리를 위해 무조건 `border-right`를 부여 |

---

### 2.3. 매크로 및 테마 렌더링 엔진 (`core/renderer.py` & `core/themes.py` & `core/macros.py`)

단일 호출 안에서 LLM이 너무 많은 코드를 짜면 속도가 느려지거나 중간에 생성이 끊깁니다. 이를 해결하기 위해 백엔드에 자체적인 매크로 분기 및 후처리기를 완벽히 분할(Decoupling)하여 구성했습니다.

#### A. `core/themes.py` (테마 스타일 처리)
- `Cute`, `Editorial`, `Minimal` 각 디자인 컨셉에 맞춰 폰트 링크 인젝션, 테마 CSS 정의, 테두리(Border) 색상 변경 및 border-radius 적용을 처리합니다.

#### B. `core/macros.py` (반복 매크로 및 그리드 스냅)
* **반복 매크로 파싱 (`process_repeat_macros`)**:
  - AI가 대량의 행/열을 일일이 타이핑하지 않고 `<repeat count="N">...</repeat>` 형태로 출력한 태그를 감지합니다.
  - 내부의 시퀀스 변수 `{i}`, `{i+1}`, `{i+6:02d}`와 같은 수식을 감지하여 0부터 N-1까지 숫자로 치환하고 반복 팽창시킵니다.
  - **수식 파싱 원리**: 정규식을 통해 `i + 상수` 혹은 `i - 상수`를 추출한 후, 현재 루프 인덱스 `step` 값과 덧셈/뺄셈 연산을 수행하여 최종 값을 포맷 문자열에 맞춰 치환합니다.
* **그리드 스냅 (`snap_css_to_grid`)**:
  - 가이드 도안 모드(`design_mode='guide'`)에서 20px 도트 그리드 배경에 컨텐츠 라인들이 정확히 정렬되도록 CSS의 모든 높이/여백(px) 단위를 강제로 20의 배수로 반올림하여 정렬(Snapping)합니다.
  - **수학적 보정 공식**:
    $$\text{Snapped Value} = \text{round}\left(\frac{\text{Original Value}}{20}\right) \times 20$$
  - 예: `height: 43px` ➡️ `height: 40px` / `margin-top: 11px` ➡️ `margin-top: 20px`

#### C. `core/renderer.py` (조립 및 레이아웃)
- 용지 크기 연산(`get_page_config`)과 분할된 모듈들을 사용해 최종 Master HTML 문서를 완성합니다.

---

### 2.4. PDF 매니저 및 가비지 컬렉터 (`core/pdf_manager.py`)

* **macOS 라이브러리 패치**: Darwin OS 감지 시 WeasyPrint가 Homebrew 기반 라이브러리(`pango`, `cairo` 등)를 원활히 바인딩할 수 있도록 process 내부의 `DYLD_FALLBACK_LIBRARY_PATH` 환경 변수를 동적으로 보정합니다. (기존의 위험한 `os.execve` 자가 재시작 메커니즘을 전면 제거하여 안정성 확보)
* **표준 SSL API 적용**: macOS의 Local SSL 검증 오류를 우회하기 위해 `ssl.create_default_context()`의 공개 속성들(`check_hostname = False`, `verify_mode = ssl.CERT_NONE`)을 정형화하여 사용합니다.
* **3계층 프록시 캐시 파이프라인**:
  - 구글 웹 폰트 CSS 및 WOFF2 바이너리와 같은 외부 네트워크 자원의 매번 다운로드되는 속도 저하를 막기 위해 캐시 레이어를 정교하게 구축했습니다.
  - `_read_from_cache(url)`: 로컬의 임시 캐시 디렉토리에 동일 자원의 해싱된 파일이 존재하는지 검사하며, `mimetypes` 표준 모듈을 통해 확장자별 올바른 MIME 타입을 바인딩합니다.
  - `_fetch_and_cache(url, timeout)`: 네트워크 통신을 거쳐 원격 리소스를 다운로드하고 이를 로컬 디렉토리에 캐싱합니다.
  - `cached_url_fetcher(url, timeout)`: 위 두 함수를 엮어 WeasyPrint에 전달되는 자원을 중간에서 가로채서 서빙하는 래퍼 역할을 수행합니다.
* **PDF 생성 (`generate_pdf`)**: WeasyPrint 라이브러리를 통해 최종 조립된 Master HTML 코드를 실제 PDF 파일 버퍼로 렌더링하여 운영체제의 `tempfile` 경로에 임의의 UUID 이름으로 저장합니다.
* **가비지 컬렉션 (`cleanup_old_pdfs`)**:
  - 새로운 PDF 생성을 요청할 때마다 디렉토리를 검사하여 **수정된 지 1시간이 넘은 찌꺼기 PDF 파일**을 자동으로 삭제(`os.remove`)합니다.
  - 이는 사용자가 페이지를 강제로 종료하여 프론트엔드의 `/api/cleanup-pdf` 이탈 이벤트가 트리거되지 못했을 경우 발생하는 디스크 용량 누수(Disk Leak)를 방지하는 중요한 방어 로직입니다.

---

## 3. 핵심 디자인 철학

1. **AI의 한계는 백엔드 전처리/후처리로 극복한다.**
   AI에게 "30칸을 그려라"라고 지시하기보다 "1칸을 그리고 반복 태그를 써라"라고 지시한 뒤 백엔드에서 30칸을 복제하는 것이 훨씬 신뢰성이 높습니다.
2. **관심사 분리 (Separation of Concerns)**
   테마 설정, 반복 매크로 파싱, 마스터 조립 로직을 모듈 단위로 완전히 쪼개어 코드 복잡도를 낮추고 유지보수성과 확장성을 극대화했습니다.
3. **Stateless 구조 유지**
   플래너 PDF는 임시 데이터입니다. 데이터베이스(DB)를 전혀 사용하지 않으며, PDF는 생성 후 일회성으로 다운로드되고 즉시 파기되도록 설계하여 인프라 유지 비용을 최소화했습니다.
