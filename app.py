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

SYSTEM_PROMPT = """You are an expert frontend developer, layout designer, and productivity tool creator.
The user wants to generate a highly professional, aesthetically pleasing, and practical planner/diary layout for printing.
Requirements:
1. DESIGN: Create a premium, clean, and highly functional layout. Use modern typography, elegant borders, ample whitespace, and subtle shading for a sophisticated look. Avoid basic, amateur designs.
2. LANGUAGE: ALL text labels, headings, and placeholders MUST BE IN ENGLISH to avoid rendering issues.
3. CONTENT: Base the core layout and structure primarily on the "Title" (Form Name). If "Description" is provided, seamlessly integrate those specific user requests into the layout.
4. STRUCTURE: Use creative CSS class names and custom styling. Avoid standard HTML boilerplates.
5. TECHNICAL (NO JAVASCRIPT): The PDF engine (WeasyPrint) does NOT support JavaScript. You MUST NOT use `<script>` tags, JS loops, or variables anywhere. Output ONLY raw, static HTML and CSS.
6. PRINTING: The layout should perfectly fit the specified page size (A4 or A5). Use mm or cm for precise dimensions. Ensure there is a printable area with `@page { size: A4; margin: 10mm; }` (Adjust size to A4 or A5 based on user input).
7. UNIVERSAL COMPLETENESS (STATIC HTML ONLY): NEVER omit or skip HTML tags. If the layout is a grid (like a calendar), explicitly write out the raw, static HTML for EVERY single cell (e.g., manually write 31 or 35 `<div>` elements). Do NOT use JS `for` loops to generate them. If it is a descriptive form, manually write all necessary lines/sections to cover the full page. Never use shortcuts.
8. SPACE UTILIZATION (FILL THE PAGE): There must be NO wasted empty space at the bottom. Use `height: 100vh; display: flex; flex-direction: column;` on the main container. For the inner content (whether it's calendar grids or note-taking lines), apply `flex-grow: 1` so they dynamically stretch to fill the entire A4/A5 page down to the bottom margin regardless of the form type.
9. DATES AND TIME: Do NOT hardcode specific years, months, or days (e.g., "2024", "October"). Instead, always provide elegant blank spaces or lines for the user to manually fill in the date information. Do not force a specific format; adapt the blanks beautifully to the current layout's design.
No extra explanations, just the code.
"""

GUIDE_SYSTEM_PROMPT = """You are an expert Bullet Journal artist on Pinterest.
The user wants a "Hand-drawing Blueprint" (a reference sketch) to help them manually copy the layout into their physical notebook using a pen and a ruler.
Requirements:
1. DESIGN PURPOSE & AESTHETIC: This is a minimalist bullet journal spread. Do NOT design it like a digital printable form.
2. FONTS: You MUST use handwriting fonts. Import them correctly via `@import url("https://fonts.googleapis.com/css2?family=Patrick+Hand&display=swap");` and fallback safely: `font-family: 'Patrick Hand', 'Comic Sans MS', cursive;`.
3. BACKGROUND: You MUST EXACTLY use this CSS for the body to ensure WeasyPrint compatibility and set the dot at the origin: `background-image: radial-gradient(circle at 1px 1px, #b0b0b0 1px, transparent 1px); background-size: 20px 20px;`. ALL other elements MUST have `background: transparent !important;` so the dots show through.
4. PIXEL-PERFECT 20px GRID ALIGNMENT: You MUST align all elements to the 20px dot grid. You MUST use `* { margin: 0; padding: 0; box-sizing: border-box; }`. Every `height`, `margin`, `padding`, and `line-height` value MUST be an exact multiple of 20px (e.g., 20px, 40px, 60px). NEVER use values like 10px or 15px. This is critical so that any drawn lines (`border-bottom`) land perfectly on top of the background dots.
5. MINIMAL RULER LINES: The user must draw these lines by hand. Minimize the total number of lines to reduce drawing fatigue. Do NOT draw massive fully-enclosed grids with 30+ boxes. Instead, use open-ended boxes (e.g., border-bottom only, or U-shapes), simple underlines, or rely on empty space to separate areas. Use thin, crisp lines (`1px solid #333`).
6. HELPER TEXT: Occasionally add small, faint helper notes like "(Leave space here)", "(List goals)", or "(5 dots wide)" to guide the user's drawing process.
7. PROPORTIONS & FULL HEIGHT: The layout MUST cover the entire page height. Use `min-height: 100vh; display: flex; flex-direction: column;` on the main container. You MUST give the largest bottom area (like a notes section or quotes box) `flex-grow: 1` so it stretches to the absolute bottom margin. NEVER leave a large empty void at the bottom half of the page.
8. LANGUAGE: ALL text must be in ENGLISH.
9. TECHNICAL (NO JAVASCRIPT): WeasyPrint does NOT support JavaScript. Output ONLY raw, static HTML and CSS. Do NOT use `<script>` tags or JS loops. Hardcode all necessary HTML manually.
10. PRINTING: Ensure there is a printable area with `@page { size: A4; margin: 10mm; }` (Adjust size based on user input).
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
    design_mode = data.get('designMode', 'print')
    
    if not title:
        return jsonify({'error': 'Title is required'}), 400
        
    try:
        model = get_gemini_model()
        
        prompt = f"""
        Title (Form Name): {title}
        Description (Additional Requests): {description}
        Page Size: {page_size}
        
        Generate the raw HTML/CSS for this planner layout based on the Title.
        If Description is provided, incorporate those specific requests.
        Remember: ALL text must be in English. It must be optimized for {page_size} printing.
        """
        
        active_prompt = GUIDE_SYSTEM_PROMPT if design_mode == 'guide' else SYSTEM_PROMPT
        
        response = model.generate_content(
            [{"role": "user", "parts": [active_prompt, prompt]}]
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
