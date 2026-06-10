# Diary Template Generator - 상세 아키텍처 가이드

본 문서는 사용자의 입력을 받아 AI가 다이어리/플래너 PDF를 동적으로 생성하는 **Diary Template Generator**의 구조와 각 컴포넌트의 동작 원리를 개발자 수준에서 상세하게 기술한 가이드입니다. 이 문서만으로도 전체 데이터 파이프라인과 소스 코드의 역할, 그리고 AI가 텍스트를 넘어 정교한 문서 레이아웃을 다루기 위해 적용된 제어 기법들을 이해할 수 있습니다.

---

## 1. 시스템 다이어그램

이 시스템은 클라이언트의 요청이 Flask 백엔드를 거쳐 Gemini AI 모델로 전달되고, 생성된 결과물이 자체 렌더링 엔진(매크로/스냅 보정)을 거쳐 최종 PDF로 변환되는 선형적인 파이프라인을 가집니다.

```mermaid
flowchart TD
    Client[Web Client (Browser)]
    API[Flask API / app.py]
    Gen[Generator Engine / core/generator.py]
    Gemini[Google Gemini AI]
    Renderer[Renderer / core/renderer.py]
    PDFMgr[PDF Manager / core/pdf_manager.py]
    WeasyPrint[WeasyPrint PDF Engine]
    
    Client -- "POST /api/generate-pdf\n(Title, Size, Mode)" --> API
    API -- "Request Layout" --> Gen
    
    Gen -- "1. Pass 1: Initial Prompt" --> Gemini
    Gemini -- "Raw HTML/CSS" --> Gen
    Gen -- "2. Pass 2: Self-Reflection Prompt" --> Gemini
    Gemini -- "Corrected HTML/CSS" --> Gen
    
    Gen -- "Parsed HTML/CSS" --> Renderer
    Renderer -- "1. process_repeat_macros()\n2. snap_css_to_grid()\n3. assemble_master_html()" --> Renderer
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

- **`templates/index.html` & `static/script.js`**: 단일 페이지 애플리케이션(SPA) 형태로 사용자가 플래너의 종류(일간, 주간, 월간, 습관 트래커 등), 용지 크기(A4, A5, B5), 디자인 모드(Print/Guide)를 선택합니다.
- **`app.py`**: Flask 앱의 진입점으로 핵심 REST API를 정의합니다.
  - `/api/generate-pdf`: 폼 데이터를 JSON으로 받아 파이프라인(`generate_layout_html` -> `generate_pdf`)을 실행.
  - `/api/download-pdf/<file_id>`: 로컬에 임시 생성된 PDF 파일을 클라이언트에게 첨부(attachment) 방식으로 내려줍니다.
  - `/api/cleanup-pdf`: 서버 디스크 공간 절약을 위해 클라이언트가 이탈하거나 명시적으로 파일 파기 요청 시 즉각 PDF를 삭제합니다.

### 2.2. 생성 엔진 (`core/generator.py` & `core/prompts.py`)

Gemini AI 모델이 단순히 "웹 페이지"를 만드는 것이 아니라 "출력용 픽셀 퍼펙트 문서"를 만들도록 하기 위해 특수한 프롬프트 엔지니어링과 **2-Pass (Self-Reflection) 기법**을 적용합니다.

1. **Pass 1 (초안 생성)**:
   - `prompts.py`에 정의된 모드별(일반/가이드) 시스템 프롬프트를 주입합니다.
   - 캔버스 너비/높이(`cw`, `ch` 변수)를 동적으로 주입하여 컨테이너 밖으로 내용이 벗어나지 않도록 강제합니다.
   - `<table>` 대신 `Flexbox` 사용, 영어 번역 강제, 불필요한 설명 텍스트 배제 등의 엄격한 제약 조건을 전달합니다.

2. **Pass 2 (규칙 검증 및 자가 교정)**:
   - LLM이 종종 디자인 제약을 무시하는 문제를 해결하기 위해, Pass 1에서 얻은 HTML/CSS를 다시 LLM에게 넘겨 오류를 검사하도록 지시합니다.
   - 예시 규칙: "바깥쪽 래퍼에 패딩이 있으면 제거할 것", "테두리 중복을 막기 위해 모든 내부 박스는 `border-bottom`, `border-right`만 사용할 것"
   - 이 과정을 통해 레이아웃이 깨질 확률을 극적으로 낮춥니다.

### 2.3. 매크로 및 렌더링 엔진 (`core/renderer.py`)

단일 호출 안에서 LLM이 너무 많은 코드를 짜면 속도가 느려지거나 중간에 생성이 끊깁니다. 이를 해결하기 위해 자체적인 매크로 문법과 CSS 후처리기를 구현했습니다.

* **반복 매크로 처리 (`process_repeat_macros`)**:
  - AI는 `31일 달력 칸`을 일일이 타이핑하지 않고 `<repeat count="31">...{i+1}...</repeat>` 형태로 작성합니다.
  - 이 모듈 내부의 정규 표현식 파서가 `count`만큼 내부 태그를 복제하고, `{i}`, `{i+1}`, `{i+6:02d}` 와 같은 인덱스 변수들을 실제 숫자(예: 0, 1, 06)로 치환합니다.

* **동적 캔버스 계산 (`get_page_config`)**:
  - A4, A5 등 용지 스펙에 맞춰 `weasyprint`에서 렌더링될 때 딱 들어맞는 픽셀(px) 너비/높이, 그리고 여백 보정 값을 계산합니다.

* **가이드 모드 그리드 스내핑 (`snap_css_to_grid`)**:
  - "손글씨 불렛 저널 모드"에서는 종이에 20px 단위의 점(Dot) 그리드가 배경에 깔립니다.
  - AI가 생성한 CSS의 모든 세로 속성(height, padding, margin, gap 등)의 픽셀 값을 정규식으로 추출해, 강제로 **20의 배수(20px, 40px, 60px...)**로 반올림하여 스냅(Snap)시킵니다. 이를 통해 실제 종이에 인쇄했을 때 컨텐츠가 도트 그리드 라인과 오차 없이 완벽하게 일치하게 됩니다.

* **마스터 HTML 조립 (`assemble_master_html`)**:
  - AI가 던져준 원시 HTML, 조립된 CSS, 매크로가 해제된 Body 요소, 그리고 동적으로 생성된 배경(Dot Grid 또는 Lined SVG) 코드를 하나의 최종 `<!DOCTYPE html>` 템플릿에 안전하게 묶어냅니다.

### 2.4. PDF 매니저 및 가비지 컬렉터 (`core/pdf_manager.py`)

* **PDF 생성 (`generate_pdf`)**: WeasyPrint 라이브러리를 통해 최종 조립된 Master HTML 코드를 실제 PDF 파일 버퍼로 렌더링하여 운영체제의 `tempfile` 경로에 임의의 UUID 이름으로 저장합니다.
* **가비지 컬렉션 (`cleanup_old_pdfs`)**:
  - 새로운 PDF 생성을 요청할 때마다 디렉토리를 검사하여 **수정된 지 1시간이 넘은 찌꺼기 PDF 파일**을 자동으로 삭제(`os.remove`)합니다.
  - 이는 사용자가 페이지를 강제로 종료하여 프론트엔드의 `/api/cleanup-pdf` 이탈 이벤트가 트리거되지 못했을 경우 발생하는 디스크 용량 누수(Disk Leak)를 방지하는 중요한 방어 로직입니다.

---

## 3. 핵심 디자인 철학

1. **AI의 한계는 백엔드 전처리/후처리로 극복한다.**
   AI에게 "30칸을 그려라"라고 지시하기보다 "1칸을 그리고 반복 태그를 써라"라고 지시한 뒤 백엔드에서 30칸을 복제하는 것이 훨씬 신뢰성이 높습니다.
2. **환각(Hallucination) 방어용 2차 검증**
   LLM이 종종 디자인 가이드(특히 CSS 테두리나 패딩)를 위반하는 현상을 막기 위해, 코드를 다시 리뷰하라는 2차 프롬프트를 던져 안정성을 대폭 향상시켰습니다.
3. **Stateless 구조 유지**
   플래너 PDF는 임시 데이터입니다. 데이터베이스(DB)를 전혀 사용하지 않으며, PDF는 생성 후 일회성으로 다운로드되고 즉시 파기되도록 설계하여 인프라 유지 비용을 최소화했습니다.
