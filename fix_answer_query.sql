-- Fix incorrect answer for Chemistry Chapter 5, Concept 9, Question 4 ONLY
-- Change correct answer from C (Chlorine) to D (Argon)

-- STEP 1: Find the EXACT question ID first
SELECT q.id, q.question_text, c.concept_name, q.correct_label
FROM questions q
JOIN concepts c ON q.concept_id = c.id
JOIN chapters ch ON c.chapter_id = ch.id
WHERE ch.chapter_number = 5
  AND ch.subject = 'Chemistry'
  AND q.question_text LIKE '%noble%'  -- Add part of question text to narrow down
ORDER BY q.id;

-- STEP 2: After identifying the exact question ID from Step 1, replace 'QUESTION_ID_HERE' below

-- Update the correct_label in questions table (ONLY ONE QUESTION)
UPDATE questions
SET correct_label = 'D'
WHERE id = QUESTION_ID_HERE;  -- Replace with actual ID from Step 1

-- Update mcq_options to mark D as correct
UPDATE mcq_options
SET is_correct = 1
WHERE question_id = QUESTION_ID_HERE  -- Replace with actual ID
AND label = 'D';

-- Update mcq_options to mark C as incorrect
UPDATE mcq_options
SET is_correct = 0
WHERE question_id = QUESTION_ID_HERE  -- Replace with actual ID
AND label = 'C';

-- STEP 3: Verify the fix
SELECT q.id, q.question_text, q.correct_label, 
       mo.label, mo.option_text, mo.is_correct
FROM questions q
JOIN mcq_options mo ON q.id = mo.question_id
WHERE q.id = QUESTION_ID_HERE  -- Replace with actual ID
ORDER BY mo.label;

