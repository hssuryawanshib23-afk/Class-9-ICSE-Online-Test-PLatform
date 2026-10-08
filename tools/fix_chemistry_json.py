"""
Fix Chemistry JSON files - Change 'reasoning' to 'reason'
Also fix other validation errors
"""

import json
import os
import glob

CHEMISTRY_FOLDER = r"Question\Chemistry"

def fix_chemistry_file(filepath):
    """Fix common errors in Chemistry JSON files"""
    print(f"\n📖 Fixing: {os.path.basename(filepath)}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    changes_made = 0
    
    # Fix each concept's questions
    for concept in data.get('concepts', []):
        for question in concept.get('questions', []):
            # Fix 1: Change 'reasoning' to 'reason'
            if question.get('form') == 'reasoning':
                question['form'] = 'reason'
                changes_made += 1
            
            # Fix 2: Change invalid thinking_type 'reasoning' to 'analytical'
            if question.get('thinking_type') == 'reasoning':
                question['thinking_type'] = 'analytical'
                changes_made += 1
    
    if changes_made > 0:
        # Save the fixed file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"   ✓ Fixed {changes_made} errors")
        return True
    else:
        print(f"   ✓ No changes needed")
        return False

def main():
    print("=" * 60)
    print("  FIXING CHEMISTRY JSON FILES")
    print("=" * 60)
    
    if not os.path.exists(CHEMISTRY_FOLDER):
        print(f"❌ Folder not found: {CHEMISTRY_FOLDER}")
        return
    
    # Get all Chemistry JSON files
    files = glob.glob(os.path.join(CHEMISTRY_FOLDER, "*.json"))
    
    if not files:
        print(f"❌ No JSON files found in {CHEMISTRY_FOLDER}")
        return
    
    total_fixed = 0
    for filepath in sorted(files):
        if fix_chemistry_file(filepath):
            total_fixed += 1
    
    print("\n" + "=" * 60)
    print(f"  ✅ Fixed {total_fixed} files")
    print("=" * 60)
    print("\nNext step: Run validation again")
    print("python Question_Data_valadating_script.py")
    print()

if __name__ == "__main__":
    main()
