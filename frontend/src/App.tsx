import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Activity, ArrowDownLeft, ArrowRight, Bell, Check, ChevronLeft, ChevronRight, CircleHelp, ClipboardList, Clock3, FileText, Globe2, LayoutDashboard, MessageSquare, Search, Send, ShieldCheck, Smartphone, TriangleAlert, Users, Zap } from 'lucide-react';
import { mock } from './mock';
import type { Escalation, Message } from './types';

const label = (s: string) => s.toLowerCase().replaceAll('_', ' ').replace(/^./, c => c.toUpperCase());
const languages: Record<string, string> = { en: 'English', es: 'Español', vi: 'Tiếng Việt', zh: '中文', tl: 'Tagalog' };
const time = (value: string) => new Date(value).toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', timeZone: 'America/Los_Angeles' });
function Pill({ value }: { value: string }) { return <span className={`pill ${value.toLowerCase()}`}><span aria-hidden="true">{value === 'reported_safe' || value === 'RESOLVED' ? '✓' : value === 'CRITICAL' || value === 'escalated' ? '!' : '•'}</span>{label(value)}</span>; }

function Evidence({ message }: { message: Message }) {
  const quotes = message.triage?.evidence_quotes ?? [];
  const parts: React.ReactNode[] = []; let offset = 0;
  const matches = quotes.map(q => ({ q, i: message.text.indexOf(q) })).filter(x => x.i >= 0).sort((a, b) => a.i - b.i);
  for (const { q, i } of matches) { if (i < offset) continue; parts.push(message.text.slice(offset, i), <mark key={i}>{q}</mark>); offset = i + q.length; }
  parts.push(message.text.slice(offset));
  return <>{parts}</>;
}

function CaseCard({ item }: { item: Escalation }) {
  const client = useQueryClient(); const [notes, setNotes] = useState('');
  const mutation = useMutation({ mutationFn: (action: 'assign' | 'acknowledge' | 'resolve') => mock.caseAction(item.case_id, action, item.version, notes), onSuccess: () => client.invalidateQueries() });
  return <article className={`case-card ${item.state === 'RESOLVED' ? 'closed' : ''}`}>
    <div className="split"><span className="eyebrow">{item.case_id} · {item.patient_id}</span><Pill value={item.state}/></div>
    <h3><TriangleAlert size={17}/> Breathing difficulty reported</h3>
    <p>{item.reason.replace('Fixture: ', '')}</p>
    <div className="case-meta"><Clock3 size={14}/>{time(item.created_at)} PT <span>·</span> {item.assigned_to ? `Assigned to ${label(item.assigned_to)}` : 'Unassigned'}</div>
    {item.state !== 'RESOLVED' && <div className="case-actions">
      {!item.assigned_to && <button className="secondary small" disabled={mutation.isPending} onClick={() => mutation.mutate('assign')}>Assign to me</button>}
      {item.state === 'OPEN' && <button className="primary small" disabled={mutation.isPending} onClick={() => mutation.mutate('acknowledge')}>Acknowledge</button>}
      {item.state === 'ACKNOWLEDGED' && <><label className="notes-label">Resolution notes<textarea value={notes} onChange={e => setNotes(e.target.value)} placeholder="Document the synthetic handoff…" maxLength={4000}/></label><button className="primary small" disabled={!notes.trim() || mutation.isPending} onClick={() => mutation.mutate('resolve')}>Resolve mock case</button></>}
    </div>}
    {item.notes && <p className="resolution"><Check size={15}/>{item.notes}</p>}
    {mutation.error && <p role="alert" className="error">{mutation.error.message}</p>}
  </article>;
}

