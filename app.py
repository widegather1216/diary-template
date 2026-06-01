import os
import re
import uuid
from flask import Flask, request, send_file, render_template, jsonify
from weasyprint import HTML
from model_config import get_gemini_model
import tempfile

app = Flask(__name__)

# 임시 PDF 저장소 생성
TEMP_PDF_DIR = os.path.join(tempfile.gettempdir(), 'formweaver_pdfs')
os.makedirs(TEMP_PDF_DIR, exist_ok=True)

SYSTEM_PROMPT = """You are an expert frontend developer and layout designer.
The user wants to generate a planner/diary layout for printing.
Create a clean, highly practical, and completely UNIQUE layout from scratch.
Use creative CSS class names and custom styling to avoid standard HTML boilerplates.
Do NOT use markdown code blocks. Output ONLY raw HTML and CSS.
The HTML must include <style> tags with the CSS.
The layout should perfectly fit the specified page size (A4 or A5).
Use mm or cm for precise dimensions.
Ensure there is a printable area with `@page { size: A4; margin: 10mm; }` 
(Adjust size to A4 or A5 based on user input).
No extra explanations, just the code.
"""

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/generate-pdf', methods=['POST'])
def generate_pdf():
    data = request.json
    if not data:
        return jsonify({'error': 'Invalid JSON request'}), 400
        
    title = data.get('title')
    description = data.get('description', '')
    page_size = data.get('pageSize', 'A4')
    
    if not title:
        return jsonify({'error': 'Title is required'}), 400
        
    try:
        model = get_gemini_model()
        
        prompt = f"""
        Title: {title}
        Description: {description}
        Page Size: {page_size}
        
        Generate the raw HTML/CSS for this planner layout. 
        It must be optimized for {page_size} printing.
        """
        
        response = model.generate_content(
            [{"role": "user", "parts": [SYSTEM_PROMPT, prompt]}]
        )
        
        try:
            html_content = response.text
        except ValueError:
            # response.text 접근 시 필터(저작권 등)에 걸리면 ValueError가 발생합니다.
            finish_reason = getattr(response.candidates[0], 'finish_reason', None)
            if finish_reason == 4: # RECITATION
                return jsonify({'error': "AI가 유사도(저작권) 필터에 걸려 생성을 중단했습니다. '양식 내용'을 조금 더 길고 독창적으로 입력해 보세요."}), 400
            elif finish_reason == 3: # SAFETY
                return jsonify({'error': "안전 필터에 의해 생성이 중단되었습니다."}), 400
            else:
                return jsonify({'error': f"생성 중단됨 (사유: {finish_reason})"}), 400
        
        # Clean up in case Gemini wraps it in markdown code blocks
        html_content = re.sub(r'^```html\s*', '', html_content, flags=re.MULTILINE)
        html_content = re.sub(r'```\s*$', '', html_content, flags=re.MULTILINE).strip()
        
        # Generate PDF using WeasyPrint
        file_id = uuid.uuid4().hex
        pdf_path = os.path.join(TEMP_PDF_DIR, f"{file_id}.pdf")
        
        print(f"[TRACKING 🔍] 새로운 임시 PDF 파일 생성 시작: {pdf_path}")
        HTML(string=html_content).write_pdf(pdf_path)
        print(f"[TRACKING ✅] 임시 PDF 파일 생성 완료 및 저장됨: {pdf_path}")
        
        return jsonify({
            'message': 'success',
            'file_id': file_id,
            'title': title,
            'page_size': page_size
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download-pdf/<file_id>', methods=['GET'])
def download_pdf(file_id):
    if not re.match(r'^[a-f0-9]+$', file_id):
        return "Invalid file ID", 400
        
    pdf_path = os.path.join(TEMP_PDF_DIR, f"{file_id}.pdf")
    if not os.path.exists(pdf_path):
        return "파일을 찾을 수 없거나 이미 삭제되었습니다.", 404
        
    title = request.args.get('title', 'planner')
    page_size = request.args.get('page_size', 'A4')
    
    return send_file(
        pdf_path, 
        mimetype='application/pdf', 
        as_attachment=True, 
        download_name=f"{title}_{page_size}.pdf"
    )

@app.route('/api/cleanup-pdf', methods=['POST'])
def cleanup_pdf():
    # navigator.sendBeacon은 주로 text/plain 형태의 JSON을 보냅니다.
    data = request.json
    if request.data and not data:
        import json
        try:
            data = json.loads(request.data)
        except:
            data = {}
            
    if data and 'file_id' in data:
        file_id = data['file_id']
        if re.match(r'^[a-f0-9]+$', file_id):
            pdf_path = os.path.join(TEMP_PDF_DIR, f"{file_id}.pdf")
            if os.path.exists(pdf_path):
                try:
                    os.remove(pdf_path)
                    print(f"[TRACKING 🗑️] 임시 PDF 파일이 정상적으로 삭제되었습니다: {pdf_path}")
                except Exception as e:
                    print(f"[TRACKING ❌] 임시 PDF 파일 삭제 실패: {pdf_path}, 원인: {e}")
            else:
                print(f"[TRACKING ⚠️] 삭제하려는 파일이 이미 존재하지 않습니다: {pdf_path}")
    return '', 204

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 7860)))
