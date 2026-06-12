from core.prompts.base_templates import SYSTEM_PROMPT_TEMPLATE, GUIDE_SYSTEM_PROMPT_TEMPLATE
from core.prompts.layout_hints import LAYOUT_HINTS
from core.prompts.review_templates import REVIEW_PROMPT_TEMPLATE

def get_system_prompts(title: str = "", description: str = ""):
    # Space-insensitive matching logic: remove all spacing
    search_text = f"{title}{description}".lower().replace(" ", "").replace("\t", "").replace("\n", "")
    
    # 5 core layout instructions are always included as a baseline (few-shot context for stability)
    base_keys = ["mandalart", "monthly", "weekly", "daily", "cornell"]
    matched_hints_dict = {key: LAYOUT_HINTS[key]["text"] for key in base_keys}
    
    # Check layout hints against keywords (with spaces removed for comparison)
    for hint_id, hint_data in LAYOUT_HINTS.items():
        if hint_id in base_keys:
            continue
        cleaned_keywords = [kw.lower().replace(" ", "") for kw in hint_data["keywords"]]
        if any(kw in search_text for kw in cleaned_keywords):
            matched_hints_dict[hint_id] = hint_data["text"]
            
    layout_hints_str = "\n".join(matched_hints_dict.values())
    
    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(layout_hints_str=layout_hints_str)
    guide_system_prompt = GUIDE_SYSTEM_PROMPT_TEMPLATE.format(layout_hints_str=layout_hints_str)
    
    return system_prompt, guide_system_prompt

def get_review_prompt(title: str, description: str, dynamic_rules: str, html_content: str) -> str:
    return REVIEW_PROMPT_TEMPLATE.format(
        title=title,
        description=description,
        dynamic_rules=dynamic_rules,
        html_content=html_content
    )
