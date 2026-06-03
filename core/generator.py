from core.model_config import get_gemini_model
from core.prompts import get_system_prompts
from core.renderer import get_page_config, assemble_master_html

def generate_layout_html(title, description, page_size, design_mode, orientation):
    """
    Generates layout HTML using Gemini API with a 2-pass verification process.
    """
    model = get_gemini_model()
    config = get_page_config(page_size, orientation)
    SYSTEM_PROMPT, GUIDE_SYSTEM_PROMPT = get_system_prompts(config['cw'], config['ch'])
    
    prompt = f"""
    Title (Form Name): {title}
    Description (Additional Requests): {description}
    Page Size: {page_size}
    Orientation: {orientation}
    
    Generate the inner HTML and `<style>` for this {page_size} {orientation} layout.
    """
    
    active_prompt = GUIDE_SYSTEM_PROMPT if design_mode == 'guide' else SYSTEM_PROMPT
    
    response = model.generate_content(
        [{"role": "user", "parts": [active_prompt, prompt]}]
    )
    
    try:
        html_content = response.text
    except ValueError:
        finish_reason = getattr(response.candidates[0], 'finish_reason', None)
        if finish_reason == 4:
            raise Exception("AI가 유사도 필터에 걸렸습니다. 독창적인 내용을 입력하세요.")
        elif finish_reason == 3:
            raise Exception("안전 필터에 의해 생성이 중단되었습니다.")
        else:
            raise Exception(f"생성 중단됨 (사유: {finish_reason})")
            
    print("[TRACKING 🔍] 2차 검증 (Self-Reflection) 요청 중...")
    
    dynamic_rules = ""
    if design_mode == 'guide':
        dynamic_rules = """7. CRITICAL: For grid rows/columns or repeating elements, NEVER use fixed fractional pixel sizes (like height: 74px). Use flex: 1; so they divide space perfectly without breaking the 20px dot grid.
8. CRITICAL: For bottom note areas or empty flex-grow sections, MUST apply background-image: repeating-linear-gradient(transparent, transparent 19px, #333 20px); to draw horizontal lines. DO NOT leave them completely empty."""
    else:
        dynamic_rules = """7. CRITICAL: For grid rows/columns, use flex: 1; so they divide space evenly.
8. CRITICAL: For bottom note areas, MUST apply background-image: repeating-linear-gradient(white, white 19px, #e5e7eb 20px); to fill the remaining space with lines."""
        
    review_prompt = f"""
Review the generated HTML below and fix any violations of the design rules:
1. CRITICAL: The outermost wrapper MUST have `padding: 0;`. Remove any padding on it.
2. CRITICAL: DO NOT include instructional texts in parentheses (e.g. `(Draw a line)`).
3. Ensure text inside boxes is vertically centered using `display: flex; align-items: center; justify-content: center;`.
4. Ensure lines/blanks use explicit characters like `_________` instead of empty spans.
5. CRITICAL: Short text labels (like 'SUN', 'MON', or 'Author:') MUST have `white-space: nowrap;` to prevent breaking mid-word.
6. CRITICAL: If you use a grid/table structure where cells have right/bottom borders, ensure the wrapper container has `border-top` and `border-left` so the outer boundaries are not missing.
{dynamic_rules}
Generated HTML:
```html
{html_content}
```
Return ONLY the corrected HTML/CSS. No explanations.
"""
    review_response = model.generate_content(
        [{"role": "user", "parts": [active_prompt, review_prompt]}]
    )
    
    try:
        html_content = review_response.text
    except ValueError:
        pass # Fallback to first pass output if blocked
    
    master_html = assemble_master_html(html_content, design_mode, page_size, orientation)
    return master_html
