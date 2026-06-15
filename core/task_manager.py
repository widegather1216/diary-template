import os
import json
import tempfile
import threading
import time
import uuid

TASK_DIR = os.path.join(tempfile.gettempdir(), 'formweaver_tasks')
os.makedirs(TASK_DIR, exist_ok=True)

class TaskManager:
    def __init__(self, max_age_seconds=600):
        self._lock = threading.Lock()
        self._max_age_seconds = max_age_seconds
        
        # Start background thread to clean up old tasks
        self._cleanup_thread = threading.Thread(target=self._gc_loop)
        self._cleanup_thread.daemon = True
        self._cleanup_thread.start()

    def _write_atomic(self, filepath: str, data: dict):
        dir_name = os.path.dirname(filepath)
        temp_file = None
        try:
            # Create a temp file in the same directory for atomic replace
            with tempfile.NamedTemporaryFile('w', dir=dir_name, delete=False, encoding='utf-8') as tf:
                json.dump(data, tf, ensure_ascii=False)
                temp_file = tf.name
            os.replace(temp_file, filepath)
        except Exception as e:
            if temp_file and os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except Exception:
                    pass
            raise e

    def create_task(self) -> str:
        task_id = str(uuid.uuid4())
        task_data = {
            'status': 'pending',
            'message': 'AI 작업 요청을 등록 중입니다...',
            'created_at': time.time()
        }
        task_path = os.path.join(TASK_DIR, f"{task_id}.json")
        with self._lock:
            self._write_atomic(task_path, task_data)
        return task_id

    def update_task(self, task_id: str, status: str, message: str = None, extra_fields: dict = None):
        task_path = os.path.join(TASK_DIR, f"{task_id}.json")
        with self._lock:
            try:
                if os.path.exists(task_path):
                    with open(task_path, 'r', encoding='utf-8') as f:
                        task_data = json.load(f)
                    task_data['status'] = status
                    if message is not None:
                        task_data['message'] = message
                    if extra_fields:
                        task_data.update(extra_fields)
                    self._write_atomic(task_path, task_data)
            except Exception as e:
                print(f"[TASK MANAGER ⚠️] 태스크 업데이트 오류 ({task_id}): {e}")

    def get_task(self, task_id: str) -> dict:
        task_path = os.path.join(TASK_DIR, f"{task_id}.json")
        with self._lock:
            try:
                if os.path.exists(task_path):
                    with open(task_path, 'r', encoding='utf-8') as f:
                        return json.load(f)
            except Exception as e:
                print(f"[TASK MANAGER ⚠️] 태스크 읽기 오류 ({task_id}): {e}")
        return None

    def _gc_loop(self):
        while True:
            time.sleep(60)  # Run cleanup check every 60 seconds
            now = time.time()
            try:
                for filename in os.listdir(TASK_DIR):
                    if not filename.endswith('.json'):
                        continue
                    filepath = os.path.join(TASK_DIR, filename)
                    if os.path.exists(filepath):
                        try:
                            mtime = os.path.getmtime(filepath)
                            age = now - mtime
                            
                            # Read task status to determine age limit
                            with open(filepath, 'r', encoding='utf-8') as f:
                                task_data = json.load(f)
                            status = task_data.get('status')
                            is_done = status in ('success', 'failed')
                            
                            # GC tasks older than max age, or completed/failed tasks older than 2 minutes
                            if age > self._max_age_seconds or (is_done and age > 120):
                                os.remove(filepath)
                        except Exception:
                            # Fallback: remove files older than max age if they cannot be read
                            try:
                                mtime = os.path.getmtime(filepath)
                                if (now - mtime) > self._max_age_seconds:
                                    os.remove(filepath)
                            except Exception:
                                pass
            except Exception as e:
                print(f"[TASK MANAGER ⚠️] GC 루프 처리 오류: {e}")
