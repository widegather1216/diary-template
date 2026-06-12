# FormWeaver (AI Diary Template Generator) 배포용 이미지
#
# 빌드:   docker build -t formweaver:latest .
# 실행:   docker run -d -p 7860:7860 --env-file .env formweaver:latest

FROM python:3.11-slim

# 시스템 의존성 (WeasyPrint 및 폰트 렌더링용)
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
        libjpeg62-turbo \
        libpng16-16 \
        ca-certificates \
        build-essential \
        python3-dev \
        python3-pip \
        python3-setuptools \
        python3-wheel \
        python3-cffi \
        libcairo2 \
        libpango-1.0-0 \
        libpangocairo-1.0-0 \
        libgdk-pixbuf-2.0-0 \
        libgdk-pixbuf-xlib-2.0-0 \
        libffi-dev \
        shared-mime-info \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 의존성 먼저 설치 (캐시 최적화)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# 앱 소스 복사
COPY app.py ./
COPY core/ ./core/
COPY templates/ ./templates/
COPY static/ ./static/

EXPOSE 7860

# 환경변수
# - PORT: Flask/Gunicorn에서 바인딩할 포트
# - PYTHONUNBUFFERED: print/log 즉시 stdout (docker logs로 실시간 확인용)
ENV PORT=7860 \
    PYTHONUNBUFFERED=1

# 헬스체크 (1GB RAM에서 OOM으로 죽으면 docker가 재기동)
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:7860/').read()" || exit 1

# 프로덕션 환경 권장: gunicorn 실행 (생성 시간이 길어질 수 있으므로 타임아웃 120초 부여)
CMD ["gunicorn", "-b", "0.0.0.0:7860", "-w", "2", "--timeout", "120", "app:app"]
