"""
Synthetic Data Generator for AI Finance Controller.
Generates two CSV files representing internal ledger and bank feed transactions
with controlled, realistic noise (date shifts, amount rounding, name variants,
duplicates, split transactions, and orphan records).
"""

import os
import csv
import random
from datetime import datetime, timedelta

def generate_synthetic_data(output_dir: str = "data/synthetic", seed: int = 42):
    random.seed(seed)
    os.makedirs(output_dir, exist_ok=True)

    base_date = datetime(2026, 8, 1)

    vendors_clients = [
        ("Acme Corp", "ACME CORP INC", "INV-2026-00"),
        ("Global Logistics LLC", "GLOBAL LOGISTICS", "LOG-884-"),
        ("CloudScale Systems", "CLOUDSCALE SYS PROV", "CS-991-"),
        ("Apex Supplies", "APEX SUP & MAT", "APX-330-"),
        ("Stripe Billing", "STRIPE TRANSFER", "STR-772-"),
        ("Vanguard Marketing", "VANGUARD MKTG AGENCY", "VNG-112-"),
        ("Horizon Telecom", "HORIZON TEL & COMM", "HT-554-"),
        ("Nexus Tech Solutions", "NEXUS TECH SOL", "NEX-401-"),
        ("Pinnacle Legal Services", "PINNACLE LEGAL LAW", "PIN-009-"),
        ("Summit Real Estate", "SUMMIT REALTY LEASE", "SRE-771-"), # Corrected spacing
        ("Delta Freight Co", "DELTA FREIGHT LOGISTICS", "DF-302-"),
        ("BioHealth Labs", "BIOHEALTH LAB TEST", "BHL-998-"),
    ]

    ledger_rows = []
    bank_rows = []

    ledger_id_counter = 1000
    bank_id_counter = 5000

    # 1. Generate ~45 Exact & Near Match base transaction pairs
    for i in range(1, 46):
        vendor_name, bank_counterparty, ref_prefix = random.choice(vendors_clients)
        ref_id = f"{ref_prefix}{100 + i}"
        amount = round(random.uniform(150.0, 12500.0), 2)
        txn_date = base_date + timedelta(days=random.randint(0, 25))

        is_credit = random.choice([True, False])
        ledger_amount = amount if is_credit else -amount

        l_id = f"LED-TXN-{ledger_id_counter}"
        ledger_id_counter += 1

        b_id = f"BNK-TXN-{bank_id_counter}"
        bank_id_counter += 1

        noise_type = random.choices(
            population=["exact", "date_shift", "amount_rounding", "ref_variant", "combined_minor_noise"],
            weights=[0.45, 0.20, 0.15, 0.10, 0.10],
            k=1
        )[0]

        bank_date = txn_date
        bank_amount = ledger_amount
        bank_ref = ref_id
        bank_cp = bank_counterparty

        if noise_type == "date_shift":
            bank_date = txn_date + timedelta(days=random.choice([-2, -1, 1, 2]))
        elif noise_type == "amount_rounding":
            diff = random.choice([-0.05, -0.01, 0.01, 0.02, 0.10, 0.25])
            bank_amount = round(ledger_amount + diff, 2)
        elif noise_type == "ref_variant":
            bank_ref = ref_id.replace("-", " ")
        elif noise_type == "combined_minor_noise":
            bank_date = txn_date + timedelta(days=random.choice([-1, 1]))
            bank_amount = round(ledger_amount + random.choice([-0.02, 0.02]), 2)
            bank_ref = ref_id.replace("-", "")

        ledger_rows.append({
            "record_id": l_id,
            "reference_id": ref_id,
            "amount": ledger_amount,
            "currency": "USD",
            "transaction_date": txn_date.strftime("%Y-%m-%d"),
            "counterparty": vendor_name,
            "description": f"Payment for invoice {ref_id}"
        })

        bank_rows.append({
            "record_id": b_id,
            "reference_id": bank_ref,
            "amount": bank_amount,
            "currency": "USD",
            "transaction_date": bank_date.strftime("%Y-%m-%d"),
            "counterparty": bank_cp,
            "description": f"BANK TRSF {bank_cp} {bank_ref}"
        })

    # 2. Ingest 3 Split Transactions (1 Ledger = 2 Bank Records)
    split_configs = [
        ("CloudScale Systems", "CS-SPLIT-801", 3500.00, 1500.00, 2000.00, 5),
        ("Apex Supplies", "APX-SPLIT-802", -4800.00, -2000.00, -2800.00, 10),
        ("Acme Corp", "ACME-SPLIT-803", 9200.00, 4200.00, 5000.00, 14),
    ]

    for vendor, ref_id, total_amt, part1_amt, part2_amt, day_offset in split_configs:
        txn_date = base_date + timedelta(days=day_offset)
        l_id = f"LED-TXN-{ledger_id_counter}"
        ledger_id_counter += 1

        ledger_rows.append({
            "record_id": l_id,
            "reference_id": ref_id,
            "amount": total_amt,
            "currency": "USD",
            "transaction_date": txn_date.strftime("%Y-%m-%d"),
            "counterparty": vendor,
            "description": f"Bulk invoice settlement {ref_id}"
        })

        b_id1 = f"BNK-TXN-{bank_id_counter}"
        bank_id_counter += 1
        bank_rows.append({
            "record_id": b_id1,
            "reference_id": f"{ref_id}-PART1",
            "amount": part1_amt,
            "currency": "USD",
            "transaction_date": txn_date.strftime("%Y-%m-%d"),
            "counterparty": vendor.upper(),
            "description": f"Partial payout 1 {ref_id}"
        })

        b_id2 = f"BNK-TXN-{bank_id_counter}"
        bank_id_counter += 1
        bank_rows.append({
            "record_id": b_id2,
            "reference_id": f"{ref_id}-PART2",
            "amount": part2_amt,
            "currency": "USD",
            "transaction_date": (txn_date + timedelta(days=1)).strftime("%Y-%m-%d"),
            "counterparty": vendor.upper(),
            "description": f"Partial payout 2 {ref_id}"
        })

    # 3. Ingest 4 Duplicates in Bank feed
    dupe_targets = random.sample(bank_rows[:20], 3)
    for target in dupe_targets:
        b_id_dupe = f"BNK-TXN-{bank_id_counter}"
        bank_id_counter += 1
        dupe_row = dict(target)
        dupe_row["record_id"] = b_id_dupe
        dupe_row["description"] = dupe_row["description"] + " (DUPLICATE FEE/POSTING)"
        bank_rows.append(dupe_row)

    # 4. Ingest 5 Ledger Orphans (Unmatched Ledger)
    for i in range(1, 6):
        l_id = f"LED-TXN-{ledger_id_counter}"
        ledger_id_counter += 1
        ref_id = f"LED-ORPHAN-{200 + i}"
        txn_date = base_date + timedelta(days=random.randint(1, 28))
        ledger_rows.append({
            "record_id": l_id,
            "reference_id": ref_id,
            "amount": round(random.uniform(500.0, 7500.0), 2),
            "currency": "USD",
            "transaction_date": txn_date.strftime("%Y-%m-%d"),
            "counterparty": f"Unmatched Ledger Vendor {i}",
            "description": f"Internal accrual record {ref_id}"
        })

    # 5. Ingest 5 Bank Orphans (Unmatched Bank)
    for i in range(1, 6):
        b_id = f"BNK-TXN-{bank_id_counter}"
        bank_id_counter += 1
        ref_id = f"BNK-ORPHAN-{700 + i}"
        txn_date = base_date + timedelta(days=random.randint(1, 28))
        bank_rows.append({
            "record_id": b_id,
            "reference_id": ref_id,
            "amount": round(random.uniform(100.0, 3200.0), 2) * random.choice([1, -1]),
            "currency": "USD",
            "transaction_date": txn_date.strftime("%Y-%m-%d"),
            "counterparty": f"UNIDENTIFIED BANK PAYEE {i}",
            "description": f"DIRECT BANK CHARGE {ref_id}"
        })

    # Shuffle rows to avoid artificial sequence ordering
    random.shuffle(ledger_rows)
    random.shuffle(bank_rows)

    # Write CSVs
    ledger_path = os.path.join(output_dir, "internal_ledger.csv")
    bank_path = os.path.join(output_dir, "bank_feed.csv")

    fieldnames = ["record_id", "reference_id", "amount", "currency", "transaction_date", "counterparty", "description"]

    with open(ledger_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(ledger_rows)

    with open(bank_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(bank_rows)

    print(f"Successfully generated synthetic dataset with seed={seed}:")
    print(f"  Internal Ledger: {len(ledger_rows)} records -> {ledger_path}")
    print(f"  Bank Feed:       {len(bank_rows)} records -> {bank_path}")
    print(f"  Total Combined:  {len(ledger_rows) + len(bank_rows)} input records")

if __name__ == "__main__":
    generate_synthetic_data()
