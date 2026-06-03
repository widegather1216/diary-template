import os
from model_config import get_gemini_model
from core.prompts import get_system_prompts
from core.renderer import get_page_config, assemble_master_html

def test_size(paper_size):
    print(f"Testing for {paper_size}...")
    
    config = get_page_config(paper_size)
    SYSTEM_PROMPT, GUIDE_SYSTEM_PROMPT = get_system_prompts(config['cw'], config['ch'])
    
    prompt = f"""
Title (Form Name): Reading Journal
Description (Additional Requests): 
Page Size: {paper_size}

Generate the inner HTML and `<style>` for this {paper_size} layout.
"""
    
    model = get_gemini_model()
    response = model.generate_content(
        [{"role": "user", "parts": [GUIDE_SYSTEM_PROMPT, prompt]}]
    )
    
    html_content = response.text
    master_html = assemble_master_html(html_content, 'guide', paper_size)
    
    filename = f"debug_output_{paper_size}.html"
    with open(filename, "w") as f:
        f.write(master_html)
    print(f"Saved to {filename}\n")

if __name__ == "__main__":
    test_size("A4")
    test_size("A5")
    test_size("B5")
