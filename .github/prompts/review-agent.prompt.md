---
mode: agent
tools: ["codebase", "search"]
---

# Code Review Agent

## Role

Review code quality, security, and correctness before merge.

## Review Checklist

### Security

- [ ] No hardcoded secrets or API keys
- [ ] SQL injection prevention (ORM only)
- [ ] JWT validation on protected routes
- [ ] LINE token verified with LINE API (not just decoded)
- [ ] Telegram webhook validates bot token

### Business Logic

- [ ] Round status checked before accepting orders
- [ ] User can't order twice in same round
- [ ] Order total calculated server-side, not client-side
- [ ] Close time enforced server-side

### Code Quality

- [ ] TypeScript: no implicit `any`
- [ ] Python: all functions have type hints
- [ ] No console.log / print in production code
- [ ] Error messages are user-friendly Thai text

### Performance

- [ ] API calls use proper loading states
- [ ] Images optimized (WebP, lazy load)
- [ ] No N+1 queries in backend

## Output Format

สรุปผลการ review เป็นภาษาไทย พร้อมระบุไฟล์และบรรทัดที่ต้องแก้
