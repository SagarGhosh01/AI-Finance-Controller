import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Integer, DateTime, Text, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.core.db import Base

class Run(Base):
    __tablename__ = "runs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    status = Column(String, default="pending")  # pending, running, completed, failed
    source_a_name = Column(String, default="Internal Ledger")
    source_b_name = Column(String, default="Bank Feed")
    total_records = Column(Integer, default=0)
    matched_count = Column(Integer, default=0)
    exception_count = Column(Integer, default=0)
    match_rate_pct = Column(Float, default=0.0)
    processing_time_ms = Column(Integer, default=0)
    llm_calls_made = Column(Integer, default=0)
    llm_tokens_used = Column(Integer, default=0)
    approved_by = Column(String, nullable=True)
    approved_at = Column(DateTime, nullable=True)

    records = relationship("Record", back_populates="run", cascade="all, delete-orphan")
    matches = relationship("Match", back_populates="run", cascade="all, delete-orphan")
    exceptions = relationship("ExceptionModel", back_populates="run", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="run", cascade="all, delete-orphan")

class Record(Base):
    __tablename__ = "records"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id = Column(String, ForeignKey("runs.id"), nullable=False)
    record_id = Column(String, nullable=False)  # original source record_id e.g. LED-TXN-1001
    source = Column(String, nullable=False)  # 'A' or 'B'
    reference_id = Column(String, nullable=True)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    transaction_date = Column(String, nullable=False)
    counterparty = Column(String, nullable=True)
    description = Column(String, nullable=True)
    raw_data = Column(JSON, nullable=True)
    status = Column(String, default="pending")  # pending, matched, exception

    run = relationship("Run", back_populates="records")

class Match(Base):
    __tablename__ = "matches"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id = Column(String, ForeignKey("runs.id"), nullable=False)
    record_ids = Column(JSON, nullable=False)  # List of record.id UUIDs involved
    record_codes = Column(JSON, nullable=True)  # List of human-readable record_ids e.g. ["LED-TXN-1001", "BNK-TXN-5001"]
    match_tier = Column(String, nullable=False)  # exact, tolerant, llm, split
    confidence = Column(Float, default=1.0)
    reasoning = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    run = relationship("Run", back_populates="matches")

class ExceptionModel(Base):
    __tablename__ = "exceptions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id = Column(String, ForeignKey("runs.id"), nullable=False)
    record_id = Column(String, ForeignKey("records.id"), nullable=False)
    record_code = Column(String, nullable=True)
    source = Column(String, nullable=False)  # 'A' or 'B'
    exception_type = Column(String, nullable=False)
    # UNMATCHED_LEDGER, UNMATCHED_BANK, AMOUNT_MISMATCH, DATE_MISMATCH, DUPLICATE_SUSPECTED, LOW_CONFIDENCE_MATCH, NEEDS_HUMAN_REVIEW
    candidate_record_id = Column(String, nullable=True)
    candidate_record_code = Column(String, nullable=True)
    confidence = Column(Float, nullable=True)
    reasoning = Column(Text, nullable=False)
    resolution_status = Column(String, default="open")  # open, accepted, rejected, manual, flagged
    resolved_by = Column(String, nullable=True)
    resolved_at = Column(DateTime, nullable=True)

    run = relationship("Run", back_populates="exceptions")
    record = relationship("Record", foreign_keys=[record_id])

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id = Column(String, ForeignKey("runs.id"), nullable=False)
    actor = Column(String, default="agent")  # agent or human
    action = Column(String, nullable=False)
    target_record_id = Column(String, nullable=True)
    details = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    run = relationship("Run", back_populates="audit_logs")
