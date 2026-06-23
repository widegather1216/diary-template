import json
import os
import sys
from core.generator import generate_default_layout_html

json_path = os.path.join("static", "pre_generated_layouts.json")

# Load existing JSON
try:
    with open(json_path, 'r', encoding='utf-8') as f:
        layouts = json.load(f)
except (FileNotFoundError, json.JSONDecodeError) as e:
    print(f"[ERROR ❌] 레이아웃 백업 파일({json_path})을 읽는 동안 오류가 발생했습니다: {e}")
    print("새로운 레이아웃 딕셔너리를 초기화합니다.")
    layouts = {}

# Mandalart update
print("Generating new Mandalart...")
mandalart_html = generate_default_layout_html(
    title="Mandalart Plan",
    style_theme="Minimal",
    category="mandalart"
)
layouts["mandalart"] = mandalart_html
layouts["Mandalart Plan"] = mandalart_html

# Weekly Planner update
print("Generating new Weekly Planner...")
weekly_html = generate_default_layout_html(
    title="위클리 플레너",
    style_theme="Minimal",
    category="weekly"
)
layouts["weekly"] = weekly_html
layouts["위클리 플레너"] = weekly_html

# Save back to JSON
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(layouts, f, ensure_ascii=False, indent=2)

print("Successfully updated pre_generated_layouts.json with new Mandalart and Weekly Planner!")
