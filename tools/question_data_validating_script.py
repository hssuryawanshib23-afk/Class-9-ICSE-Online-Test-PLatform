import json
import os

# ================= CONFIG =================
# Validate both Physics and Chemistry questions
PHYSICS_FOLDER = r"C:\Users\Dell\Desktop\Harsh\Projects\classplus chatbot\Question\Physics"
CHEMISTRY_FOLDER = r"C:\Users\Dell\Desktop\Harsh\Projects\classplus chatbot\Question\Chemistry"

ALLOWED_FORMS = {
    "definition",
    "identification",
    "trap",
    "application",
    "comparison",
    "reason"
}

ALLOWED_DIFFICULTY = {"easy", "medium", "hard"}

ALLOWED_THINKING = {
    "recall",
    "conceptual",
    "application",
    "analytical"
}

ALLOWED_OPTION_LABELS = {"A", "B", "C", "D"}
# =========================================


def validate_file(filepath):
    errors = []

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        return [f"❌ Invalid JSON format: {e}"]

    # ---------- CHAPTER ----------
    chapter = data.get("chapter")
    if not chapter:
        errors.append("Missing 'chapter' object")
        return errors

    for field in ["subject", "chapter_number", "chapter_name"]:
        if field not in chapter:
            errors.append(f"Missing chapter field: {field}")

    # ---------- CONCEPTS ----------
    concepts = data.get("concepts")
    if not isinstance(concepts, list) or len(concepts) == 0:
        errors.append("Missing or empty 'concepts' list")
        return errors

    for ci, concept in enumerate(concepts):
        cname = concept.get("concept_name")
        if not cname:
            errors.append(f"Concept[{ci}] missing 'concept_name'")
            continue

        questions = concept.get("questions")
        if not isinstance(questions, list) or len(questions) != 6:
            errors.append(
                f"Concept '{cname}' must have EXACTLY 6 questions (found {len(questions) if questions else 0})"
            )
            continue

        for qi, q in enumerate(questions):
            prefix = f"Concept '{cname}' → Question[{qi}]"

            # Required fields
            for field in [
                "form",
                "difficulty",
                "thinking_type",
                "question_text",
                "key_concept",
                "options",
                "correct_label"
            ]:
                if field not in q:
                    errors.append(f"{prefix} missing field '{field}'")

            # Enums
            if q.get("form") not in ALLOWED_FORMS:
                errors.append(f"{prefix} invalid form: {q.get('form')}")

            if q.get("difficulty") not in ALLOWED_DIFFICULTY:
                errors.append(f"{prefix} invalid difficulty: {q.get('difficulty')}")

            if q.get("thinking_type") not in ALLOWED_THINKING:
                errors.append(f"{prefix} invalid thinking_type: {q.get('thinking_type')}")

            # ---------- OPTIONS ----------
            options = q.get("options")
            if not isinstance(options, list) or len(options) != 4:
                errors.append(f"{prefix} must have EXACTLY 4 options")
                continue

            correct_count = 0
            labels_seen = set()

            for oi, opt in enumerate(options):
                oprefix = f"{prefix} → Option[{oi}]"

                label = opt.get("label")
                text = opt.get("text")
                is_correct = opt.get("is_correct")

                if label not in ALLOWED_OPTION_LABELS:
                    errors.append(f"{oprefix} invalid label: {label}")
                else:
                    labels_seen.add(label)

                if not text or not isinstance(text, str):
                    errors.append(f"{oprefix} missing or empty text")

                if is_correct is True:
                    correct_count += 1

            if labels_seen != ALLOWED_OPTION_LABELS:
                errors.append(f"{prefix} must contain labels A, B, C, D exactly once")

            if correct_count != 1:
                errors.append(f"{prefix} must have EXACTLY ONE correct option")

            if q.get("correct_label") not in ALLOWED_OPTION_LABELS:
                errors.append(f"{prefix} invalid correct_label: {q.get('correct_label')}")

    return errors


def main():
    print("\n🔍 VALIDATING QUESTION DATASET...\n")

    total_errors = 0
    
    # Validate Physics questions
    print("=" * 60)
    print("📚 PHYSICS QUESTIONS")
    print("=" * 60)
    
    if os.path.exists(PHYSICS_FOLDER):
        physics_files = [f for f in os.listdir(PHYSICS_FOLDER) if f.endswith(".json")]
        for file in physics_files:
            path = os.path.join(PHYSICS_FOLDER, file)
            errors = validate_file(path)

            if errors:
                print(f"\n❌ Physics/{file} — INVALID")
                for err in errors:
                    print("   -", err)
                total_errors += len(errors)
            else:
                print(f"✅ Physics/{file} — VALID")
    else:
        print(f"⚠️ Physics folder not found: {PHYSICS_FOLDER}")
    
    # Validate Chemistry questions
    print("\n" + "=" * 60)
    print("🧪 CHEMISTRY QUESTIONS")
    print("=" * 60)
    
    if os.path.exists(CHEMISTRY_FOLDER):
        chemistry_files = [f for f in os.listdir(CHEMISTRY_FOLDER) if f.endswith(".json")]
        for file in chemistry_files:
            path = os.path.join(CHEMISTRY_FOLDER, file)
            errors = validate_file(path)

            if errors:
                print(f"\n❌ Chemistry/{file} — INVALID")
                for err in errors:
                    print("   -", err)
                total_errors += len(errors)
            else:
                print(f"✅ Chemistry/{file} — VALID")
    else:
        print(f"⚠️ Chemistry folder not found: {CHEMISTRY_FOLDER}")

    print("\n" + "=" * 60)
    if total_errors == 0:
        print("🎉 ALL FILES PASSED VALIDATION")
    else:
        print(f"⚠️ Validation completed with {total_errors} total errors")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
