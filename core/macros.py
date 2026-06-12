# core/macros.py
import re

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
    pattern = re.compile(r'<repeat\s+count=["\'&quot;]?(\d+)["\'&quot;]?\s*>((?:(?!<repeat).)*?)</repeat>', re.IGNORECASE | re.DOTALL)
    
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
            
            # Match {i}, {i+1}, {8+i}, {i:02d}, {i+6:02d}, {8+i:02d}
            text = re.sub(r'\{([^}]*i[^}]*)\}', eval_expr, text)
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
