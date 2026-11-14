# Deployment: Render + Supabase

| Environment | Branch | Render service | Supabase project |
|---|---|---|---|
| Staging | develop | brainmint-api-staging | brainmint-staging |
| Production | main | brainmint-api | brainmint-prod |

## One-time setup
1. Supabase: create the staging and production projects. Use the pooler connection string as DATABASE_URL (not the direct connection).
2. Render: New -> Blueprint, point it at this repo. It reads render.yaml.
3. Fill in every `sync: false` variable in the Render dashboard. SECRET_KEY is generated automatically.
4. Add the custom domain in Render and the DNS records. HTTPS is automatic.
5. Add the email provider's SPF/DKIM records to DNS.
6. Create the first admin from the Render shell (Ashutosh's script).
7. Enable Supabase backups on production and test a restore.

## Deploys
Merge to develop deploys staging; merge to main deploys production. Render runs `alembic upgrade head` before each deploy, then waits for /health to return 200.

## Rollback
Render dashboard -> service -> Events -> Rollback. If the bad deploy included a migration, run `alembic downgrade -1` first.

## Notes
- Pre-deploy command and always-on instances need a paid Render plan.
- The rate limiter is in memory, so run one instance per service.