# core/themes.py

THEME_CONFIG = {
    'Cute': {
        'fonts': '<link href="https://fonts.googleapis.com/css2?family=Pacifico&family=Quicksand:wght@400;600&display=swap" rel="stylesheet">',
        'css': "body { font-family: 'Quicksand', sans-serif; color: #4a4a4a; } h1, h2, h3, .title { font-family: 'Pacifico', cursive; color: #7a8b99; }",
        'border_color': '#8fa1b3',
        'soften_borders': True
    },
    'Editorial': {
        'fonts': '<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;1,600&family=Cormorant+Garamond:wght@400;600&display=swap" rel="stylesheet">',
        'css': "body { font-family: 'Cormorant Garamond', serif; color: #2b2b2b; background-color: #fdfdfd !important; } h1, h2, h3, .title { font-family: 'Playfair Display', serif; text-transform: uppercase; letter-spacing: 1px; }",
        'border_color': '#2b2b2b',
        'soften_borders': False
    },
    'Minimal': {
        'fonts': '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap" rel="stylesheet">',
        'css': "body { font-family: 'Inter', sans-serif; color: #1a1a1a; }",
        'border_color': '#2c3e50',
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
