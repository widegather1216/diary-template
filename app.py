import os
import re
from flask import Flask, request, send_file, render_template, jsonify

from core.generator import generate_layout_html
from core.pdf_manager import generate_pdf, cleanup_pdf, get_pdf_path

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/generate-pdf', methods=['POST'])
def generate_pdf_route():
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
        master_html = generate_layout_html(title, description, page_size, design_mode, orientation)
        file_id, pdf_path = generate_pdf(master_html)
        
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
        
    pdf_path = get_pdf_path(file_id)
    if not pdf_path:
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
def cleanup_pdf_route():
    data = request.json
    if request.data and not data:
        import json
        try:
            data = json.loads(request.data)
        except:
            data = {}
            
    if data and 'file_id' in data:
        cleanup_pdf(data['file_id'])
    return '', 204

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 7860)))
