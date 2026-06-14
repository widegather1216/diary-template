import json
from pydantic import BaseModel
from google.genai import types

from core.model_config import get_gemini_client
from core.prompts import get_system_prompts, get_review_prompt
from core.renderer import get_page_config, assemble_master_html

class LayoutResponse(BaseModel):
    html: str

def _request_initial_layout(client, title, description, page_size, orientation, style_theme, active_prompt, config, category=None):
    style_instructions = {
        'Minimal': "Use sans-serif fonts (e.g., 'Inter', 'Helvetica'), thin 1px borders, abundant whitespace, and completely remove any unnecessary decorations or shading. Keep it clean and modern.",
        'Cute': "Use bubbly or hand-drawn fonts (e.g., 'Quicksand', 'Architects Daughter'), rounded borders (e.g., `border-radius: 12px`), dotted/dashed lines, and soft aesthetics. It should look friendly, cozy, and cute like a journaling notebook.",
        'Editorial': "Use elegant serif fonts (e.g., 'Playfair Display', 'Times New Roman'), alternating thick and thin lines for borders, high contrast typography, and magazine-style sophisticated layouts."
    }
    style_detail = style_instructions.get(style_theme, style_instructions['Minimal'])
    
    metadata_hint = ""
    if category == 'monthly':
        metadata_hint = "\n    - [CRITICAL] TARGET METADATA: MUST include 'Year' (년도) and 'Month' (달/월) fields grouped together."
    elif category == 'daily':
        metadata_hint = "\n    - [CRITICAL] TARGET METADATA: MUST include 'Date' (날짜) and 'Weather' (날씨) or 'Mood' (기분) fields grouped together."
    elif category == 'weekly':
        metadata_hint = "\n    - [CRITICAL] TARGET METADATA: MUST include 'Date/Week' (날짜/주차) fields grouped together."
    elif category == 'cornell':
        metadata_hint = "\n    - [CRITICAL] TARGET METADATA: MUST include 'Date' and 'Subject' (주제) fields grouped together."
    elif category == 'ledger':
        metadata_hint = "\n    - [CRITICAL] TARGET METADATA: MUST include 'Date' and 'Page' fields grouped together."
    elif category == 'reading_note':
        metadata_hint = "\n    - [CRITICAL] TARGET METADATA: MUST include 'Book Title', 'Author', 'Genre', 'Date Read', and 'Rating' (5 stars/circles) fields. Layout them across the full width or align left below the title, allowing ample space for writing (DO NOT align them to the right)."
    elif category == 'recipe':
        metadata_hint = "\n    - [CRITICAL] TARGET METADATA: MUST include 'Recipe Name', 'Prep Time', 'Cook Time', and 'Rating' fields. Layout them across the full width or align left below the title, allowing ample space for writing (DO NOT align them to the right)."
        
    prompt = f"""
    [TARGET DESIGN PARAMETERS]
    - Form Title (Name): {title}
    - Canvas Width: {config['cw']}px
    - Canvas Height: {config['ch']}px
    - Design Style Theme: {style_theme}
    - Style Guide Instructions: {style_detail}
    - Page Size: {page_size}
    - Page Orientation: {orientation}{metadata_hint}
    - Description / Custom Requests: {description}
    
    Generate the inner HTML and `<style>` according to the parameters and description above.
    """
    
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
        return result.get("html", "")
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

def _request_self_reflection(client, title, description, active_prompt, html_content, design_mode):
    print("[TRACKING 🔍] 2차 검증 (Self-Reflection) 요청 중...")
    
    dynamic_rules = ""
    if design_mode == 'guide':
        dynamic_rules = """8. CRITICAL: For guide mode, you MUST use `display: flex; flex-direction: column` and NEVER use `<table>`. Let Flexbox naturally handle vertical heights using `flex: 1`.
9. CRITICAL: You MUST prevent double borders. The outermost wrapper MUST have ONLY `border-top` and `border-left`. ALL inner boxes MUST have ONLY `border-bottom` and `border-right`. DO NOT use `border: 1px solid #333` anywhere."""
    else:
        dynamic_rules = """8. CRITICAL: For grid rows/columns, use flex: 1; so they divide space evenly.
8a. CRITICAL: Do NOT hardcode absolute pixel dimensions for the outermost wrapper (e.g. do NOT use width: 700px; height: 1040px;). Use width: 100%; height: 100%; (or flex layout) to allow responsive auto-scaling."""
        
    dynamic_rules += "\n9. CRITICAL: For bottom note areas, DO NOT use CSS gradients. MUST apply `class=\"lined-bg\"` to a `<div>` to render the SVG lined background."
        
    review_prompt = get_review_prompt(
        title=title,
        description=description,
        dynamic_rules=dynamic_rules,
        html_content=html_content
    )
    
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
        return result.get("html", html_content)
    except ValueError:
        return html_content # Fallback to first pass output if blocked

def generate_layout_html(title, description, page_size, design_mode, orientation, style_theme='Minimal', category=None):
    """
    Generates layout HTML using Gemini API with a 2-pass verification process.
    Uses the modern google-genai client.
    """
    client = get_gemini_client()
    config = get_page_config(page_size, orientation)
    SYSTEM_PROMPT, GUIDE_SYSTEM_PROMPT = get_system_prompts(title=title, description=description, category=category)
    
    active_prompt = GUIDE_SYSTEM_PROMPT if design_mode == 'guide' else SYSTEM_PROMPT
    
    # Pass 1: Generate initial layout
    html_content = _request_initial_layout(
        client=client,
        title=title,
        description=description,
        page_size=page_size,
        orientation=orientation,
        style_theme=style_theme,
        active_prompt=active_prompt,
        config=config,
        category=category
    )
    
    # Pass 2: Self-Reflection
    html_content = _request_self_reflection(
        client=client,
        title=title,
        description=description,
        active_prompt=active_prompt,
        html_content=html_content,
        design_mode=design_mode
    )
        
    master_html = assemble_master_html(html_content, design_mode, page_size, orientation, style_theme)
    return master_html
