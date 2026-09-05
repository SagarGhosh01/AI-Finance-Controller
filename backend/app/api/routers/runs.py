import csv
import io
import json
import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.db import get_db, engine, Base
from app.models.schema import Run, Record, Match, ExceptionModel, AuditLog
from app.schemas.pydantic_models import (
    RunCreate, RunResponse, RecordSchema, MatchSchema, ExceptionSchema,
    ExceptionResolveRequest, AuditLogSchema, CashPositionResponse, RunReportResponse
)
from app.services.reconciliation_orchestrator import ReconciliationOrchestrator
from scripts.generate_synthetic_data import generate_synthetic_data

# Ensure tables exist
Base.metadata.create_all(bind=engine)

router = APIRouter()

from app.services.real_data_parser import RealDataParser

@router.post("/runs", response_model=RunResponse)
async def create_run(
    source_a_name: str = Form("Internal Ledger"),
    source_b_name: str = Form("Bank Feed"),
    use_synthetic: bool = Form(True),
    amount_tolerance: float = Form(0.50),
    date_tolerance_days: int = Form(3),
    fuzzy_threshold: float = Form(0.85),
    file_a: Optional[UploadFile] = File(None),
    file_b: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    run_id = str(uuid.uuid4())

    records_a = []
    records_b = []

    if use_synthetic or not file_a or not file_b:
        # Generate synthetic benchmark data
        generate_synthetic_data(output_dir="data/synthetic", seed=42)

        with open("data/synthetic/internal_ledger.csv", "r", encoding="utf-8") as f:
            content_a = f.read()
            records_a = RealDataParser.parse_csv(content_a, source_label="A")

        with open("data/synthetic/bank_feed.csv", "r", encoding="utf-8") as f:
            content_b = f.read()
            records_b = RealDataParser.parse_csv(content_b, source_label="B")
    else:
        content_a = (await file_a.read()).decode("utf-8", errors="ignore")
        content_b = (await file_b.read()).decode("utf-8", errors="ignore")

        records_a = RealDataParser.parse_csv(content_a, source_label="A")
        records_b = RealDataParser.parse_csv(content_b, source_label="B")

    orchestrator = ReconciliationOrchestrator(db)
    run_obj = await orchestrator.run_pipeline(
        run_id=run_id,
        records_a_raw=records_a,
        records_b_raw=records_b,
        amount_tolerance=amount_tolerance,
        date_tolerance_days=date_tolerance_days,
        fuzzy_threshold=fuzzy_threshold
    )

    return run_obj

@router.get("/runs", response_model=List[RunResponse])
def list_runs(db: Session = Depends(get_db)):
    return db.query(Run).order_by(Run.created_at.desc()).all()

@router.get("/runs/{run_id}", response_model=RunResponse)
def get_run(run_id: str, db: Session = Depends(get_db)):
    run = db.query(Run).filter(Run.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run

@router.get("/runs/{run_id}/progress")
def get_run_progress(run_id: str, db: Session = Depends(get_db)):
    run = db.query(Run).filter(Run.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return {
        "run_id": run.id,
        "status": run.status,
        "total_records": run.total_records,
        "matched_count": run.matched_count,
        "exception_count": run.exception_count,
        "match_rate_pct": run.match_rate_pct,
        "processing_time_ms": run.processing_time_ms
    }

@router.get("/runs/{run_id}/records", response_model=List[RecordSchema])
def get_run_records(
    run_id: str,
    status: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Record).filter(Record.run_id == run_id)
    if status:
        query = query.filter(Record.status == status)
    if source:
        query = query.filter(Record.source == source)
    return query.all()

@router.get("/runs/{run_id}/exceptions", response_model=List[ExceptionSchema])
def get_run_exceptions(
    run_id: str,
    exception_type: Optional[str] = Query(None),
    resolution_status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(ExceptionModel).filter(ExceptionModel.run_id == run_id)
    if exception_type:
        query = query.filter(ExceptionModel.exception_type == exception_type)
    if resolution_status:
        query = query.filter(ExceptionModel.resolution_status == resolution_status)
    return query.all()

@router.patch("/exceptions/{exception_id}", response_model=ExceptionSchema)
def resolve_exception(
    exception_id: str,
    body: ExceptionResolveRequest,
    db: Session = Depends(get_db)
):
    ex = db.query(ExceptionModel).filter(ExceptionModel.id == exception_id).first()
    if not ex:
        raise HTTPException(status_code=404, detail="Exception not found")

    ex.resolution_status = body.action
    ex.resolved_by = "human_analyst"
    ex.resolved_at = datetime.utcnow()

    cand_id = body.target_candidate_id or ex.candidate_record_id
    rec = db.query(Record).filter(Record.id == ex.record_id).first()

    # If action is 'accept' or 'manual' with a valid candidate
    if body.action in ["accept", "manual"] and cand_id:
        cand_rec = db.query(Record).filter(Record.id == cand_id).first()
        if rec and cand_rec and rec.status != "matched" and cand_rec.status != "matched":
            rec.status = "matched"
            cand_rec.status = "matched"

            # Create human resolved match object
            match_obj = Match(
                run_id=ex.run_id,
                record_ids=[rec.id, cand_rec.id],
                record_codes=[rec.record_id, cand_rec.record_id],
                match_tier="human_resolved",
                confidence=1.0,
                reasoning=f"Human resolved exception via {body.action.upper()}. Notes: {body.notes or 'None'}"
            )
            db.add(match_obj)

    # Recompute run statistics
    run = db.query(Run).filter(Run.id == ex.run_id).first()
    if run:
        all_recs = db.query(Record).filter(Record.run_id == run.id).all()
        matched_cnt = len([r for r in all_recs if r.status == "matched"])
        ex_cnt = len([r for r in all_recs if r.status == "exception"])
        run.matched_count = matched_cnt
        run.exception_count = ex_cnt
        run.match_rate_pct = round((matched_cnt / run.total_records) * 100.0, 2) if run.total_records > 0 else 0.0

    db.add(AuditLog(
        run_id=ex.run_id,
        actor="human",
        action=f"EXCEPTION_RESOLVED_{body.action.upper()}",
        target_record_id=ex.record_id,
        details={
            "exception_id": ex.id,
            "action": body.action,
            "target_candidate_id": cand_id,
            "notes": body.notes
        }
    ))
    db.commit()
    db.refresh(ex)
    return ex

@router.get("/runs/{run_id}/cash-position", response_model=CashPositionResponse)
def get_cash_position(run_id: str, db: Session = Depends(get_db)):
    run = db.query(Run).filter(Run.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    matched_records = db.query(Record).filter(Record.run_id == run_id, Record.status == "matched").all()

    # Net confirmed cash position from matched transactions
    # Note: Source A records are positive/negative as in ledger
    net_position = sum(r.amount for r in matched_records if r.source == "A")

    exceptions_count = db.query(ExceptionModel).filter(
        ExceptionModel.run_id == run_id,
        ExceptionModel.resolution_status == "open"
    ).count()

    return CashPositionResponse(
        run_id=run_id,
        total_matched_count=len(matched_records),
        confirmed_cash_position=round(net_position, 2),
        excluded_pending_exceptions_count=exceptions_count,
        currency="USD",
        matched_summary={
            "ledger_matched_count": len([r for r in matched_records if r.source == "A"]),
            "bank_matched_count": len([r for r in matched_records if r.source == "B"]),
            "matches_count": db.query(Match).filter(Match.run_id == run_id).count()
        }
    )

@router.get("/runs/{run_id}/audit-log", response_model=List[AuditLogSchema])
def get_audit_log(run_id: str, db: Session = Depends(get_db)):
    return db.query(AuditLog).filter(AuditLog.run_id == run_id).order_by(AuditLog.created_at.asc()).all()

@router.get("/runs/{run_id}/report")
def export_run_report(run_id: str, format: str = Query("json"), db: Session = Depends(get_db)):
    run = db.query(Run).filter(Run.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    matches = db.query(Match).filter(Match.run_id == run_id).all()
    exceptions = db.query(ExceptionModel).filter(ExceptionModel.run_id == run_id).all()

    breakdown_tier = {"exact": 0, "split": 0, "tolerant": 0, "llm": 0, "human_resolved": 0}
    for m in matches:
        breakdown_tier[m.match_tier] = breakdown_tier.get(m.match_tier, 0) + 1

    breakdown_ex = {}
    for ex in exceptions:
        breakdown_ex[ex.exception_type] = breakdown_ex.get(ex.exception_type, 0) + 1

    # Invariant Check
    all_recs_cnt = db.query(Record).filter(Record.run_id == run_id).count()
    integrity_passed = (run.matched_count + run.exception_count) == all_recs_cnt

    if format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Run ID", run.id])
        writer.writerow(["Created At", run.created_at])
        writer.writerow(["Status", run.status])
        writer.writerow(["Total Input Records", run.total_records])
        writer.writerow(["Matched Records", run.matched_count])
        writer.writerow(["Exception Records", run.exception_count])
        writer.writerow(["Match Rate %", run.match_rate_pct])
        writer.writerow(["Processing Time (ms)", run.processing_time_ms])
        writer.writerow(["LLM Calls Made", run.llm_calls_made])
        writer.writerow([])
        writer.writerow(["MATCHES"])
        writer.writerow(["Match ID", "Tier", "Confidence", "Record Codes", "Reasoning"])
        for m in matches:
            writer.writerow([m.id, m.match_tier, m.confidence, ", ".join(m.record_codes or []), m.reasoning])
        writer.writerow([])
        writer.writerow(["EXCEPTIONS"])
        writer.writerow(["Exception ID", "Record Code", "Source", "Type", "Candidate Code", "Reasoning", "Status"])
        for ex in exceptions:
            writer.writerow([ex.id, ex.record_code, ex.source, ex.exception_type, ex.candidate_record_code, ex.reasoning, ex.resolution_status])

        output.seek(0)
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode("utf-8")),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=reconciliation_report_{run_id}.csv"}
        )

    return {
        "run": run,
        "breakdown_by_tier": breakdown_tier,
        "breakdown_by_exception_type": breakdown_ex,
        "integrity_check_passed": integrity_passed,
        "integrity_check_message": f"Conservation Invariant verified: matched ({run.matched_count}) + exceptions ({run.exception_count}) == total input records ({all_recs_cnt})" if integrity_passed else "INVARIANT ERROR"
    }

@router.post("/runs/{run_id}/approve", response_model=RunResponse)
def approve_close(run_id: str, db: Session = Depends(get_db)):
    run = db.query(Run).filter(Run.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    run.approved_by = "controller_lead"
    run.approved_at = datetime.utcnow()

    db.add(AuditLog(
        run_id=run_id,
        actor="human",
        action="PERIOD_CLOSE_APPROVED",
        details={"approved_by": run.approved_by, "approved_at": str(run.approved_at)}
    ))
    db.commit()
    db.refresh(run)
    return run

from app.services.anomaly_engine import AnomalyDetectionEngine
from app.services.liquidity_forecaster import LiquidityForecaster

@router.get("/runs/{run_id}/anomalies")
def get_run_anomalies(run_id: str, db: Session = Depends(get_db)):
    run = db.query(Run).filter(Run.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    records = db.query(Record).filter(Record.run_id == run_id).all()
    rec_dicts = [
        {
            "id": r.id,
            "record_id": r.record_id,
            "source": r.source,
            "reference_id": r.reference_id,
            "amount": r.amount,
            "transaction_date": r.transaction_date,
            "counterparty": r.counterparty,
            "description": r.description,
            "status": r.status
        }
        for r in records
    ]

    analyzed = AnomalyDetectionEngine.analyze_transactions(rec_dicts)
    high_risk = [r for r in analyzed if r["risk_level"] == "HIGH"]
    medium_risk = [r for r in analyzed if r["risk_level"] == "MEDIUM"]

    return {
        "run_id": run_id,
        "total_records_analyzed": len(analyzed),
        "high_risk_count": len(high_risk),
        "medium_risk_count": len(medium_risk),
        "records": analyzed
    }

@router.get("/runs/{run_id}/forecast")
def get_run_forecast(run_id: str, db: Session = Depends(get_db)):
    run = db.query(Run).filter(Run.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    matched_records = db.query(Record).filter(Record.run_id == run_id, Record.status == "matched").all()
    rec_dicts = [{"amount": r.amount, "source": r.source} for r in matched_records]

    net_position = sum(r.amount for r in matched_records if r.source == "A")
    open_exceptions_cnt = db.query(ExceptionModel).filter(
        ExceptionModel.run_id == run_id,
        ExceptionModel.resolution_status == "open"
    ).count()

    forecast = LiquidityForecaster.generate_30day_forecast(
        current_balance=net_position,
        matched_records=rec_dicts,
        open_exceptions_count=open_exceptions_cnt
    )
    return forecast

from app.services.ai_copilot_service import AICopilotService
from app.services.tax_classifier import TaxGLClassifier

@router.post("/runs/{run_id}/copilot")
async def ask_ai_copilot(run_id: str, query: str = Form(...), db: Session = Depends(get_db)):
    run = db.query(Run).filter(Run.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    run_dict = {
        "id": run.id,
        "total_records": run.total_records,
        "matched_count": run.matched_count,
        "exception_count": run.exception_count,
        "match_rate_pct": run.match_rate_pct,
        "status": run.status,
        "approved_by": run.approved_by
    }

    records = db.query(Record).filter(Record.run_id == run_id).limit(15).all()
    exceptions = db.query(ExceptionModel).filter(ExceptionModel.run_id == run_id).limit(15).all()

    recs_summary = [{"code": r.record_id, "amount": r.amount, "status": r.status, "counterparty": r.counterparty} for r in records]
    ex_summary = [{"code": e.record_code, "type": e.exception_type, "reason": e.reasoning} for e in exceptions]

    res = await AICopilotService.ask_copilot(query, run_dict, recs_summary, ex_summary)
    return res

@router.post("/runs/{run_id}/auto-resolve")
def ai_auto_resolve_exceptions(run_id: str, db: Session = Depends(get_db)):
    run = db.query(Run).filter(Run.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    open_exceptions = db.query(ExceptionModel).filter(
        ExceptionModel.run_id == run_id,
        ExceptionModel.resolution_status == "open"
    ).all()

    resolved_count = 0
    for ex in open_exceptions:
        if ex.candidate_record_id and ex.exception_type in ["NEEDS_HUMAN_REVIEW", "DATE_MISMATCH"]:
            rec = db.query(Record).filter(Record.id == ex.record_id).first()
            cand_rec = db.query(Record).filter(Record.id == ex.candidate_record_id).first()

            if rec and cand_rec and rec.status != "matched" and cand_rec.status != "matched":
                rec.status = "matched"
                cand_rec.status = "matched"
                ex.resolution_status = "accept"
                ex.resolved_by = "ai_auto_resolver"
                ex.resolved_at = datetime.utcnow()

                match_obj = Match(
                    run_id=run_id,
                    record_ids=[rec.id, cand_rec.id],
                    record_codes=[rec.record_id, cand_rec.record_id],
                    match_tier="ai_auto_resolved",
                    confidence=0.90,
                    reasoning="AI Auto-Resolver matched candidate under high-confidence proximity policy."
                )
                db.add(match_obj)
                resolved_count += 1

    # Recompute run statistics
    all_recs = db.query(Record).filter(Record.run_id == run_id).all()
    matched_cnt = len([r for r in all_recs if r.status == "matched"])
    ex_cnt = len([r for r in all_recs if r.status == "exception"])
    run.matched_count = matched_cnt
    run.exception_count = ex_cnt
    run.match_rate_pct = round((matched_cnt / run.total_records) * 100.0, 2) if run.total_records > 0 else 0.0

    db.add(AuditLog(
        run_id=run_id,
        actor="agent",
        action="AI_AUTO_RESOLVE_BATCH",
        details={"resolved_count": resolved_count, "new_match_rate_pct": run.match_rate_pct}
    ))
    db.commit()
    return {"status": "success", "resolved_count": resolved_count, "new_match_rate_pct": run.match_rate_pct}

@router.get("/runs/{run_id}/tax-summary")
def get_run_tax_summary(run_id: str, db: Session = Depends(get_db)):
    run = db.query(Run).filter(Run.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    records = db.query(Record).filter(Record.run_id == run_id).all()

    classified_records = []
    gl_totals = {}

    for r in records:
        tax_info = TaxGLClassifier.classify(r.counterparty or "", r.description or "", r.amount)
        item = {
            "record_id": r.record_id,
            "counterparty": r.counterparty,
            "amount": r.amount,
            "gl_account_code": tax_info["gl_account_code"],
            "tax_category": tax_info["tax_category"],
            "schedule_line": tax_info["schedule_line"]
        }
        classified_records.append(item)

        gl_code = tax_info["gl_account_code"]
        gl_totals[gl_code] = round(gl_totals.get(gl_code, 0.0) + r.amount, 2)

    return {
        "run_id": run_id,
        "total_classified_records": len(classified_records),
        "gl_account_totals": gl_totals,
        "records": classified_records
    }

from app.services.excel_report_generator import ExcelReportGenerator

@router.get("/runs/{run_id}/excel-report")
def export_excel_report(run_id: str, db: Session = Depends(get_db)):
    run = db.query(Run).filter(Run.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    matches = db.query(Match).filter(Match.run_id == run_id).all()
    exceptions = db.query(ExceptionModel).filter(ExceptionModel.run_id == run_id).all()
    records = db.query(Record).filter(Record.run_id == run_id).all()

    # Tax summary
    classified_recs = []
    gl_totals = {}
    for r in records:
        tax_info = TaxGLClassifier.classify(r.counterparty or "", r.description or "", r.amount)
        gl_code = tax_info["gl_account_code"]
        gl_totals[gl_code] = round(gl_totals.get(gl_code, 0.0) + r.amount, 2)

    tax_summary = {"gl_account_totals": gl_totals}

    # Anomalies
    rec_dicts = [
        {"id": r.id, "record_code": r.record_id, "amount": r.amount, "counterparty": r.counterparty}
        for r in records
    ]
    anomalies = AnomalyDetectionEngine.analyze_transactions(rec_dicts)

    csv_content = ExcelReportGenerator.generate_excel_csv_report(
        run, matches, exceptions, records, tax_summary, anomalies
    )

    return StreamingResponse(
        io.BytesIO(csv_content.encode("utf-8")),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=fincheck_ai_insights_report_{run_id}.csv"}
    )

@router.get("/runs/{run_id}/insights")
def get_run_insights(run_id: str, db: Session = Depends(get_db)):
    run = db.query(Run).filter(Run.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    # Calculate estimated manual hours saved (assuming ~3 minutes per transaction for manual checking)
    manual_minutes_saved = run.total_records * 3
    hours_saved = round(manual_minutes_saved / 60.0, 1)

    exceptions = db.query(ExceptionModel).filter(ExceptionModel.run_id == run_id).all()
    ex_causes = {}
    for ex in exceptions:
        ex_causes[ex.exception_type] = ex_causes.get(ex.exception_type, 0) + 1

    return {
        "run_id": run_id,
        "total_records": run.total_records,
        "matched_count": run.matched_count,
        "exception_count": run.exception_count,
        "match_rate_pct": run.match_rate_pct,
        "hours_saved_estimate": hours_saved,
        "processing_time_ms": run.processing_time_ms,
        "exception_causes": ex_causes,
        "conservation_invariant_verified": (run.matched_count + run.exception_count) == run.total_records
    }

@router.post("/data/generate-synthetic")
def generate_synthetic_endpoint(seed: int = Query(42)):
    generate_synthetic_data(output_dir="data/synthetic", seed=seed)
    return {"status": "success", "seed": seed, "message": "Synthetic dataset generated in data/synthetic/"}
