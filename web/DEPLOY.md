# Deploying the web app (free)

The app is one Next.js project. It talks directly to your Neon Postgres, so there is no second server.
Your existing Streamlit app keeps running untouched until you decide to switch.

## 1. One-time database step (safe, additive)
Open the Neon SQL editor and run `migrations/001_login_attempts.sql`.
It only creates a new table (`login_attempts`) used for login throttling. The Streamlit app never touches it.

## 2. Deploy on Vercel
1. Go to vercel.com, sign in with GitHub, click **Add New → Project**, and import this repository.
2. Set **Root Directory** to `web`.
3. Add these Environment Variables:

| Name | Value |
|---|---|
| `DATABASE_URL` | Neon connection string (use the **pooled** one; it already ends in `?sslmode=require`) |
| `SESSION_SECRET` | A long random string. Generate one with `openssl rand -base64 48` |

4. Click **Deploy**. Every push to a branch gets its own preview URL; `main` becomes the live site.

Use a **Neon branch** (a copy of your data) as `DATABASE_URL` while testing, then switch the variable to the
production database when you are ready to go live.

## Free-tier notes
- Vercel Hobby is for personal, non-commercial use. If you charge for the service, move to a paid plan or
  to Cloudflare Pages / Netlify. The app is standard Next.js, so moving is a re-import.
- Neon free pauses the database when idle; the first request after a quiet period can take about a second.

## Local development
```bash
cp .env.example .env.local   # fill in values
npm install
npm run dev                  # http://localhost:3000
```

## Compatibility with the Streamlit app
- Passwords are bcrypt (`$2b$`) in both apps, so existing users can log in here with the same password.
- Recovery codes are stored in the same `users.recovery_code` column in the same format, so the Streamlit
  "forgot password" flow still works for accounts created here.
