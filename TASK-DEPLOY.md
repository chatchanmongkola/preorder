# Preorder App — Production Deployment Guide

Deploy target: **Vercel** (frontend static + backend ASGI serverless) + **Supabase** (PostgreSQL).

---

## Prerequisites

- [ ] Vercel account (vercel.com) — install CLI: `npm i -g vercel`
- [ ] Supabase account (supabase.com) — create a project
- [ ] LINE Developers account with a **LINE Login** channel (production channel, not dev)
- [ ] Telegram bot token from [@BotFather](https://t.me/BotFather) (or reuse dev token)
- [ ] A domain (e.g. `preorder.example.com`) pointed to Vercel's nameservers

---

## Step 1 — Supabase (Production Database)

### 1.1 Create a Supabase project
1. Go to [supabase.com](https://supabase.com) → **New project**
2. Note the **Database URL** (found in Project Settings → Database → Connection string → URI)
   - Format: `postgresql+psycopg2://postgres:[PASSWORD]@db.[REF].supabase.co:5432/postgres`
   - Use `psycopg2` (not `psycopg2` if Supabase suggests `psycopg2` — keep `psycopg2`)

### 1.2 Run migrations against Supabase
```bash
# Install vercel CLI first if needed
# Set DATABASE_URL locally to point to Supabase, then run:
cd backend
DATABASE_URL="postgresql+psycopg2://postgres:YOUR_PASSWORD@db.REF.supabase.co:5432/postgres" \
  alembic upgrade head
```

> **Or** run migrations via Vercel CLI after deploying (see Step 2.5).

---

## Step 2 — Backend (FastAPI → Vercel Serverless)

### 2.1 Create `backend/api/index.py`
Vercel requires a Python serverless entry point:

```python
from app.main import app

handler = app
```

### 2.2 Create `backend/vercel.json`
```json
{
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "api/index.py"
    }
  ]
}
```

### 2.3 Add `vercel` to `.gitignore` (optional)
```gitignore
.vercel
```

### 2.4 Deploy backend to Vercel
```bash
cd backend
vercel --prod
```

### 2.5 Run migrations on the deployed backend (one-time)
```bash
# Trigger migration via Vercel CLI one-off command, or
# Set DATABASE_URL in Vercel env vars and call:
curl -X POST https://your-backend.vercel.app/health
# Then connect to Supabase directly and run:
#   alembic upgrade head
# from your local machine with DATABASE_URL set to Supabase
```

---

## Step 3 — Frontend (Vite → Vercel Static)

### 3.1 No special config needed
Vercel auto-detects Vite projects. Ensure these files exist:

- `frontend/vercel.json` (optional — Vercel auto-detects Vite)
- `frontend/package.json` with `build` script: `"build": "tsc && vite build"`

### 3.2 Deploy frontend to Vercel
```bash
cd frontend
vercel --prod
```

> If using a monorepo, link both projects separately in Vercel, or use a root-level `vercel.json` that delegates to each.

---

## Step 4 — Environment Variables

### 4.1 Backend env vars (set in Vercel project → Settings → Environment Variables)

| Variable | Value | Notes |
|----------|-------|-------|
| `ENVIRONMENT` | `production` | Disables dev-login bypass |
| `DEV_AUTH_BYPASS` | `false` | |
| `DATABASE_URL` | `postgresql+psycopg2://postgres:...@db.REF.supabase.co:5432/postgres` | From Supabase |
| `LINE_CLIENT_ID` | `1234567890` | From LINE Developers channel |
| `LINE_CLIENT_SECRET` | `...` | From LINE Developers channel |
| `LINE_REDIRECT_URI` | `https://your-domain.com/login/callback` | |
| `TELEGRAM_BOT_TOKEN` | `123456:ABC-DEF...` | From @BotFather |
| `TELEGRAM_CHAT_ID` | `-1001234567890` | Your admin Telegram group ID |
| `TELEGRAM_WEBHOOK_SECRET` | `choose-a-strong-secret` | |
| `JWT_SECRET` | `generate-a-strong-random-string` | `openssl rand -hex 32` |
| `FRONTEND_URL` | `https://your-domain.com` | CORS allow-origin |

### 4.2 Frontend env vars (set in Vercel project → Settings → Environment Variables)

| Variable | Value | Notes |
|----------|-------|-------|
| `VITE_API_URL` | `https://your-backend.vercel.app` | Backend production URL |
| `VITE_LINE_CLIENT_ID` | `1234567890` | Same as backend LINE_CLIENT_ID |
| `VITE_LINE_REDIRECT_URI` | `https://your-domain.com/login/callback` | |

---

## Step 5 — External Services Configuration

### 5.1 LINE Login channel
1. Go to [LINE Developers Console](https://developers.line.biz/console/)
2. Open your production channel → **Channel settings**
3. Set **Callback URL** to: `https://your-backend.vercel.app/auth/line/callback`
4. (Optional) Set **LIFF** if using LIFF — not used here

### 5.2 Telegram bot webhook
After backend is deployed, set the webhook:
```bash
curl -X POST "https://api.telegram.org/bot<TELEGRAM_BOT_TOKEN>/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://your-backend.vercel.app/webhook/telegram",
    "secret_token": "your-telegram-webhook-secret"
  }'
```

Verify:
```bash
curl "https://api.telegram.org/bot<TELEGRAM_BOT_TOKEN>/getWebhookInfo"
```

### 5.3 Custom domain (optional)
1. In Vercel dashboard → your project → **Domains**
2. Add your domain (`preorder.example.com`)
3. Configure DNS as instructed (CNAME to `cname.vercel-dns.com`)
4. Repeat for both frontend and backend projects (or use one domain with rewrites)

---

## Step 6 — Verification Checklist

- [ ] `https://your-backend.vercel.app/health` returns `{"data":{"status":"ok"},"error":null,"message":"healthy"}`
- [ ] `https://your-backend.vercel.app/auth/dev-login` returns **404** (disabled in production)
- [ ] Frontend loads and shows login page (LINE button)
- [ ] LINE login flow completes successfully (redirect → callback → JWT stored)
- [ ] `/rounds/current` returns the current open round
- [ ] Menu loads after selecting a round
- [ ] Order submission (POST /orders) succeeds
- [ ] Telegram bot responds to `/status` in the admin group
- [ ] Telegram webhook responds (check `getWebhookInfo`)

---

## How to Change Configuration

### Vercel (recommended for prod)
1. Go to [vercel.com](https://vercel.com) → your project → **Settings** → **Environment Variables**
2. Add/update variables → click **Save**
3. **Redeploy** the project (new deployment picks up new env vars)

### Vercel CLI
```bash
vercel env add VARIABLE_NAME production
vercel deploy --prod
```

### Local `.env` files (dev only)
Edit `backend/.env` or `frontend/.env` — these are **not** used in production (Vercel ignores local .env).

---

## Appendix: Files Created/Modified for Production

| File | Purpose |
|------|---------|
| `backend/api/index.py` | Vercel Python serverless entry point |
| `backend/vercel.json` | Vercel build/routing config for backend |
| `backend/.vercel/` | Vercel project link (auto-generated) |
| `frontend/.vercel/` | Vercel project link (auto-generated) |

No changes needed to existing `backend/.env` or `frontend/.env` — they remain for local dev only.
