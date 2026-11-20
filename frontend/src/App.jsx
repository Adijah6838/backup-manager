import { useState, useEffect } from "react";
const API = "http://127.0.0.1:8010/api";
export default function App() {
  const [jobs, setJobs] = useState([]);
  const [backups, setBackups] = useState([]);
  const [dash, setDash] = useState(null);
  const [dbName, setDbName] = useState("shop_db");
  const [bType, setBType] = useState("full");
  const [schedule, setSchedule] = useState("daily");
  const [retention, setRetention] = useState(30);
  const [jobId, setJobId] = useState(1);
  const [simulate, setSimulate] = useState("success");
  const [result, setResult] = useState(null);
  const load = async () => { const j = await (await fetch(`${API}/jobs`)).json(); setJobs(j.jobs); const b = await (await fetch(`${API}/backups`)).json(); setBackups(b.backups); const d = await (await fetch(`${API}/dashboard`)).json(); setDash(d); };
  useEffect(() => { load(); }, []);
  const addJob = async () => { const r = await fetch(`${API}/jobs`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ db_name: dbName, backup_type: bType, schedule, retention_days: retention }) }); setResult(await r.json()); load(); };
  const runBackup = async () => { const r = await fetch(`${API}/backups/run`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ job_id: jobId, simulate, size_mb: 120 }) }); setResult(await r.json()); load(); };
  const verify = async (id) => { const r = await fetch(`${API}/backups/${id}/verify`, { method: "POST" }); setResult(await r.json()); load(); };
  const restore = async (id) => { const r = await fetch(`${API}/restore`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ backup_id: id }) }); setResult(await r.json()); load(); };
  const retentionApply = async () => { const r = await fetch(`${API}/retention/apply`, { method: "POST" }); setResult(await r.json()); load(); };
  const report = async () => { const r = await fetch(`${API}/recovery-report`); setResult(await r.json()); };
  return (<div style={{ maxWidth: 900, margin: "auto", padding: 20, fontFamily: "sans-serif" }}>
    <h1>💾 Backup & Recovery Manager</h1><p>Simulated - no real DB touched.</p>
    {dash && <div style={{ background: "#eef", padding: 12 }}><b>Dashboard:</b> Jobs {dash.total_jobs} | Backups {dash.total_backups} | Completed {dash.completed} | Failed {dash.failed} | Verified {dash.verified} | Expired {dash.expired} | Success {dash.success_rate}%</div>}
    <h3>Create Backup Job</h3><input value={dbName} onChange={e => setDbName(e.target.value)} placeholder="DB name" style={{ padding: 10 }} /><select value={bType} onChange={e => setBType(e.target.value)} style={{ padding: 10, marginLeft: 8 }}><option value="full">full</option><option value="incremental">incremental</option><option value="differential">differential</option></select><select value={schedule} onChange={e => setSchedule(e.target.value)} style={{ padding: 10, marginLeft: 8 }}><option value="daily">daily</option><option value="weekly">weekly</option><option value="hourly">hourly</option></select><input type="number" value={retention} onChange={e => setRetention(Number(e.target.value))} style={{ padding: 10, marginLeft: 8, width: 80 }} /><button onClick={addJob} style={{ padding: 10, marginLeft: 8 }}>Create Job</button>
    <h3>Run Backup</h3><select value={jobId} onChange={e => setJobId(Number(e.target.value))} style={{ padding: 10 }}>{jobs.map(j => <option key={j.id} value={j.id}>{j.id} - {j.db_name} ({j.backup_type}/{j.schedule}, retention {j.retention_days}d)</option>)}</select><select value={simulate} onChange={e => setSimulate(e.target.value)} style={{ padding: 10, marginLeft: 8 }}><option value="success">Success</option><option value="fail">Fail</option><option value="corrupt">Corrupt</option><option value="incomplete">Incomplete</option></select><button onClick={runBackup} style={{ padding: 10, marginLeft: 8 }}>Run Backup</button><button onClick={retentionApply} style={{ padding: 10, marginLeft: 8 }}>Apply Retention</button><button onClick={report} style={{ padding: 10, marginLeft: 8 }}>Recovery Report</button>
    {result && <pre style={{ background: result.error || result.verified === false || result.restored === false ? "#ffe6e6" : "#e6ffe6", padding: 12 }}>{JSON.stringify(result, null, 2)}</pre>}
    <h3>Backup History ({backups.length})</h3>{backups.slice().reverse().map(b => <div key={b.id} style={{ border: "1px solid #ddd", padding: 10, marginTop: 8, background: b.status === "completed" ? "#e6ffe6" : "#ffe6e6" }}><b>#{b.id} {b.db_name} {b.type}</b> | {b.status} | Size {b.size_mb} MB | Checksum {b.checksum || "none"} | Verified: {b.verified ? "✅" : "❌"}<br /><small>{b.created_at} | {b.notification}</small><br /><button onClick={() => verify(b.id)} style={{ marginTop: 6 }}>Verify</button><button onClick={() => restore(b.id)} style={{ marginLeft: 8, marginTop: 6 }}>Restore Simulation</button></div>)}
  </div>);
}