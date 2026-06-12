import json
from pydantic import BaseModel
from google.genai import types

from core.model_config import get_gemini_client
from core.prompts import get_system_prompts
from core.renderer import get_page_config, assemble_master_html

class LayoutResponse(BaseModel):
    html: str

def generate_layout_html(title, description, page_size, design_mode, orientation, style_theme='Minimal'):
    """
    Generates layout HTML using Gemini API with a 2-pass verification process.
    Uses the modern google-genai client.
    """
    client = get_gemini_client()
    config = get_page_config(page_size, orientation)
    SYSTEM_PROMPT, GUIDE_SYSTEM_PROMPT = get_system_prompts()
    
    style_instructions = {
        'Minimal': "Use sans-serif fonts (e.g., 'Inter', 'Helvetica'), thin 1px borders, abundant whitespace, and completely remove any unnecessary decorations or shading. Keep it clean and modern.",
        'Cute': "Use bubbly or hand-drawn fonts (e.g., 'Quicksand', 'Patrick Hand'), rounded borders (e.g., `border-radius: 12px`), dotted/dashed lines, and soft aesthetics. It should look friendly, cozy, and cute like a journaling notebook.",
        'Editorial': "Use elegant serif fonts (e.g., 'Playfair Display', 'Times New Roman'), alternating thick and thin lines for borders, high contrast typography, and magazine-style sophisticated layouts."
    }
    style_detail = style_instructions.get(style_theme, style_instructions['Minimal'])
    
    prompt = f"""
    [TARGET DESIGN PARAMETERS]
    - Form Title (Name): {title}
    - Canvas Width: {config['cw']}px
    - Canvas Height: {config['ch']}px
    - Design Style Theme: {style_theme}
    - Style Guide Instructions: {style_detail}
    - Page Size: {page_size}
    - Page Orientation: {orientation}
    - Description / Custom Requests: {description}
    
    Generate the inner HTML and `<style>` according to the parameters and description above.
    """
    
    active_prompt = GUIDE_SYSTEM_PROMPT if design_mode == 'guide' else SYSTEM_PROMPT
    
    response = client.models.generate_content(
        model='gemini-3.1-flash-lite',
        contents=[active_prompt, prompt],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=LayoutResponse,
            temperature=0.2,
            max_output_tokens=8192,
        )
    )
    
    try:
        result = json.loads(response.text)
        html_content = result.get("html", "")
    except ValueError:
        finish_reason = None
        if response.candidates:
            finish_reason = response.candidates[0].finish_reason
            
        if finish_reason == 'SAFETY':
            raise Exception("안전 필터에 의해 생성이 중단되었습니다.")
        elif finish_reason == 'RECITATION':
            raise Exception("AI가 유사도 필터에 걸렸습니다. 독창적인 내용을 입력하세요.")
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
7a. CRITICAL: Do NOT remove the right or bottom borders of the cells on the edges (do NOT use `:nth-child` to set `border-right: none` or `border-bottom: none`). The cells' right/bottom borders must remain to form the right/bottom outer edges of the grid, ensuring the entire grid border is completely closed.
7b. CRITICAL: For Weekly Planners or Calendars, do NOT use generic placeholders like 'DAY 1', 'DAY 2', or 'Day {{i+1}}'. Write the actual day names (e.g. 'MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN') manually.
7c. CRITICAL: Ensure the top-right corner of the outer border is completely closed. If the Title is borderless, place it OUTSIDE the bordered grid container. Do not apply border-top/left to a container that includes a borderless title and leaves the top-right side open.
7d. CRITICAL: For Mandalart, explicitly style sub-cells with a thin, lighter border (e.g. border-right and border-bottom) and NEVER remove or hide borders on any edge sub-cells using :last-child or :nth-child resets. Keep all inner sub-cell borders visible.
7e. CRITICAL: For Calendars, do NOT write hardcoded date numbers (1, 2, 3...) inside the grid cells unless explicitly requested. Leave date cells completely blank.
7f. CRITICAL: Do NOT write code expressions like `split(",")` or array indexing in HTML text content (e.g. `MON,TUE...split(",")[0]` is strictly forbidden). HTML text must be plain text. If you need distinct text values for repeating blocks (like day names), write each block manually without using the `<repeat>` macro.
7g. CRITICAL: For Daily Planners, do NOT hardcode absolute pixel heights on timetable slots (e.g. do NOT use height: 40px; on slots). Slots must use flex: 1; so they stretch and fill the timetable column, ensuring the bottom of the timetable is closed with the last slot's bottom border.
8. CRITICAL: Replace `white-space: nowrap;` on the main Title with `word-break: keep-all; overflow-wrap: normal;` so words wrap at spaces but do not break in the middle of a word.
{dynamic_rules}
Generated HTML:
```html
{html_content}
```
Return ONLY the corrected HTML/CSS. No explanations.
"""
    
    review_response = client.models.generate_content(
        model='gemini-3.1-flash-lite',
        contents=[active_prompt, review_prompt],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=LayoutResponse,
            temperature=0.2,
            max_output_tokens=8192,
        )
    )
    
    try:
        result = json.loads(review_response.text)
        html_content = result.get("html", "")
    except ValueError:
        pass # Fallback to first pass output if blocked
        
    master_html = assemble_master_html(html_content, design_mode, page_size, orientation, style_theme)
    return master_html
