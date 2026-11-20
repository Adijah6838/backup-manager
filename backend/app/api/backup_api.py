from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from ..services.backup import JOBS, BACKUPS, create_job, run_backup, verify, restore, apply_retention, dashboard
router = APIRouter()
class JobIn(BaseModel):
    db_name: str
    backup_type: str = "full"
    schedule: str = "daily"
    retention_days: int = 30
class RunIn(BaseModel):
    job_id: int
    simulate: str = "success"
    size_mb: int = 120
class RestoreIn(BaseModel):
    backup_id: int
    target_db: Optional[str] = None
@router.post("/jobs")
def add_job(body: JobIn):
    return create_job(body.db_name, body.backup_type, body.schedule, body.retention_days)
@router.get("/jobs")
def list_jobs():
    return {"total": len(JOBS), "jobs": list(JOBS.values())}
@router.post("/backups/run")
def run(body: RunIn):
    return run_backup(body.job_id, body.simulate, body.size_mb)
@router.get("/backups")
def list_backups(status: str = ""):
    items = list(BACKUPS.values())
    if status:
        items = [b for b in items if b["status"] == status]
    return {"total": len(items), "backups": items}
@router.get("/backups/{bid}")
def get_backup(bid: int):
    return BACKUPS.get(bid, {"error": "not found"})
@router.post("/backups/{bid}/verify")
def do_verify(bid: int):
    return verify(bid)
@router.post("/restore")
def do_restore(body: RestoreIn):
    return restore(body.backup_id, body.target_db)
@router.post("/retention/apply")
def retention():
    return apply_retention()
@router.get("/dashboard")
def dash():
    return dashboard()
@router.get("/recovery-report")
def report():
    d = dashboard()
    return {**d, "message": f"Recovery Report: {d['verified']} verified backups available for restore out of {d['total_backups']} total. Failed: {d['failed']}."}