# Diary Template Generator - 상세 아키텍처 가이드

본 문서는 사용자의 입력을 받아 AI가 다이어리/플래너 PDF를 동적으로 생성하는 **Diary Template Generator**의 구조와 각 컴포넌트의 동작 원리를 개발자 수준에서 상세하게 기술한 가이드입니다. 이 문서만으로도 전체 데이터 파이프라인과 소스 코드의 역할, 그리고 AI가 텍스트를 넘어 정교한 문서 레이아웃을 다루기 위해 적용된 제어 기법들을 이해할 수 있습니다.

---

## 1. 시스템 다이어그램

이 시스템은 클라이언트의 요청이 Flask 백엔드를 거쳐 Gemini AI 모델로 전달되고, 생성된 결과물이 자체 렌더링 엔진(매크로/테마/스냅 보정)을 거쳐 최종 PDF로 변환되는 선형적인 파이프라인을 가집니다.

```mermaid
flowchart TD
    Client[Web Client (Browser)]
    API[Flask API / app.py]
    Gen[Generator Engine / core/generator.py]
    Gemini[Google Gemini AI]
    Renderer[Renderer / core/renderer.py]
    Themes[Themes / core/themes.py]
    Macros[Macros / core/macros.py]
    PDFMgr[PDF Manager / core/pdf_manager.py]
    WeasyPrint[WeasyPrint PDF Engine]
    
    Client -- "POST /api/generate-pdf\n(Title, Size, Mode)" --> API
    API -- "Request Layout" --> Gen
    
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
    API -- "JSON Response {file_id}" --> Client
    
    Client -- "GET /api/download-pdf/{id}" --> API
    API -- "Return PDF File" --> Client
```

---

## 2. 모듈별 상세 분석

### 2.1. 프론트엔드 및 진입점 (`static/`, `templates/`, `app.py`)

- **`templates/index.html` & `static/script.js`**: 단일 페이지 애플리케이션(SPA) 형태로 사용자가 플래너의 종류, 용지 크기(A4, A5, B5), 디자인 모드(Print/Guide)를 선택합니다.
- **`app.py`**: Flask 앱의 진입점으로 핵심 REST API를 정의합니다.
  - `/api/generate-pdf`: 폼 데이터를 JSON으로 받아 파이프라인(`generate_layout_html` -> `generate_pdf`)을 실행.
  - `/api/download-pdf/<file_id>`: 로컬에 임시 생성된 PDF 파일을 클라이언트에게 첨부(attachment) 방식으로 내려줍니다.
  - `/api/cleanup-pdf`: 서버 디스크 공간 절약을 위해 클라이언트가 이탈하거나 명시적으로 파일 파기 요청 시 즉각 PDF를 삭제합니다.

#### 2.2. 생성 엔진 (`core/generator.py` & `core/prompts/` 패키지 & `core/model_config.py`)

Gemini AI 모델이 단순히 "웹 페이지"를 만드는 것이 아니라 "출력용 픽셀 퍼펙트 문서"를 만들도록 하기 위해 특수한 프롬프트 엔지니어링과 **2-Pass (Self-Reflection) 기법**을 적용합니다.

1. **`core/model_config.py`**:
   - 공식 지원되는 최신 **`google-genai` SDK**를 사용해 Gemini 클라이언트를 안전하게 초기화합니다.
2. **`core/prompts/` 패키지**:
   - 기존의 비대한 단일 프롬프트 파일을 구조적이고 관리하기 쉬운 기능별 파일로 분리하여 패키지화했습니다.
   - **`layout_hints.py`**: 27개 이상의 다채로운 플래너 양식(만다라트, 먼슬리 등)의 핵심 가이드 텍스트와 검색 키워드 사전(`LAYOUT_HINTS`)을 정의합니다.
   - **`base_templates.py`**: 기본 및 핸드 드로잉 가이드 모드의 `SYSTEM_PROMPT` 뼈대를 관리하며, 템플릿 포맷팅 시 혼선을 주지 않도록 매크로용 중괄호를 `{{i}}`로 안전하게 이스케이프 처리했습니다.
   - **`review_templates.py`**: 2차 자가검증에 쓰일 엄격한 테두리 및 레이아웃 관련 디자인 룰(`REVIEW_PROMPT_TEMPLATE`)을 관리합니다.
   - **`__init__.py`**: 모듈 간 결합을 총괄하고 외부 진입점인 `get_system_prompts()`와 `get_review_prompt()` 함수를 제공합니다.
