import re
import urllib.parse
from core.config import PAGE_DIMENSIONS, PAGE_MARGIN_PX, GRID_UNIT_H, GRID_UNIT_V, MIN_CANVAS_WIDTH
from core.macros import process_repeat_macros, snap_css_to_grid
from core.themes import apply_theme_aesthetics, THEME_CONFIG

def get_page_config(paper_size='A4', orientation='portrait'):
    """
    Calculates dynamic pixel-perfect container dimensions and offsets
    based on the requested paper size and orientation.
    """
    W, H = PAGE_DIMENSIONS.get(paper_size, PAGE_DIMENSIONS['A4'])
    
    if orientation == 'landscape':
        W, H = H, W
    
    # Target margin ~40px
    avail_w = W - (PAGE_MARGIN_PX * 2)
    cw = int(avail_w // GRID_UNIT_H) * GRID_UNIT_H
    if cw < MIN_CANVAS_WIDTH: cw = MIN_CANVAS_WIDTH
    
    avail_h = H - (PAGE_MARGIN_PX * 2)
    ch = int(avail_h // GRID_UNIT_V) * GRID_UNIT_V
    
    half_cw = cw / 2
    shift_x = -10 if half_cw % 20 != 0 else 0
    top_pos = (H - ch) / 2 # Perfect vertical centering
    
    return {
        'W': W, 'H': H,
        'cw': cw, 'ch': ch,
        'shift_x': shift_x,
        'top': top_pos
    }

def _clean_llm_output(llm_output):
    """Extracts style and body from raw LLM HTML output, stripping unwanted tags."""
    style_match = re.search(r'<style>(.*?)</style>', llm_output, re.DOTALL | re.IGNORECASE)
    llm_style = style_match.group(1) if style_match else ""
    
    body_match = re.search(r'<body>(.*?)</body>', llm_output, re.DOTALL | re.IGNORECASE)
    llm_body = body_match.group(1) if body_match else llm_output
    
    # Strip residual HTML wrapper tags and markdown fences in a single pass
    cleanup_pattern = re.compile(
        r'<style>.*?</style>|<!DOCTYPE.*?>|<html.*?>|</html>|<head.*?>|</head>|^```html\s*|```\s*$',
        re.DOTALL | re.IGNORECASE | re.MULTILINE
    )
    llm_body = cleanup_pattern.sub('', llm_body).strip()
    
    return llm_style, llm_body

def _generate_background_css(line_color):
    """Generates CSS classes for lined, grid, and dot SVG backgrounds."""
    backgrounds = {
        'lined-bg': f"<svg xmlns='http://www.w3.org/2000/svg' width='20' height='20'><rect x='0' y='19' width='20' height='1' fill='{line_color}'/></svg>",
        'grid-bg': f"<svg xmlns='http://www.w3.org/2000/svg' width='20' height='20'><path d='M 20 0 L 20 20 L 0 20' fill='none' stroke='{line_color}' stroke-width='1'/></svg>",
        'dot-bg': f"<svg xmlns='http://www.w3.org/2000/svg' width='20' height='20'><circle cx='1' cy='1' r='1' fill='{line_color}'/></svg>",
    }
    css_parts = []
    for class_name, svg in backgrounds.items():
        encoded = urllib.parse.quote(svg)
        css_parts.append(f"""
.{class_name} {{
    background-image: url("data:image/svg+xml,{encoded}") !important;
    background-position: top !important;
    background-repeat: repeat !important;
}}""")
    return "\n".join(css_parts)

def assemble_master_html(llm_output, design_mode, page_size, orientation='portrait', style_theme='Minimal'):
    """
    Cleans up the LLM-generated HTML, applies aesthetics, and wraps it in the page container.
    """
    config = get_page_config(page_size, orientation)
    cw, ch = config['cw'], config['ch']
    shift_x, top_pos = config['shift_x'], config['top']
    
    llm_style, llm_body = _clean_llm_output(llm_output)
    
    # Process repeat loops
    llm_body = process_repeat_macros(llm_body)
    
    # Inject themes/styles
    llm_body, llm_style, google_fonts, theme_css = apply_theme_aesthetics(llm_body, llm_style, style_theme, design_mode)
    
    if design_mode == 'guide':
        llm_style = snap_css_to_grid(llm_style)
        llm_body = snap_css_to_grid(llm_body)
    
    dot_css = ""
    line_color = '#333' if design_mode == 'guide' else THEME_CONFIG.get(style_theme, THEME_CONFIG['Minimal']).get('line_color', '#e5e7eb')
    
    lined_bg_css = _generate_background_css(line_color)
    
    if design_mode == 'guide':
        bg_x = (config['W'] - cw) / 2
        bg_y = top_pos
        # Crisp 1x1 dot at (0,0) to prevent WeasyPrint antialiasing blur
        dot_svg = "<svg xmlns='http://www.w3.org/2000/svg' width='20' height='20'><rect x='0' y='0' width='1' height='1' fill='#b0b0b0'/></svg>"
        dot_svg_encoded = urllib.parse.quote(dot_svg)
        dot_css = f"""
    background-image: url("data:image/svg+xml,{dot_svg_encoded}") !important;
    background-position: {bg_x}px {bg_y}px !important;
        """
        lined_bg_css += """
.page-container * {
    background-color: transparent !important;
}
"""
    
    css_page_size = f"{page_size} landscape" if orientation == "landscape" else page_size
    
    master_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
{google_fonts}
<style>
@page {{ size: {css_page_size}; margin: 0; }}
* {{ box-sizing: border-box; margin: 0; padding: 0; background-color: transparent; }}

body {{
    width: 100%; min-height: 1500px;
    margin: 0 !important; padding: 0 !important;
    background-color: white !important;
    word-break: keep-all !important;
    overflow-wrap: break-word !important;
    {dot_css}
}}

.page-container {{
    position: absolute !important;
    top: {top_pos}px !important; 
    left: 50% !important; 
    margin-left: -{cw // 2}px !important;
    width: {cw}px !important; 
    height: {ch}px !important;
    display: flex; 
    flex-direction: column;
    overflow: hidden !important;
}}

{theme_css}
{lined_bg_css}
{llm_style}
</style>
</head>
<body>
    <div class="page-container">
{llm_body}
    </div>
</body>
</html>"""
    return master_html
