import json
from typing_extensions import TypedDict
from google.generativeai.types import GenerationConfig

from core.model_config import get_gemini_model
from core.prompts import get_system_prompts
from core.renderer import get_page_config, assemble_master_html

class LayoutResponse(TypedDict):
    html: str

def generate_layout_html(title, description, page_size, design_mode, orientation, style_theme='Minimal'):
    """
    Generates layout HTML using Gemini API with a 2-pass verification process.
    """
    model = get_gemini_model()
    config = get_page_config(page_size, orientation)
    SYSTEM_PROMPT, GUIDE_SYSTEM_PROMPT = get_system_prompts(config['cw'], config['ch'], style_theme)
    
    prompt = f"""
    Title (Form Name): {title}
    Description (Additional Requests): {description}
    Page Size: {page_size}
    Orientation: {orientation}
    
    Generate the inner HTML and `<style>` for this {page_size} {orientation} layout.
    """
    
    
    active_prompt = GUIDE_SYSTEM_PROMPT if design_mode == 'guide' else SYSTEM_PROMPT
    
    response = model.generate_content(
        [{"role": "user", "parts": [active_prompt, prompt]}],
        generation_config=GenerationConfig(
            response_mime_type="application/json",
            response_schema=LayoutResponse,
            temperature=0.2,
        )
    )
    
    try:
        result = json.loads(response.text)
        html_content = result.get("html", "")
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
        dynamic_rules = """8. CRITICAL: For guide mode, you MUST use `display: flex; flex-direction: column` and NEVER use `<table>`. Let Flexbox naturally handle vertical heights using `flex: 1`.
9. CRITICAL: You MUST prevent double borders. The outermost wrapper MUST have ONLY `border-top` and `border-left`. ALL inner boxes MUST have ONLY `border-bottom` and `border-right`. DO NOT use `border: 1px solid #333` anywhere."""
    else:
        dynamic_rules = """8. CRITICAL: For grid rows/columns, use flex: 1; so they divide space evenly.
8a. CRITICAL: Do NOT hardcode absolute pixel dimensions for the outermost wrapper (e.g. do NOT use width: 700px; height: 1040px;). Use width: 100%; height: 100%; (or flex layout) to allow responsive auto-scaling."""
        
    dynamic_rules += "\n9. CRITICAL: For bottom note areas, DO NOT use CSS gradients. MUST apply `class=\"lined-bg\"` to a `<div>` to render the SVG lined background."
        
    review_prompt = f"""
Review the generated HTML below and fix any violations of the design rules:
1. CRITICAL: The outermost wrapper MUST have `padding: 0;`. Remove any padding on it.
2. CRITICAL: DO NOT include instructional texts in parentheses (e.g. `(Draw a line)`).
3. Ensure text inside boxes is vertically centered using `display: flex; align-items: center; justify-content: center;`.
4. CRITICAL: NEVER use literal underscores (`__________`) for blank spaces! Remove them entirely. Instead, use a flex container with `border-bottom` for the blank area.
5. CRITICAL: Ensure `overflow: hidden;` is applied to all boxes and cells so text doesn't spill out. DO NOT use `white-space: nowrap;` on large sections.
6. CRITICAL: For text label + blank line rows, DO NOT hardcode widths. Use `white-space: nowrap;` on the label, and `flex: 1; border-bottom: 1px solid #333;` on the blank area. The parent MUST have `align-items: flex-end;`.
7. CRITICAL: To prevent double-thick (2px) borders, do NOT use generic border: 1px solid ... on all cells. Let the wrapper container have border-top and border-left, and let inner cells/rows only have border-right and border-bottom.
8. CRITICAL: Replace `white-space: nowrap;` on the main Title with `word-break: keep-all; overflow-wrap: normal;` so words wrap at spaces but do not break in the middle of a word.
{dynamic_rules}
Generated HTML:
```html
{html_content}
```
Return ONLY the corrected HTML/CSS. No explanations.
"""
    review_response = model.generate_content(
        [{"role": "user", "parts": [active_prompt, review_prompt]}],
        generation_config=GenerationConfig(
            response_mime_type="application/json",
            response_schema=LayoutResponse,
            temperature=0.2,
        )
    )
    
    try:
        result = json.loads(review_response.text)
        html_content = result.get("html", "")
    except ValueError:
        pass # Fallback to first pass output if blocked
        
    master_html = assemble_master_html(html_content, design_mode, page_size, orientation, style_theme)
    return master_html
