import re

def validate_layout(html_content, title, description, category, design_mode):
    """
    Validates if the generated HTML layout is valid and correct.
    Returns (is_valid, reason)
    """
    # 1. CSS/Style presence check
    if "<style" not in html_content.lower() or "</style>" not in html_content.lower():
        return False, "Layout does not contain a <style> block."
    
    # 2. Literal underscores check (3 or more underscores)
    if re.search(r'_{3,}', html_content):
        return False, "Layout contains literal underscores (___) which are strictly forbidden. Use border-bottom instead."
        
    # 3. Code residue checks (such as split() or list array indexing inside text)
    if "split(" in html_content or ".split" in html_content:
        return False, "Layout contains code-like expressions ('split') in text content, which is forbidden."
        
    # 4. Repeat tag validation
    # Check for forbidden self-closing <repeat> tag
    if re.search(r'<repeat[^>]*/>', html_content):
        return False, "Layout contains a self-closing <repeat /> tag, which is forbidden. Always use opening and closing tags: <repeat count=\"N\">...</repeat>."
        
    # Check for unmatched repeat tags
    open_repeats = len(re.findall(r'<repeat\b', html_content))
    close_repeats = len(re.findall(r'</repeat>', html_content))
    if open_repeats != close_repeats:
        return False, f"Mismatch in repeat tags: found {open_repeats} opening tags and {close_repeats} closing tags."
        
    # 5. Empty or extremely short content check
    if len(html_content.strip()) < 150:
        return False, "Generated layout content is too short or empty."

    # 6. Check for instructional text in parentheses e.g. (Draw grid) or (Add notes)
    if re.search(r'\((?:Draw|Write|Add|Insert|Put)\s+[^)]+\)', html_content, re.IGNORECASE):
        return False, "Layout contains instructional text in parentheses (e.g. '(Draw lines)'), which is forbidden."

    return True, ""
