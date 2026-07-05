# Preorder App — Implementation Tasks

Tracking checklist for the full build (Docker dev → features → Vercel prod).
Check items off as completed; recheck before moving to the next phase.

## Phase 0 — Dockerized Dev Environment
- [x] `backend/Dockerfile` (python:3.11-slim, uvicorn --reload)
- [x] `backend/requirements.txt`
- [x] `frontend/Dockerfile` (node:20-alpine, vite dev server)
- [x] `frontend/package.json` scaffold
- [x] root `docker-compose.yml` (db + backend + frontend)
- [x] `.dockerignore` for backend and frontend
- [x] `backend/.env.example`, `frontend/.env.example`
- [x] Verify: `docker compose up --build` starts all 3 containers; backend `/health` and frontend root both respond (db port remapped to host 5433 to avoid local Postgres conflict)

## Phase 1 — Database Schema & Migrations
- [x] Alembic init in `backend/migrations`
- [x] SQLAlchemy models: User, Round, MenuItem, Order (unique user_id+round_id), OrderItem
- [x] Initial Alembic migration generated
- [x] `backend/app/seed.py` (1 open round, 5 menu items, 2 test users, sample orders)
- [x] Verify: `alembic upgrade head` + seed script run cleanly inside container (confirmed via psql: 6 tables, 2 users, 1 open round, 5 menu items, 1 order)

## Phase 2 — Backend Core & Auth
- [x] `backend/app/core/config.py` (env settings incl. `ENVIRONMENT`)
- [x] `backend/app/core/security.py` (JWT create/verify, LINE token verify helper)
- [x] `POST /auth/line/callback`, `GET /auth/me`
- [x] Dev-only `POST /auth/dev-login` gated by `ENVIRONMENT != production`
- [x] Standard `{data, error, message}` response wrapper
- [x] Verify: dev-login issues JWT; `/auth/me` works; missing/invalid token → 401 (all confirmed via curl)

## Phase 3 — Rounds & Menu API
- [x] `round_service.py` status computation
- [x] `GET /rounds/current`, `GET /rounds/:id`, `GET /rounds/:id/summary`
- [x] `GET /menu?round_id=`
- [x] Verify: seeded round/menu returned correctly (curl-verified, summary totals match seed data)

## Phase 4 — Orders API
- [x] `POST /orders` (round-open check, duplicate-order check, server-side total calc)
- [x] `GET /orders/my`
- [x] `PATCH /orders/:id` (only while round open)
- [x] `DELETE /orders/:id`
- [x] Verify: pytest covers duplicate order + edit-after-close rejection (5/5 passing) + live curl smoke test against seed data

## Phase 5 — Telegram Bot Integration
- [x] `telegram_service.py` (send message, Thai summary formatting)
- [x] `POST /webhook/telegram` with secret validation
- [x] Commands: `/status /open /close /summary /addmenu /listorders`
- [x] Auto-summary sent on round close
- [x] Verify: command parsing unit-tested with mocked Telegram API call (7/7 passing); webhook rejects unauthenticated calls (curl-verified 401/200)

## Phase 6 — Frontend Implementation
- [x] Tailwind + shadcn/ui setup, Sarabun font, color tokens (tailwind.config.js, postcss.config.js, index.css; shadcn-style `Button`/`Card` primitives in `src/components/ui/`)
- [x] `frontend/src/api/` client + React Query hooks (`client.ts` axios instance w/ Bearer interceptor, `auth.ts`/`rounds.ts`/`menu.ts`/`orders.ts`, hooks in `src/hooks/`)
- [x] LINE login page + dev-mode bypass button (`import.meta.env.DEV`) — `src/pages/Login.tsx`, real LINE redirect wired but untested (LIFF skipped per user request)
- [x] Pages: Home, Login, Menu, Cart, OrderDetail, Summary (+ Orders list page), routed in `App.tsx` with `RequireAuth` guard + `AuthProvider`/`CartProvider`
- [x] Verify: `npm run build` (tsc + vite build) passes clean; live curl smoke test confirms API response shapes match frontend TS types exactly (Round/MenuItem/Order); CORS preflight confirmed allowing `localhost:5173` origin + Authorization header

## Phase 7 — Testing, Review & Task Tracking
- [x] Create this `TASKS.md` (first implementation step)
- [x] Backend tests: `test_auth.py` (10 tests), `test_rounds.py` (9 tests) — `test_orders.py` (5) and `test_telegram.py` (7) done in earlier phases. **31/31 passing.**
- [x] Frontend tests: `CartContext.test.tsx` (7 tests — incl. regression test for the setQuantity add-new-line bug), `client.test.ts` (4 tests for API error-message resolution). **11/11 passing.**
- [x] Ran `.github/prompts/review-agent.prompt.md` checklist: no hardcoded secrets (all via env/settings), ORM-only (no raw SQL), JWT validated on all protected routes, LINE token verified via LINE `/verify` API, Telegram webhook validates secret token, round status + duplicate-order + server-side total all enforced server-side, no `any` in frontend, no `console.log` in frontend code, only `print()` found in `backend/app/seed.py` (a one-off dev script, not request-path code) — acceptable.

## Bugs found & fixed during Phase 7 testing
- **Order submission silently failed with an unhelpful message.** Root cause: `apiClient` (axios) rejects with a generic `AxiosError` on any non-2xx response *before* the code ever reaches `res.data.error`, so the UI showed raw text like "Request failed with status code 409" instead of the backend's real Thai reason (e.g. "คุณสั่งออเดอร์ในรอบนี้ไปแล้ว"). Fixed with a response interceptor in `frontend/src/api/client.ts` (`resolveApiErrorMessage`) that unwraps the `{data,error,message}` envelope from the error response and rethrows a normal `Error` with the real message.
- **Users could never edit an existing order from the UI.** Business rule allows editing an order until the round closes, but `Cart.tsx` always called `createOrder` (POST), which the backend correctly rejects with 409 once an order already exists for that round — there was no path to PATCH it. Fixed: `Cart.tsx` now detects an existing order for the round (via `useMyOrders`) and calls `updateOrder` instead, with UI copy that reflects "editing" vs "creating"; `Menu.tsx` also pre-hydrates the cart from the existing order so the user doesn't start from an empty cart when revisiting.
- **`CartContext.setQuantity` could never add a new line.** It only accepted a menu item ID and used `.map()`, which is a no-op for IDs not already in `lines`. It happened to work before because call sites only ever called it on items already in the cart, but this silently broke the new cart-hydration-from-existing-order feature. Fixed by changing the signature to accept the full `MenuItem` (matching `addItem`) so it can both add and update; covered by a regression test in `CartContext.test.tsx`.

## Phase 8 — Migrate to Vercel Prod
- [ ] `vercel.json` for frontend + backend ASGI serverless entry
- [ ] Point `DATABASE_URL` to Supabase; run migrations there
- [ ] Set real LINE/Telegram/JWT env vars in Vercel; confirm `ENVIRONMENT=production` disables dev-login
- [ ] Update LINE redirect URI + Telegram webhook URL to prod domain