3. **`core/generator.py` (2-Pass 자가 교정 및 제어 흐름 분할)**:
   - 복잡했던 LLM 호출 및 검증 흐름을 독립된 서브 함수로 세분화했습니다.
   - **`_request_initial_layout(...)`** (초안 생성): `base_templates`를 참조하여 API를 호출하고 HTML/CSS 초안을 생성 및 안전성/유사성 필터 예외 처리를 수행합니다.
   - **`_request_self_reflection(...)`** (자가 검증): 1차 초안을 디자인 규칙(`review_templates`)과 동적 보정 룰을 입혀 Gemini에 재전송함으로써, 레이아웃의 완성도를 높이고 버그가 없는 최종 수정본을 확보합니다.
   - **`generate_layout_html(...)`**: 위 단계적 함수들을 체이닝하여 전체적인 초안 생성부터 자가 검증, 마스터 HTML 결합까지의 생성 라이프사이클을 조율합니다.

### 2.3. 매크로 및 테마 렌더링 엔진 (`core/renderer.py` & `core/themes.py` & `core/macros.py`)

단일 호출 안에서 LLM이 너무 많은 코드를 짜면 속도가 느려지거나 중간에 생성이 끊깁니다. 이를 해결하기 위해 백엔드에 자체적인 매크로 분기 및 후처리기를 완벽히 분할(Decoupling)하여 구성했습니다.

* **`core/themes.py` (테마 스타일 처리)**:
  - `Cute`, `Editorial`, `Minimal` 각 디자인 컨셉에 맞춰 폰트 링크 인젝션, 테마 CSS 정의, 테두리(Border) 색상 변경 및 border-radius 적용을 처리합니다.
* **`core/macros.py` (반복 매크로 및 그리드 스냅)**:
  - **반복 매크로 (`process_repeat_macros`)**: AI가 대량의 행/열을 일일이 타이핑하지 않고 `<repeat count="N">` 형태로 출력한 태그를 감지하여, {i} 등 시퀀스 변수를 숫자로 치환하고 반복 팽창시킵니다.
  - **그리드 스냅 (`snap_css_to_grid`)**: 가이드 도안 모드에서 20px 도트 그리드 배경에 컨텐츠 라인들이 정확히 정렬되도록 CSS의 모든 높이/여백(px) 단위를 강제로 20의 배수로 반올림하여 정렬(Snapping)합니다.
* **`core/renderer.py` (조립 및 레이아웃)**:
  - 용지 크기 연산(`get_page_config`)과 분할된 모듈들을 사용해 최종 Master HTML 문서를 완성합니다.

### 2.4. PDF 매니저 및 가비지 컬렉터 (`core/pdf_manager.py`)

* **PDF 생성 (`generate_pdf`)**: WeasyPrint 라이브러리를 통해 최종 조립된 Master HTML 코드를 실제 PDF 파일 버퍼로 렌더링하여 운영체제의 `tempfile` 경로에 임의의 UUID 이름으로 저장합니다.
* **가비지 컬렉션 (`cleanup_old_pdfs`)**:
  - 새로운 PDF 생성을 요청할 때마다 디렉토리를 검사하여 **수정된 지 1시간이 넘은 찌꺼기 PDF 파일**을 자동으로 삭제(`os.remove`)합니다.
  - 이는 사용자가 페이지를 강제로 종료하여 프론트엔드의 `/api/cleanup-pdf` 이탈 이벤트가 트리거되지 못했을 경우 발생하는 디스크 용량 누수(Disk Leak)를 방지하는 중요한 방어 로직입니다.

### 2.5. 테스트 디렉토리 구조 (`tests/`)
- 루트에 흩어져 있던 테스트 도구들을 `/tests/` 디렉토리로 모아 프로젝트 정렬 상태를 정돈하였습니다.
- `test_macro.py`: 반복 매크로의 동작성 검증.
- `test_generation.py`, `test_ledger.py`, `test_all.py`: 용지 크기 및 모드별 다이어리 템플릿 대량 자동 생성.
- `test_pdf.py`: WeasyPrint를 사용한 PDF 로컬 빌드 및 인쇄 상태 검증.
- 모든 출력 결과는 `tests/output/` 경로 아래 독립적으로 축적됩니다.

---

## 3. 핵심 디자인 철학

1. **AI의 한계는 백엔드 전처리/후처리로 극복한다.**
   AI에게 "30칸을 그려라"라고 지시하기보다 "1칸을 그리고 반복 태그를 써라"라고 지시한 뒤 백엔드에서 30칸을 복제하는 것이 훨씬 신뢰성이 높습니다.
2. **관심사 분리 (Separation of Concerns)**
   테마 설정, 반복 매크로 파싱, 마스터 조립 로직을 모듈 단위로 완전히 쪼개어 코드 복잡도를 낮추고 유지보수성과 확장성을 극대화했습니다.
3. **Stateless 구조 유지**
   플래너 PDF는 임시 데이터입니다. 데이터베이스(DB)를 전혀 사용하지 않으며, PDF는 생성 후 일회성으로 다운로드되고 즉시 파기되도록 설계하여 인프라 유지 비용을 최소화했습니다.
