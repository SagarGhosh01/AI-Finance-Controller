"""
Real Financial Data Parser & Live Connector Module.
Flexibly normalizes real bank statements, payment processor feeds (Stripe, Razorpay, QuickBooks, Xero),
and custom CSV exports into standardized transaction objects.
"""

import io
import csv
import re
from datetime import datetime, timezone
from typing import List, Dict, Any, Tuple

def parse_amount(val: Any) -> float:
    if val is None:
        return 0.0
    s = str(val).strip()
    if not s:
        return 0.0
    # Remove currency symbols and commas e.g. "$1,250.50" -> "1250.50"
    clean_s = re.sub(r"[^\d\.\-\+]", "", s)
    try:
        return float(clean_s)
    except ValueError:
        return 0.0

def normalize_date(date_str: Any) -> str:
    if not date_str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")
    s = str(date_str).strip()

    # Try common financial date formats
    formats = [
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%m/%d/%Y",
        "%Y/%m/%d",
        "%d-%m-%Y",
        "%m-%d-%Y",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%SZ",
        "%b %d, %Y"
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(s.split(" ")[0], fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue

    return s

class RealDataParser:
    @staticmethod
    def parse_csv(csv_content: str, source_label: str = "A") -> List[Dict[str, Any]]:
        """
        Flexibly parses any real bank statement or ledger CSV, auto-detecting column headers.
        """
        reader = csv.DictReader(io.StringIO(csv_content))
        rows = list(reader)

        if not rows:
            return []

        # Auto-detect column headers
        sample_row = rows[0]
        headers = {k.lower().strip().replace("_", ""): k for k in sample_row.keys() if k}

        # Candidate column mappings
        rec_id_col = next((headers[k] for k in ["recordid", "txnid", "transactionid", "id", "refno"] if k in headers), None)
        ref_id_col = next((headers[k] for k in ["referenceid", "reference", "invoicenumber", "invoice", "ref", "paymentid", "description"] if k in headers), None)
        amt_col = next((headers[k] for k in ["amount", "txnamount", "netamount", "total", "val"] if k in headers), None)
        debit_col = next((headers[k] for k in ["debit", "debitamount", "paidout"] if k in headers), None)
        credit_col = next((headers[k] for k in ["credit", "creditamount", "received"] if k in headers), None)
        date_col = next((headers[k] for k in ["transactiondate", "date", "txndate", "createdat", "postingdate"] if k in headers), None)
        cp_col = next((headers[k] for k in ["counterparty", "payee", "merchant", "customer", "vendor", "description", "name"] if k in headers), None)

        normalized_records = []
        row_num = 1000

        for r in rows:
            row_num += 1

            # Extract amount
            amt = 0.0
            if amt_col and r.get(amt_col):
                amt = parse_amount(r[amt_col])
            elif debit_col and r.get(debit_col):
                amt = -abs(parse_amount(r[debit_col]))
            elif credit_col and r.get(credit_col):
                amt = abs(parse_amount(r[credit_col]))

            # Extract reference & ID
            rec_id = str(r.get(rec_id_col)) if rec_id_col and r.get(rec_id_col) else f"{'LED' if source_label == 'A' else 'BNK'}-REAL-{row_num}"
            ref_id = str(r.get(ref_id_col)) if ref_id_col and r.get(ref_id_col) else rec_id

            txn_date = normalize_date(r.get(date_col)) if date_col else datetime.now(timezone.utc).strftime("%Y-%m-%d")
            counterparty = str(r.get(cp_col, "Real Financial Transaction"))

            normalized_records.append({
                "record_id": rec_id,
                "reference_id": ref_id,
                "amount": round(amt, 2),
                "currency": str(r.get("currency", "USD")),
                "transaction_date": txn_date,
                "counterparty": counterparty,
                "description": str(r.get("description", f"Real financial record from {source_label}"))
            })

        return normalized_records
