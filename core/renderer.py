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
    Supports sequential variables inside the loop:
    {i} -> 0, 1, 2...
    {i+1} -> 1, 2, 3...
    {i+6} -> 6, 7, 8...
    {i:02d} -> 00, 01, 02...
    {i+6:02d} -> 06, 07, 08...
    """
    pattern = re.compile(r'<repeat\s+count="(\d+)">((?:(?!<repeat).)*?)</repeat>', re.IGNORECASE | re.DOTALL)
    
    def replacer(m):
        count = int(m.group(1))
        inner = m.group(2)
        result = []
        for i in range(count):
            text = inner
            # Find and evaluate all {i+X} or {i:02d} or {i+X:02d} patterns
            def eval_expr(match):
                expr = match.group(1).replace('i', str(i)).strip()
                # If there's a format specifier like :02d
                if ':' in expr:
                    val_str, fmt = expr.split(':', 1)
                    try:
                        val = eval(val_str)
                        return format(val, fmt)
                    except:
                        return match.group(0)
                else:
                    try:
                        return str(eval(expr))
                    except:
                        return match.group(0)
            
            # Match {i}, {i+1}, {i:02d}, {i+6:02d}
            text = re.sub(r'\{(i[^}]*)\}', eval_expr, text)
            result.append(text)
        return "".join(result)

    while pattern.search(html_content):
        html_content = pattern.sub(replacer, html_content)
    return html_content

def snap_css_to_grid(content):
    """
    Finds vertical CSS properties and snaps their px values to the nearest multiple of 20.
    """
    props = ['height', 'min-height', 'max-height', 'margin', 'padding', 'margin-top', 'margin-bottom', 
             'padding-top', 'padding-bottom', 'gap', 'row-gap', 'top', 'bottom', 'line-height']
    
    # Use (?<!-) to ensure we don't match "bottom" inside "border-bottom"
    prop_pattern = r'(?<!-)\b(' + '|'.join(props) + r')\s*:([^;\"\'<]+)(;?)'
    
    def prop_replacer(match):
        prop_name = match.group(1)
        prop_values = match.group(2)
        semicolon = match.group(3)
        
        def px_replacer(px_match):
            val = float(px_match.group(1))
            if val == 0:
                return "0px"
            snapped = int(round(val / 20.0) * 20)
            if snapped == 0 and val > 0:
                snapped = 20
            return f"{snapped}px"
            
        snapped_values = re.sub(r'([\d\.]+)px', px_replacer, prop_values)
        return f"{prop_name}:{snapped_values}{semicolon}"
        
    return re.sub(prop_pattern, prop_replacer, content, flags=re.IGNORECASE)
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
    
    llm_body = process_repeat_macros(llm_body)
    
    # Safe Aesthetic Color Injection (Replaces raw #333 borders with theme colors)
    if design_mode != 'guide':
        if style_theme == 'Fancy':
            llm_body = llm_body.replace('#333', '#8fa1b3') # Muted pastel blue
            llm_body = llm_body.replace('border-radius: 0', 'border-radius: 8px') # Soften borders
        elif style_theme == 'Antique':
            llm_body = llm_body.replace('#333', '#5c4033') # Vintage dark brown
        elif style_theme == 'Minimal':
            llm_body = llm_body.replace('#333', '#2c3e50') # Charcoal gray
    
    if design_mode == 'guide':
        llm_style = snap_css_to_grid(llm_style)
        llm_body = snap_css_to_grid(llm_body)
    
    dot_css = ""
    lined_bg_css = ""
    if design_mode == 'guide':
        bg_x = (config['W'] - cw) / 2
        bg_y = top_pos
        # Crisp 1x1 dot at (0,0) to prevent WeasyPrint antialiasing blur
        dot_svg = "<svg xmlns='http://www.w3.org/2000/svg' width='20' height='20'><rect x='0' y='0' width='1' height='1' fill='#b0b0b0'/></svg>"
        import urllib.parse
        dot_svg_encoded = urllib.parse.quote(dot_svg)
        dot_css = f"""
    background-image: url("data:image/svg+xml,{dot_svg_encoded}") !important;
    background-position: {bg_x}px {bg_y}px !important;
        """
        lined_svg = "<svg xmlns='http://www.w3.org/2000/svg' width='20' height='20'><rect x='0' y='19' width='20' height='1' fill='#333'/></svg>"
        lined_svg_encoded = urllib.parse.quote(lined_svg)
        lined_bg_css = f"""
.lined-bg {{
    background-image: url("data:image/svg+xml,{lined_svg_encoded}") !important;
    background-position: top !important;
}}
.page-container * {{
    background-color: transparent !important;
}}
        """
    
    css_page_size = f"{page_size} landscape" if orientation == "landscape" else page_size
    
    # Typography & Theme CSS Injection
    google_fonts = ""
    theme_css = ""
    if design_mode != 'guide':
        if style_theme == 'Fancy':
            google_fonts = '<link href="https://fonts.googleapis.com/css2?family=Pacifico&family=Quicksand:wght@400;600&display=swap" rel="stylesheet">'
            theme_css = "body { font-family: 'Quicksand', sans-serif; color: #4a4a4a; } h1, h2, h3, .title { font-family: 'Pacifico', cursive; color: #7a8b99; }"
        elif style_theme == 'Antique':
            google_fonts = '<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;1,600&family=Cormorant+Garamond:wght@400;600&display=swap" rel="stylesheet">'
            theme_css = "body { font-family: 'Cormorant Garamond', serif; color: #3b2f2f; background-color: #fcfaf5 !important; } h1, h2, h3, .title { font-family: 'Playfair Display', serif; }"
        else: # Minimal
            google_fonts = '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap" rel="stylesheet">'
            theme_css = "body { font-family: 'Inter', sans-serif; color: #1a1a1a; }"
    
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
