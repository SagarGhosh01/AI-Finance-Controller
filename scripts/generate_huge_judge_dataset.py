"""
Huge Benchmark Dataset Generator for Judge Live Demonstration.
Generates 210+ combined transaction records across Internal Ledger and Bank Feed
containing every real-world financial scenario, multi-currency, fraud anomalies,
split transactions, fee deductions, date shifts, and vendor typos.
"""

import os
import csv
import random
from datetime import datetime, timedelta

def generate_huge_judge_dataset(output_dir: str = "data/judge_dataset", seed: int = 100):
    random.seed(seed)
    os.makedirs(output_dir, exist_ok=True)

    base_date = datetime(2026, 8, 1)

    enterprise_vendors = [
        ("Acme Corp", "ACME CORP INC", "INV-2026-", "USD", "6010-SOFTWARE_SAAS"),
        ("Global Logistics LLC", "GLOBAL LOGISTICS INC", "LOG-884-", "USD", "6020-LOGISTICS_FREIGHT"),
        ("CloudScale Systems", "CLOUDSCALE SYS PROV", "CS-991-", "USD", "6010-SOFTWARE_SAAS"),
        ("Apex Supplies", "APEX SUP & MAT", "APX-330-", "USD", "6030-OFFICE_SUPPLIES"),
        ("Stripe Billing", "STRIPE TRANSFER", "STR-772-", "USD", "4010-REVENUE_SALES"),
        ("Vanguard Marketing", "VANGUARD MKTG AGENCY", "VNG-112-", "USD", "6070-MARKETING_ADVERTISING"),
        ("Horizon Telecom", "HORIZON TEL & COMM", "HT-554-", "USD", "6060-TELECOM_UTILITIES"),
        ("Nexus Tech Solutions", "NEXUS TECH SOL", "NEX-401-", "USD", "6040-LEGAL_PROFESSIONAL"),
        ("Pinnacle Legal Services", "PINNACLE LEGAL LAW", "PIN-009-", "USD", "6040-LEGAL_PROFESSIONAL"),
        ("Summit Real Estate", "SUMMIT REALTY LEASE", "SRE-771-", "USD", "6050-REAL_ESTATE_LEASE"),
        ("EuroSupply GmbH", "EUROSUPPLY GMBH FRA", "EUR-501-", "EUR", "6020-LOGISTICS_FREIGHT"),
        ("UK Telecom Ltd", "UK TELECOM LONDON", "UKT-902-", "GBP", "6060-TELECOM_UTILITIES"),
        ("Bharat Tech Services", "BHARAT TECH BANGALORE", "IND-303-", "INR", "6040-LEGAL_PROFESSIONAL"),
    ]

    ledger_rows = []
    bank_rows = []

    ledger_id_counter = 2000
    bank_id_counter = 7000

    # 1. 80 Exact & Near Match base transaction pairs
    for i in range(1, 81):
        vendor_name, bank_cp, ref_prefix, curr, gl_code = random.choice(enterprise_vendors)
        ref_id = f"{ref_prefix}{100 + i}"

        # Standard amount
        amt = round(random.uniform(250.0, 18500.0), 2)
        txn_date = base_date + timedelta(days=random.randint(0, 28))

        is_credit = random.choice([True, False])
        ledger_amt = amt if is_credit else -amt

        l_id = f"LED-JUDGE-{ledger_id_counter}"
        ledger_id_counter += 1

        b_id = f"BNK-JUDGE-{bank_id_counter}"
        bank_id_counter += 1

        noise = random.choices(
            population=["exact", "date_shift", "rounding", "ref_variant", "fee_deduction"],
            weights=[0.40, 0.25, 0.15, 0.10, 0.10],
            k=1
        )[0]

        bank_date = txn_date
        bank_amt = ledger_amt
        bank_ref = ref_id

        if noise == "date_shift":
            bank_date = txn_date + timedelta(days=random.choice([-3, -2, -1, 1, 2, 3]))
        elif noise == "rounding":
            diff = random.choice([-0.25, -0.05, 0.05, 0.15, 0.35])
            bank_amt = round(ledger_amt + diff, 2)
        elif noise == "ref_variant":
            bank_ref = ref_id.replace("-", " ")
        elif noise == "fee_deduction":
            fee = round(abs(ledger_amt) * 0.029, 2)  # 2.9% Stripe/Processor fee
            bank_amt = round(ledger_amt - fee, 2) if ledger_amt > 0 else round(ledger_amt + fee, 2)

        ledger_rows.append({
            "record_id": l_id,
            "reference_id": ref_id,
            "amount": ledger_amt,
            "currency": curr,
            "transaction_date": txn_date.strftime("%Y-%m-%d"),
            "counterparty": vendor_name,
            "description": f"Internal ledger entry {ref_id} ({gl_code})"
        })

        bank_rows.append({
            "record_id": b_id,
            "reference_id": bank_ref,
            "amount": bank_amt,
            "currency": curr,
            "transaction_date": bank_date.strftime("%Y-%m-%d"),
            "counterparty": bank_cp,
            "description": f"BANK STATEMENT POSTING {bank_cp} {bank_ref}"
        })

    # 2. 5 Split Transactions (1 Ledger = 2 Bank Records)
    split_cases = [
        ("CloudScale Systems", "CS-SPLIT-901", 12000.00, 5000.00, 7000.00, 4),
        ("Stripe Billing", "STR-SPLIT-902", 25000.00, 10000.00, 15000.00, 9),
        ("Acme Corp", "ACME-SPLIT-903", 8500.00, 3500.00, 5000.00, 14),
        ("Apex Supplies", "APX-SPLIT-904", -6400.00, -3000.00, -3400.00, 18),
        ("Global Logistics LLC", "LOG-SPLIT-905", 14200.00, 6200.00, 8000.00, 22),
    ]

    for vendor, ref_id, total_amt, p1_amt, p2_amt, day_off in split_cases:
        txn_date = base_date + timedelta(days=day_off)
        l_id = f"LED-JUDGE-{ledger_id_counter}"
        ledger_id_counter += 1

        ledger_rows.append({
            "record_id": l_id,
            "reference_id": ref_id,
            "amount": total_amt,
            "currency": "USD",
            "transaction_date": txn_date.strftime("%Y-%m-%d"),
            "counterparty": vendor,
            "description": f"Bulk settlement invoice {ref_id}"
        })

        b_id1 = f"BNK-JUDGE-{bank_id_counter}"
        bank_id_counter += 1
        bank_rows.append({
            "record_id": b_id1,
            "reference_id": f"{ref_id}-PART1",
            "amount": p1_amt,
            "currency": "USD",
            "transaction_date": txn_date.strftime("%Y-%m-%d"),
            "counterparty": vendor.upper(),
            "description": f"Partial payout 1 of {ref_id}"
        })

        b_id2 = f"BNK-JUDGE-{bank_id_counter}"
        bank_id_counter += 1
        bank_rows.append({
            "record_id": b_id2,
            "reference_id": f"{ref_id}-PART2",
            "amount": p2_amt,
            "currency": "USD",
            "transaction_date": (txn_date + timedelta(days=1)).strftime("%Y-%m-%d"),
            "counterparty": vendor.upper(),
            "description": f"Partial payout 2 of {ref_id}"
        })

    # 3. 5 Structuring & Fraud Anomaly Injections
    anomalies = [
        ("BSA Structuring Suspect 1", "STRUCT-9950", 9950.00, 2),
        ("BSA Structuring Suspect 2", "STRUCT-9980", 9980.00, 11),
        ("Round Number Outlier 1", "ROUND-10000", 10000.00, 15),
        ("Round Number Outlier 2", "ROUND-25000", 25000.00, 21),
        ("Unidentified Phantom Payee", "PHANTOM-777", 8450.00, 25),
    ]

    for vendor, ref_id, amt, day_off in anomalies:
        txn_date = base_date + timedelta(days=day_off)
        l_id = f"LED-JUDGE-{ledger_id_counter}"
        ledger_id_counter += 1

        ledger_rows.append({
            "record_id": l_id,
            "reference_id": ref_id,
            "amount": amt,
            "currency": "USD",
            "transaction_date": txn_date.strftime("%Y-%m-%d"),
            "counterparty": vendor,
            "description": f"High risk anomaly test {ref_id}"
        })

    # 4. 8 Duplicates in Bank feed
    dupe_targets = random.sample(bank_rows[:30], 6)
    for target in dupe_targets:
        b_id_dupe = f"BNK-JUDGE-{bank_id_counter}"
        bank_id_counter += 1
        dupe_row = dict(target)
        dupe_row["record_id"] = b_id_dupe
        dupe_row["description"] = dupe_row["description"] + " (DUPLICATE POSTING)"
        bank_rows.append(dupe_row)

    # 5. 10 Ledger Orphans
    for i in range(1, 11):
        l_id = f"LED-JUDGE-{ledger_id_counter}"
        ledger_id_counter += 1
        ref_id = f"LED-ORPHAN-{400 + i}"
        txn_date = base_date + timedelta(days=random.randint(1, 28))
        ledger_rows.append({
            "record_id": l_id,
            "reference_id": ref_id,
            "amount": round(random.uniform(1200.0, 9800.0), 2),
            "currency": "USD",
            "transaction_date": txn_date.strftime("%Y-%m-%d"),
            "counterparty": f"Unmatched Internal Ledger Vendor {i}",
            "description": f"Internal accrual record {ref_id}"
        })

    # 6. 10 Bank Orphans
    for i in range(1, 11):
        b_id = f"BNK-JUDGE-{bank_id_counter}"
        bank_id_counter += 1
        ref_id = f"BNK-ORPHAN-{800 + i}"
        txn_date = base_date + timedelta(days=random.randint(1, 28))
        bank_rows.append({
            "record_id": b_id,
            "reference_id": ref_id,
            "amount": round(random.uniform(450.0, 4800.0), 2) * random.choice([1, -1]),
            "currency": "USD",
            "transaction_date": txn_date.strftime("%Y-%m-%d"),
            "counterparty": f"UNIDENTIFIED DIRECT BANK PAYEE {i}",
            "description": f"DIRECT BANK DEBIT {ref_id}"
        })

    random.shuffle(ledger_rows)
    random.shuffle(bank_rows)

    ledger_path = os.path.join(output_dir, "internal_ledger_judge.csv")
    bank_path = os.path.join(output_dir, "bank_feed_judge.csv")

    fieldnames = ["record_id", "reference_id", "amount", "currency", "transaction_date", "counterparty", "description"]

    with open(ledger_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(ledger_rows)

    with open(bank_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(bank_rows)

    # Also overwrite data/synthetic so UI "Use Synthetic Sample Data" runs this massive dataset live!
    synth_dir = "data/synthetic"
    os.makedirs(synth_dir, exist_ok=True)
    with open(os.path.join(synth_dir, "internal_ledger.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(ledger_rows)

    with open(os.path.join(synth_dir, "bank_feed.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(bank_rows)

    print("==========================================================================")
    print(f"  HUGE JUDGE DEMO DATASET GENERATED SUCCESSFULLY (Seed: {seed})")
    print(f"  Internal Ledger: {len(ledger_rows)} records -> {ledger_path}")
    print(f"  Bank Feed:       {len(bank_rows)} records -> {bank_path}")
    print(f"  TOTAL COMBINED:  {len(ledger_rows) + len(bank_rows)} input records")
    print("==========================================================================")

if __name__ == "__main__":
    generate_huge_judge_dataset()
