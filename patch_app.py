import re

def patch():
    with open("app.py", "r") as f:
        content = f.read()
    
    # We will completely replace the constants SYSTEM_PROMPT, GUIDE_SYSTEM_PROMPT, BASE_CSS, BASE_CSS_GUIDE
    # And add the new functions.
    # To do this safely, we will just rewrite app.py
    pass
patch()
