import os
from model_config import get_gemini_model

SYSTEM_PROMPT = """You are an expert frontend developer, layout designer, and productivity tool creator.
The user wants to generate a highly professional, aesthetically pleasing, and practical planner/diary layout for printing.
Requirements:
1. DESIGN: Create a premium, clean, and highly functional layout. Use modern typography, elegant borders, ample whitespace, and subtle shading for a sophisticated look. Avoid basic, amateur designs.
2. LANGUAGE: ALL text labels, headings, and placeholders MUST BE IN ENGLISH to avoid rendering issues.
3. CONTENT: Base the core layout and structure primarily on the "Title" (Form Name). If "Description" is provided, seamlessly integrate those specific user requests into the layout.
4. STRUCTURE: Use creative CSS class names and custom styling. Avoid standard HTML boilerplates.
5. TECHNICAL (CRITICAL: ABSOLUTELY NO JAVASCRIPT): WeasyPrint CANNOT run JavaScript. If you use `<script>`, `document.write`, or any JS loop, the system will CRASH and the output will be BLANK. You MUST manually write out every single HTML tag.
6. PRINTING: The layout should perfectly fit the specified page size (A4 or A5). Use mm or cm for precise dimensions. Ensure there is a printable area with `@page { size: A4; margin: 10mm; }` (Adjust size to A4 or A5 based on user input).
7. UNIVERSAL COMPLETENESS (HARDCODE EVERYTHING): You MUST manually copy and paste the `<div>` elements for the grid. For a monthly planner, write exactly 35 separate `<div class="day-cell">...</div>` blocks in the HTML. Do NOT use JavaScript to generate them. Do NOT use shortcuts or `...`.
8. SPACE UTILIZATION (FILL THE PAGE): There must be NO wasted empty space at the bottom. Use `height: 100vh; display: flex; flex-direction: column;` on the main container. For the inner content (whether it's calendar grids or note-taking lines), apply `flex-grow: 1` so they dynamically stretch to fill the entire A4/A5 page down to the bottom margin regardless of the form type.
No extra explanations, just the code.
"""

prompt = f"""
Title (Form Name): Monthly Planner
Description (Additional Requests): 
Page Size: A4

Generate the raw HTML/CSS for this planner layout based on the Title.
If Description is provided, incorporate those specific requests.
Remember: ALL text must be in English. It must be optimized for A4 printing.
"""

def test():
    model = get_gemini_model()
    response = model.generate_content(
        [{"role": "user", "parts": [SYSTEM_PROMPT, prompt]}]
    )
    print("Generated HTML length:", len(response.text))
    with open("debug_output.html", "w") as f:
        f.write(response.text)
    print("Saved to debug_output.html")

if __name__ == "__main__":
    test()
