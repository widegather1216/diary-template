import os
import re
import uuid
import tempfile
from flask import Flask, request, send_file, render_template, jsonify

from model_config import get_gemini_model
from core.prompts import get_system_prompts
from core.renderer import get_page_config, assemble_master_html

app = Flask(__name__)

TEMP_PDF_DIR = os.path.join(tempfile.gettempdir(), 'formweaver_pdfs')
os.makedirs(TEMP_PDF_DIR, exist_ok=True)

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
    design_mode = data.get('designMode', 'print')
    orientation = data.get('orientation')
    
    if not title:
        return jsonify({'error': 'Title is required'}), 400

    if not orientation:
        combined_text = f"{title} {description}".lower()
        if any(keyword in combined_text for keyword in ["가로", "landscape", "가로형", "가로방향", "넓게"]):
            orientation = "landscape"
        else:
            orientation = "portrait"
        
    try:
        model = get_gemini_model()
        
        config = get_page_config(page_size, orientation)
        SYSTEM_PROMPT, GUIDE_SYSTEM_PROMPT = get_system_prompts(config['cw'], config['ch'])
        
        prompt = f"""
        Title (Form Name): {title}
        Description (Additional Requests): {description}
        Page Size: {page_size}
        Orientation: {orientation}
        
        Generate the inner HTML and `<style>` for this {page_size} {orientation} layout.
        """
        
        active_prompt = GUIDE_SYSTEM_PROMPT if design_mode == 'guide' else SYSTEM_PROMPT
        
        response = model.generate_content(
            [{"role": "user", "parts": [active_prompt, prompt]}]
        )
        
        try:
            html_content = response.text
        except ValueError:
            finish_reason = getattr(response.candidates[0], 'finish_reason', None)
            if finish_reason == 4:
                return jsonify({'error': "AI가 유사도 필터에 걸렸습니다. 독창적인 내용을 입력하세요."}), 400
            elif finish_reason == 3:
                return jsonify({'error': "안전 필터에 의해 생성이 중단되었습니다."}), 400
            else:
                return jsonify({'error': f"생성 중단됨 (사유: {finish_reason})"}), 400
                
        print("[TRACKING 🔍] 2차 검증 (Self-Reflection) 요청 중...")
        review_prompt = f"""
Review the generated HTML below and fix any violations of the design rules:
1. CRITICAL: The outermost wrapper MUST have `padding: 0;`. Remove any padding on it.
2. CRITICAL: DO NOT include instructional texts in parentheses (e.g. `(Draw a line)`).
3. Ensure text inside boxes is vertically centered using `display: flex; align-items: center; justify-content: center;`.
4. Ensure lines/blanks use explicit characters like `_________` instead of empty spans.
5. CRITICAL: Short text labels (like 'SUN', 'MON', or 'Author:') MUST have `white-space: nowrap;` to prevent breaking mid-word.
6. CRITICAL: If you use a grid/table structure where cells have right/bottom borders, ensure the wrapper container has `border-top` and `border-left` so the outer boundaries are not missing.

Generated HTML:
```html
{html_content}
```
Return ONLY the corrected HTML/CSS. No explanations.
"""
        review_response = model.generate_content(
            [{"role": "user", "parts": [active_prompt, review_prompt]}]
        )
        
        try:
            html_content = review_response.text
        except ValueError:
            pass # Fallback to first pass output if blocked
        
        master_html = assemble_master_html(html_content, design_mode, page_size, orientation)
        
        file_id = uuid.uuid4().hex
        pdf_path = os.path.join(TEMP_PDF_DIR, f"{file_id}.pdf")
        
        print(f"[TRACKING 🔍] 새로운 임시 PDF 파일 생성 시작: {pdf_path}")
        from weasyprint import HTML
        HTML(string=master_html).write_pdf(pdf_path)
        print(f"[TRACKING ✅] 임시 PDF 파일 생성 완료: {pdf_path}")
        
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
                except Exception as e:
                    pass
    return '', 204

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 7860)))
