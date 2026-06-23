# FormWeaver - 개발자/에이전트 온보딩 가이드 (AGENTS.md)

이 문서는 새로운 대화창이나 다른 에이전트가 이 워크스페이스에 진입했을 때, 프로젝트의 성격, 아키텍처, 코드 디자인 철학 및 이전 작업 내역을 즉각적으로 파악하고 생산성을 낼 수 있도록 돕는 개발 지침서입니다.

---

## 1. 프로젝트 개요 (FormWeaver)
FormWeaver는 사용자의 자연어 요구사항을 바탕으로 AI(Gemini)가 아름다운 맞춤형 다이어리/플래너 템플릿(HTML/CSS)을 동적으로 생성하고, 이를 PDF로 다운로드하거나 멀티 페이지 단위로 연결 및 커스텀할 수 있는 **AI 기반 다이어리 스타터 제작 도구**입니다.

### 주요 기능
- **단일 페이지 생성기 (Main Page)**: 양식 이름과 요구사항, 스타일 테마를 지정하면 AI가 자가검증(Self-Reflection)을 거쳐 1장짜리 고품질 플래너 레이아웃을 빌드하고 PDF 다운로드를 제공합니다.
- **멀티 페이지 에디터 (Multi-Page Editor Builder)**: 사용자가 필요한 속지(먼슬리, 데일리 등)를 AI로 각각 만들고 복제할 수 있으며, 요소 클릭을 통해 속지 간 하이퍼링크를 연결한 뒤 일괄 인쇄(PDF 저장)할 수 있는 웹 오서링(Authoring) 도구입니다.

---

## 2. 핵심 기술 스택 및 구조
- **백엔드**: Python 3, Flask, `google-genai` SDK, `WeasyPrint` (PDF 렌더링 엔진)
- **프론트엔드**: Vanilla HTML, Vanilla CSS (테마별 HSL 및 세련된 다크모드/질감 효과), Vanilla JavaScript (SPA 형태 제어 및 링크 드래깅/바인딩 모션)
- **AI 엔진**: Gemini 2.5/3.5 (1차 초안 생성 및 2차 자가검증 셀프 리플렉션 2-Pass 구조)

