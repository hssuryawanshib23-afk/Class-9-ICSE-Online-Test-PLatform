import json
import os
import copy

JSON_FOLDER = r"C:\Users\Dell\Desktop\Harsh\Projects\classplus chatbot\Question"

def normalize_question(q):
    # --- Fix form ---
    if q.get("form") == "reasoning":
        q["form"] = "reason"

    # --- Fix thinking_type ---
    if q.get("thinking_type") == "reasoning":
        q["thinking_type"] = "analytical"

    # --- Fix correct_label ---
    if "correct_label" not in q or not q["correct_label"]:
        for opt in q.get("options", []):
            if opt.get("is_correct") is True:
                q["correct_label"] = opt.get("label")
                break

def main():
    print("\n🔧 NORMALIZING DATASET...\n")

    for filename in os.listdir(JSON_FOLDER):
        if not filename.endswith(".json"):
            continue

        path = os.path.join(JSON_FOLDER, filename)

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        original = copy.deepcopy(data)

        for concept in data.get("concepts", []):
            for q in concept.get("questions", []):
                normalize_question(q)

        if data != original:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"✅ Fixed: {filename}")
        else:
            print(f"⏭ No change: {filename}")

    print("\n🎉 NORMALIZATION COMPLETE")

if __name__ == "__main__":
    main()
