from app.services.backup import create_job, run_backup, verify, restore
def test_valid_backup_verify():
    j = create_job("shop_db", "full", "daily", 30)
    b = run_backup(j["id"], "success", 120)
    v = verify(b["id"])
    assert v["verified"] is True
def test_failed_backup():
    j = create_job("fail_db", "full", "daily", 30)
    b = run_backup(j["id"], "fail")
    assert b["status"] == "failed" and "NOTIFICATION" in b["notification"]
def test_corrupt_detection():
    j = create_job("corrupt_db", "full", "daily", 30)
    b = run_backup(j["id"], "corrupt", 120)
    v = verify(b["id"])
    assert v["verified"] is False and "CORRUPT" in v["reason"]
def test_incomplete_detection():
    j = create_job("inc_db", "full", "daily", 30)
    b = run_backup(j["id"], "incomplete", 0)
    v = verify(b["id"])
    assert v["verified"] is False
def test_restore_blocked_unverified():
    j = create_job("rb_db", "full", "daily", 30)
    b = run_backup(j["id"], "corrupt", 120)
    r = restore(b["id"])
    assert r["restored"] is False