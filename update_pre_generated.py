import json
import os
from core.generator import generate_layout_html

json_path = os.path.join("static", "pre_generated_layouts.json")

# Load existing JSON
with open(json_path, 'r', encoding='utf-8') as f:
    layouts = json.load(f)

# Mandalart update
print("Generating new Mandalart...")
mandalart_html = generate_layout_html(
    title="Mandalart Plan",
    description="",
    page_size="A4",
    design_mode="print",
    orientation="portrait",
    style_theme="Minimal"
)
layouts["Mandalart Plan"] = mandalart_html

# Weekly Planner update
print("Generating new Weekly Planner...")
weekly_html = generate_layout_html(
    title="위클리 플레너",
    description="",
    page_size="A4",
    design_mode="print",
    orientation="portrait",
    style_theme="Minimal"
)
layouts["위클리 플레너"] = weekly_html

# Save back to JSON
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(layouts, f, ensure_ascii=False, indent=2)

print("Successfully updated pre_generated_layouts.json with new Mandalart and Weekly Planner!")
