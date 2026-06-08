import os
import time
import uuid
import tempfile
from weasyprint import HTML

TEMP_PDF_DIR = os.path.join(tempfile.gettempdir(), 'formweaver_pdfs')
os.makedirs(TEMP_PDF_DIR, exist_ok=True)

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
    Generates a PDF from the provided master_html using WeasyPrint.
    Returns the file_id of the generated PDF.
    """
    # 새로운 PDF 생성 전에 오래된 찌꺼기 파일들 정리 (예: 1시간 이상 된 파일)
    cleanup_old_pdfs(max_age_hours=1)
    
    file_id = uuid.uuid4().hex
    pdf_path = os.path.join(TEMP_PDF_DIR, f"{file_id}.pdf")
    
    print(f"[TRACKING 🔍] 새로운 임시 PDF 파일 생성 시작: {pdf_path}")
    HTML(string=master_html).write_pdf(pdf_path)
    print(f"[TRACKING ✅] 임시 PDF 파일 생성 완료: {pdf_path}")
    
    return file_id, pdf_path

def cleanup_pdf(file_id):
    """
    Deletes the generated PDF file to free up space.
    """
    pdf_path = os.path.join(TEMP_PDF_DIR, f"{file_id}.pdf")
    if os.path.exists(pdf_path):
        try:
            os.remove(pdf_path)
        except Exception as e:
            pass

def get_pdf_path(file_id):
    """
    Returns the path to the PDF file if it exists, else None.
    """
    pdf_path = os.path.join(TEMP_PDF_DIR, f"{file_id}.pdf")
    if os.path.exists(pdf_path):
        return pdf_path
    return None
