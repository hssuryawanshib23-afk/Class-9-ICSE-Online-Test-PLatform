# 🔄 Dual Database Setup Guide (SQLite Local + PostgreSQL Hosted)

## ✅ What Was Fixed

Your app now works with **both databases**:

- ✅ **SQLite** for local development (offline)
- ✅ **PostgreSQL** (Neon.tech) for hosted production

The code automatically detects which database to use based on the `USE_POSTGRES` environment variable.

---

## 🚀 Quick Start

### **1. Test Local (SQLite)**

```powershell
# Make sure USE_POSTGRES is NOT set
$env:USE_POSTGRES = "false"

# Run the test script
python test_db_connection.py

# Run the app
streamlit run streamlit_app.py
```

### **2. Run Migration for SQLite**

If admin_tests table doesn't exist locally:

```powershell
cd "C:\Users\Dell\Desktop\Harsh\Projects\classplus chatbot"
sqlite3 database/quiz.db < add_admin_tests_sqlite.sql
```

Or paste into SQLite browser:

- Open `database/quiz.db` in DB Browser for SQLite
- Execute SQL tab → Paste contents of `add_admin_tests_sqlite.sql`
- Click Execute

---

## 🌐 How Database Detection Works

```python
# In db_connection.py
USE_POSTGRES = os.getenv("USE_POSTGRES", "false").lower() == "true"

# Local: SQLite
if not USE_POSTGRES:
    conn = sqlite3.connect("database/quiz.db")

# Hosted: PostgreSQL (Neon)
else:
    conn = psycopg2.connect(...)  # Uses streamlit secrets
```

---

## 🔧 What Changed in Code

### 1. **Database Connection Helper Functions**

```python
get_placeholder()       # Returns %s (PostgreSQL) or ? (SQLite)
adapt_query(query)      # Converts PostgreSQL → SQLite syntax
get_last_insert_id()    # Handles RETURNING vs lastrowid
```

### 2. **Query Placeholders**

**Before (PostgreSQL only):**

```python
cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
```

**After (Database-agnostic):**

```python
placeholder = get_placeholder()
cur.execute(f"SELECT * FROM users WHERE id = {placeholder}", (user_id,))
```

### 3. **Insert with ID Return**

**Before:**

```python
cur.execute("INSERT INTO tests (...) VALUES (%s, %s) RETURNING id", (...))
test_id = cur.fetchone()[0]
```

**After:**

```python
if USE_POSTGRES:
    cur.execute(f"... RETURNING id", (...))
    test_id = cur.fetchone()[0]
else:
    cur.execute(f"...", (...))
    test_id = cur.lastrowid
```

### 4. **Boolean Fields**

**Before:**

```python
cur.execute("UPDATE admin_tests SET is_active = true WHERE id = %s", (id,))
```

**After:**

```python
active_val = "true" if USE_POSTGRES else "1"
cur.execute(f"UPDATE admin_tests SET is_active = {active_val} WHERE id = {placeholder}", (id,))
```

### 5. **Timestamps**

**Before:**

```python
cur.execute("INSERT INTO tests (..., started_at) VALUES (%s, NOW())", (...))
```

**After:**

```python
timestamp = "NOW()" if USE_POSTGRES else "CURRENT_TIMESTAMP"
cur.execute(f"INSERT INTO tests (..., started_at) VALUES ({placeholder}, {timestamp})", (...))
```

---

## 📁 Files Modified

1. ✅ **`db_connection.py`** - Added helper functions
2. ✅ **`generate_test_engine.py`** - All queries database-agnostic
3. ✅ **`streamlit_app.py`** - All queries database-agnostic
4. ✅ **`test_db_connection.py`** - New test script

---

## 🧪 Testing Checklist

### Local (SQLite):

```powershell
# 1. Ensure USE_POSTGRES is not set or is "false"
$env:USE_POSTGRES = "false"

# 2. Test connection
python test_db_connection.py

# 3. Run migration if needed
sqlite3 database/quiz.db < add_admin_tests_sqlite.sql

# 4. Run app
streamlit run streamlit_app.py

# 5. Test features:
- [  ] Login as admin
- [  ] Create test
- [  ] View tests
- [  ] Login as student
- [  ] Take admin test
- [  ] Create custom test
```

### Hosted (PostgreSQL):

```bash
# On Streamlit Cloud or production:

# 1. Ensure USE_POSTGRES=true is set in environment
# 2. Run migration in Neon SQL Editor (add_admin_tests.sql)
# 3. Push code to repository
# 4. App auto-deploys and uses PostgreSQL
# 5. Test all features online
```

---

## 🔐 Environment Variables

### Local Development (.env file):

```env
USE_POSTGRES=false
```

### Production (Streamlit Secrets):

```toml
# .streamlit/secrets.toml
USE_POSTGRES = "true"

[postgres]
host = "your-neon-host.neon.tech"
database = "your-database"
user = "your-user"
password = "your-password"
port = "5432"
```

---

## 🐛 Troubleshooting

### "Table admin_tests does not exist" (Local)

```powershell
sqlite3 database/quiz.db < add_admin_tests_sqlite.sql
```

### "Table admin_tests does not exist" (Hosted)

Go to Neon.tech SQL Editor → Run `add_admin_tests.sql`

### "Wrong number of bindings"

The placeholder is wrong. Check if `get_placeholder()` is used.

### "near '%s': syntax error" (SQLite)

PostgreSQL syntax is being used. Make sure queries use `get_placeholder()`.

### "column is_active does not exist"

Migration not run. Execute the SQL migration file.

---

## 📊 Database Comparison

| Feature        | SQLite (Local)      | PostgreSQL (Hosted) |
| -------------- | ------------------- | ------------------- |
| Placeholder    | `?`                 | `%s`                |
| Auto-increment | `AUTOINCREMENT`     | `SERIAL`            |
| Return ID      | `lastrowid`         | `RETURNING id`      |
| Boolean        | `INTEGER (0/1)`     | `BOOLEAN`           |
| Timestamp      | `CURRENT_TIMESTAMP` | `NOW()`             |

---

## ✅ Verification Commands

```powershell
# Test local database
python test_db_connection.py

# Check tables in SQLite
sqlite3 database/quiz.db ".tables"

# Check admin_tests table
sqlite3 database/quiz.db "SELECT * FROM admin_tests;"

# Run app locally
streamlit run streamlit_app.py
```

---

## 🎯 Summary

**Before:**

- ❌ Code only worked with PostgreSQL
- ❌ Couldn't run locally without PostgreSQL

**After:**

- ✅ Works with SQLite locally
- ✅ Works with PostgreSQL on Neon.tech
- ✅ Automatic database detection
- ✅ No code changes needed to switch
- ✅ Same codebase for dev and production

**Your workflow:**

1. Develop locally with SQLite (fast, offline)
2. Push to GitHub
3. Streamlit Cloud automatically uses PostgreSQL (Neon)
4. Both environments work perfectly! 🎉

---

**Need Help?**
Run: `python test_db_connection.py` to diagnose issues.