### 핵심 디렉토리 구조
- [app.py](file:///Users/kimbeomjun/diary-template/app.py): Flask 애플리케이션 진입점 및 API 라우터 (비동기 태스크 실행, SSE 스트리밍 전담)
- [core/](file:///Users/kimbeomjun/diary-template/core/): 핵심 비즈니스 로직
  - [core/generator.py](file:///Users/kimbeomjun/diary-template/core/generator.py): AI 레이아웃 생성 및 Reflection 파이프라인
  - [core/renderer.py](file:///Users/kimbeomjun/diary-template/core/renderer.py): Master HTML 최종 조립 및 치수 스냅 조율
  - [core/themes.py](file:///Users/kimbeomjun/diary-template/core/themes.py): 미니멀/큐트/에디토리얼 테마별 전용 CSS 명세 인젝터
  - [core/prompts/](file:///Users/kimbeomjun/diary-template/core/prompts/): AI 레이아웃 지침, 27가지 플래너 상세 힌트 및 CSS 자가검증 룰
- [templates/](file:///Users/kimbeomjun/diary-template/templates/): HTML 템플릿 (`index.html` - 메인 화면, `editor.html` - 에디터 화면)
- [static/](file:///Users/kimbeomjun/diary-template/static/): 정적 자산
  - `style.css` / `script.js`: 메인 화면 스타일 및 제어 스크립트
  - `editor.css` / `editor.js`: 에디터 화면 스타일 및 링킹/편집 인터랙션 스크립트

---

## 3. 개발 및 디자인 규칙 (Critical Rules)
새로운 작업을 진행할 에이전트는 다음 규칙을 **반드시** 준수해야 합니다:

1. **디자인 철학 (Premium Aesthetics)**:
   - 브라우저 기본 폰트나 원색(단순 빨강, 파랑 등) 대신 harmonized HSL 팔레트, 미묘한 그라데이션, 미세한 노이즈 질감 배경, 유려한 폰트(Outfit, Inter, Nanum Pen Script 등)를 조합하여 현대적이고 고급스러운 감각을 제공해야 합니다.
2. **CSS 및 UI 프레임워크 정책**:
   - **Tailwind CSS는 기본적으로 사용을 금지합니다.** 사용자가 명시적으로 Tailwind 사용을 요구한 경우에만 버전을 확인하고 동의를 받아 사용할 수 있으며, 그 외에는 바닐라 CSS 파일(`style.css` 및 `editor.css`)에 규칙적으로 구조화하여 정의하십시오.
3. **플레이스홀더 및 이미지 리소스**:
   - 가짜 이미지나 단순 플레이스홀더를 사용하지 마십시오. 필요하다면 에이전트 내장 `generate_image` 툴을 활용해 실제 어울리는 아름다운 그래픽 소스를 생성하여 제공해야 합니다.
4. **PDF 인쇄/배경 그래픽 안내**:
   - 에디터에서 PDF 인쇄 시, CSS 배경선과 테마 색상이 소실되지 않도록 시스템 인쇄 대화상자에서 **[배경 그래픽(Background graphics)] 옵션을 활성화**해야 온전한 디자인이 보존됩니다.

---

## 4. 최근 주요 개선 및 변경 내역
최근 대화창을 통해 다음과 같은 중요 UX/성능 개선 작업이 완료되었습니다:
- **Mandalart 프롬프트 고도화**: LLM 생성 도중 레이아웃 깨짐 현상을 제어하기 위해 힌트와 Few-shot 예시 사전을 구조적으로 개선하여 에러 리젠율을 최적화했습니다.
- **PDF 속도 및 SSE 실시간 스트리밍**: 비동기 백그라운드 스레드와 SSE API를 결합하여 다량의 템플릿 생성 과정을 웹소켓 없이도 직관적으로 브라우저에 피드백합니다.
- **에디터 진입 트랜지션 애니메이션**:
  - 메인 페이지에서 "나만의 다중 페이지 다이어리 만들기" 이동 링크 클릭 시, 다이어리 판형이 `scale(4.5)` 확대 및 블러 처리되며 빨려 들어가는 듯이 사라지는 모션 구현 ([script.js](file:///Users/kimbeomjun/diary-template/static/script.js) 내 클릭 인터셉터 및 [style.css](file:///Users/kimbeomjun/diary-template/static/style.css) 참조).
  - 에디터 로드 시 좌우 사이드 패널이 양쪽에서 슬라이딩 인 되고, 중앙의 `.paper-container`가 큰 스케일에서 정스케일로 연착륙하며 흐려짐이 걷히는 모션으로 자연스러운 이어짐 연출 ([editor.css](file:///Users/kimbeomjun/diary-template/static/editor.css) 참조).
- **HTTPS 환경 하의 IFrame Same-Origin Policy 보안 회피 및 비동기 렌더링 (★)**:
  - 실서버(HTTPS) 환경에서 `about:blank` iframe에 직접 `doc.write`하여 렌더링을 제어할 시 발생하는 보안 예외(SOP)와 비동기 렌더링 경쟁 상태(Race Condition)를 해결했습니다.
  - 동일 Origin의 정적 파일인 `/static/blank.html`을 `iframe.src`로 설정한 뒤, `onload` 콜백 내부에서 `doc.write`와 `setupIframeInteractions`를 일괄 실행하도록 결합하여 타이밍 오류를 원천 차단했습니다.

---

## 5. 다음 에이전트를 위한 작업 팁
- **로컬 웹서버 실행**: 터미널에서 `python3 app.py`를 제안하여 실행하십시오. (개발 도중 빌드 검증을 엄격히 권장)
- **정적 파일 캐시 무효화 (Cache-Busting)**:
  - 서버 배포 시 브라우저 또는 CDN 캐시로 인해 수정사항이 무시되는 경우가 잦습니다. `editor.js`나 `editor.css`를 수정하는 경우 반드시 `templates/editor.html` 내부의 리소스 주소 뒤 쿼리 스트링(`editor.js?v=XX`) 버전을 명시적으로 올려주어야 실서버에 즉각 갱신됩니다.
- **테스트 편의성을 위한 Mock 템플릿 fetch**:
  - 수동으로 링크 모션 등의 편집 동작을 테스트할 때 매번 AI 생성을 기다리는 낭비를 줄이기 위해, 필요 시 `static/pre_generated_layouts.json` 정적 리소스 데이터를 비동기 `fetch`하여 메모리 `pages` 상태에 세팅해놓고 개발하는 기법이 유용합니다.
- **테스트 코드 동작 확인**: 의존성 환경이 독립되어 있을 수 있으므로 가상환경 경로를 통해 모듈 단위 테스트(`.venv/bin/python -m pytest tests/...`)를 검증하십시오.
- 추가 아키텍처에 대한 상세 정보는 [architecture.md](file:///Users/kimbeomjun/diary-template/architecture.md)에 다이어그램과 함께 상세히 정리되어 있으므로 함께 참고하시기 바랍니다.
