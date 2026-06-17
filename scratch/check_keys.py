import json

with open("/Users/kimbeomjun/diary-template/static/pre_generated_layouts.json", "r") as f:
    layouts = json.load(f)

print(list(layouts.keys()))
