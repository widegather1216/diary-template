# Diary Template Generator 📔

AI를 활용하여 사용자 맞춤형 다이어리 및 플래너 템플릿 PDF를 동적으로 생성하는 웹 애플리케이션입니다.

## 🌟 주요 기능

- **맞춤형 레이아웃 생성**: 사용자가 입력한 제목, 설명, 용지 크기(A4, A5, B5), 방향(가로/세로), 디자인 모드(일반/가이드)에 맞게 다이어리 양식을 자동 생성합니다.
- **2-Pass AI 검증**: Google Gemini API를 활용해 레이아웃을 1차 생성하고, 디자인 규칙(예: 겹침 현상, 부적절한 여백, 구조적 오류 등) 위반 여부를 2차로 검증 및 교정하여 안정성을 극대화합니다.
- **커스텀 반복 매크로 엔진 (`<repeat>`)**: AI 모델의 텍스트 출력 제한(토큰 리밋)을 우회하기 위해, 달력이나 습관 트래커와 같은 반복 UI 요소를 자체 매크로 처리기로 자동화합니다.
- **그리드 스내핑 (Guide 모드)**: 수작업 기반 다이어리를 위한 가이드 모드에서는 AI가 생성한 CSS의 모든 세로 픽셀 값을 20px 배수로 강제 보정(Snap)하여 종이 도트 그리드 배경과 완벽하게 일치시킵니다.
- **자동 파일 라이프사이클 관리**: 생성된 임시 PDF 파일이 무한정 쌓여 디스크 용량을 차지하지 않도록 브라우저 종료 시 삭제 API 호출 및 주기적 찌꺼기 파일(1시간 경과) 청소를 수행합니다.

## 🛠️ 기술 스택

- **Backend**: Python 3, Flask, Gunicorn
- **AI Model**: Google Gemini (`google-generativeai`)
- **PDF Rendering**: WeasyPrint
- **Frontend**: HTML5, Vanilla JavaScript, CSS3
- **Deployment**: Docker, docker-compose, Nginx

## 📂 프로젝트 핵심 구조

```text
diary-template/
├── app.py                   # Flask 앱 진입점 및 REST API 라우터
├── core/                    # 코어 비즈니스 로직
│   ├── generator.py         # 2-Pass 프롬프트 검증 및 모델 연동
│   ├── model_config.py      # Gemini 모델 초기화 및 설정
│   ├── pdf_manager.py       # 임시 PDF 파일 생성, 보관, 삭제(Garbage Collection)
│   ├── prompts.py           # 모드별 시스템 프롬프트 관리
│   └── renderer.py          # HTML 조립, 반복 매크로 치환 및 CSS 픽셀 보정 로직
├── static/                  # 프론트엔드 정적 리소스 (JS, CSS, 커스텀 폰트)
├── templates/               # Flask Jinja2 템플릿 (index.html)
└── Dockerfile               # 배포용 Docker 이미지 빌드 파일
```

## 🚀 실행 방법

### 로컬 환경에서 실행

1. 저장소를 클론하고 프로젝트 디렉토리로 이동합니다.
2. 파이썬 가상 환경을 생성하고 의존성 패키지를 설치합니다.
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. 환경 변수 파일(`.env`)을 설정합니다.
   ```bash
   cp .env.example .env
   ```
   `.env` 파일을 열어 Gemini API 키 등을 알맞게 설정합니다.
4. 애플리케이션을 실행합니다.
   ```bash
   python app.py
   ```
5. 웹 브라우저에서 `http://localhost:7860` 으로 접속합니다.

### Docker를 이용한 실행

Docker가 설치되어 있다면 아래 명령어로 즉시 구동할 수 있습니다.
```bash
docker-compose up --build -d
```
이후 `http://localhost:7860` 으로 접속하여 이용합니다.

## 📡 주요 API 엔드포인트

- `POST /api/generate-pdf`: 폼 데이터를 JSON 형식으로 받아 AI를 통해 레이아웃 HTML을 생성한 뒤 PDF로 변환합니다. 변환에 성공하면 고유 식별자인 `file_id`를 반환합니다.
- `GET /api/download-pdf/<file_id>`: 생성 완료된 특정 `file_id`의 PDF 파일을 다운로드 형식으로 제공합니다.
- `POST /api/cleanup-pdf`: 클라이언트가 다이어리를 다운로드했거나 탭을 닫았을 때, 낭비되는 스토리지 확보를 위해 임시 PDF를 즉시 삭제합니다.
