import { Run, RecordItem, ExceptionItem, CashPosition, AuditLogItem, RunReport } from '../types';

const API_BASE = '/api';

export async function createRun(formData: FormData): Promise<Run> {
  const res = await fetch(`${API_BASE}/runs`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) throw new Error('Failed to create run');
  return res.json();
}

export async function listRuns(): Promise<Run[]> {
  const res = await fetch(`${API_BASE}/runs`);
  if (!res.ok) throw new Error('Failed to fetch runs');
  return res.json();
}

export async function getRun(runId: string): Promise<Run> {
  const res = await fetch(`${API_BASE}/runs/${runId}`);
  if (!res.ok) throw new Error('Failed to fetch run detail');
  return res.json();
}

export async function getRunProgress(runId: string): Promise<any> {
  const res = await fetch(`${API_BASE}/runs/${runId}/progress`);
  if (!res.ok) throw new Error('Failed to fetch progress');
  return res.json();
}

export async function getRunRecords(runId: string, status?: string): Promise<RecordItem[]> {
  const url = new URL(`${window.location.origin}${API_BASE}/runs/${runId}/records`);
  if (status) url.searchParams.append('status', status);
  const res = await fetch(url.toString());
  if (!res.ok) throw new Error('Failed to fetch records');
  return res.json();
}

export async function getRunExceptions(runId: string, exceptionType?: string): Promise<ExceptionItem[]> {
  const url = new URL(`${window.location.origin}${API_BASE}/runs/${runId}/exceptions`);
  if (exceptionType) url.searchParams.append('exception_type', exceptionType);
  const res = await fetch(url.toString());
  if (!res.ok) throw new Error('Failed to fetch exceptions');
  return res.json();
}

export async function resolveException(
  exceptionId: string,
  action: 'accept' | 'reject' | 'manual' | 'flag',
  notes?: string
): Promise<ExceptionItem> {
  const res = await fetch(`${API_BASE}/exceptions/${exceptionId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ action, notes }),
  });
  if (!res.ok) throw new Error('Failed to resolve exception');
  return res.json();
}

export async function getCashPosition(runId: string): Promise<CashPosition> {
  const res = await fetch(`${API_BASE}/runs/${runId}/cash-position`);
  if (!res.ok) throw new Error('Failed to fetch cash position');
  return res.json();
}

export async function getAuditLog(runId: string): Promise<AuditLogItem[]> {
  const res = await fetch(`${API_BASE}/runs/${runId}/audit-log`);
  if (!res.ok) throw new Error('Failed to fetch audit log');
  return res.json();
}

export async function getRunReport(runId: string): Promise<RunReport> {
  const res = await fetch(`${API_BASE}/runs/${runId}/report`);
  if (!res.ok) throw new Error('Failed to fetch run report');
  return res.json();
}

export async function approveClose(runId: string): Promise<Run> {
  const res = await fetch(`${API_BASE}/runs/${runId}/approve`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error('Failed to approve close');
  return res.json();
}

export async function generateSyntheticData(seed: number = 42): Promise<any> {
  const res = await fetch(`${API_BASE}/data/generate-synthetic?seed=${seed}`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error('Failed to generate synthetic data');
  return res.json();
}
