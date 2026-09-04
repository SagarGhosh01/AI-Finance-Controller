"""
Reconciliation Orchestrator & Pipeline Service.
Executes end-to-end reconciliation, classifies exceptions, enforces conservation invariants,
and persists complete run audit logs.
"""

import time
import asyncio
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from app.models.schema import Run, Record, Match, ExceptionModel, AuditLog
from app.services.matching_engine import Tier1DeterministicMatcher, days_diff
from app.services.llm_matcher import LLMMatcher
from app.core.config import settings

class ReconciliationOrchestrator:
    def __init__(self, db: Session):
        self.db = db
        self.t1_matcher = Tier1DeterministicMatcher()
        self.llm_matcher = LLMMatcher()

    async def run_pipeline(
        self,
        run_id: str,
        records_a_raw: List[Dict[str, Any]],
        records_b_raw: List[Dict[str, Any]],
        amount_tolerance: float = 0.50,
        date_tolerance_days: int = 3,
        fuzzy_threshold: float = 0.85
    ) -> Run:
        start_time = time.time()

        # Fetch or create run object
        run = self.db.query(Run).filter(Run.id == run_id).first()
        if not run:
            run = Run(id=run_id, status="running")
            self.db.add(run)
            self.db.commit()
        else:
            run.status = "running"
            self.db.commit()

        # Update matcher settings
        self.t1_matcher.amount_tolerance = amount_tolerance
        self.t1_matcher.date_tolerance_days = date_tolerance_days
        self.t1_matcher.fuzzy_threshold = fuzzy_threshold

        total_input_count = len(records_a_raw) + len(records_b_raw)
        run.total_records = total_input_count

        # 1. Ingest records into DB
        db_records: Dict[str, Record] = {}
        for r_data in records_a_raw:
            rec = Record(
                run_id=run_id,
                record_id=str(r_data["record_id"]),
                source="A",
                reference_id=str(r_data.get("reference_id", "")),
                amount=float(r_data["amount"]),
                currency=str(r_data.get("currency", "USD")),
                transaction_date=str(r_data["transaction_date"]),
                counterparty=str(r_data.get("counterparty", "")),
                description=str(r_data.get("description", "")),
                raw_data=r_data,
                status="pending"
            )
            self.db.add(rec)
            db_records[rec.record_id] = rec

        for r_data in records_b_raw:
            rec = Record(
                run_id=run_id,
                record_id=str(r_data["record_id"]),
                source="B",
                reference_id=str(r_data.get("reference_id", "")),
                amount=float(r_data["amount"]),
                currency=str(r_data.get("currency", "USD")),
                transaction_date=str(r_data["transaction_date"]),
                counterparty=str(r_data.get("counterparty", "")),
                description=str(r_data.get("description", "")),
                raw_data=r_data,
                status="pending"
            )
            self.db.add(rec)
            db_records[rec.record_id] = rec

        self.db.commit()

        # Log start audit
        self.db.add(AuditLog(
            run_id=run_id,
            actor="agent",
            action="INGESTION_COMPLETE",
            details={"source_a_count": len(records_a_raw), "source_b_count": len(records_b_raw)}
        ))
        self.db.commit()

        # Prepare dict lists for pure matcher
        recs_a_dict = [
            {"id": db_records[r["record_id"]].id, "record_id": r["record_id"], "reference_id": r.get("reference_id"),
             "amount": float(r["amount"]), "transaction_date": r["transaction_date"],
             "counterparty": r.get("counterparty"), "description": r.get("description")}
            for r in records_a_raw
        ]
        recs_b_dict = [
            {"id": db_records[r["record_id"]].id, "record_id": r["record_id"], "reference_id": r.get("reference_id"),
             "amount": float(r["amount"]), "transaction_date": r["transaction_date"],
             "counterparty": r.get("counterparty"), "description": r.get("description")}
            for r in records_b_raw
        ]

        # 2. Execute Tier 1 Deterministic Match Pass
        t1_matches, duplicates, rem_a, rem_b = self.t1_matcher.run(recs_a_dict, recs_b_dict)

        matched_db_record_ids = set()

        for m in t1_matches:
            match_obj = Match(
                run_id=run_id,
                record_ids=m["record_ids"],
                record_codes=m["record_codes"],
                match_tier=m["match_tier"],
                confidence=m["confidence"],
                reasoning=m["reasoning"]
            )
            self.db.add(match_obj)
            for r_uuid in m["record_ids"]:
                matched_db_record_ids.add(r_uuid)
                rec = self.db.query(Record).filter(Record.id == r_uuid).first()
                if rec:
                    rec.status = "matched"

        self.db.commit()

        self.db.add(AuditLog(
            run_id=run_id,
            actor="agent",
            action="TIER1_MATCH_COMPLETE",
            details={"matches_found": len(t1_matches), "records_matched": len(matched_db_record_ids)}
        ))
        self.db.commit()

        # 3. Execute Tier 2 LLM Match Pass for remaining unmatched records
        llm_calls_made = 0
        llm_tokens_used = 0
        llm_matches_count = 0

        tasks = []
        task_rem_a = []

        for r_a in rem_a:
            # Pick top 5 Proximity candidates from rem_b (by amount & date closeness)
            amt_a = r_a["amount"]
            date_a = r_a["transaction_date"]

            sorted_cand_b = sorted(
                rem_b,
                key=lambda c: (abs(amt_a - c["amount"]), days_diff(date_a, c["transaction_date"]))
            )[:5]

            tasks.append(self.llm_matcher.evaluate_pair(r_a, sorted_cand_b))
            task_rem_a.append((r_a, sorted_cand_b))

        if tasks:
            llm_results = await asyncio.gather(*tasks)

            for (r_a, sorted_cand_b), res in zip(task_rem_a, llm_results):
                if res.get("llm_called"):
                    llm_calls_made += 1
                    llm_tokens_used += res.get("tokens_used", 0)

                if res.get("match") and res.get("confidence", 0.0) >= settings.LLM_CONFIDENCE_THRESHOLD:
                    cand_uuid = res.get("matched_record_id")
                    if cand_uuid and cand_uuid not in matched_db_record_ids and r_a["id"] not in matched_db_record_ids:
                        cand_dict = next((c for c in sorted_cand_b if c["id"] == cand_uuid), None)
                        cand_code = cand_dict["record_id"] if cand_dict else cand_uuid

                        matched_db_record_ids.add(r_a["id"])
                        matched_db_record_ids.add(cand_uuid)
                        llm_matches_count += 1

                        rec_a_obj = self.db.query(Record).filter(Record.id == r_a["id"]).first()
                        rec_b_obj = self.db.query(Record).filter(Record.id == cand_uuid).first()
                        if rec_a_obj:
                            rec_a_obj.status = "matched"
                        if rec_b_obj:
                            rec_b_obj.status = "matched"

                        match_obj = Match(
                            run_id=run_id,
                            record_ids=[r_a["id"], cand_uuid],
                            record_codes=[r_a["record_id"], cand_code],
                            match_tier="llm",
                            confidence=res.get("confidence", 0.85),
                            reasoning=res.get("reasoning")
                        )
                        self.db.add(match_obj)

        self.db.commit()

        self.db.add(AuditLog(
            run_id=run_id,
            actor="agent",
            action="TIER2_LLM_COMPLETE",
            details={"llm_calls": llm_calls_made, "llm_matches": llm_matches_count, "tokens_used": llm_tokens_used}
        ))
        self.db.commit()

        # 4. Classify Exceptions for all remaining unmatched records
        # Duplicate mapping
        duplicate_map = {dup["record"]["id"]: dup for dup in duplicates}

        all_records = self.db.query(Record).filter(Record.run_id == run_id).all()
        exception_count = 0

        # Unmatched A and B dicts
        unmatched_a_recs = [r for r in all_records if r.source == "A" and r.status != "matched"]
        unmatched_b_recs = [r for r in all_records if r.source == "B" and r.status != "matched"]

        for rec in all_records:
            if rec.status != "matched":
                rec.status = "exception"
                exception_count += 1

                # Determine classification
                ex_type = "UNMATCHED_LEDGER" if rec.source == "A" else "UNMATCHED_BANK"
                cand_id = None
                cand_code = None
                conf = None
                reason = f"Unmatched transaction in {run.source_a_name if rec.source == 'A' else run.source_b_name}."

                if rec.id in duplicate_map:
                    dup_info = duplicate_map[rec.id]
                    ex_type = "DUPLICATE_SUSPECTED"
                    cand_id = dup_info["primary_record"]["id"]
                    cand_code = dup_info["primary_record"]["record_id"]
                    reason = dup_info["reasoning"]
                else:
                    # Search for closest candidate on opposing side
                    opp_recs = unmatched_b_recs if rec.source == "A" else unmatched_a_recs
                    if opp_recs:
                        closest = min(opp_recs, key=lambda c: (abs(rec.amount - c.amount), days_diff(rec.transaction_date, c.transaction_date)))
                        amt_diff = abs(rec.amount - closest.amount)
                        d_diff = days_diff(rec.transaction_date, closest.transaction_date)

                        if amt_diff <= 0.05 and d_diff > date_tolerance_days:
                            ex_type = "DATE_MISMATCH"
                            cand_id = closest.id
                            cand_code = closest.record_id
                            reason = f"Amount matches candidate {closest.record_id} (${closest.amount:.2f}), but date diff is {d_diff} days (exceeds threshold of {date_tolerance_days} days)."
                        elif d_diff <= date_tolerance_days and 0.05 < amt_diff <= 25.0:
                            ex_type = "AMOUNT_MISMATCH"
                            cand_id = closest.id
                            cand_code = closest.record_id
                            reason = f"Date aligns with candidate {closest.record_id} ({closest.transaction_date}), but amount differs by ${amt_diff:.2f}."
                        elif amt_diff <= 2.0 or d_diff <= 2:
                            ex_type = "NEEDS_HUMAN_REVIEW"
                            cand_id = closest.id
                            cand_code = closest.record_id
                            reason = f"Potential partial candidate {closest.record_id} found (Amount diff: ${amt_diff:.2f}, Date diff: {d_diff}d). Requires human review."

                ex_obj = ExceptionModel(
                    run_id=run_id,
                    record_id=rec.id,
                    record_code=rec.record_id,
                    source=rec.source,
                    exception_type=ex_type,
                    candidate_record_id=cand_id,
                    candidate_record_code=cand_code,
                    confidence=conf,
                    reasoning=reason,
                    resolution_status="open"
                )
                self.db.add(ex_obj)

        self.db.commit()

        # 5. Calculate Final Summary & Verify Conservation Invariant
        total_matched_records = len([r for r in all_records if r.status == "matched"])
        total_exception_records = len([r for r in all_records if r.status == "exception"])

        # Conservation Invariant Check
        assert total_matched_records + total_exception_records == total_input_count, \
            f"INVARIANT VIOLATION: matched ({total_matched_records}) + exceptions ({total_exception_records}) != total ({total_input_count})"

        elapsed_ms = int((time.time() - start_time) * 1000)

        run.status = "completed"
        run.matched_count = total_matched_records
        run.exception_count = total_exception_records
        run.match_rate_pct = round((total_matched_records / total_input_count) * 100.0, 2) if total_input_count > 0 else 0.0
        run.processing_time_ms = elapsed_ms
        run.llm_calls_made = llm_calls_made
        run.llm_tokens_used = llm_tokens_used

        self.db.commit()

        self.db.add(AuditLog(
            run_id=run_id,
            actor="agent",
            action="RUN_COMPLETED",
            details={
                "total_records": total_input_count,
                "matched_records": total_matched_records,
                "exception_records": total_exception_records,
                "match_rate_pct": run.match_rate_pct,
                "processing_time_ms": elapsed_ms
            }
        ))
        self.db.commit()

        return run
