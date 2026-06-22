# core/themes.py

THEME_CONFIG = {
    'Cute': {
        'fonts_css': """
@font-face {
    font-family: 'Nanum Pen Script';
    src: url('static/fonts/NanumPenScript-Regular.ttf') format('truetype');
    font-weight: normal;
    font-style: normal;
}
@font-face {
    font-family: 'Pacifico';
    src: url('static/fonts/Pacifico-Regular.ttf') format('truetype');
    font-weight: normal;
    font-style: normal;
}
@font-face {
    font-family: 'Quicksand';
    src: url('static/fonts/Quicksand-Variable.ttf') format('truetype');
}
""",
        'css': """
body { font-family: 'Quicksand', 'Nanum Pen Script', sans-serif; color: #3d348b; }
h1, h2, h3, .title { font-family: 'Pacifico', 'Nanum Pen Script', cursive; color: #f15bb5; }
.page-container { position: relative; }
.page-container::before {
    content: ''; position: absolute; top: -8px; left: -8px;
    width: 12px; height: 12px;
    border-top: 1px solid #e0b1cb; border-left: 1px solid #e0b1cb;
    pointer-events: none;
}
.page-container::after {
    content: ''; position: absolute; bottom: -8px; right: -8px;
    width: 12px; height: 12px;
    border-bottom: 1px solid #e0b1cb; border-right: 1px solid #e0b1cb;
    pointer-events: none;
}
.header-block {
    background-color: #fff0f3; color: #d90429;
    padding: 6px 12px; border-radius: 20px;
    font-family: 'Pacifico', 'Nanum Pen Script', cursive;
    border: 1.5px dashed #e0b1cb; text-align: center;
}
.card {
    border: 2px dashed #e0b1cb; border-radius: 16px;
    padding: 15px; background-color: #fffbfc;
    box-shadow: 0 4px 10px rgba(224, 177, 203, 0.1);
}
.checkbox-circle {
    width: 16px; height: 16px; border: 2px solid #e0b1cb;
    border-radius: 50%; display: inline-block;
    background: #ffffff; vertical-align: middle;
}
.badge {
    background: #f15bb5; color: #ffffff;
    padding: 2px 8px; font-size: 0.75rem; border-radius: 10px;
    font-family: 'Quicksand', sans-serif; font-weight: 600;
    display: inline-block;
}
""",
        'border_color': '#e0b1cb',
        'line_color': 'rgba(224, 177, 203, 0.4)',
        'soften_borders': True
    },
    'Editorial': {
        'fonts_css': """
@font-face {
    font-family: 'Playfair Display';
    src: url('static/fonts/PlayfairDisplay-Variable.ttf') format('truetype');
    font-weight: normal;
    font-style: normal;
}
@font-face {
    font-family: 'Playfair Display';
    src: url('static/fonts/PlayfairDisplay-Italic-Variable.ttf') format('truetype');
    font-weight: normal;
    font-style: italic;
}
@font-face {
    font-family: 'Inter';
    src: url('static/fonts/Inter-Variable.ttf') format('truetype');
}
""",
        'css': """
body { font-family: 'Inter', sans-serif; color: #1a1a1a; background-color: #faf9f6 !important; }
h1, h2, h3, .title {
    font-family: 'Playfair Display', serif;
    text-transform: uppercase; letter-spacing: 0.05em;
    font-weight: 700; color: #0d1b2a;
}
.page-container { position: relative; }
.page-container::before {
    content: ''; position: absolute; top: -8px; left: -8px;
    width: 12px; height: 12px;
    border-top: 1px solid #4a4e69; border-left: 1px solid #4a4e69;
    pointer-events: none;
}
.page-container::after {
    content: ''; position: absolute; bottom: -8px; right: -8px;
    width: 12px; height: 12px;
    border-bottom: 1px solid #4a4e69; border-right: 1px solid #4a4e69;
    pointer-events: none;
}
.header-block {
    background-color: #f4f1ea; color: #0d1b2a;
    padding: 8px 15px; border-bottom: 2px solid #4a4e69;
    font-family: 'Playfair Display', serif; font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.05em; text-align: center;
}
.card {
    border: 1px solid #4a4e69; border-radius: 0;
    padding: 20px; background-color: #faf9f6;
    box-shadow: 4px 4px 0px rgba(74, 78, 105, 0.15);
}
.checkbox-circle {
    width: 12px; height: 12px; border: 1.5px solid #4a4e69;
    border-radius: 0; display: inline-block; vertical-align: middle;
}
.badge {
    border: 1.5px solid #4a4e69; color: #4a4e69;
    padding: 2px 8px; font-size: 0.7rem; text-transform: uppercase;
    font-family: 'Inter', sans-serif; font-weight: 600;
    letter-spacing: 0.05em; display: inline-block;
}
""",
        'border_color': '#4a4e69',
        'line_color': 'rgba(74, 78, 105, 0.25)',
        'soften_borders': False
    },
    'Minimal': {
        'fonts_css': """
@font-face {
    font-family: 'Inter';
    src: url('static/fonts/Inter-Variable.ttf') format('truetype');
}
""",
        'css': """
body { font-family: 'Inter', sans-serif; color: #2b2d42; }
h1, h2, h3, .title { font-weight: 800; letter-spacing: -0.03em; color: #1d3557; }
.page-container { position: relative; }
.page-container::before {
    content: ''; position: absolute; top: -8px; left: -8px;
    width: 12px; height: 12px;
    border-top: 1px solid #8d99ae; border-left: 1px solid #8d99ae;
    pointer-events: none;
}
.page-container::after {
    content: ''; position: absolute; bottom: -8px; right: -8px;
    width: 12px; height: 12px;
    border-bottom: 1px solid #8d99ae; border-right: 1px solid #8d99ae;
    pointer-events: none;
}
.header-block {
    background-color: #f1f5f9; color: #1e293b;
    padding: 6px 12px; border-radius: 4px;
    font-family: 'Inter', sans-serif; font-weight: 600;
    letter-spacing: -0.02em; text-align: center;
}
.card {
    border: 1px solid #e2e8f0; border-radius: 8px;
    padding: 15px; background-color: #ffffff;
    box-shadow: 0 1px 3px rgba(0,0,0,0.02);
}
.checkbox-circle {
    width: 14px; height: 14px; border: 1.2px solid #cbd5e1;
    border-radius: 50%; display: inline-block; vertical-align: middle;
}
.badge {
    background: #e2e8f0; color: #475569;
    padding: 2px 6px; font-size: 0.7rem; border-radius: 4px;
    font-family: 'Inter', sans-serif; font-weight: 600;
    display: inline-block;
}
""",
        'border_color': '#8d99ae',
        'line_color': 'rgba(141, 153, 174, 0.25)',
        'soften_borders': False
    }
}

def apply_theme_aesthetics(html_body, html_style, style_theme, design_mode):
    """
    Applies theme-specific fonts, body styling, and border color replacements to the generated HTML and CSS.
    If the design mode is 'guide', it bypasses decorative aesthetics to maintain blueprint purity.
    """
    if design_mode == 'guide':
        return html_body, html_style, "", ""
        
    theme = THEME_CONFIG.get(style_theme, THEME_CONFIG['Minimal'])
    border_color = theme['border_color']
    
    # Replaces raw #333 borders with theme colors
    html_body = html_body.replace('#333', border_color)
    html_style = html_style.replace('#333', border_color)
    if theme.get('soften_borders'):
        html_body = html_body.replace('border-radius: 0', 'border-radius: 12px')
        html_style = html_style.replace('border-radius: 0', 'border-radius: 12px')
    
    # Wrap fonts_css in <style> tag for HTML injection
    google_fonts = f"<style>\n{theme['fonts_css']}\n</style>"
    
    return html_body, html_style, google_fonts, theme['css']
