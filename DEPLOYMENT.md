# 🚀 Deployment Guide - Streamlit Community Cloud

## ✅ What I Fixed for You:

1. ✅ Updated all code to work with **both SQLite (local) and PostgreSQL (cloud)**
2. ✅ Created `db_connection.py` - automatic database switching
3. ✅ Updated `auth.py`, `streamlit_app.py`, `generate_test_engine.py`
4. ✅ Created PostgreSQL schema file
5. ✅ Created migration script
6. ✅ Added `requirements.txt` with PostgreSQL support

---

## 📋 STEP-BY-STEP DEPLOYMENT

### **Step 1: Get Free PostgreSQL Database**

Go to **[Render.com](https://render.com)** (or Neon/Supabase)

1. Sign up free
2. Click "New +" → "PostgreSQL"
3. Name: `classplus-db`
4. Keep defaults → **Create Database**
5. **Save these credentials** (shown once):
   - Host: `dpg-xxxx.oregon-postgres.render.com`
   - Database: `classplus_db`
   - Username: `classplus_user`
   - Password: `xxxxx`
   - Port: `5432`

---

### **Step 2: Setup PostgreSQL Schema**

1. In Render dashboard, click your database
2. Go to "Shell" tab (or use any PostgreSQL client)
3. Copy entire content of `schema_postgres.sql`
4. Paste and run in Shell
5. ✅ Tables created!

---

### **Step 3: Migrate Your Existing Data**

**On your local machine:**

```powershell
# Install PostgreSQL driver
pip install psycopg2-binary

# Run migration script
python migrate_to_postgres.py
```

Enter your PostgreSQL credentials when prompted.

This will copy ALL your data from SQLite to PostgreSQL:

- ✅ Users (admin, students)
- ✅ Chapters, Concepts, Questions
- ✅ MCQ Options
- ✅ Test attempts & responses

---

### **Step 4: Push to GitHub**

```powershell
cd "C:\Users\Dell\Desktop\Harsh\Projects\classplus chatbot"

git init
git add .
git commit -m "Ready for Streamlit Cloud deployment"

# Create repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/classplus-chatbot.git
git push -u origin main
```

---

### **Step 5: Deploy on Streamlit Cloud**

1. Go to **[share.streamlit.io](https://share.streamlit.io)**
2. Sign in with GitHub
3. Click "New app"
4. Select:
   - Repository: `YOUR_USERNAME/classplus-chatbot`
   - Branch: `main`
   - Main file: `streamlit_app.py`
5. Click "Advanced settings"
6. Add **Secrets** (paste this with YOUR credentials):

```toml
[postgres]
host = "dpg-xxxx.oregon-postgres.render.com"
database = "classplus_db"
user = "classplus_user"
password = "your_password_here"
port = "5432"
```

7. Add **Environment Variables**:

   ```
   USE_POSTGRES = true
   ```

8. Click **Deploy!** 🚀

---

### **Step 6: Verify Deployment**

Once deployed (2-3 minutes):

1. App opens at: `https://your-app.streamlit.app`
2. Test login with your admin account
3. Check if data is visible
4. Take a test as student
5. Check admin analytics

---

## 🎯 How It Works Now:

### **Local Development:**

```python
USE_POSTGRES = false  # Uses SQLite (quiz.db)
```

### **Production (Streamlit Cloud):**

```python
USE_POSTGRES = true  # Uses PostgreSQL (from secrets)
```

The code automatically detects the environment! 🧠

---

## 🆘 Troubleshooting

### **"ModuleNotFoundError: psycopg2"**

- Fixed: `requirements.txt` already includes it

### **"Connection refused"**

- Check PostgreSQL credentials in Streamlit secrets
- Ensure database is active on Render

### **"Table doesn't exist"**

- Run `schema_postgres.sql` in PostgreSQL first

### **Data not showing**

- Run `migrate_to_postgres.py` to transfer data
- Check `USE_POSTGRES=true` in environment variables

---

## ✅ Final Checklist

- [ ] PostgreSQL database created on Render
- [ ] Schema created (`schema_postgres.sql`)
- [ ] Data migrated (`migrate_to_postgres.py`)
- [ ] Code pushed to GitHub
- [ ] Secrets added to Streamlit Cloud
- [ ] `USE_POSTGRES=true` set
- [ ] App deployed successfully
- [ ] Login works
- [ ] Data visible

---

## 🎉 You're Done!

Your app is now live at:
**`https://your-app-name.streamlit.app`**

Share this link with anyone - it works 24/7! 🚀

---

## 💡 Future Updates

To update your live app:

```bash
git add .
git commit -m "Update feature"
git push
```

Streamlit Cloud auto-deploys on every push! ⚡
