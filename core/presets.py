import re

def get_preset_example(title, description, design_mode):
    combined_text = f"{title} {description}".lower()
    
    PRESETS = {
        "mandalart": {
            "keywords": ["만다라트", "mandalart", "mandala"],
            "skeleton": """
<div style="display: flex; flex-direction: column; min-height: 100%;">
  <div class="title" style="text-align: center; margin-bottom: 20px;">Mandalart</div>
  <!-- Main 3x3 Grid -->
  <div style="flex: 1; display: flex; flex-direction: column; border-top: 1px solid #333; border-left: 1px solid #333; box-sizing: border-box;">
    <repeat count="3">
      <div style="display: flex; flex: 1;">
        <repeat count="3">
          <!-- Inner 3x3 Block -->
          <div style="flex: 1; display: flex; flex-direction: column; border-bottom: 1px solid #333; border-right: 1px solid #333; box-sizing: border-box; min-width: 0;">
            <repeat count="3">
              <div style="display: flex; flex: 1;">
                <repeat count="3">
                  <div style="flex: 1; border-bottom: 1px solid #ccc; border-right: 1px solid #ccc; box-sizing: border-box; min-width: 0; overflow: hidden;">
                  </div>
                </repeat>
              </div>
            </repeat>
          </div>
        </repeat>
      </div>
    </repeat>
  </div>
</div>
"""
        },
        "monthly": {
            "keywords": ["달력", "먼슬리", "월간", "캘린더", "calendar", "monthly"],
            "skeleton": """
<div style="display: flex; flex-direction: column; min-height: 100%;">
  <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 20px;">
    <div class="title">Monthly Planner</div>
    <div style="display: flex; align-items: flex-end; width: 250px;">
      <span style="white-space: nowrap; margin-right: 5px;">Month:</span>
      <div style="flex: 1; border-bottom: 1px solid #333; height: 1.5em;"></div>
    </div>
  </div>
  
  <div style="display: flex; width: 100%; border-top: 1px solid #333; border-left: 1px solid #333; box-sizing: border-box;">
    <repeat count="7">
      <div style="flex: 1; border-bottom: 1px solid #333; border-right: 1px solid #333; box-sizing: border-box; text-align: center; min-width: 0;">DAY</div>
    </repeat>
  </div>
  
  <div style="flex: 1; display: flex; flex-direction: column; border-left: 1px solid #333; box-sizing: border-box;">
    <repeat count="5">
      <div style="display: flex; flex: 1; width: 100%;">
        <repeat count="7">
          <div style="flex: 1; border-bottom: 1px solid #333; border-right: 1px solid #333; box-sizing: border-box; min-width: 0; overflow: hidden;"></div>
        </repeat>
      </div>
    </repeat>
  </div>
</div>
"""
        },
        "weekly": {
            "keywords": ["위클리", "주간", "weekly", "week"],
            "skeleton": """
<div style="display: flex; flex-direction: column; min-height: 100%;">
  <div class="title" style="text-align: center; margin-bottom: 20px;">Weekly Planner</div>
  <div style="flex: 1; display: flex; flex-direction: column; border-top: 1px solid #333; border-left: 1px solid #333; box-sizing: border-box;">
    <div style="display: flex;">
      <repeat count="7">
        <div style="flex: 1; border-bottom: 1px solid #333; border-right: 1px solid #333; box-sizing: border-box; text-align: center; min-width: 0;">DAY {{i+1}}</div>
      </repeat>
    </div>
    <div style="display: flex; flex: 1;">
      <repeat count="7">
        <div style="flex: 1; border-bottom: 1px solid #333; border-right: 1px solid #333; box-sizing: border-box; min-width: 0; overflow: hidden; display: flex; flex-direction: column;">
          <div class="lined-bg" style="flex: 1;"></div>
        </div>
      </repeat>
    </div>
  </div>
</div>
"""
        },
        "daily": {
            "keywords": ["데일리", "일일", "하루", "daily", "day", "타임블록", "timeblock"],
            "skeleton": """
<div style="display: flex; flex-direction: column; min-height: 100%;">
  <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 20px;">
    <div class="title">Daily Planner</div>
    <div style="display: flex; align-items: flex-end; width: 250px;">
      <span style="white-space: nowrap; margin-right: 5px;">Date:</span>
      <div style="flex: 1; border-bottom: 1px solid #333; height: 1.5em;"></div>
    </div>
  </div>
  
  <div style="flex: 1; display: flex; gap: 20px;">
    <!-- Schedule Column -->
    <div style="flex: 1; display: flex; flex-direction: column; border-top: 1px solid #333; border-left: 1px solid #333; box-sizing: border-box;">
      <div style="border-bottom: 1px solid #333; border-right: 1px solid #333; box-sizing: border-box; text-align: center;">Schedule</div>
      <repeat count="15">
        <div style="display: flex; flex: 1; min-width: 0; box-sizing: border-box;">
          <div style="width: 60px; border-bottom: 1px solid #333; border-right: 1px solid #333; box-sizing: border-box; text-align: center;">{{i+7:02d}}:00</div>
          <div style="flex: 1; border-bottom: 1px solid #333; border-right: 1px solid #333; box-sizing: border-box; min-width: 0;"></div>
        </div>
      </repeat>
    </div>
    
    <!-- Tasks and Notes Column -->
    <div style="flex: 1; display: flex; flex-direction: column; gap: 20px;">
      <div style="flex: 1; display: flex; flex-direction: column; border-top: 1px solid #333; border-left: 1px solid #333; box-sizing: border-box;">
        <div style="border-bottom: 1px solid #333; border-right: 1px solid #333; box-sizing: border-box; text-align: center;">To-Do List</div>
        <repeat count="8">
          <div style="display: flex; flex: 1; min-width: 0; box-sizing: border-box;">
            <div style="width: 40px; border-bottom: 1px solid #333; border-right: 1px solid #333; box-sizing: border-box; display: flex; align-items: center; justify-content: center;"><div style="width: 14px; height: 14px; border: 1px solid #333;"></div></div>
            <div style="flex: 1; border-bottom: 1px solid #333; border-right: 1px solid #333; box-sizing: border-box; min-width: 0;"></div>
          </div>
        </repeat>
      </div>
      <div style="flex: 1; display: flex; flex-direction: column; border-top: 1px solid #333; border-left: 1px solid #333; box-sizing: border-box;">
        <div style="border-bottom: 1px solid #333; border-right: 1px solid #333; box-sizing: border-box; text-align: center;">Notes</div>
        <div class="lined-bg" style="flex: 1; border-bottom: 1px solid #333; border-right: 1px solid #333; box-sizing: border-box;"></div>
      </div>
    </div>
  </div>
</div>
"""
        },
        "habit": {
            "keywords": ["해빗", "습관", "habit", "tracker", "트래커"],
            "skeleton": """
<div style="display: flex; flex-direction: column; min-height: 100%;">
  <div class="title" style="text-align: center; margin-bottom: 20px;">Habit Tracker</div>
  <div style="flex: 1; display: flex; flex-direction: column; border-top: 1px solid #333; border-left: 1px solid #333; box-sizing: border-box;">
    <!-- Header Row -->
    <div style="display: flex; flex: 1;">
      <div style="width: 120px; border-bottom: 1px solid #333; border-right: 1px solid #333; box-sizing: border-box; text-align: center;">Habit</div>
      <repeat count="31">
        <div style="flex: 1; border-bottom: 1px solid #333; border-right: 1px solid #333; box-sizing: border-box; text-align: center; min-width: 0;">{{i+1}}</div>
      </repeat>
    </div>
    <!-- Data Rows -->
    <repeat count="15">
      <div style="display: flex; flex: 1;">
        <div style="width: 120px; border-bottom: 1px solid #333; border-right: 1px solid #333; box-sizing: border-box;"></div>
        <repeat count="31">
          <div style="flex: 1; border-bottom: 1px solid #333; border-right: 1px solid #333; box-sizing: border-box; min-width: 0;"></div>
        </repeat>
      </div>
    </repeat>
  </div>
</div>
"""
        }
    }

    for preset_key, data in PRESETS.items():
        for keyword in data["keywords"]:
            if keyword in combined_text:
                example_html = data["skeleton"]
                return f"\\n\\n[REFERENCE SKELETON FOR '{keyword.upper()}']\\nUse the following structural HTML template as a foundational starting point. If the user's Description asks for specific changes (like removing sections or adding new ones), flexibly modify this structure to fulfill their request using flexbox.\\n```html\\n{example_html.strip()}\\n```\\n"
    
    return ""

