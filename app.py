import os
import re
import uuid
from flask import Flask, request, send_file, render_template, jsonify
from model_config import get_gemini_model
import tempfile

app = Flask(__name__)

TEMP_PDF_DIR = os.path.join(tempfile.gettempdir(), 'formweaver_pdfs')
os.makedirs(TEMP_PDF_DIR, exist_ok=True)

def get_page_config(paper_size='A4'):
    page_dimensions = {
        'A4': (793.7, 1122.5),
        'A5': (559.4, 793.7),
        'B5': (665.2, 944.9)
    }
    W, H = page_dimensions.get(paper_size, page_dimensions['A4'])
    
    # Target margin ~40px
    target_margin = 40
    avail_w = W - (target_margin * 2)
    cw = int(avail_w // 140) * 140
    if cw < 280: cw = 280
    
    avail_h = H - (target_margin * 2)
    ch = int(avail_h // 20) * 20
    
    half_cw = cw / 2
    shift_x = -10 if half_cw % 20 != 0 else 0
    top_pos = 60 # 3 dots
    
    return {
        'W': W, 'H': H,
        'cw': cw, 'ch': ch,
        'shift_x': shift_x,
        'top': top_pos
    }

def get_system_prompts(cw, ch):
    SYSTEM_PROMPT = f"""You are an expert frontend developer and layout designer.
The user wants a highly professional planner/diary layout for printing.
Requirements:
1. DESIGN: Premium, clean, functional layout. Modern typography, elegant borders, subtle shading. Avoid amateur designs.
2. LANGUAGE: ALL text labels and placeholders MUST BE IN ENGLISH.
3. CANVAS CONSTRAINTS (CRITICAL): Your output will be placed inside a container EXACTLY {cw}px wide and {ch}px tall. Do NOT write `<html>`, `<body>`, or `@page`. Write ONLY the inner HTML elements and `<style>`.
4. STRUCTURE: Do NOT use CSS Grid (`display: grid`) due to WeasyPrint bugs. Use simple Flexbox.
5. ADAPTIVE LAYOUT (CRITICAL): Adapt the layout perfectly to the requested Title (e.g., Reading Journal, Habit Tracker, Monthly Planner). ONLY IF the user requests a calendar/planner, set column width to EXACTLY {cw // 7}px and manually write out exactly 35 or 42 `<div>` cells without loops. For all other formats, design freely using 20px multiples.
6. SPACE UTILIZATION (FILL {ch}px): You MUST visually fill the entire {ch}px height. For bottom note areas, use `flex-grow: 1;` and CSS `repeating-linear-gradient(white, white 19px, #e5e7eb 20px)` to fill the remaining space with lines.
7. NO JAVASCRIPT: Output ONLY pure, static HTML/CSS. If you use `<script>`, you fail.
No extra explanations, just code.
"""

    GUIDE_SYSTEM_PROMPT = f"""You are an expert Bullet Journal artist.
The user wants a "Hand-drawing Blueprint" (a reference sketch) to copy manually.
Requirements:
1. CANVAS & GRID (CRITICAL): Your output is placed inside a container EXACTLY {cw}px wide and {ch}px tall. The system automatically draws a 20px dot grid background perfectly aligned with this container. Do NOT write `<body>` or `@page`. Write ONLY inner HTML and `<style>`.
2. PIXEL-PERFECT 20px MATH: Every `height`, `width`, `margin`, `padding` MUST be a multiple of 20px. For example, `{cw // 7}px` is an exact multiple of 20px, so it perfectly aligns. NEVER use fractional sizes, `10px`, or `%`.
3. STRUCTURE (NO GRID): Do NOT use CSS Grid (`display: grid`) due to PDF engine bugs. Use Flexbox.
4. FONTS: Use handwriting fonts. `@import url("https://fonts.googleapis.com/css2?family=Patrick+Hand&display=swap");` and `font-family: 'Patrick Hand', cursive;`.
5. ADAPTIVE LAYOUT (CRITICAL): Adapt the layout perfectly to the requested Title (e.g., Reading Journal, Habit Tracker). ONLY IF it is a calendar, manually write exactly 35 or 42 `<div>` cells with no loops.
6. MINIMAL RULER LINES: Minimize lines. Use thin `border-bottom: 1px solid #333`. Ensure every element has `background-color: transparent !important;` so dots show through.
7. SPACE UTILIZATION (FILL {ch}px): You must fill the {ch}px height. Give the last notes element `flex-grow: 1;` so it expands.
8. NO HELPER TEXT: Do not print instructions like "(Draw line here)". No javascript.
No extra explanations, just code.
"""
    return SYSTEM_PROMPT, GUIDE_SYSTEM_PROMPT

def assemble_master_html(llm_output, design_mode, page_size):
    config = get_page_config(page_size)
    cw, ch = config['cw'], config['ch']
    shift_x, top_pos = config['shift_x'], config['top']
    
    style_match = re.search(r'<style>(.*?)</style>', llm_output, re.DOTALL | re.IGNORECASE)
    llm_style = style_match.group(1) if style_match else ""
    
    body_match = re.search(r'<body>(.*?)</body>', llm_output, re.DOTALL | re.IGNORECASE)
    llm_body = body_match.group(1) if body_match else llm_output
    
    llm_body = re.sub(r'<style>.*?</style>', '', llm_body, flags=re.DOTALL | re.IGNORECASE)
    llm_body = re.sub(r'<!DOCTYPE.*?>', '', llm_body, flags=re.IGNORECASE)
    llm_body = re.sub(r'<html.*?>|</html>', '', llm_body, flags=re.IGNORECASE)
    llm_body = re.sub(r'<head.*?>|</head>', '', llm_body, flags=re.IGNORECASE)
    llm_body = re.sub(r'^```html\s*', '', llm_body, flags=re.MULTILINE)
    llm_body = re.sub(r'```\s*$', '', llm_body, flags=re.MULTILINE).strip()
    
    dot_css = ""
    if design_mode == 'guide':
        dot_css = f"""
    background-image: radial-gradient(circle, #b0b0b0 1px, transparent 1px) !important;
    background-size: 20px 20px !important;
    background-position: calc(50% + {shift_x}px) {top_pos}px !important;
        """
    
    master_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
@page {{ size: {page_size}; margin: 0; }}
* {{ box-sizing: border-box; margin: 0; padding: 0; background-color: transparent; }}

body {{
    width: 100vw; height: 100vh;
    margin: 0 !important; padding: 0 !important;
    overflow: hidden !important;
    background-color: white !important;
    {dot_css}
}}

.page-container {{
    position: absolute !important;
    top: {top_pos}px !important; 
    left: 50% !important; 
    margin-left: -{cw // 2}px !important;
    width: {cw}px !important; 
    height: {ch}px !important;
    display: flex; 
    flex-direction: column;
    overflow: hidden !important;
}}

{llm_style}
</style>
</head>
<body>
    <div class="page-container">
{llm_body}
    </div>
</body>
</html>"""
    return master_html

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
    
    if not title:
        return jsonify({'error': 'Title is required'}), 400
        
    try:
        model = get_gemini_model()
        
        config = get_page_config(page_size)
        SYSTEM_PROMPT, GUIDE_SYSTEM_PROMPT = get_system_prompts(config['cw'], config['ch'])
        
        prompt = f"""
        Title (Form Name): {title}
        Description (Additional Requests): {description}
        Page Size: {page_size}
        
        Generate the inner HTML and `<style>` for this {page_size} layout.
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
        
        master_html = assemble_master_html(html_content, design_mode, page_size)
        
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
