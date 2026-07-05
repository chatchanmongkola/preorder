# Preorder Preorder App — Copilot Agent Instructions

## Project Overview

A preorder preorder web application for Thai users aged 30-60.
Users login via LINE, browse menu, and place preorders per round.
Admin manages everything via Telegram bot.

## Tech Stack

- Frontend: React 18 + TypeScript + Vite + Tailwind CSS + shadcn/ui
- Backend: Python 3.11 + FastAPI + SQLAlchemy + Alembic
- Database: PostgreSQL (Supabase)
- Auth: LINE Login (LINE OA)
- Notifications: Telegram Bot API
- Deploy: Vercel (frontend) + Vercel Serverless (backend)

## Key Business Rules

1. Orders are grouped in "rounds" (รอบ) with open/close datetime
2. Each round has max 5-10 item types (not quantity, but SKU types)
3. When round closes → auto-send summary to Telegram group
4. Admin can open/close rounds via Telegram commands
5. Users can only order once per round (can edit before close)
6. LINE Login is mandatory - no guest checkout

## UX Principles

- Clean, minimal design — large fonts, high contrast
- Thai language primary, simple vocabulary
- Mobile-first (most users on phone)
- Max 3 taps to complete an order

## Code Standards

- TypeScript strict mode, no `any`
- Python: type hints everywhere, Pydantic v2 models
- All API responses in { data, error, message } format
- Thai comments for business logic
- English for technical comments
- Test files alongside source: `*.test.ts`, `test_*.py`

## Environment Variables

Frontend (.env):
VITE_API_URL, VITE_LINE_CLIENT_ID, VITE_LINE_REDIRECT_URI

Backend (.env):
DATABASE_URL, LINE_CLIENT_ID, LINE_CLIENT_SECRET,
LINE_REDIRECT_URI, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID,
JWT_SECRET, FRONTEND_URL

## Folder Conventions

- Frontend components: PascalCase
- Backend files: snake_case
- DB migrations: use Alembic, never edit schema directly
