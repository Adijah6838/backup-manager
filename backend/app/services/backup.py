from datetime import datetime, timezone
JOBS = {}
BACKUPS = {}
NEXT_JOB = [1]
NEXT_BACKUP = [1]
VALID_TYPES = ["full", "incremental", "differential"]
VALID_SCHEDULES = ["daily", "weekly", "hourly"]
def create_job(db_name, backup_type="full", schedule="daily", retention_days=30):
    if backup_type not in VALID_TYPES:
        return {"error": f"Invalid backup_type '{backup_type}'. Must be {VALID_TYPES}"}
    if schedule not in VALID_SCHEDULES:
        return {"error": f"Invalid schedule '{schedule}'. Must be {VALID_SCHEDULES}"}
    if retention_days < 1 or retention_days > 365:
        return {"error": "Invalid retention_days. Must be 1-365"}
    jid = NEXT_JOB[0]; NEXT_JOB[0] += 1
    JOBS[jid] = {"id": jid, "db_name": db_name, "backup_type": backup_type, "schedule": schedule, "retention_days": retention_days, "status": "active"}
    return JOBS[jid]
def run_backup(job_id, simulate="success", size_mb=120):
    job = JOBS.get(job_id)
    if not job:
        return {"error": "job not found"}
    bid = NEXT_BACKUP[0]; NEXT_BACKUP[0] += 1
    now = datetime.now(timezone.utc).isoformat()
    if simulate == "fail":
        b = {"id": bid, "job_id": job_id, "db_name": job["db_name"], "type": job["backup_type"], "status": "failed", "size_mb": 0, "checksum": None, "created_at": now, "verified": False, "notification": "NOTIFICATION: Backup FAILED! Alert sent to DBA team."}
    elif simulate == "corrupt":
        b = {"id": bid, "job_id": job_id, "db_name": job["db_name"], "type": job["backup_type"], "status": "completed", "size_mb": size_mb, "checksum": "BAD-CHECKSUM", "created_at": now, "verified": False, "notification": ""}
    elif simulate == "incomplete":
        b = {"id": bid, "job_id": job_id, "db_name": job["db_name"], "type": job["backup_type"], "status": "completed", "size_mb": 0, "checksum": None, "created_at": now, "verified": False, "notification": ""}
    else:
        b = {"id": bid, "job_id": job_id, "db_name": job["db_name"], "type": job["backup_type"], "status": "completed", "size_mb": size_mb, "checksum": f"SHA256-{bid}ABC123", "created_at": now, "verified": False, "notification": ""}
    BACKUPS[bid] = b
    return b
def verify(backup_id):
    b = BACKUPS.get(backup_id)
    if not b:
        return {"error": "backup not found"}
    if b["status"] != "completed":
        return {"backup_id": backup_id, "verified": False, "reason": f"Status is '{b['status']}', not completed"}
    if not b["checksum"] or b["checksum"] == "BAD-CHECKSUM":
        b["verified"] = False
        return {"backup_id": backup_id, "verified": False, "reason": "Invalid or missing checksum - CORRUPT"}
    if not b["size_mb"] or b["size_mb"] <= 0:
        b["verified"] = False
        return {"backup_id": backup_id, "verified": False, "reason": "Size is 0 - INCOMPLETE backup"}
    b["verified"] = True
    return {"backup_id": backup_id, "verified": True, "reason": "Checksum OK, size OK - backup is valid"}
def restore(backup_id, target_db=None):
    b = BACKUPS.get(backup_id)
    if not b:
        return {"error": "backup not found"}
    v = verify(backup_id)
    if not v["verified"]:
        return {"backup_id": backup_id, "restored": False, "reason": f"Cannot restore unverified backup: {v['reason']}"}
    return {"backup_id": backup_id, "restored": True, "target_db": target_db or f"{b['db_name']}_restored", "reason": "Restore simulation successful - no real DB touched"}
def apply_retention():
    # Simulated: mark backups older than retention as expired - for demo, expire all with retention_days=1 and id even
    expired = []
    for b in BACKUPS.values():
        job = JOBS.get(b["job_id"])
        if job and job["retention_days"] <= 1:
            if b["status"] == "completed":
                b["status"] = "expired"; expired.append(b["id"])
    return {"expired": expired, "count": len(expired)}
def dashboard():
    total = len(BACKUPS)
    completed = sum(1 for b in BACKUPS.values() if b["status"] == "completed")
    failed = sum(1 for b in BACKUPS.values() if b["status"] == "failed")
    verified = sum(1 for b in BACKUPS.values() if b["verified"])
    return {"total_jobs": len(JOBS), "total_backups": total, "completed": completed, "failed": failed, "verified": verified, "expired": sum(1 for b in BACKUPS.values() if b["status"] == "expired"), "success_rate": round(completed / max(total, 1) * 100, 1)}