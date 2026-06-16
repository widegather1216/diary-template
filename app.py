import os
import re
import threading
import json
import time
from flask import Flask, request, send_file, render_template, jsonify, Response

from core.generator import generate_layout_html
from core.pdf_manager import generate_pdf, cleanup_pdf, get_pdf_path
from core.task_manager import TaskManager
from core.themes import THEME_CONFIG
from core.prompts.layout_hints import LAYOUT_HINTS

app = Flask(__name__)

# Thread-safe in-memory task manager with garbage collection
task_manager = TaskManager()

def bg_generate_task(task_id, data):
    title = data.get('title')
    description = data.get('description', '')
    page_size = data.get('pageSize', 'A4')
    design_mode = data.get('designMode', 'print')
    orientation = data.get('orientation')
    style_theme = data.get('styleTheme', 'Minimal')
    
    if not orientation:
        combined_text = f"{title} {description}".lower()
        if any(keyword in combined_text for keyword in ["가로", "landscape", "가로형", "가로방향", "넓게"]):
            orientation = "landscape"
        else:
            orientation = "portrait"

    def progress_callback(status, message):
        task_manager.update_task(task_id, status, message)

    try:
        master_html = generate_layout_html(
            title=title,
            description=description,
            page_size=page_size,
            design_mode=design_mode,
            orientation=orientation,
            style_theme=style_theme,
            progress_callback=progress_callback
        )
        
        progress_callback('rendering', '도면을 PDF 문서로 굽는 중입니다...')
        file_id, pdf_path = generate_pdf(master_html)
        
        task_manager.update_task(task_id, 'success', extra_fields={
            'file_id': file_id,
            'title': title,
            'page_size': page_size
        })
    except Exception as e:
        task_manager.update_task(task_id, 'failed', message=f'생성 실패: {str(e)}')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/config', methods=['GET'])
def get_config():
    # Unify configurations to avoid duplicate frontend data
    category_mappings = {hint_id: hint_data["keywords"] for hint_id, hint_data in LAYOUT_HINTS.items()}
    return jsonify({
        'themes': THEME_CONFIG,
        'category_mappings': category_mappings
    })

@app.route('/api/generate-pdf', methods=['POST'])
def generate_pdf_route():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Invalid JSON request'}), 400
        
    title = data.get('title')
    if not title:
        return jsonify({'error': 'Title is required'}), 400

    task_id = task_manager.create_task()
    
    # Start thread
    thread = threading.Thread(target=bg_generate_task, args=(task_id, data))
    thread.daemon = True
    thread.start()
    
    return jsonify({'task_id': task_id})

@app.route('/api/task-status/<task_id>', methods=['GET'])
def get_task_status(task_id):
    task = task_manager.get_task(task_id)
    if not task:
        return jsonify({'status': 'failed', 'message': '태스크를 찾을 수 없거나 이미 만료되었습니다.'}), 404
    return jsonify(task)

@app.route('/api/task-stream/<task_id>', methods=['GET'])
def task_stream(task_id):
    def event_generator():
        last_status = None
        last_message = None
        
        while True:
            task = task_manager.get_task(task_id)
            if not task:
                yield f"data: {json.dumps({'status': 'failed', 'message': '태스크를 찾을 수 없거나 이미 만료되었습니다.'}, ensure_ascii=False)}\n\n"
                break
                
            current_status = task.get('status')
            current_message = task.get('message')
            
            # Send message when status or message changes
            if current_status != last_status or current_message != last_message:
                yield f"data: {json.dumps(task, ensure_ascii=False)}\n\n"
                last_status = current_status
                last_message = current_message
                
            # Exit loop if task has completed or failed
            if current_status in ('success', 'failed'):
                break
                
            time.sleep(0.5)
            
    return Response(event_generator(), mimetype='text/event-stream')

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
    data = request.get_json(silent=True)
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
