LAYOUT_HINTS = {
    "mandalart": {
        "keywords": ["mandalart", "만다라트", "만다라", "3x3", "81", "만달아트", "목표달성"],
        "text": "    - [Mandalart]: MUST be an 81-cell nested grid! Create a main 3x3 flex grid (3 rows, 3 cells per row). Inside EVERY single one of the 9 main cells, create ANOTHER nested 3x3 grid (3 sub-rows, 3 sub-cells per sub-row). You MUST use nested `<repeat count=\"3\">` tags to generate this outer-and-inner 3x3x3x3 layout cleanly (total 81 cells). To ensure all inner grid lines are visible, explicitly style sub-cells with a thin, lighter border (e.g., `.sub-cell { border-right: 1px solid #ccc; border-bottom: 1px solid #ccc; }` or `#e5e7eb` for Cute/Minimal, or `#333` for guide mode) and NEVER remove or hide borders on any edge sub-cells (do NOT use `:last-child` or `:nth-child` resets on sub-cells)."
    },
    "monthly": {
        "keywords": ["monthly", "calendar", "월간", "캘린더", "달력", "한달", "계획표", "먼슬리", "플래너", "플레너", "스케줄러", "스케쥴러", "월별"],
        "text": "    - [Monthly Calendar / Planner]: Create a 7-column header row for days (Sun-Sat) with a fixed short height (e.g., `height: 30px;` or `flex: 0 0 auto;`). Write the actual day names ('SUN', 'MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT') manually. Do NOT use generic placeholders like 'DAY 1', 'DAY 2', or 'Day {i+1}'. Followed by a 7-column flex grid for dates (exactly 5 rows) where each date row uses `flex: 1` to stretch and fill the remaining height. By default, include a 'Notes' area at the bottom using `class=\"lined-bg\"`, unless the user explicitly requests to exclude or modify it. This rule also applies when 'Calendar' (캘린더) is requested. Unless 'Yearly' (연간) is explicitly requested alongside it, 'Calendar' MUST always be generated as a 1-month Monthly Calendar grid (5 rows, 7 columns), NOT a yearly 12-month overview layout. Do NOT populate date cells with hardcoded numbers (1, 2, 3... 31) unless explicitly requested; keep all date cells empty."
    },
    "weekly": {
        "keywords": ["weekly", "주간", "위클리", "일주일", "주별", "플래너", "플레너", "스케줄러", "스케쥴러"],
        "text": "    - [Weekly Planner]: Create a standard Weekly Planner layout based on orientation. For Portrait: a 2-column layout where the Left column has 4 horizontal blocks for MON, TUE, WED, THU, and the Right column has 3 horizontal blocks for FRI, SAT, SUN, and a Notes block at the bottom. Each day block has a bold day header on the left and blank writing lines on the right. For Landscape: a 7-column layout (MON to SUN) with equal widths, and a full-width 'Notes' area at the bottom (height: 150px, `class=\"lined-bg\"`). Do NOT use generic placeholders like 'DAY 1', 'DAY 2', or 'Day {i+1}'."
    },
    "daily": {
        "keywords": ["daily", "데일리", "일간", "하루", "오늘", "일기장", "저널", "journal", "다이어리", "다이얼리", "스케줄러", "스케쥴러", "플래너", "플레너"],
        "text": "    - [Daily Planner / Journal]: Create a standard 2-column Daily Planner layout: Left Column (flex: 1.2, border-right) is a Timetable/Schedule showing a vertical stack of hourly slots (e.g., 06:00 to 22:00 using repeat macro, where each slot uses `flex: 1` to stretch and fill the column's height, containing a time label and a blank line); Right Column (flex: 1) contains a 'Priorities / To-Do List' at the top (with 5-6 checkbox rows) and a 'Notes' area at the bottom (flex: 1, border-top, must use `class=\"lined-bg\"`)."
    },
    "yearly": {
        "keywords": ["yearly", "연간", "연간 계획", "1년", "이어리", "year", "신년 계획", "새해 계획", "플래너", "플레너", "스케줄러", "스케쥴러"],
        "text": "    - [Yearly Overview / Calendar]: Create a 3x4 or 4x3 grid of 12 boxes representing the months, each containing a header for the month name and a blank space/grid for key events or milestones."
    },
    "todo": {
        "keywords": ["to-do", "todo", "투두", "할 일", "할일", "태스크", "checklist", "체크리스트", "해야할일", "해야할 일", "업무 목록"],
        "text": "    - [To-Do List / Task Manager]: Create a clean checklist layout with a status/priority column, a wide task description column (with blank lines or checkable circles/boxes), and a deadline column."
    },
    "habit": {
        "keywords": ["habit", "해빗", "습관", "루틴", "트래커", "tracker", "습관 트래커", "습관 형성", "습관 기록", "루틴 체크", "매일 습관"],
        "text": "    - [Habit Tracker]: Create a grid with a wide first column for the habit name, and exactly 31 narrow columns for the days of the month."
    },
    "ledger": {
        "keywords": ["ledger", "가계부", "금전", "지출", "용돈", "소비", "expense", "budget", "용돈 기입장", "용돈기입장", "자산 관리", "재정 기록", "돈 관리"],
        "text": "    - [Ledger / Expense Tracker]: Create a table-like flex structure with columns like Date, Description, Category, Amount. Ensure data rows have `flex: 1` or explicitly fill vertical space."
    },
    "cornell": {
        "keywords": ["cornell", "코넬", "노트", "필기", "notes", "코넬식", "필기 노트", "강의 노트", "수업 필기"],
        "text": "    - [Cornell Notes]: Create a standard Cornell Notes structure: Top Header Row (height: 60px) for Title, Date, Subject; Middle Row (flex: 1) split into a Left Column for 'Keywords / Cues' (width: 30%, border-right) and a Right Column for 'Notes' (flex: 1, must use `class=\"lined-bg\"`); Bottom Row (height: 150px, border-top) for 'Summary' (must use `class=\"lined-bg\"`)."
    },
    "diet": {
        "keywords": ["diet", "meal", "식단", "식단표", "다이어트", "식사", "food", "메뉴 플래너", "메뉴 플레너", "식단 일기"],
        "text": "    - [Diet / Meal Planner]: Create columns or rows for Breakfast, Lunch, Dinner, and Snacks for each day of the week."
    },
    "reading_note": {
        "keywords": ["reading note", "book review", "독서록", "독서 노트", "책 리뷰", "서평", "북리뷰", "책 기록", "독서 일기", "독후감", "독서 감상문"],
        "text": "    - [Reading Note / Book Review]: Create a dedicated layout for reviewing a single book. Include a header with fields for Book Title, Author, Genre, Date Read, and Star Rating (e.g., 5 blank circles or stars). The main body should feature structured sections for 'Key Summary' (lined or blank box), 'Memorable Quotes' (lined or dotted box), and 'Personal Thoughts' (lined box)."
    },
    "reading_tracker": {
        "keywords": ["reading tracker", "book log", "독서 기록", "독서 리스트", "책 목록", "독서 트래커", "책장", "도서 목록", "책 리스트", "book list"],
        "text": "    - [Reading Tracker / Book Log]: Create a table-like tracker to list multiple books. Columns should include No., Book Title & Author, Dates Read, Rating (e.g., small stars/circles), and a brief one-line review."
    },
    "travel": {
        "keywords": ["travel", "itinerary", "여행", "일정표", "휴가", "trip", "여행 계획", "여행 일정", "이티너러리", "패킹 리스트", "준비물 리스트"],
        "text": "    - [Travel Planner / Itinerary]: Create sections for Travel Details (Dates, Destination), a Packing Checklist, and a Day-by-Day itinerary table (Time, Activity, Budget/Cost)."
    },
    "fitness": {
        "keywords": ["fitness", "workout", "헬스", "운동", "피트니스", "트레이닝", "gym", "운동 일지", "헬스 일지", "운동 기록", "운동 트래커", "오운완"],
        "text": "    - [Fitness / Workout Tracker]: Create a table structure with columns for Exercise Name, Sets, Reps, Weight, and Cardio/Duration to log physical activities."
    },
    "project": {
        "keywords": ["project", "goal", "목표", "프로젝트", "로드맵", "roadmap", "달성", "목표 달성표", "프로젝트 관리", "마일스톤"],
        "text": "    - [Project / Goal Tracker]: Create sections for Goal Description, Action Steps (checkboxes), and a Progress Tracker."
    },
    "gratitude": {
        "keywords": ["gratitude", "감사", "긍정", "일기", "affirmation", "감사 일기", "감사 저널", "긍정 확언", "행복 일기", "마음 챙김 일기"],
        "text": "    - [Gratitude Journal / 감사 일기]: Create a structured 1-column or 2-column emotional wellness layout. Include a header for Date and Daily Affirmation (empty underline or box). The main section must feature 3-5 horizontal rows for \"Today's Gratitude\" (using checkboxes or numbered bullets with flex underlines), a \"Mood & Emotion Tracker\" area (5 small circles/icons with labels underneath: Happy, Calm, Tired, Stressed, Sad), and a bottom \"Self-Reflection\" notes area (flex-grow: 1, min-height: 100px, must use class=\"lined-bg\")."
    },
    "mood": {
        "keywords": ["mood", "감정", "기분", "무드", "emotion", "무드 트래커", "기분 트래커", "감정 트래커", "감정 기록", "기분 기록"],
        "text": "    - [Mood Tracker / 감정 추적기]: Create a visual grid or pixel layout for tracking monthly mood. Typically, create a 31-cell layout (e.g., a 6x6 grid where the last 5 cells are styled as legends or hidden, or a linear calendar bar). Include a Legend area showing 5 color-coded boxes with labels (e.g., Productive, Joyful, Tired, Stressed, Sad). Each day cell must contain only the day number (1 to 31) and remain blank inside for coloring."
    },
    "study": {
        "keywords": ["study", "스터디", "공부", "시험", "학습", "수험생", "공부 계획", "공부 플래너", "공부 플레너", "스터디 플래너", "스터디 플레너", "시험 대비"],
        "text": "    - [Study Planner / 스터디 플래너]: Create a highly structured layout for student/exam prep: Top row (height: 50px) for Target/Goal and D-Day; Left Column (flex: 1.2, border-right) for \"Study Schedule & Timeline\" (vertical stack of hours 06:00 to 24:00 using repeat macro); Right Column (flex: 1) contains a \"Subjects & Tasks\" checklist at the top (5-6 rows with checkable boxes and estimated study times) and a \"Daily Review / Notes\" area at the bottom (flex: 1, border-top, must use class=\"lined-bg\")."
    },
    "time_blocking": {
        "keywords": ["time block", "시간 블록", "타임 블록", "시간 관리", "시간 계획", "타임 블로킹", "시간 블로킹", "24시간 타임라인", "시간표"],
        "text": "    - [Time Blocking Planner / 시간 블록 플래너]: Create a layout focused on hourly schedule visualization: Left Column (width: 80px) is a vertical time indicator list (e.g., 05:00 to 24:00). Right Column (flex: 1) is a matching vertical stack of blank grid blocks representing hourly slots, allowing the user to color/block time ranges. Include a small \"Top Tasks\" checkbox list (3-4 items) and a \"Key Takeaways\" area (must use class=\"lined-bg\") on a side panel or at the bottom."
    },
    "routine": {
        "keywords": ["routine", "루틴", "습관 형성", "루틴 관리", "루틴 플래너", "루틴 플레너", "모닝 루틴", "나이트 루틴", "아침 루틴", "저녁 루틴"],
        "text": "    - [Routine Planner / 루틴 플래너]: Create a 2-column daily/weekly routine layout: Left Column (flex: 1, border-right) is dedicated to \"Morning Routine\" (a vertical checklist of habits with checkboxes and times); Right Column (flex: 1) is for \"Evening Routine\" (a vertical checklist of winding-down habits). Below these columns, include a full-width weekly grid (Habit vs MON-SUN checklist) for tracking routine compliance over the week."
    },
    "mindmap": {
        "keywords": ["mind map", "마인드맵", "브레인스토밍", "생각 정리", "idea", "아이디어", "생각 그물", "아이디어 맵", "생각 매핑"],
        "text": "    - [Mind Map / Brainstorming Board / 마인드맵]: Create a non-linear visual layout: A large central box labeled \"Core Idea/Topic\" with a bold border. Arrange 4 to 6 smaller boxes (\"Sub-topics\") branching outwards symmetrically, connected visually by styled connectors (e.g., thin border lines or flex-based lines). The remaining whitespace should contain subtle dot-grid backgrounds or blank notes area."
    },
    "retrospective": {
        "keywords": ["review", "retrospective", "회고", "성찰", "kpt", "피드백", "주간 회고", "월간 회고", "셀프 피드백", "회고록"],
        "text": "    - [Review & Retrospective / 회고 플래너]: Create a structured feedback layout (e.g., KPT framework): Top Header for Review Period (Week/Month) and rating (1-5 stars/circles). The main body is split into three equal vertical blocks or a 3-box grid for \"Keep\" (What went well, to continue), \"Problem\" (Challenges/Obstacles), and \"Try\" (Actionable improvements for next time). Each box must feature a lined background (must use class=\"lined-bg\")."
    },
    "budget": {
        "keywords": ["budget", "wishlist", "예산", "위시리스트", "저축", "savings", "위시 리스트", "구매 계획", "저축 트래커", "용돈 계획", "예산안"],
        "text": "    - [Budget & Wishlist Planner / 예산 및 위시리스트]: Create a 2-column financial planner: Left Column (flex: 1.2, border-right) contains a \"Monthly Budget Table\" with rows for Income, Fixed Expenses, Variable Expenses, and Savings Goal (using columns: Item, Budget, Actual, Diff); Right Column (flex: 1) contains a \"Wishlist Tracker\" (columns: Item, Price, Priority, Get) and a \"Savings Progress\" section with visual savings milestones (e.g., a vertical progress bar or segmented circles)."
    },
    "recipe": {
        "keywords": ["recipe", "레시피", "요리법", "조리법", "cooking", "chef", "요리 기록", "레시피 기록", "쿡북", "recipe book"],
        "text": "    - [Recipe Card / 레시피 카드]: Create a cooking log layout: Top Header for Recipe Name, Prep Time, Cook Time, and Rating. Two-column split: Left Column (width: 40%, border-right) for \"Ingredients\" list (with checkable boxes and amount lines); Right Column (flex: 1) for \"Directions\" (numbered step-by-step rows using repeat macro, e.g., Step 1 to Step 6, each with a small number circle and writing line). Include a bottom notes section for \"Chef's Tips\"."
    },
    "pet": {
        "keywords": ["pet", "animal", "반려동물", "강아지", "고양이", "집사", "동물 케어", "반려견 일지", "반려묘 일지", "펫 다이어리", "펫 다이얼리", "댕댕이", "냥냥이"],
        "text": "    - [Pet Care Log / 반려동물 케어 일지]: Create a daily pet health log: Top header for Pet Name, Date, and Weight. Main body split into grid panels: \"Meals & Water\" (time, amount, checkbox), \"Activity & Walk\" (duration, route), \"Health & Symptoms\" (checkboxes for energy, digestion, mood), and a \"Medication / Vet Notes\" area (must use class=\"lined-bg\")."
    },
    "sleep": {
        "keywords": ["sleep", "energy", "수면", "에너지", "컨디션", "잠", "dream", "꿈", "수면 패턴", "수면 일기", "잠 기록", "꿈 일기"],
        "text": "    - [Sleep & Energy Tracker / 수면 및 에너지 트래커]: Create a daily/weekly sleep log: A horizontal timeline grid (22:00 to 10:00) where the user can shade sleep hours. Below the timeline, include a vertical \"Energy Level Graph\" grid (x-axis: Morning, Noon, Afternoon, Night; y-axis: 1 to 5) for plotting daily energy fluctuations. Also include small sections for \"Sleep Quality\" rating and \"Dream Journal\" (must use class=\"lined-bg\")."
    },
    "blank_note": {
        "keywords": ["blank", "grid note", "dot note", "lined note", "메모", "모눈", "도트", "노트 패드", "free note", "무지 노트", "유선 노트", "그리드 노트", "줄 노트", "메모지", "자유 노트"],
        "text": "    - [Blank Note Layouts (Grid/Dot/Lined) / 메모 및 기본 노트]: Create standard note-taking templates: For Grid Note, fill the entire canvas with a uniform 20px grid of thin light-gray lines. For Dot Note, fill the canvas with a 20px grid of small dot elements. For Lined Note, create a header area (Title, Date) and fill the rest of the canvas with horizontal writing lines (must use class=\"lined-bg\") with a consistent 24px spacing."
    }
}

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
    
    SYSTEM_PROMPT = f"""You are an expert frontend developer and layout designer.
The user wants a professional planner/diary layout for printing.

Requirements:
1. DESIGN (CRITICAL): Style theme & instructions specified in the user request parameters. Adjust typography, borders, shading, spacing. Avoid amateur designs.
   - Main title: ALWAYS use <h1> or <div class="title">. Subtitles: <h2>.
2. LANGUAGE & CONTENT (CRITICAL): TRANSLATE all text/placeholders and the main title (even if the Form Title parameter is provided in Korean) to English. Output ONLY actual planner content. No hints/parentheses.
3. CANVAS CONSTRAINTS (CRITICAL): Output fits inside a container with dimensions specified in user parameters. Do NOT write <html>, <body>, or @page. Write ONLY inner HTML & <style>. Outer wrapper must have padding: 0. Outer wrapper must fill container dynamically (width: 100%; height: 100%; or flex). DO NOT hardcode absolute px width/height on outermost wrapper.
4. STRUCTURE & SAFETIES (CRITICAL):
   - Use Flexbox. Do NOT use CSS Grid or position: absolute for layout.
   - NEVER use line-height smaller than font-size.
   - ALWAYS include * {{ word-break: keep-all; overflow-wrap: normal; }} in <style> (wrap strictly at spaces, not mid-word).
   - Vertically center text in boxes: display: flex; align-items: center; justify-content: center;.
   - Short labels (SUN, Author:): white-space: nowrap;. Title/long text: do NOT use nowrap.
   - Prevent 2px double-borders: outer wrapper has `border-top` and `border-left`, while inner cells only have `border-right` and `border-bottom` (with `box-sizing: border-box`). Do NOT remove the right or bottom borders of the cells on the edges (do NOT use `:nth-child` to set `border-right: none` or `border-bottom: none`). The right/bottom borders of the cells must remain to form the right/bottom outer edges of the grid, ensuring the entire grid border is completely closed.
   - To prevent the top-right corner from being open/disconnected: If the Title (or header) is borderless, it MUST be placed OUTSIDE the bordered grid container. Do not apply `border-top` or `border-left` to a global wrapper container if it contains any borderless elements (like a borderless title) alongside bordered grid cells.
   - Underlines: do NOT use literal underscores (_____). Use flex container, label with nowrap, empty div with flex: 1 & border-bottom.
5. DYNAMIC REPEAT MACRO (CRITICAL): Use <repeat count="N">...</repeat> for grids/repetition. Use sequence variables: {{i}}, {{i+1}}, {{i+6:02d}} (always keep 'i' as the starting variable in mathematical expressions like {{i+8:02d}}).
   - Count must strictly use double quotes (count="N"). No self-closing <repeat count="N" /> tags.
   - Do NOT use the repeat macro if you need to output unique non-numeric strings (like day names MON, TUE...) inside the loop. In such cases, you MUST write the HTML elements manually. NEVER use split() or Javascript to bypass this.
6. ADAPTIVE LAYOUT (CRITICAL): Adapt to Title/Description. Description takes precedence over reference skeletons. Grids: leave date cells blank.
   - Even grid: cells get flex: 1, min-width: 0, box-sizing: border-box.
   - Uneven grid (Ledger): header & data rows must use matching flex values or % widths.
7. SPACE UTILIZATION: Fill designated canvas height. Default Notes area: flex-grow: 1, min-height: 100px, class="lined-bg". Main wrapper: display: flex; flex-direction: column; height: 100%.
8. COMMON LAYOUT HINTS (CRITICAL STRUCTURES):
{layout_hints_str}
9. NO JAVASCRIPT: Output ONLY pure HTML/CSS. No <script>.
No extra explanations, just code.
"""

    GUIDE_SYSTEM_PROMPT = f"""You are an expert Bullet Journal artist.
The user wants a "Hand-drawing Blueprint" (a reference sketch) to copy manually.

Requirements:
1. DESIGN (CRITICAL): Purely structural hand-drawn look. No decorations, cursive fonts, or double borders. Use only thin, single solid lines for grids. Use 'Patrick Hand' font.
2. CANVAS & GRID (CRITICAL): Container dimensions specified in user parameters. System draws a 20px dot grid background. Do NOT write <body> or @page. Write ONLY inner HTML & <style>. Outer wrapper must have padding: 0. Outer wrapper must fill container dynamically (width: 100%; height: 100%;). DO NOT hardcode absolute px width/height.
3. UNIDIRECTIONAL BORDER FLEXBOX (CRITICAL): Do NOT use <table>, CSS Grid, or standard borders. To prevent 2px borders, use display: flex and strict border rules:
   - Outermost wrapper: border-top: 1px solid #333; border-left: 1px solid #333; box-sizing: border-box; width: 100%;
   - Inner boxes, rows, cells: border-bottom: 1px solid #333; border-right: 1px solid #333; box-sizing: border-box;
   - NEVER use border: 1px solid #333; on anything. NEVER use border-top/left on inner children.
   - Do NOT remove the right or bottom borders of the cells on the edges (do NOT use `:nth-child` to set `border-right: none` or `border-bottom: none`). The right/bottom borders of the cells must remain to form the right/bottom outer edges of the grid, ensuring the entire grid border is completely closed.
   - To prevent the top-right corner from being open/disconnected: If the Title is borderless, place it OUTSIDE the bordered grid container. Do not apply border-top/left to a global container that contains both a borderless title and the grid.
4. FLEXIBLE GRID SIZING (CRITICAL): To fill canvas height perfectly, use flex: 1 or explicit %/px widths. Do NOT calculate complex pixel heights. Let flexbox handle it.
5. LINED BACKGROUNDS (NOTES AREA): Fill remaining space stably. Apply class="lined-bg" to <div>. Use flex-grow: 1; min-height: 100px; border-bottom: 1px solid #333; border-right: 1px solid #333; box-sizing: border-box;.
6. LANGUAGE & CONTENT (CRITICAL): TRANSLATE all text/placeholders and the main title (even if the Form Title parameter is provided in Korean) to English. Output ONLY actual planner content. No hints/parentheses.
7. FONTS: System loaded handwriting fonts. Set font-family: 'Patrick Hand', cursive; where needed.
8. DYNAMIC REPEAT MACRO (CRITICAL): Use <repeat count="N">...</repeat> for grids. Use sequence variables: {{i}}, {{i+1}}, {{i+6:02d}} (always keep 'i' as the starting variable in mathematical expressions like {{i+8:02d}}). Count must strictly use double quotes (count="N"). No self-closing tags. Do NOT use the repeat macro if you need to output unique non-numeric strings (like day names MON, TUE...) inside the loop. Write the HTML elements manually.
9. ADAPTIVE LAYOUT (CRITICAL): Adapt to Title. Description takes precedence over reference skeletons. Grids: leave date cells blank.
   - Even grid: cells get flex: 1, min-width: 0, box-sizing: border-box.
   - Uneven grid: matching flex values or % widths.
10. TEXT HANDLING (CRITICAL):
    - ALWAYS include * {{ word-break: keep-all; overflow-wrap: normal; }} in <style> (wrap strictly at spaces, not mid-word).
    - NEVER use literal underscores (____).
    - ALWAYS apply overflow: hidden; to all cells/boxes.
    - NEVER use white-space: nowrap; on large cells. Title (Form Name): do NOT use nowrap.
11. COMMON LAYOUT HINTS (CRITICAL STRUCTURES):
{layout_hints_str}
No extra explanations, just code.
"""

    return SYSTEM_PROMPT, GUIDE_SYSTEM_PROMPT
