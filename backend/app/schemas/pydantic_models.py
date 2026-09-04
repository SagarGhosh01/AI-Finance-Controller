from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
from datetime import datetime

class RecordSchema(BaseModel):
    id: str
    run_id: str
    record_id: str
    source: str
    reference_id: Optional[str] = None
    amount: float
    currency: str = "USD"
    transaction_date: str
    counterparty: Optional[str] = None
    description: Optional[str] = None
    status: str

    class Config:
        from_attributes = True

class MatchSchema(BaseModel):
    id: str
    run_id: str
    record_ids: List[str]
    record_codes: Optional[List[str]] = None
    match_tier: str
    confidence: float
    reasoning: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class ExceptionSchema(BaseModel):
    id: str
    run_id: str
    record_id: str
    record_code: Optional[str] = None
    source: str
    exception_type: str
    candidate_record_id: Optional[str] = None
    candidate_record_code: Optional[str] = None
    confidence: Optional[float] = None
    reasoning: str
    resolution_status: str
    resolved_by: Optional[str] = None
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ExceptionResolveRequest(BaseModel):
    action: str  # accept, reject, manual, flag
    target_candidate_id: Optional[str] = None
    notes: Optional[str] = None

class RunCreate(BaseModel):
    source_a_name: str = "Internal Ledger"
    source_b_name: str = "Bank Feed"
    use_synthetic: bool = True
    amount_tolerance: float = 0.50
    date_tolerance_days: int = 3
    fuzzy_threshold: float = 0.85

class RunResponse(BaseModel):
    id: str
    created_at: datetime
    status: str
    source_a_name: str
    source_b_name: str
    total_records: int
    matched_count: int
    exception_count: int
    match_rate_pct: float
    processing_time_ms: int
    llm_calls_made: int
    llm_tokens_used: int
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class AuditLogSchema(BaseModel):
    id: str
    run_id: str
    actor: str
    action: str
    target_record_id: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True

class CashPositionResponse(BaseModel):
    run_id: str
    total_matched_count: int
    confirmed_cash_position: float
    excluded_pending_exceptions_count: int
    currency: str = "USD"
    matched_summary: Dict[str, Any]

class RunReportResponse(BaseModel):
    run: RunResponse
    breakdown_by_tier: Dict[str, int]
    breakdown_by_exception_type: Dict[str, int]
    integrity_check_passed: bool
    integrity_check_message: str
