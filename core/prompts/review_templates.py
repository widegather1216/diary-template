REVIEW_PROMPT_TEMPLATE = """Review the generated HTML below and fix any violations of the design rules.
CRITICAL: You MUST also preserve and correctly apply the user's original request parameters and custom requests. Do NOT remove or revert any custom layout/style changes requested by the user.

[USER'S ORIGINAL REQUEST]
- Title: {title}
- Custom Requests / Description: {description}

[DESIGN RULES]
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
7h. CRITICAL: Ensure the Notes/Memo area (`.lined-bg`) is never left open at the top. If the block above it has no bottom border, or if there is margin between them, the Notes block MUST have its own top border or the parent wrapper must close it.
7i. CRITICAL: Ensure visual breathing room (Negative Space). If sections are too tight, verify row gaps and margins. Check font sizes for a clean typography hierarchy. Use subtle dotted/dashed lines for secondary grids or circular checklists for Cute theme where appropriate.
7j. CRITICAL: Column Height Alignment. For multi-column layouts, verify if the bottom lines of adjacent columns match. Use `align-items: stretch` on the parent and `height: 100%` on children to sync heights.
7k. CRITICAL: Margin Unity. Ensure all padding, margins, and gaps use uniform modular spacing (8px/20px multiples) to establish a clean vertical rhythm.
7l. CRITICAL: Bullet/Digit Axis. Verify if vertical checklists or timetables have fixed width columns for numbers/icons (e.g. `width: 40px` or `width: 50px`) to prevent horizontal layout shift and ensure vertical axis alignment.
8. CRITICAL: Replace `white-space: nowrap;` on the main Title with `word-break: keep-all; overflow-wrap: normal;` so words wrap at spaces but do not break in the middle of a word.
{dynamic_rules}
Generated HTML:
```html
{html_content}
```
Return ONLY the corrected HTML/CSS. No explanations.
"""
