# 🚀 Deployment Guide to Production

This guide will help you deploy all local changes to your production environment (Streamlit Cloud + Neon.tech PostgreSQL).

---

## 📋 Pre-Deployment Checklist

- ✅ All features tested locally with SQLite
- ✅ No syntax errors
- ✅ Database migration files ready
- ✅ Git repository initialized

---

## Step 1: Apply Database Migration to Neon.tech

### Option A: Using Neon.tech Web Console (Recommended)

1. **Login to Neon.tech**

   - Go to https://neon.tech
   - Login to your account
   - Select your project

2. **Open SQL Editor**

   - Click on "SQL Editor" in the left sidebar
   - Or go to your database dashboard

3. **Run Migration Script**

   - Open the file `add_admin_tests.sql` from your project
   - Copy the entire content
   - Paste it into the SQL Editor
   - Click "Run" or press Ctrl+Enter
   - Wait for confirmation: "Query executed successfully"

4. **Verify Tables Created**
   Run this query to verify:

   ```sql
   SELECT table_name
   FROM information_schema.tables
   WHERE table_name LIKE 'admin%';
   ```

   You should see:

   - `admin_tests`
   - `admin_test_questions`
   - `admin_test_attempts`
   - `admin_test_responses`

---

## Step 2: Push Code to GitHub

### If Git is Already Set Up:

```powershell
# Check status
git status

# Add all changes
git add .

# Commit with descriptive message
git commit -m "Add admin test feature with SQLite/PostgreSQL compatibility"

# Push to GitHub
git push origin main
```

### If Git is NOT Set Up Yet:

```powershell
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Add admin test feature with dual database support"

# Add remote (replace with your GitHub repo URL)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# Push
git branch -M main
git push -u origin main
```

---

## Step 3: Configure Streamlit Cloud

### Set Environment Variable

1. **Go to Streamlit Cloud**

   - Visit https://share.streamlit.io
   - Login and find your app

2. **Open App Settings**

   - Click the ⋮ menu next to your app
   - Select "Settings"

3. **Add Environment Variable**

   - Go to "Secrets" section
   - Add this line:

   ```toml
   USE_POSTGRES = "true"
   ```

   - Click "Save"

4. **Reboot App**
   - Click "Reboot app" to apply changes
   - Wait for app to restart (30-60 seconds)

---

## Step 4: Verify Deployment

### Check Database Connection

1. Login as admin
2. Go to "Create Test" tab
3. Try creating a test
4. If successful, check "Manage Tests" tab

### Test Student Features

1. Login as a student
2. Go to "Take Admin Test" tab
3. Verify tests appear
4. Take a test
5. Submit and check results

### Check Admin Results

1. Login as admin
2. Go to "Manage Tests"
3. Expand a test
4. Check "Show Detailed Results"
5. Verify student data and weak chapter analysis appears

---

## 🔍 Troubleshooting

### Issue: "no such table: admin_tests"

**Solution:** Migration not applied. Re-run Step 1.

### Issue: "column mismatch" errors

**Solution:**

1. Drop old tables in Neon.tech:
   ```sql
   DROP TABLE IF EXISTS admin_test_responses CASCADE;
   DROP TABLE IF EXISTS admin_test_attempts CASCADE;
   DROP TABLE IF EXISTS admin_test_questions CASCADE;
   DROP TABLE IF EXISTS admin_tests CASCADE;
   ```
2. Re-run migration from `add_admin_tests.sql`

### Issue: App still using SQLite syntax

**Solution:**

1. Verify `USE_POSTGRES = "true"` in Streamlit Secrets
2. Reboot the app
3. Check app logs for errors

### Issue: Connection refused to Neon.tech

**Solution:**

1. Verify your Neon.tech database is not paused
2. Check connection string in Streamlit Secrets
3. Ensure your IP is not blocked

---

## 📊 Post-Deployment Verification

Run these checks after deployment:

### Admin Side

- [ ] Can create tests with custom difficulty distribution
- [ ] Can activate/deactivate tests
- [ ] Can view detailed student results
- [ ] Weak chapter analysis shows correctly
- [ ] Can delete tests

### Student Side

- [ ] Can see available admin tests
- [ ] Can take admin tests
- [ ] Questions show difficulty badges (🟢🟡🔴)
- [ ] Test submission works
- [ ] Results are saved correctly

---

## 🎉 Success!

If all checks pass, your production deployment is complete!

**Key Features Now Live:**

- ✅ Admin test creation with full control
- ✅ Difficulty distribution enforcement (40/30/30)
- ✅ Student test-taking with difficulty badges
- ✅ Comprehensive results analytics
- ✅ Weak chapter identification
- ✅ Dual database support (SQLite local, PostgreSQL production)

---

## 📞 Need Help?

**Common Resources:**

- Neon.tech Docs: https://neon.tech/docs
- Streamlit Cloud Docs: https://docs.streamlit.io/streamlit-community-cloud
- Check app logs in Streamlit Cloud for detailed errors

**Quick Links:**

- Database Migration File: `add_admin_tests.sql`
- SQLite Migration (local): `add_admin_tests_sqlite.sql`
- Connection Config: `db_connection.py`
