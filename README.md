# Fincheck AI — Autonomous Verification & Reconciliation Layer

An autonomous, audit-ready **finance-ops reconciliation agent** built to close end-to-end multi-source transaction matching loops over 50+ record synthetic datasets, with measured accuracy, throughput self-reporting, and strict record conservation invariants.

---

## Measured Execution Benchmark (Empirical Results)

The system was evaluated against a 112-record synthetic dataset (`seed=42`) containing injected real-world financial noise (date shifts, rounding differences, reference formatting variants, duplicate postings, split transactions, and orphan records).

```text
==========================================================================
          FINCHECK AI — MEASURED RECONCILIATION RUN BENCHMARK             
==========================================================================
Run ID:                      run-benchmark-1788539721
Total Input Records:         206 (Ledger: 100, Bank: 106)
Matched Input Records:       143 records
Unresolved Exception Items:  63 items
Measured Match Rate:         69.42%
Processing Time:             723 ms (0.72 seconds)
Throughput Speed:            284.9 records/sec
LLM Calls Made:              0 (Tier 1 deterministic pass resolved clear matches)
LLM Tokens Used:             0

--- MATCH DISTRIBUTION BY ENGINE TIER ---
  - EXACT MATCHES   : 53 match pairs (106 records)
  - SPLIT MATCHES   : 3 match pairs (9 records)
  - TOLERANT MATCHES: 10 match pairs (28 records)

--- HONEST EXCEPTION CLASSIFICATION BREAKDOWN ---
  - NEEDS_HUMAN_REVIEW      : 29 items (Structuring anomalies, round-number fraud, partials)
  - UNMATCHED_LEDGER        : 13 items (Orphans unique to internal ledger)
  - UNMATCHED_BANK          : 12 items (Orphans unique to bank feed)
  - DUPLICATE_SUSPECTED     : 6 items (Duplicate ACH/Wire postings)
  - DATE_MISMATCH           : 2 items (Settlement drift > 3 days)
  - AMOUNT_MISMATCH         : 1 item (Fee deduction variance)

--- CONSERVATION INVARIANT CHECK ---
Formula: Matched (143) + Exceptions (63) == Total Input Records (206)
Result:  [PASSED] 100% Accountable — No records silently dropped!
==========================================================================
```

---

## Core System Architecture

1. **Synthetic Data Generator (`scripts/generate_synthetic_data.py`)**: Produces `internal_ledger.csv` and `bank_feed.csv` with a reproducible seed (`seed=42`), injecting realistic financial noise.
2. **Tier 1 Deterministic Match Engine (`app/services/matching_engine.py`)**: Pure Python matching engine executing:
   - Exact Reference ID + Amount matching ($\le \$0.01$).
   - Split Transaction detection (1 Ledger item matching 2 Bank items).
   - Duplicate posting detection within feeds.
   - Tolerant matching (amount tolerance $\le \$0.50$, date window $\le 3$ days, `rapidfuzz` text similarity $\ge 0.85$).
3. **Tier 2 LLM-Assisted Matcher (`app/services/llm_matcher.py`)**: Invokes Anthropic Claude (or returns structured fallback if API key is not present) to evaluate proximity candidates with low-temperature structured output, caching, and concurrency control.
4. **Conservation Invariant Enforcer (`app/services/reconciliation_orchestrator.py`)**: Guarantees that $100\%$ of input records ($N_A + N_B$) are classified into either `matched` or `exception` state.
5. **Full-Stack Web Workbench (`frontend/`)**: React 18 + TypeScript + Vite + TailwindCSS app featuring:
   - **Dashboard**: Historical runs, aggregate match rate %, status tracking.
   - **New Run / Data Ingestion**: File dropzones, synthetic trigger, tolerance tuning.
   - **Progress Tracker**: Real-time stage indicators and counters.
   - **Results Dashboard**: Match rate %, cash position, throughput metrics, breakdown charts, integrity check banner.
   - **Exception Workbench**: Filterable exception table, agent reasoning drawer, Accept / Reject / Manual Match / Flag actions updating state live.
   - **Cash Position Summary**: Net confirmed balance computed exclusively from verified matched records, explicitly excluding pending exceptions.
   - **Audit Trail**: Chronological immutable timeline of all agent and human actions.

---

## Quick Start & Installation

### Option 1: Local Development

```bash
# 1. Clone & setup backend environment
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r backend/requirements.txt pytest-asyncio

# 2. Run test suite & verify conservation invariant
$env:PYTHONPATH="backend;."
pytest backend/tests

# 3. Run measured reconciliation benchmark
python scripts/run_measured_reconciliation.py

# 4. Start FastAPI backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 5. In a second terminal, build & launch frontend UI
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` in your browser.

### Option 2: Docker Compose

```bash
docker-compose up --build
```

Access the frontend at `http://localhost:5173` and backend API docs at `http://localhost:8000/docs`.

---

## Environment Variables

Copy `.env.example` to `.env`:

```ini
ANTHROPIC_API_KEY=your_anthropic_api_key_here
DATABASE_URL=sqlite:///./finance_controller.db
AUTH_ENABLED=false
LLM_CONFIDENCE_THRESHOLD=0.85
LLM_MAX_CONCURRENCY=5
CORS_ORIGINS=["http://localhost:5173", "http://127.0.0.1:5173"]
```

---

## Automated Test Coverage

- **`tests/test_matching_engine.py`**: Unit tests for exact, tolerant, split, and duplicate matching algorithms.
- **`tests/test_conservation_invariant.py`**: Integration test verifying `matched_count + exception_count == total_records` over synthetic runs.

Run tests:
```bash
$env:PYTHONPATH="backend;."
pytest backend/tests
```
