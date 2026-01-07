-- Fix incorrect answer for Chapter 5, Concept 9, Question 4
-- Change correct answer from C (Chlorine) to D (Argon)

-- Step 1: Find the question
SELECT q.id, q.question_text, ch.chapter_number, ch.subject, c.concept_name
FROM questions q
JOIN concepts c ON q.concept_id = c.id
JOIN chapters ch ON c.chapter_id = ch.id
WHERE ch.chapter_number = 5
  AND ch.subject = 'Chemistry'  -- Assuming Chemistry based on elements mentioned
ORDER BY q.id;

-- Step 2: Update the correct_label in questions table
UPDATE questions
SET correct_label = 'D'
WHERE id IN (
    SELECT q.id
    FROM questions q
    JOIN concepts c ON q.concept_id = c.id
    JOIN chapters ch ON c.chapter_id = ch.id
    WHERE ch.chapter_number = 5
      AND ch.subject = 'Chemistry'
      -- Add more specific filter if needed based on question text
)
AND correct_label = 'C';

-- Step 3: Update mcq_options to mark D as correct and C as incorrect
UPDATE mcq_options
SET is_correct = 1
WHERE question_id IN (
    SELECT q.id
    FROM questions q
    JOIN concepts c ON q.concept_id = c.id
    JOIN chapters ch ON c.chapter_id = ch.id
    WHERE ch.chapter_number = 5
      AND ch.subject = 'Chemistry'
)
AND label = 'D';

UPDATE mcq_options
SET is_correct = 0
WHERE question_id IN (
    SELECT q.id
    FROM questions q
    JOIN concepts c ON q.concept_id = c.id
    JOIN chapters ch ON c.chapter_id = ch.id
    WHERE ch.chapter_number = 5
      AND ch.subject = 'Chemistry'
)
AND label = 'C';

-- Step 4: Verify the fix
SELECT q.id, q.question_text, q.correct_label, 
       mo.label, mo.option_text, mo.is_correct
FROM questions q
JOIN mcq_options mo ON q.id = mo.question_id
JOIN concepts c ON q.concept_id = c.id
JOIN chapters ch ON c.chapter_id = ch.id
WHERE ch.chapter_number = 5
  AND ch.subject = 'Chemistry'
ORDER BY q.id, mo.label;
