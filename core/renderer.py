import re

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

def process_repeat_macros(html_content):
    """
    Recursively finds <repeat count="N">...</repeat> tags and multiplies the inner HTML N times.
    Processes innermost tags first to support nested loops.
    """
    pattern = re.compile(r'<repeat\s+count="(\d+)">((?:(?!<repeat).)*?)</repeat>', re.IGNORECASE | re.DOTALL)
    while pattern.search(html_content):
        html_content = pattern.sub(lambda m: m.group(2) * int(m.group(1)), html_content)
    return html_content

def assemble_master_html(llm_output, design_mode, page_size, orientation='portrait'):
    """
    Cleans up the LLM-generated HTML and wraps it inside the strict page-container.
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
    
    llm_body = process_repeat_macros(llm_body)
    
    dot_css = ""
    if design_mode == 'guide':
        bg_x = (config['W'] - cw) / 2
        bg_y = top_pos
        dot_css = f"""
    background-image: radial-gradient(circle, #b0b0b0 1px, transparent 1px) !important;
    background-size: 20px 20px !important;
    background-position: {bg_x - 10}px {bg_y - 10}px !important;
        """
    
    css_page_size = f"{page_size} landscape" if orientation == "landscape" else page_size
    
    master_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
@page {{ size: {css_page_size}; margin: 0; }}
* {{ box-sizing: border-box; margin: 0; padding: 0; background-color: transparent; }}

body {{
    width: 100vw; height: 100vh;
    margin: 0 !important; padding: 0 !important;
    overflow: hidden !important;
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
