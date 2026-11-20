# Database Backup and Recovery Management Tool
Simulated backup manager. Configure jobs, run backups, verify, restore simulation, retention, history, failure notifications, recovery reports, monitoring.
## Safety
Simulated - no real DB files touched.
## Run Backend (Terminal 1)
cd backend; uvicorn app.main:app --port 8010 --reload
## Run Frontend (Terminal 2)
cd frontend; npm run dev
# http://localhost:5173/
## Test
cd backend; python -m pytest tests -v
## Endpoints
- POST /api/jobs {db_name, backup_type, schedule, retention_days}
- GET /api/jobs
- POST /api/backups/run {job_id, simulate, size_mb}
- GET /api/backups?status=
- POST /api/backups/{id}/verify
- POST /api/restore {backup_id, target_db}
- POST /api/retention/apply
- GET /api/dashboard
- GET /api/recovery-report
## Rules
- backup_type: full, incremental, differential
- schedule: daily, weekly, hourly
- retention_days: 1-365
- Verify fails if: not completed, bad/missing checksum, size 0
- Restore blocked if unverified
## Scenarios
- success: valid backup, verify passes, restore works
- fail: backup failed + notification
- corrupt: BAD-CHECKSUM, verify fails
- incomplete: size 0, verify fails