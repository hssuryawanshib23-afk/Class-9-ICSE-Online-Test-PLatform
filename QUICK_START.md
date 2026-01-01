# ⚡ Quick Start Guide - Admin Test Feature

## 🚀 5-Minute Setup

### Step 1: Run Database Migration (Choose one)

**PostgreSQL:**

```bash
psql -h your_host -U your_user -d your_db -f add_admin_tests.sql
```

**SQLite:**

```bash
cd "C:\Users\Dell\Desktop\Harsh\Projects\classplus chatbot"
sqlite3 database/quiz.db < add_admin_tests_sqlite.sql
```

### Step 2: Restart Streamlit App

```bash
streamlit run streamlit_app.py
```

### Step 3: Test as Admin

1. Login with admin credentials
2. Go to **"📝 Create Test"** tab
3. Create a test:
   - Name: "Test 1"
   - Chapters: 2, 3
   - Questions: 20
   - Duration: 30 min
4. Click **"🚀 Create Test"**

### Step 4: Test as Student

1. Logout and login as student
2. Go to **"📋 Take Admin Test"** tab
3. See "Test 1" listed
4. Click **"Start Test"**
5. Complete and submit

✅ Done! Feature is working.

---

## 📋 What Changed?

### Files Modified:

1. ✅ [`generate_test_engine.py`](generate_test_engine.py) - Added difficulty distribution functions
2. ✅ [`streamlit_app.py`](streamlit_app.py) - Added admin/student interfaces

### Files Created:

1. ✅ [`add_admin_tests.sql`](add_admin_tests.sql) - PostgreSQL migration
2. ✅ [`add_admin_tests_sqlite.sql`](add_admin_tests_sqlite.sql) - SQLite migration
3. ✅ [`ADMIN_TEST_FEATURE_GUIDE.md`](ADMIN_TEST_FEATURE_GUIDE.md) - Complete guide
4. ✅ [`VISUAL_FLOW_DIAGRAMS.md`](VISUAL_FLOW_DIAGRAMS.md) - Visual documentation

### Database Tables Added:

- `admin_tests` - Test metadata
- `admin_test_questions` - Question mappings
- `admin_test_attempts` - Student attempts
- `admin_test_responses` - Answer tracking

---

## 🎯 Key Features

### For Admins:

```
✅ Create tests with custom difficulty %
✅ Select specific chapters
✅ Set duration and question count
✅ Manage tests (activate/deactivate/delete)
✅ View test statistics
```

### For Students:

```
✅ View all active admin tests
✅ Take admin tests
✅ Create custom tests (40/30/30 distribution enforced)
✅ Track attempts on each test
```

---

## 🔧 Configuration

### Default Difficulty Distribution:

```python
EASY:   30%
MEDIUM: 30%
HARD:   40%
```

### Modify in [`generate_test_engine.py`](generate_test_engine.py):

```python
def generate_test_with_difficulty_cap(
    chapters,
    total_questions,
    easy_pct=30,      # Change here
    medium_pct=30,    # Change here
    hard_pct=40       # Change here
):
```

---

## 🧪 Testing Commands

### Check Tables Created:

```sql
-- PostgreSQL
SELECT table_name FROM information_schema.tables
WHERE table_name LIKE 'admin%';

-- SQLite
SELECT name FROM sqlite_master
WHERE type='table' AND name LIKE 'admin%';
```

### View Admin Tests:

```sql
SELECT * FROM admin_tests;
```

### View Test Questions:

```sql
SELECT at.test_name, COUNT(atq.id) as question_count
FROM admin_tests at
LEFT JOIN admin_test_questions atq ON at.id = atq.admin_test_id
GROUP BY at.test_name;
```

---

## 🐛 Common Issues

### "Table does not exist"

**Fix:** Run the migration SQL file again

### "Not enough questions"

**Fix:** Lower the question count or adjust difficulty %

### Admin tests not visible to students

**Fix:** Check `is_active = true` in database

### Can't create test

**Fix:** Ensure difficulty % totals exactly 100%

---

## 📞 Need Help?

Check these files:

1. [`ADMIN_TEST_FEATURE_GUIDE.md`](ADMIN_TEST_FEATURE_GUIDE.md) - Detailed guide
2. [`VISUAL_FLOW_DIAGRAMS.md`](VISUAL_FLOW_DIAGRAMS.md) - Visual explanations

---

## ✅ Feature Checklist

- [x] Database tables created
- [x] Admin can create tests
- [x] Student can view tests
- [x] Student can take tests
- [x] Results are saved
- [x] Difficulty caps enforced
- [x] Statistics tracking works

---

**That's it! Your admin test feature is ready to use! 🎉**
