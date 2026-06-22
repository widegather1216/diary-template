import os
import sys
import time
import uuid
import tempfile
import urllib.parse
import urllib.request
import mimetypes
import ssl

if sys.platform == "darwin":
    brew_lib_path = "/opt/homebrew/lib"
    if os.path.exists(brew_lib_path):
        dyld_path = os.environ.get("DYLD_FALLBACK_LIBRARY_PATH", "")
        if brew_lib_path not in dyld_path:
            os.environ["DYLD_FALLBACK_LIBRARY_PATH"] = f"{brew_lib_path}:{dyld_path}".strip(":")

from weasyprint import HTML, default_url_fetcher
from core.config import TEMP_PDF_DIR, CACHE_DIR

# Create SSL context that bypasses local certificate verification issues (e.g. on macOS)
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE


def _pdf_path(file_id):
    """Returns the filesystem path for a given PDF file ID."""
    return os.path.join(TEMP_PDF_DIR, f"{file_id}.pdf")


def _read_from_cache(url):
    """Checks the cache for a previously fetched URL. Returns a dict or None."""
    safe_filename = urllib.parse.quote_plus(url)
    cache_path = os.path.join(CACHE_DIR, safe_filename)

    if os.path.exists(cache_path):
        try:
            with open(cache_path, 'rb') as f:
                content = f.read()

            mime_type, _ = mimetypes.guess_type(url)
            # Special case: Google Fonts CSS URLs like css2?family=...
            if mime_type is None and 'css' in url:
                mime_type = 'text/css'

            res = {'string': content}
            if mime_type:
                res['mime_type'] = mime_type
            return res
        except Exception as e:
            print(f"[WEASYPRINT CACHE ⚠️] 캐시 읽기 실패, 일반 다운로드: {e}")

    return None


def _fetch_and_cache(url, timeout):
    """Fetches a URL from the network, saves to cache, and returns a dict."""
    safe_filename = urllib.parse.quote_plus(url)
    cache_path = os.path.join(CACHE_DIR, safe_filename)

    try:
        print(f"[WEASYPRINT CACHE 🌐] 캐시 미스, 다운로드 시작: {url}")
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        )
        with urllib.request.urlopen(req, timeout=timeout, context=ssl_context) as response:
            content = response.read()

        with open(cache_path, 'wb') as f:
            f.write(content)

        mime_type = response.headers.get('Content-Type')
        return {
            'string': content,
            'mime_type': mime_type
        }
    except Exception as e:
        print(f"[WEASYPRINT CACHE ❌] 우회 다운로드 실패 ({e}), 기본 페처로 시도합니다.")
        try:
            res = default_url_fetcher(url, timeout)
            if res and 'string' in res:
                with open(cache_path, 'wb') as f:
                    f.write(res['string'])
            return res
        except Exception as fallback_err:
            print(f"[WEASYPRINT CACHE ❌] 기본 페처 다운로드 최종 실패: {fallback_err}")
            raise fallback_err


def cached_url_fetcher(url, timeout=15):
    # Only cache HTTP/HTTPS requests
    if not url.startswith('http://') and not url.startswith('https://'):
        return default_url_fetcher(url, timeout)

    cached = _read_from_cache(url)
    if cached is not None:
        return cached

    return _fetch_and_cache(url, timeout)

def cleanup_old_pdfs(max_age_hours=1):
    """
    Deletes PDF files older than max_age_hours to prevent disk leak 
    in edge cases where beforeunload event fails to fire.
    """
    now = time.time()
    try:
        for filename in os.listdir(TEMP_PDF_DIR):
            if not filename.endswith('.pdf'):
                continue
            filepath = os.path.join(TEMP_PDF_DIR, filename)
            if os.path.exists(filepath):
                mtime = os.path.getmtime(filepath)
                if (now - mtime) > (max_age_hours * 3600):
                    try:
                        os.remove(filepath)
                        print(f"[TRACKING 🧹] 오래된 임시 PDF 삭제 완료: {filepath}")
                    except Exception:
                        pass
    except Exception as e:
        print(f"[TRACKING ⚠️] 오래된 임시 PDF 삭제 중 오류: {e}")

def generate_pdf(master_html):
    """
    Generates a PDF from the provided master_html using WeasyPrint with cached_url_fetcher.
    Returns the file_id of the generated PDF.
    """
    cleanup_old_pdfs(max_age_hours=1)
    
    file_id = uuid.uuid4().hex
    pdf_path = _pdf_path(file_id)
    
    # WeasyPrint가 static/fonts/... 로컬 경로를 인식할 수 있도록 base_url을 프로젝트 루트로 설정
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    print(f"[TRACKING 🔍] 새로운 임시 PDF 파일 생성 시작: {pdf_path}")
    HTML(string=master_html, base_url=project_root, url_fetcher=cached_url_fetcher).write_pdf(pdf_path)
    print(f"[TRACKING ✅] 임시 PDF 파일 생성 완료: {pdf_path}")
    
    return file_id, pdf_path

def cleanup_pdf(file_id):
    """
    Deletes the generated PDF file to free up space.
    """
    pdf_path = _pdf_path(file_id)
    if os.path.exists(pdf_path):
        try:
            os.remove(pdf_path)
        except Exception as e:
            pass

def get_pdf_path(file_id):
    """
    Returns the path to the PDF file if it exists, else None.
    """
    pdf_path = _pdf_path(file_id)
    if os.path.exists(pdf_path):
        return pdf_path
    return None
