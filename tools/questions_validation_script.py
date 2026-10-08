"""
Questions JSON Validation Script
Validates all Biology, Chemistry, and Physics question files
Reports errors, missing chapters, and statistics
"""

import json
import os
from pathlib import Path

# Color codes for terminal
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(60)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.RESET}\n")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.RESET}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.RESET}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.RESET}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.RESET}")

def validate_question(question, chapter_num, concept_name, q_index):
    """Validate individual question structure"""
    errors = []
    
    required_fields = [
        "question_id", "form", "difficulty", "thinking_type",
        "question_text", "options", "correct_label", "key_concept"
    ]
    
    for field in required_fields:
        if field not in question:
            errors.append(f"Missing field '{field}'")
    
    # Validate options
    if "options" in question:
        if len(question["options"]) != 4:
            errors.append(f"Expected 4 options, found {len(question['options'])}")
        
        labels = []
        correct_count = 0
        for opt in question["options"]:
            if "label" not in opt or "text" not in opt or "is_correct" not in opt:
                errors.append("Option missing required fields (label/text/is_correct)")
            else:
                labels.append(opt["label"])
                if opt["is_correct"]:
                    correct_count += 1
        
        # Check for duplicate labels
        if len(labels) != len(set(labels)):
            errors.append(f"Duplicate option labels: {labels}")
        
        # Check for exactly one correct answer
        if correct_count != 1:
            errors.append(f"Expected 1 correct answer, found {correct_count}")
        
        # Validate correct_label matches
        if "correct_label" in question:
            if question["correct_label"] not in labels:
                errors.append(f"correct_label '{question['correct_label']}' not in option labels")
    
    # Validate difficulty
    if "difficulty" in question:
        if question["difficulty"] not in ["easy", "medium", "hard"]:
            errors.append(f"Invalid difficulty: {question['difficulty']}")
    
    return errors

