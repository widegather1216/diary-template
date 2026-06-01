import os
import re
from flask import Flask, request, send_file, render_template, jsonify
from weasyprint import HTML
from model_config import get_gemini_model
import tempfile

app = Flask(__name__)

SYSTEM_PROMPT = """You are an expert frontend developer and layout designer.
The user wants to generate a planner/diary layout for printing.
Create a clean, highly practical, straight-line based layout.
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
        
        html_content = response.text
        
        # Clean up in case Gemini wraps it in markdown code blocks
        html_content = re.sub(r'^```html\s*', '', html_content, flags=re.MULTILINE)
        html_content = re.sub(r'```\s*$', '', html_content, flags=re.MULTILINE).strip()
        
        # Generate PDF using WeasyPrint
        pdf_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        pdf_path = pdf_file.name
        pdf_file.close()
        
        HTML(string=html_content).write_pdf(pdf_path)
        
        return send_file(
            pdf_path, 
            mimetype='application/pdf', 
            as_attachment=True, 
            download_name=f"{title}_{page_size}.pdf"
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 7860)))
