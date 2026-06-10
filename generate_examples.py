import sys
import os
import subprocess

# Add project root to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

from core.generator import generate_layout_html
from core.pdf_manager import generate_pdf

examples = [
    {"style": "Minimal", "title": "Daily Planner", "filename": "style_minimal.png"},
    {"style": "Fancy", "title": "Gratitude Journal", "filename": "style_fancy.png"},
    {"style": "Antique", "title": "Reading Log", "filename": "style_antique.png"}
]

out_dir = os.path.join(project_root, 'static', 'images')
os.makedirs(out_dir, exist_ok=True)

for ex in examples:
    print(f"Generating HTML for {ex['style']}...")
    html_content = generate_layout_html(
        title=ex['title'],
        description="",
        page_size="A4",
        design_mode="print",
        orientation="portrait",
        style_theme=ex['style']
    )
    
    print(f"Generating PDF for {ex['style']}...")
    file_id, pdf_path = generate_pdf(html_content)
    
    png_path = os.path.join(out_dir, ex['filename'])
    print(f"Converting PDF to PNG at {png_path}...")
    
    # Use sips to convert the first page to PNG
    # sips will output a png for the first page
    res = subprocess.run(["sips", "-s", "format", "png", pdf_path, "--out", png_path], capture_output=True, text=True)
    if res.returncode != 0:
        print(f"Error converting {ex['style']}: {res.stderr}")
    
    # cleanup temp pdf
    if os.path.exists(pdf_path):
        os.remove(pdf_path)

print("All examples generated successfully.")
