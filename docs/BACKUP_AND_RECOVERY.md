# Backup and recovery runbook — LocalHub

## Database backup
```bash
pg_dump --format=custom --file=localhub-$(date +%Y%m%d%H%M%S).dump "$DATABASE_URL"
```

## Restore
```bash
pg_restore --clean --if-exists --dbname="$DATABASE_URL" localhub-<timestamp>.dump
python manage.py migrate --check
```

## Verification after restore
1. Run `python manage.py check`.
2. Run `python manage.py reconcile_payments`.
3. Run the backend test suite against the restored database when possible.
4. Confirm outbox backlog and payment attempt counts.

## Notes
- Keep backups encrypted and outside the application host.
- Test restore in an isolated environment before production use.
- This runbook is a development baseline, not a completed operational drill.