-- EMERGENCY REVERT: Undo the broad changes to Chemistry Chapter 5
-- This reverts ALL Chemistry Ch5 questions back to their original state

-- Step 1: Revert correct_label from D back to C for all Chemistry Ch5 questions
UPDATE questions
SET correct_label = 'C'
WHERE id IN (
    SELECT q.id
    FROM questions q
    JOIN concepts c ON q.concept_id = c.id
    JOIN chapters ch ON c.chapter_id = ch.id
    WHERE ch.chapter_number = 5
      AND ch.subject = 'Chemistry'
)
AND correct_label = 'D';

-- Step 2: Revert mcq_options - mark C as correct again
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
AND label = 'C';

-- Step 3: Revert mcq_options - mark D as incorrect again
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
AND label = 'D';

-- Step 4: Verify everything is back to C
SELECT COUNT(*) as questions_reverted
FROM questions q
JOIN concepts c ON q.concept_id = c.id
JOIN chapters ch ON c.chapter_id = ch.id
WHERE ch.chapter_number = 5
  AND ch.subject = 'Chemistry'
  AND q.correct_label = 'C';
