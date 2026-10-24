# API Contract

Base URL: `/api/v1`. Interactive docs at `/docs` (disabled in production).

## Response envelope
Success:
{ "success": true, "data": { }, "message": "optional" }

Error:
{ "success": false, "error": { "code": "VALIDATION_ERROR", "message": "...", "details": [ { "field": "email", "message": "..." } ] } }

| HTTP | error.code | When |
|---|---|---|
| 400 | BAD_REQUEST | Malformed request |
| 401 | UNAUTHORIZED | Missing/invalid admin token |
| 403 | FORBIDDEN | Not allowed |
| 404 | NOT_FOUND | Unknown route or record (SCR-018) |
| 409 | CONFLICT | Duplicate resource |
| 422 | VALIDATION_ERROR | Field-level validation (details lists fields) |
| 429 | RATE_LIMITED | Too many requests |
| 500 | INTERNAL_ERROR | Unexpected server error |

## Endpoints
| Method | Path | Auth | Owner | Purpose |
|---|---|---|---|---|
| GET | /health | none | Farjan | Health check |
| GET | /services, /services/{slug} | none | Krishna | Services |
| GET | /content/... | none | Krishna | About, FAQ, footer, legal |
| POST | /enquiries | none | Guna | Service enquiry form |
| POST | /contact | none | Guna | Contact Us form |
| POST | /admin/auth/login | none | Ashutosh | Admin login |
| * | /admin/enquiries... | admin | Guna | Enquiry management |
| * | /admin/content... | admin | Krishna | Content management |

Exact schemas: see /docs (generated from the code).