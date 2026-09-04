import pytest
from app.services.matching_engine import Tier1DeterministicMatcher

def test_exact_matching():
    matcher = Tier1DeterministicMatcher()
    recs_a = [
        {"id": "a1", "record_id": "LED-101", "reference_id": "INV-1001", "amount": 1500.00, "transaction_date": "2026-08-01"}
    ]
    recs_b = [
        {"id": "b1", "record_id": "BNK-501", "reference_id": "INV-1001", "amount": 1500.00, "transaction_date": "2026-08-01"}
    ]

    matches, dupes, rem_a, rem_b = matcher.run(recs_a, recs_b)

    assert len(matches) == 1
    assert matches[0]["match_tier"] == "exact"
    assert matches[0]["confidence"] == 1.0
    assert len(rem_a) == 0
    assert len(rem_b) == 0

def test_tolerant_matching():
    matcher = Tier1DeterministicMatcher(amount_tolerance=0.50, date_tolerance_days=3, fuzzy_threshold=0.85)
    recs_a = [
        {"id": "a1", "record_id": "LED-102", "reference_id": "LOG-884-102", "amount": 2450.00, "transaction_date": "2026-08-05", "counterparty": "Global Logistics"}
    ]
    recs_b = [
        {"id": "b1", "record_id": "BNK-502", "reference_id": "LOG 884 102", "amount": 2450.25, "transaction_date": "2026-08-07", "counterparty": "GLOBAL LOGISTICS LLC"}
    ]

    matches, dupes, rem_a, rem_b = matcher.run(recs_a, recs_b)

    assert len(matches) == 1
    assert matches[0]["match_tier"] == "tolerant"
    assert matches[0]["confidence"] >= 0.85
    assert len(rem_a) == 0
    assert len(rem_b) == 0

def test_split_transaction_matching():
    matcher = Tier1DeterministicMatcher()
    recs_a = [
        {"id": "a1", "record_id": "LED-103", "reference_id": "CS-SPLIT-801", "amount": 3500.00, "transaction_date": "2026-08-10"}
    ]
    recs_b = [
        {"id": "b1", "record_id": "BNK-503", "reference_id": "CS-SPLIT-801-PART1", "amount": 1500.00, "transaction_date": "2026-08-10"},
        {"id": "b2", "record_id": "BNK-504", "reference_id": "CS-SPLIT-801-PART2", "amount": 2000.00, "transaction_date": "2026-08-11"}
    ]

    matches, dupes, rem_a, rem_b = matcher.run(recs_a, recs_b)

    assert len(matches) == 1
    assert matches[0]["match_tier"] == "split"
    assert len(matches[0]["record_ids"]) == 3
    assert len(rem_a) == 0
    assert len(rem_b) == 0

def test_duplicate_detection():
    matcher = Tier1DeterministicMatcher()
    recs_a = [
        {"id": "a1", "record_id": "LED-104", "reference_id": "APX-330-104", "amount": 800.00, "transaction_date": "2026-08-12"}
    ]
    recs_b = [
        {"id": "b1", "record_id": "BNK-505", "reference_id": "APX-330-104", "amount": 800.00, "transaction_date": "2026-08-12"},
        {"id": "b2", "record_id": "BNK-506", "reference_id": "APX-330-104", "amount": 800.00, "transaction_date": "2026-08-12"}
    ]

    matches, dupes, rem_a, rem_b = matcher.run(recs_a, recs_b)

    assert len(dupes) == 1
    assert dupes[0]["record"]["id"] == "b2"
