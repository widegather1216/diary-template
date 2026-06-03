import os
import uuid
import tempfile
from weasyprint import HTML

TEMP_PDF_DIR = os.path.join(tempfile.gettempdir(), 'formweaver_pdfs')
os.makedirs(TEMP_PDF_DIR, exist_ok=True)

def generate_pdf(master_html):
    """
    Generates a PDF from the provided master_html using WeasyPrint.
    Returns the file_id of the generated PDF.
    """
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