export default function App() {
  const client = useQueryClient();
  const [tab, setTab] = useState('board'); const [selected, setSelected] = useState('P-0001');
  const [search, setSearch] = useState(''); const [tier, setTier] = useState('all'); const [page, setPage] = useState(0);
  const [phone, setPhone] = useState(false); const [reply, setReply] = useState(''); const [notice, setNotice] = useState(false);
  const [sourceId, setSourceId] = useState(() => crypto.randomUUID()); const [lastReply, setLastReply] = useState<Parameters<typeof mock.inbound>[0] | null>(null);
  const [feedback, setFeedback] = useState('');
  const board = useQuery({ queryKey: ['board'], queryFn: mock.board });
  const thread = useQuery({ queryKey: ['thread', selected], queryFn: () => mock.thread(selected) });
  const cases = useQuery({ queryKey: ['cases'], queryFn: mock.cases });
  const audit = useQuery({ queryKey: ['audit'], queryFn: mock.audit });
  const jobs = useQuery({ queryKey: ['jobs'], queryFn: mock.jobs });
  const submit = useMutation({ mutationFn: mock.inbound, onSuccess: result => { setFeedback(result.duplicate ? 'Duplicate recognized · original mock job retained' : 'Mock reply retained · human review required · no AI call'); setReply(''); setSourceId(crypto.randomUUID()); void client.invalidateQueries(); } });
  const active = cases.data?.filter(c => c.state !== 'RESOLVED') ?? [];
  const rows = board.data?.patients.items.filter(r => (tier === 'all' || r.tier === tier) && `${r.patient.display_name} ${r.patient.patient_id} ${r.patient.language}`.toLowerCase().includes(search.toLowerCase())) ?? [];
  const visible = rows.slice(page * 7, page * 7 + 7);
  const choosePatient = (id: string) => { setSelected(id); setReply(''); setFeedback(''); setLastReply(null); setSourceId(crypto.randomUUID()); submit.reset(); };
  const send = () => { if (!thread.data) return; const input = { event_id: 'E-001', patient_id: selected, source_message_id: sourceId, text: reply, language: thread.data.patient.language }; setLastReply(input); submit.mutate(input); };

  return <div className="app-shell">
    <aside className="sidebar">
      <a className="brand" href="/" aria-label="Tether home"><img src="/tether.svg" alt=""/><span>tether<span className="brand-dot">.</span></span></a>
      <div className="workspace"><span className="workspace-icon"><Users size={18}/></span><div><strong>Northstar Care</strong><span>Synthetic agency A</span></div></div>
      <p className="nav-label">COORDINATION</p>
      <nav aria-label="Main navigation">
        <button className={tab === 'board' ? 'active' : ''} onClick={() => setTab('board')}><LayoutDashboard size={18}/>Outreach desk</button>
        <button className={tab === 'audit' ? 'active' : ''} onClick={() => setTab('audit')}><ClipboardList size={18}/>Activity log</button>
        <button className={tab === 'ops' ? 'active' : ''} onClick={() => setTab('ops')}><Activity size={18}/>Operations</button>
      </nav>
      <div className="sidebar-note"><ShieldCheck size={21}/><strong>People stay in the loop.</strong><p>Only a coordinator can acknowledge and resolve a case in the live design.</p><span>Stage A · UI preview</span></div>
      <div className="profile"><span className="avatar">DC</span><div><strong>Dana Carter</strong><span>Coordinator persona</span></div></div>
    </aside>
    <div className="main-shell">
      <header className="topbar"><div><span className="status-dot"/> Synthetic workspace <span className="topbar-divider">/</span> us-east-1</div><div className="topbar-right"><span className="mock-badge">MOCK MODE</span><span className="date">Oct 23, 2026 · Pacific</span><Bell size={18}/></div></header>
      <main>
        <div className="page-heading"><div><p className="eyebrow">A LITTLE CONNECTION. A CLEAR NEXT STEP.</p><h1>{tab === 'board' ? 'Keep every patient in view.' : tab === 'audit' ? 'A record of every step.' : 'See what is actually running.'}</h1><p>{tab === 'board' ? 'Coordinate outage outreach, understand replies, and get people to a human.' : 'Transparent evidence, with simulated and live behavior clearly separated.'}</p></div><div className="shift"><span className="status-dot"/><span>Evening desk<br/><strong>Dana’s workspace</strong></span></div></div>
        <div className="demo-banner"><CircleHelp size={16}/><span><strong>SYNTHETIC DEMO DATA</strong> · Browser preview only. No live Bedrock, SMS, email, or AWS storage. Refresh resets this session.</span></div>
        {board.isLoading && <div role="status" className="panel empty">Loading the synthetic board…</div>}
        {board.error && <div role="alert" className="panel error">{board.error.message}<button onClick={() => void board.refetch()}>Retry</button></div>}
        {tab === 'board' && board.data && <>
          <section className="event-banner">
            <div className="event-icon"><Zap size={25}/></div><div className="event-main"><div className="inline"><span className="eyebrow">OUTAGE NOTICE · E-001</span><Pill value="needs_confirmation"/></div><h2>East San Jose power shutoff</h2><p>Bay Valley Electric <span className="muted">(fictional)</span> · Starts Oct 23, 8:00 PM PT</p><div className="event-tags"><span>ZIP matching · approximate geography</span><span><Clock3 size={13}/> Restoration unknown</span></div></div>
            <button className="secondary" aria-expanded={notice} onClick={() => setNotice(!notice)}><FileText size={16}/>{notice ? 'Hide notice' : 'Review uncertainty'}<ArrowRight size={15}/></button>
          </section>
          {notice && <section className="notice-panel"><h3>Confirmation is required before outreach</h3><p>“East San Jose and foothill communities may lose power Friday evening. Restoration time is not yet known.”</p><p><strong>Unconfirmed:</strong> foothill communities and restoration time. The preview uses authored fixture data. Live notice extraction and confirmation arrive in Stage C.</p><button className="secondary small" disabled>Analyze notice · Stage C</button></section>}
          <div className="stats-grid">
            <div className="stat"><span><Users size={17}/>Matched patients</span><strong>{board.data.total_affected}<small>of 60 synthetic profiles</small></strong><p>Confirmed ZIPs · agency A</p></div>
            <div className="stat"><span><Clock3 size={17}/>Awaiting reply</span><strong>{board.data.counts.awaiting_reply}<small>follow-up needed</small></strong><p>Seeded preview statuses</p></div>
            <div className="stat attention"><span><TriangleAlert size={17}/>Active cases</span><strong>{active.length}<small>{active.filter(c => c.state === 'OPEN').length} unacknowledged</small></strong><p>Human action required</p></div>
            <div className="stat"><span><MessageSquare size={17}/>Human review</span><strong>{board.data.counts.human_review}<small>clarification needed</small></strong><p>Unknowns remain visible</p></div>
          </div>
          <div className="work-grid">
            <div className="left-column">
              <section className="panel patient-panel"><div className="panel-title"><div><h2>Patient outreach</h2><p>Priority order from the synthetic fixture</p></div><span className="count-tag">{board.data.total_affected} people</span></div>
                <div className="filters"><label className="search"><Search size={17}/><input aria-label="Search patients" placeholder="Search name or patient ID…" value={search} onChange={e => { setSearch(e.target.value); setPage(0); }}/></label><select aria-label="Filter by priority" value={tier} onChange={e => { setTier(e.target.value); setPage(0); }}><option value="all">All priorities</option><option value="CRITICAL">Critical</option><option value="HIGH">High</option><option value="MEDIUM">Medium</option></select></div>
                <div className="table-scroll"><table><thead><tr><th>Priority</th><th>Patient</th><th>Backup</th><th>Outreach status</th><th><span className="sr-only">Open</span></th></tr></thead><tbody>{visible.map(row => <tr className={selected === row.patient.patient_id ? 'selected-row' : ''} key={row.patient.patient_id}><td><Pill value={row.tier}/></td><td><button className="patient-link" onClick={() => choosePatient(row.patient.patient_id)}>{row.patient.display_name}</button><span className="table-sub">{languages[row.patient.language]} · {row.patient.devices[0]?.type.replaceAll('_', ' ')}</span></td><td><strong>{row.patient.devices[0]?.backup_hours == null ? 'Unknown' : `${row.patient.devices[0].backup_hours} hrs`}</strong><span className="table-sub">{row.patient.patient_id}</span></td><td><Pill value={row.status}/></td><td><button className="icon-button" aria-label={`Open ${row.patient.display_name}`} onClick={() => choosePatient(row.patient.patient_id)}><ChevronRight size={17}/></button></td></tr>)}</tbody></table>{!rows.length && <div className="empty">No patients match these filters.</div>}</div>
                <div className="pagination"><span>{rows.length ? page * 7 + 1 : 0}–{Math.min(page * 7 + 7, rows.length)} of {rows.length} patients</span><div><button className="icon-button" aria-label="Previous page" disabled={page === 0} onClick={() => setPage(p => p - 1)}><ChevronLeft size={17}/></button><span>Page {page + 1}</span><button className="icon-button" aria-label="Next page" disabled={(page + 1) * 7 >= rows.length} onClick={() => setPage(p => p + 1)}><ChevronRight size={17}/></button></div></div>
              </section>
              <section className="panel thread-panel"><div className="panel-title"><div><h2>{thread.data?.patient.display_name ?? 'Patient thread'}</h2><p>{selected} · Original messages and exact evidence</p></div><div className="segmented"><button className={!phone ? 'selected' : ''} onClick={() => setPhone(false)}><MessageSquare size={15}/>Thread</button><button className={phone ? 'selected' : ''} onClick={() => setPhone(true)}><Smartphone size={15}/>Simulator</button></div></div>
                {thread.isLoading && <p className="empty" role="status">Loading thread…</p>}
                {thread.error && <p className="error" role="alert">{thread.error.message}</p>}
                {thread.data && <div className={phone ? 'phone-wrap' : 'conversation'}>
                  {phone && <div className="phone-header"><span className="phone-notch"/><Smartphone size={18}/><strong>Simulated SMS</strong><span>{languages[thread.data.patient.language]} · no messages leave this browser</span></div>}
                  <div className="messages">{thread.data.messages.items.length === 0 && <div className="empty"><MessageSquare size={22}/><p>No messages yet. Open the simulator to try a reply.</p></div>}{thread.data.messages.items.map(m => <article className={`message ${m.direction}`} key={m.message_id}><div className="message-meta">{m.direction === 'in' ? 'Patient reply' : 'Care team'} <span>· {time(m.created_at)} PT · MOCK</span></div><p><Evidence message={m}/></p>{m.triage && <><p className="translation"><Globe2 size={14}/>{m.triage.english_translation}</p><div className="finding"><strong><ArrowDownLeft size={14}/> Authored triage fixture</strong><span>Emergency: {m.triage.emergency} · Device running: {m.triage.device_running === null ? 'unknown' : m.triage.device_running ? 'yes' : 'no'} · Backup: {m.triage.backup_hours_left ?? 'unknown'}</span><span>Fixture confidence {Math.round(m.triage.confidence * 100)}% · uncalibrated, no live model call</span></div></>}{!m.triage && m.direction === 'in' && <span className="review-note">Human review · no model interpretation</span>}</article>)}</div>
                  {phone && <form className="reply-form" onSubmit={e => { e.preventDefault(); send(); }}><label htmlFor="reply">Send a synthetic reply</label><textarea id="reply" value={reply} onChange={e => setReply(e.target.value)} placeholder="Type in the patient’s language…" maxLength={4000}/><div className="split"><span>{reply.length}/4000</span><button className="primary" disabled={!reply.trim() || submit.isPending}><Send size={15}/>Send mock reply</button></div><p className="form-note">No authentication or delivery is simulated. New replies go to human review.</p></form>}
                  {feedback && <p className="feedback" role="status"><Check size={16}/>{feedback}</p>}
                  {phone && lastReply && <button className="text-button replay" onClick={() => submit.mutate(lastReply)}>Replay same source ID</button>}
                  {submit.error && <p className="error" role="alert">{submit.error.message}</p>}
                </div>}
              </section>
            </div>
            <aside className="right-column"><section className="panel case-panel"><div className="panel-title"><div><h2>Escalation queue</h2><p>Patient state ≠ case state</p></div><span className="alert-count">{active.length}</span></div><div className="case-list">{cases.isLoading && <p role="status">Loading cases…</p>}{cases.error && <p role="alert" className="error">{cases.error.message}</p>}{cases.data?.map(c => <CaseCard key={c.case_id} item={c}/>)}{!active.length && <div className="empty"><Check size={22}/><p>No active mock cases.</p></div>}</div><div className="case-foot"><ShieldCheck size={16}/><span>Preview actions only. Email publication, acknowledgment and resolution are separate.</span></div></section>
              <section className="next-step"><span className="eyebrow">WORKING CHECKPOINT</span><h3>The foundation is local.</h3><p>Shared contracts and this preview are ready for team review. Live intake, Bedrock and notifications begin in Stage B.</p><div><span className="tiny-dot"/> AWS access pending</div><button className="text-button" onClick={() => setTab('ops')}>View implementation status<ArrowRight size={15}/></button></section>
            </aside>
          </div>
        </>}
        {tab === 'audit' && <section className="panel"><div className="panel-title"><div><h2>Activity log</h2><p>Current browser session · mock actions only</p></div><span className="count-tag">{audit.data?.length ?? 0} entries</span></div>{audit.error && <p className="error" role="alert">{audit.error.message}</p>}<div className="table-scroll"><table><thead><tr><th>Time (Pacific)</th><th>Actor</th><th>Action</th><th>Mode</th></tr></thead><tbody>{audit.data?.map(a => <tr key={a.audit_id}><td>{time(a.created_at)}</td><td>{a.actor}</td><td>{a.action}</td><td><span className="mock-badge">MOCK</span></td></tr>)}</tbody></table></div></section>}
        {tab === 'ops' && <><div className="ops-grid">{[['Local jobs', `${jobs.data?.length ?? 0}`, 'Observed browser records'], ['Model calls', '0', 'This adapter never invokes Bedrock'], ['Queue depth / DLQ', 'Unknown', 'CloudWatch is not connected'], ['Estimated AWS cost', 'Unknown', 'Model and service rates unconfigured']].map(([name, value, detail]) => <section className="panel ops-card" key={name}><span className="eyebrow">{name}</span><strong>{value}</strong><p>{detail}</p></section>)}</div><section className="panel"><div className="panel-title"><div><h2>Stage readiness</h2><p>Evidence is scoped to the local foundation.</p></div></div><div className="readiness">{[['A · Foundation', 'Local preview', 'Canonical schemas, generated types, mock interface, preflight and SAM baseline.'], ['B · First deployed flow', 'Blocked', 'Account/profile credentials, model, published Guardrail, identity provider and SNS confirmation are required.'], ['C–E · Product, recovery, evidence', 'Planned', 'Deployment, live authorization, durable workers, shared budgets and measured load/evaluation remain to be implemented.']].map(([name, status, detail]) => <div key={name}><strong>{name}</strong><span className="count-tag">{status}</span><p>{detail}</p></div>)}</div></section><section className="panel jobs-panel"><div className="panel-title"><div><h2>Mock job ledger</h2><p>Source: browser memory · current session; reset on refresh</p></div></div>{!jobs.data?.length ? <p className="empty">Send a simulator reply to create a mock job.</p> : jobs.data.map(j => <div className="job-row" key={j.envelope.job_id}><code>{j.envelope.job_id.slice(0, 8)}</code><Pill value={j.state}/><span>0 model attempts · {time(j.observed_at)} PT</span></div>)}</section></>}
        <footer><span><img src="/tether.svg" alt=""/> Tether · Built around the next human action.</span><span>SYNTHETIC DEMO DATA · Not for clinical use</span></footer>
      </main>
    </div>
  </div>;
}
