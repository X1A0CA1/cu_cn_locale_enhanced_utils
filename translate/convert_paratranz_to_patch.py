import json

INPUT_FILE = "zh-CN_Enhanced_paratranz.json"
OUTPUT_FILE = "translated_nested.json"

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

result = {}

for item in data:
    key = item.get("key")
    translation = item.get("translation")

    if not key or not translation:
        continue

    parts = key.split(".")
    current = result

    for part in parts[:-1]:
        current = current.setdefault(part, {})

    current[parts[-1]] = translation

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f"已保存到 {OUTPUT_FILE}")
