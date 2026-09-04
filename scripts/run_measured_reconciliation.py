"""
Measured Run Execution Script for AI Finance Controller.
Runs full reconciliation over synthetic dataset and prints exact audit metrics.
"""

import sys
import os
import asyncio
import csv
from datetime import datetime

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath("backend"))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.schema import Base, Run, Record, Match, ExceptionModel
from app.services.reconciliation_orchestrator import ReconciliationOrchestrator
from scripts.generate_synthetic_data import generate_synthetic_data
from scripts.generate_huge_judge_dataset import generate_huge_judge_dataset

async def main():
    print("==========================================================================")
    print("          AI FINANCE CONTROLLER — MEASURED RECONCILIATION RUN             ")
    print("==========================================================================")

    # 1. Load huge 206-record judge dataset
    generate_huge_judge_dataset(output_dir="data/judge_dataset", seed=100)

    with open("data/judge_dataset/internal_ledger_judge.csv", "r", encoding="utf-8") as f:
        records_a = list(csv.DictReader(f))

    with open("data/judge_dataset/bank_feed_judge.csv", "r", encoding="utf-8") as f:
        records_b = list(csv.DictReader(f))

    total_input = len(records_a) + len(records_b)

    # 2. Setup SQLite database session
    engine = create_engine("sqlite:///finance_controller.db")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    run_id = f"run-benchmark-{int(datetime.utcnow().timestamp())}"

    # 3. Execute Pipeline
    orchestrator = ReconciliationOrchestrator(session)
    run_obj = await orchestrator.run_pipeline(
        run_id=run_id,
        records_a_raw=records_a,
        records_b_raw=records_b,
        amount_tolerance=0.50,
        date_tolerance_days=3,
        fuzzy_threshold=0.85
    )

    # 4. Fetch Audit Details
    matches = session.query(Match).filter(Match.run_id == run_id).all()
    exceptions = session.query(ExceptionModel).filter(ExceptionModel.run_id == run_id).all()
    all_recs = session.query(Record).filter(Record.run_id == run_id).all()

    matched_recs = [r for r in all_recs if r.status == "matched"]
    exception_recs = [r for r in all_recs if r.status == "exception"]

    tier_breakdown = {}
    for m in matches:
        tier_breakdown[m.match_tier] = tier_breakdown.get(m.match_tier, 0) + 1

    ex_breakdown = {}
    for ex in exceptions:
        ex_breakdown[ex.exception_type] = ex_breakdown.get(ex.exception_type, 0) + 1

    invariant_passed = (len(matched_recs) + len(exception_recs)) == total_input

    print("\n--- MEASURED EXECUTION METRICS ---")
    print(f"Run ID:                      {run_obj.id}")
    print(f"Total Input Records:         {total_input} (Ledger: {len(records_a)}, Bank: {len(records_b)})")
    print(f"Matched Input Records:       {len(matched_recs)}")
    print(f"Unresolved Exception Items:  {len(exception_recs)}")
    print(f"Measured Match Rate:         {run_obj.match_rate_pct}%")
    print(f"Processing Time:             {run_obj.processing_time_ms} ms ({run_obj.processing_time_ms / 1000:.2f} s)")
    print(f"Throughput Speed:            {(total_input / (run_obj.processing_time_ms / 1000)):.1f} records/sec")
    print(f"LLM Calls Made:              {run_obj.llm_calls_made}")
    print(f"LLM Tokens Used:             {run_obj.llm_tokens_used}")

    print("\n--- MATCH DISTRIBUTION BY ENGINE TIER ---")
    for tier, cnt in tier_breakdown.items():
        print(f"  - {tier.upper():<16}: {cnt} match pairs")

    print("\n--- HONEST EXCEPTION CLASSIFICATION BREAKDOWN ---")
    for ex_t, cnt in ex_breakdown.items():
        print(f"  - {ex_t:<24}: {cnt} items")

    print("\n--- CONSERVATION INVARIANT CHECK ---")
    print(f"Formula: Matched ({len(matched_recs)}) + Exceptions ({len(exception_recs)}) == Total Input ({total_input})")
    print(f"Result:  {'[PASSED] 100% Accountable' if invariant_passed else '[FAILED] Invariant Error'}")
    print("==========================================================================")

    session.close()

if __name__ == "__main__":
    asyncio.run(main())
