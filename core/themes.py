# core/themes.py

THEME_CONFIG = {
    'Cute': {
        'fonts': '<link href="https://fonts.googleapis.com/css2?family=Pacifico&family=Quicksand:wght@400;600&family=Nanum+Pen+Script&display=swap" rel="stylesheet">',
        'css': "body { font-family: 'Quicksand', 'Nanum Pen Script', sans-serif; color: #3d348b; } h1, h2, h3, .title { font-family: 'Pacifico', 'Nanum Pen Script', cursive; color: #f15bb5; } .page-container { position: relative; } .page-container::before { content: ''; position: absolute; top: -8px; left: -8px; width: 12px; height: 12px; border-top: 1px solid #e0b1cb; border-left: 1px solid #e0b1cb; pointer-events: none; } .page-container::after { content: ''; position: absolute; bottom: -8px; right: -8px; width: 12px; height: 12px; border-bottom: 1px solid #e0b1cb; border-right: 1px solid #e0b1cb; pointer-events: none; }",
        'border_color': '#e0b1cb',
        'soften_borders': True
    },
    'Editorial': {
        'fonts': '<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;1,600&family=Inter:wght@300;400;600&display=swap" rel="stylesheet">',
        'css': "body { font-family: 'Inter', sans-serif; color: #1a1a1a; background-color: #faf9f6 !important; } h1, h2, h3, .title { font-family: 'Playfair Display', serif; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 700; color: #0d1b2a; } .page-container { position: relative; } .page-container::before { content: ''; position: absolute; top: -8px; left: -8px; width: 12px; height: 12px; border-top: 1px solid #4a4e69; border-left: 1px solid #4a4e69; pointer-events: none; } .page-container::after { content: ''; position: absolute; bottom: -8px; right: -8px; width: 12px; height: 12px; border-bottom: 1px solid #4a4e69; border-right: 1px solid #4a4e69; pointer-events: none; }",
        'border_color': '#4a4e69',
        'soften_borders': False
    },
    'Minimal': {
        'fonts': '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap" rel="stylesheet">',
        'css': "body { font-family: 'Inter', sans-serif; color: #2b2d42; } h1, h2, h3, .title { font-weight: 800; letter-spacing: -0.03em; color: #1d3557; } .page-container { position: relative; } .page-container::before { content: ''; position: absolute; top: -8px; left: -8px; width: 12px; height: 12px; border-top: 1px solid #8d99ae; border-left: 1px solid #8d99ae; pointer-events: none; } .page-container::after { content: ''; position: absolute; bottom: -8px; right: -8px; width: 12px; height: 12px; border-bottom: 1px solid #8d99ae; border-right: 1px solid #8d99ae; pointer-events: none; }",
        'border_color': '#8d99ae',
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
        
    return html_body, html_style, theme['fonts'], theme['css']
