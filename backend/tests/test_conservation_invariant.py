import pytest
import asyncio
import csv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.schema import Base, Run, Record
from app.services.reconciliation_orchestrator import ReconciliationOrchestrator
from scripts.generate_synthetic_data import generate_synthetic_data

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

@pytest.mark.asyncio
async def test_conservation_invariant_on_synthetic_data(db_session):
    # Generate synthetic dataset
    generate_synthetic_data(output_dir="data/synthetic", seed=42)

    with open("data/synthetic/internal_ledger.csv", "r", encoding="utf-8") as f:
        recs_a = list(csv.DictReader(f))

    with open("data/synthetic/bank_feed.csv", "r", encoding="utf-8") as f:
        recs_b = list(csv.DictReader(f))

    total_input = len(recs_a) + len(recs_b)

    orchestrator = ReconciliationOrchestrator(db_session)
    run_obj = await orchestrator.run_pipeline(
        run_id="test-run-invariant-001",
        records_a_raw=recs_a,
        records_b_raw=recs_b
    )

    all_records = db_session.query(Record).filter(Record.run_id == run_obj.id).all()

    matched_cnt = len([r for r in all_records if r.status == "matched"])
    exception_cnt = len([r for r in all_records if r.status == "exception"])

    assert len(all_records) == total_input
    assert matched_cnt + exception_cnt == total_input
    assert run_obj.total_records == total_input
    assert run_obj.matched_count == matched_cnt
    assert run_obj.exception_count == exception_cnt
    assert run_obj.match_rate_pct == round((matched_cnt / total_input) * 100.0, 2)
