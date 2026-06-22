import threading
import time
import uuid


class TaskManager:
    """Thread-safe in-memory task manager with automatic garbage collection."""
    
    def __init__(self, max_age_seconds=600):
        self._lock = threading.Lock()
        self._tasks = {}
        self._max_age_seconds = max_age_seconds
        
        self._cleanup_thread = threading.Thread(target=self._gc_loop)
        self._cleanup_thread.daemon = True
        self._cleanup_thread.start()

    def create_task(self) -> str:
        task_id = str(uuid.uuid4())
        task_data = {
            'status': 'pending',
            'message': 'AI 작업 요청을 등록 중입니다...',
            'created_at': time.time()
        }
        with self._lock:
            self._tasks[task_id] = task_data
        return task_id

    def update_task(self, task_id: str, status: str, message: str = None, extra_fields: dict = None):
        with self._lock:
            task_data = self._tasks.get(task_id)
            if task_data is not None:
                task_data['status'] = status
                if message is not None:
                    task_data['message'] = message
                if extra_fields:
                    task_data.update(extra_fields)

    def get_task(self, task_id: str) -> dict:
        with self._lock:
            task_data = self._tasks.get(task_id)
            if task_data is not None:
                return dict(task_data)  # Return a copy
        return None

    def _gc_loop(self):
        while True:
            time.sleep(60)
            now = time.time()
            with self._lock:
                expired = [
                    tid for tid, data in self._tasks.items()
                    if (now - data.get('created_at', 0)) > self._max_age_seconds
                    or (data.get('status') in ('success', 'failed') and (now - data.get('created_at', 0)) > 120)
                ]
                for tid in expired:
                    del self._tasks[tid]
