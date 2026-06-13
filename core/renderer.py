import re
import urllib.parse
from core.macros import process_repeat_macros, snap_css_to_grid
from core.themes import apply_theme_aesthetics, THEME_CONFIG

def get_page_config(paper_size='A4', orientation='portrait'):
    """
    Calculates dynamic pixel-perfect container dimensions and offsets
    based on the requested paper size and orientation.
    """
    page_dimensions = {
        'A4': (793.7, 1122.5),
        'A5': (559.4, 793.7),
        'B5': (665.2, 944.9)
    }
    W, H = page_dimensions.get(paper_size, page_dimensions['A4'])
    
    if orientation == 'landscape':
        W, H = H, W
    
    # Target margin ~40px
    target_margin = 40
    avail_w = W - (target_margin * 2)
    cw = int(avail_w // 140) * 140
    if cw < 280: cw = 280
    
    avail_h = H - (target_margin * 2)
    ch = int(avail_h // 20) * 20
    
    half_cw = cw / 2
    shift_x = -10 if half_cw % 20 != 0 else 0
    top_pos = (H - ch) / 2 # Perfect vertical centering
    
    return {
        'W': W, 'H': H,
        'cw': cw, 'ch': ch,
        'shift_x': shift_x,
        'top': top_pos
    }

def assemble_master_html(llm_output, design_mode, page_size, orientation='portrait', style_theme='Minimal'):
    """
    Cleans up the LLM-generated HTML, applies aesthetics, and wraps it in the page container.
    """
    config = get_page_config(page_size, orientation)
    cw, ch = config['cw'], config['ch']
    shift_x, top_pos = config['shift_x'], config['top']
    
    style_match = re.search(r'<style>(.*?)</style>', llm_output, re.DOTALL | re.IGNORECASE)
    llm_style = style_match.group(1) if style_match else ""
    
    body_match = re.search(r'<body>(.*?)</body>', llm_output, re.DOTALL | re.IGNORECASE)
    llm_body = body_match.group(1) if body_match else llm_output
    
    llm_body = re.sub(r'<style>.*?</style>', '', llm_body, flags=re.DOTALL | re.IGNORECASE)
    llm_body = re.sub(r'<!DOCTYPE.*?>', '', llm_body, flags=re.IGNORECASE)
    llm_body = re.sub(r'<html.*?>|</html>', '', llm_body, flags=re.IGNORECASE)
    llm_body = re.sub(r'<head.*?>|</head>', '', llm_body, flags=re.IGNORECASE)
    llm_body = re.sub(r'^```html\s*', '', llm_body, flags=re.MULTILINE)
    llm_body = re.sub(r'```\s*$', '', llm_body, flags=re.MULTILINE).strip()
    
    # Process repeat loops
    llm_body = process_repeat_macros(llm_body)
    
    # Inject themes/styles
    llm_body, llm_style, google_fonts, theme_css = apply_theme_aesthetics(llm_body, llm_style, style_theme, design_mode)
    
    if design_mode == 'guide':
        llm_style = snap_css_to_grid(llm_style)
        llm_body = snap_css_to_grid(llm_body)
    
    dot_css = ""
    line_color = '#333' if design_mode == 'guide' else THEME_CONFIG.get(style_theme, THEME_CONFIG['Minimal']).get('line_color', '#e5e7eb')
    
    # 1. Lined Background SVG
    lined_svg = f"<svg xmlns='http://www.w3.org/2000/svg' width='20' height='20'><rect x='0' y='19' width='20' height='1' fill='{line_color}'/></svg>"
    lined_svg_encoded = urllib.parse.quote(lined_svg)
    
    # 2. Grid (Graph) Background SVG
    grid_svg = f"<svg xmlns='http://www.w3.org/2000/svg' width='20' height='20'><path d='M 20 0 L 20 20 L 0 20' fill='none' stroke='{line_color}' stroke-width='1'/></svg>"
    grid_svg_encoded = urllib.parse.quote(grid_svg)
    
    # 3. Dot Grid Background SVG
    dot_pattern_svg = f"<svg xmlns='http://www.w3.org/2000/svg' width='20' height='20'><circle cx='1' cy='1' r='1' fill='{line_color}'/></svg>"
    dot_pattern_svg_encoded = urllib.parse.quote(dot_pattern_svg)
    
    lined_bg_css = f"""
.lined-bg {{
    background-image: url("data:image/svg+xml,{lined_svg_encoded}") !important;
    background-position: top !important;
    background-repeat: repeat !important;
}}
.grid-bg {{
    background-image: url("data:image/svg+xml,{grid_svg_encoded}") !important;
    background-position: top !important;
    background-repeat: repeat !important;
}}
.dot-bg {{
    background-image: url("data:image/svg+xml,{dot_pattern_svg_encoded}") !important;
    background-position: top !important;
    background-repeat: repeat !important;
}}
"""
    
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