def validate_json_file(filepath, subject, expected_chapter):
    """Validate a single JSON file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        errors = []
        warnings = []
        
        # Check structure
        if "chapter" not in data:
            errors.append("Missing 'chapter' key")
            return {"valid": False, "errors": errors, "warnings": warnings}
        
        if "concepts" not in data:
            errors.append("Missing 'concepts' key")
            return {"valid": False, "errors": errors, "warnings": warnings}
        
        chapter_info = data["chapter"]
        
        # Validate chapter info
        if chapter_info.get("subject") != subject:
            warnings.append(f"Subject mismatch: expected '{subject}', found '{chapter_info.get('subject')}'")
        
        if chapter_info.get("chapter_number") != expected_chapter:
            warnings.append(f"Chapter number mismatch: expected {expected_chapter}, found {chapter_info.get('chapter_number')}")
        
        # Validate concepts and questions
        concepts = data["concepts"]
        total_questions = 0
        question_errors = []
        
        for c_idx, concept in enumerate(concepts):
            if "concept_name" not in concept:
                errors.append(f"Concept {c_idx+1} missing 'concept_name'")
                continue
            
            concept_name = concept["concept_name"]
            
            if "questions" not in concept:
                errors.append(f"Concept '{concept_name}' missing 'questions'")
                continue
            
            questions = concept["questions"]
            total_questions += len(questions)
            
            for q_idx, question in enumerate(questions):
                q_errors = validate_question(question, expected_chapter, concept_name, q_idx)
                if q_errors:
                    question_errors.append({
                        "concept": concept_name,
                        "question_num": q_idx + 1,
                        "errors": q_errors
                    })
        
        return {
            "valid": len(errors) == 0 and len(question_errors) == 0,
            "concepts": len(concepts),
            "total_questions": total_questions,
            "errors": errors,
            "warnings": warnings,
            "question_errors": question_errors
        }
        
    except json.JSONDecodeError as e:
        return {
            "valid": False,
            "errors": [f"JSON Decode Error: {str(e)}"],
            "warnings": []
        }
    except Exception as e:
        return {
            "valid": False,
            "errors": [f"Error: {str(e)}"],
            "warnings": []
        }

def validate_subject(subject_name, total_chapters):
    """Validate all chapters for a subject"""
    print_header(f"{subject_name} Validation")
    
    base_path = Path(__file__).parent / "Question" / subject_name
    
    found_chapters = []
    missing_chapters = []
    results = {}
    
    # Check which chapters exist
    for chapter_num in range(1, total_chapters + 1):
        # Try different naming patterns
        patterns = [
            f"{subject_name} Chapter {chapter_num}.json",
            f"chapter_{chapter_num}.json",
            f"Chapter {chapter_num}.json"
        ]
        
        found = False
        for pattern in patterns:
            filepath = base_path / pattern
            if filepath.exists():
                found_chapters.append(chapter_num)
                found = True
                
                print_info(f"Validating Chapter {chapter_num}...")
                result = validate_json_file(filepath, subject_name, chapter_num)
                results[chapter_num] = result
                
                if result["valid"]:
                    print_success(f"Chapter {chapter_num}: {result['concepts']} concepts, {result['total_questions']} questions")
                else:
                    print_error(f"Chapter {chapter_num}: VALIDATION FAILED")
                
                # Show warnings
                for warning in result.get("warnings", []):
                    print_warning(f"  {warning}")
                
                # Show errors
                for error in result.get("errors", []):
                    print_error(f"  {error}")
                
                # Show question errors (first 5 only)
                q_errors = result.get("question_errors", [])
                if q_errors:
                    print_error(f"  Found {len(q_errors)} questions with errors:")
                    for qe in q_errors[:5]:
                        print(f"    • Concept: {qe['concept']}, Q{qe['question_num']}")
                        for err in qe['errors']:
                            print(f"      - {err}")
                    if len(q_errors) > 5:
                        print(f"    ... and {len(q_errors) - 5} more question errors")
                
                break
        
        if not found:
            missing_chapters.append(chapter_num)
    
    # Summary
    print(f"\n{Colors.BOLD}Summary for {subject_name}:{Colors.RESET}")
    print(f"  Total Chapters: {total_chapters}")
    print(f"  Found: {len(found_chapters)} chapters")
    print(f"  Missing: {len(missing_chapters)} chapters")
    
    if missing_chapters:
        print_warning(f"Missing chapters: {', '.join(map(str, missing_chapters))}")
    
    # Overall statistics
    total_concepts = sum(r.get("concepts", 0) for r in results.values())
    total_questions = sum(r.get("total_questions", 0) for r in results.values())
    valid_files = sum(1 for r in results.values() if r["valid"])
    
    print(f"  Valid files: {valid_files}/{len(found_chapters)}")
    print(f"  Total concepts: {total_concepts}")
    print(f"  Total questions: {total_questions}")
    
    return {
        "found": found_chapters,
        "missing": missing_chapters,
        "results": results,
        "total_concepts": total_concepts,
        "total_questions": total_questions,
        "valid_files": valid_files
    }

def main():
    print_header("QUESTIONS VALIDATION SCRIPT")
    print(f"{Colors.BOLD}Validating all question files for Biology, Chemistry, and Physics{Colors.RESET}\n")
    
    # Define subjects and their total chapters
    subjects = {
        "Biology": 19,
        "Chemistry": 9,
        "Physics": 10
    }
    
    overall_stats = {}
    
    for subject, total_chapters in subjects.items():
        stats = validate_subject(subject, total_chapters)
        overall_stats[subject] = stats
    
    # Final summary
    print_header("OVERALL SUMMARY")
    
    for subject, stats in overall_stats.items():
        status = f"{Colors.GREEN}✓{Colors.RESET}" if len(stats["missing"]) == 0 else f"{Colors.RED}✗{Colors.RESET}"
        print(f"{status} {Colors.BOLD}{subject}:{Colors.RESET}")
        print(f"    Chapters: {len(stats['found'])}/{subjects[subject]} "
              f"({Colors.GREEN if stats['valid_files'] == len(stats['found']) else Colors.RED}"
              f"{stats['valid_files']} valid{Colors.RESET})")
        print(f"    Concepts: {stats['total_concepts']}")
        print(f"    Questions: {stats['total_questions']}")
        if stats["missing"]:
            print(f"    {Colors.YELLOW}Missing: {', '.join(map(str, stats['missing']))}{Colors.RESET}")
    
    # Grand total
    total_questions = sum(s["total_questions"] for s in overall_stats.values())
    total_concepts = sum(s["total_concepts"] for s in overall_stats.values())
    total_found = sum(len(s["found"]) for s in overall_stats.values())
    total_expected = sum(subjects.values())
    
    print(f"\n{Colors.BOLD}Grand Total:{Colors.RESET}")
    print(f"  Chapters: {total_found}/{total_expected}")
    print(f"  Concepts: {total_concepts}")
    print(f"  Questions: {total_questions}")
    
    print(f"\n{Colors.GREEN}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}Validation Complete!{Colors.RESET}")
    print(f"{Colors.GREEN}{'='*60}{Colors.RESET}\n")

if __name__ == "__main__":
    main()
