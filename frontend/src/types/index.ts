export interface Run {
  id: string;
  created_at: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  source_a_name: string;
  source_b_name: string;
  total_records: number;
  matched_count: number;
  exception_count: number;
  match_rate_pct: number;
  processing_time_ms: number;
  llm_calls_made: number;
  llm_tokens_used: number;
  approved_by?: string | null;
  approved_at?: string | null;
}

export interface RecordItem {
  id: string;
  run_id: string;
  record_id: string;
  source: 'A' | 'B';
  reference_id?: string;
  amount: number;
  currency: string;
  transaction_date: string;
  counterparty?: string;
  description?: string;
  status: 'pending' | 'matched' | 'exception';
}

export interface MatchItem {
  id: string;
  run_id: string;
  record_ids: string[];
  record_codes?: string[];
  match_tier: 'exact' | 'tolerant' | 'llm' | 'split' | 'human_resolved';
  confidence: number;
  reasoning?: string;
  created_at: string;
}

export interface ExceptionItem {
  id: string;
  run_id: string;
  record_id: string;
  record_code?: string;
  source: 'A' | 'B';
  exception_type:
    | 'UNMATCHED_LEDGER'
    | 'UNMATCHED_BANK'
    | 'AMOUNT_MISMATCH'
    | 'DATE_MISMATCH'
    | 'DUPLICATE_SUSPECTED'
    | 'LOW_CONFIDENCE_MATCH'
    | 'NEEDS_HUMAN_REVIEW';
  candidate_record_id?: string;
  candidate_record_code?: string;
  confidence?: number;
  reasoning: string;
  resolution_status: 'open' | 'accept' | 'reject' | 'manual' | 'flag';
  resolved_by?: string;
  resolved_at?: string;
}

export interface CashPosition {
  run_id: string;
  total_matched_count: number;
  confirmed_cash_position: number;
  excluded_pending_exceptions_count: number;
  currency: string;
  matched_summary: {
    ledger_matched_count: number;
    bank_matched_count: number;
    matches_count: number;
  };
}

export interface AuditLogItem {
  id: string;
  run_id: string;
  actor: 'agent' | 'human';
  action: string;
  target_record_id?: string;
  details?: any;
  created_at: string;
}

export interface RunReport {
  run: Run;
  breakdown_by_tier: Record<string, number>;
  breakdown_by_exception_type: Record<string, number>;
  integrity_check_passed: boolean;
  integrity_check_message: string;
}
