# core/config.py
"""
Central configuration constants for the diary-template project.
All magic numbers, directory names, and shared constants are defined here.
"""
import os
import tempfile

# --- AI Model ---
MODEL_NAME = 'gemini-3.1-flash-lite'
MAX_GENERATION_ATTEMPTS = 3

# --- Gemini API Generation Config ---
GENERATION_TEMPERATURE = 0.2
GENERATION_MAX_OUTPUT_TOKENS = 8192

# --- Page Dimensions (96 DPI pixel equivalents of ISO paper sizes) ---
PAGE_DIMENSIONS = {
    'A4': (793.7, 1122.5),
    'A5': (559.4, 793.7),
    'B5': (665.2, 944.9),
}

# --- Layout Grid Constants ---
PAGE_MARGIN_PX = 40
GRID_UNIT_H = 140     # Horizontal grid quantization unit
GRID_UNIT_V = 20      # Vertical grid quantization unit (matches snap_css_to_grid)
MIN_CANVAS_WIDTH = 280

# --- Temporary Directories ---
TEMP_PDF_DIR = os.path.join(tempfile.gettempdir(), 'formweaver_pdfs')
CACHE_DIR = os.path.join(tempfile.gettempdir(), 'weasyprint_url_cache')
TASK_DIR = os.path.join(tempfile.gettempdir(), 'formweaver_tasks')

# Ensure directories exist at import time
os.makedirs(TEMP_PDF_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(TASK_DIR, exist_ok=True)

# --- Orientation Detection Keywords ---
LANDSCAPE_KEYWORDS = ["가로", "landscape", "가로형", "가로방향", "넓게"]

# --- Prompt System ---
BASE_LAYOUT_HINT_KEYS = ["mandalart", "monthly", "weekly", "daily", "cornell"]
