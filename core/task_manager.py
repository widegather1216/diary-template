import threading
import time
import uuid

class TaskManager:
    def __init__(self, max_age_seconds=600):
        self._tasks = {}
        self._lock = threading.Lock()
        self._max_age_seconds = max_age_seconds
        
        # Start background thread to clean up old tasks
        self._cleanup_thread = threading.Thread(target=self._gc_loop)
        self._cleanup_thread.daemon = True
        self._cleanup_thread.start()

    def create_task(self) -> str:
        task_id = str(uuid.uuid4())
        with self._lock:
            self._tasks[task_id] = {
                'status': 'pending',
                'message': 'AI 작업 요청을 등록 중입니다...',
                'created_at': time.time()
            }
        return task_id

    def update_task(self, task_id: str, status: str, message: str = None, extra_fields: dict = None):
        with self._lock:
            if task_id in self._tasks:
                task = self._tasks[task_id]
                task['status'] = status
                if message is not None:
                    task['message'] = message
                if extra_fields:
                    task.update(extra_fields)

    def get_task(self, task_id: str) -> dict:
        with self._lock:
            return self._tasks.get(task_id)

    def _gc_loop(self):
        while True:
            time.sleep(60)  # Run cleanup check every 60 seconds
            now = time.time()
            with self._lock:
                to_delete = []
                for task_id, task in self._tasks.items():
                    created_at = task.get('created_at', 0)
                    is_done = task.get('status') in ('success', 'failed')
                    age = now - created_at
                    
                    # Delete tasks older than max age, or completed/failed tasks older than 2 minutes
                    if age > self._max_age_seconds or (is_done and age > 120):
                        to_delete.append(task_id)
                
                for task_id in to_delete:
                    del self._tasks[task_id]
