import source from '../../data/mock.json';
import type { Accepted, Audit, Board, Escalation, Inbound, Job, Message, Thread } from './types';

// This adapter is browser memory only. It never calls AWS or promises durability/authentication.
const fixture = source as { board: Board; thread: Thread };
const clone = <T,>(value: T): T => structuredClone(value);
export function createMockAdapter() {
  const board = clone(fixture.board);
  const threads = new Map<string, Thread>([[fixture.thread.patient.patient_id, clone(fixture.thread)]]);
  const submissions = new Map<string, { payload: string; accepted: Accepted }>();
  const jobs = new Map<string, Job>();
  const audit: Audit[] = [{ audit_id: 'audit-fixture', event_id: 'E-001', actor: 'mock:fixture', action: 'Loaded synthetic preview', resource_id: 'E-001', created_at: board.patients.observed_at, correlation_id: 'fixture', mode: 'MOCK' }];
  const now = () => new Date().toISOString();
  const record = (action: string, resource_id: string) => audit.unshift({ audit_id: crypto.randomUUID(), event_id: 'E-001', actor: 'mock:dana', action, resource_id, created_at: now(), correlation_id: crypto.randomUUID(), mode: 'MOCK' });
  const getThread = (id: string): Thread => {
    const patient = board.patients.items.find(row => row.patient.patient_id === id)?.patient;
    if (!patient) throw new Error('Patient not found in this synthetic agency.');
    if (!threads.has(id)) threads.set(id, { patient, messages: { items: [], next_cursor: null, observed_at: now() }, cases: [] });
    return threads.get(id)!;
  };
  return {
    board: async () => clone(board),
    thread: async (id: string) => clone(getThread(id)),
    cases: async () => clone([...threads.values()].flatMap(t => t.cases)),
    audit: async () => clone(audit),
    jobs: async () => clone([...jobs.values()]),
    async inbound(input: Inbound): Promise<Accepted> {
      const thread = getThread(input.patient_id);
      if (input.event_id !== board.event.event_id) throw new Error('Event not found.');
      if (!input.text.trim() || input.text.length > 4000) throw new Error('Enter a reply of 1–4,000 characters.');
      const key = `${input.event_id}:${input.patient_id}:${input.source_message_id}`;
      const payload = JSON.stringify([input.event_id, input.patient_id, input.text, input.language]);
      const existing = submissions.get(key);
      if (existing) {
        if (existing.payload !== payload) throw new Error('IDEMPOTENCY_CONFLICT: use a new source ID for a different message.');
        return { ...existing.accepted, state: jobs.get(existing.accepted.job_id)!.state, duplicate: true };
      }
      const id = crypto.randomUUID();
      const messageId = crypto.randomUUID();
      const created = now();
      const accepted: Accepted = { job_id: id, resource_id: messageId, state: 'ACCEPTED', status_url: `/jobs/${id}`, duplicate: false };
      const message: Message = { message_id: messageId, source_message_id: input.source_message_id, patient_id: input.patient_id, event_id: input.event_id, direction: 'in', text: input.text, language: input.language, created_at: created, sequence: thread.messages.items.length + 1, triage: null, processing_state: 'HUMAN_REVIEW', delivery: 'acknowledged', mode: 'MOCK' };
      thread.messages.items.push(message);
      thread.messages.observed_at = created;
      // All new mock replies remain unclassified. Only the initial fixture has authored triage.
      const row = board.patients.items.find(row => row.patient.patient_id === input.patient_id)!;
      const previous = row.status;
      if (!thread.cases.some(c => c.state !== 'RESOLVED')) row.status = 'human_review';
      if (previous !== row.status) { board.counts[previous] -= 1; board.counts[row.status] = (board.counts[row.status] ?? 0) + 1; }
      jobs.set(id, { envelope: { schema_version: 1, job_id: id, kind: 'triage', tenant_id: 'agency-a', event_id: input.event_id, event_version: 1, patient_id: input.patient_id, source_message_id: input.source_message_id, created_at: created, deadline_at: new Date(Date.now() + 300000).toISOString(), correlation_id: id, payload_ref: `records://agency-a/${messageId}` }, state: 'HUMAN_REVIEW', version: 1, attempts: 0, result_urls: [], error_code: 'MOCK_NO_MODEL', observed_at: created, mode: 'MOCK' });
      submissions.set(key, { payload, accepted });
      record('Mock reply retained for human review', messageId);
      return clone(accepted);
    },
    async caseAction(id: string, action: 'assign' | 'acknowledge' | 'resolve', version: number, notes = ''): Promise<Escalation> {
      const item = [...threads.values()].flatMap(t => t.cases).find(c => c.case_id === id);
      if (!item) throw new Error('Case not found.');
      if (version !== item.version) throw new Error('VERSION_CONFLICT: refresh this case before trying again.');
      if (item.state === 'RESOLVED') throw new Error('This case is already resolved.');
      if (action === 'assign') item.assigned_to = 'dana';
      if (action === 'acknowledge') {
        if (item.state !== 'OPEN') throw new Error('This case is already acknowledged.');
        item.state = 'ACKNOWLEDGED'; item.acknowledged_at = now();
      }
      if (action === 'resolve') {
        if (item.state !== 'ACKNOWLEDGED') throw new Error('Acknowledge the case before resolving.');
        if (!notes.trim()) throw new Error('Add resolution notes.');
        item.state = 'RESOLVED'; item.resolved_at = now(); item.resolved_by = 'dana'; item.notes = notes.trim();
      }
      item.version += 1;
      record(`Mock case ${action}`, id);
      return clone(item);
    },
  };
}
export const mock = createMockAdapter();
