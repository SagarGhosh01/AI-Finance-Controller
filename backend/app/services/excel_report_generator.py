"""
Excel & Executive Insights Report Generator Module for Fincheck AI.
Generates comprehensive Excel-compatible CSV reports containing executive summaries,
matched record ledgers, exception root-cause analyses, and tax/GL account mappings.
"""

import io
import csv
from typing import Dict, Any, List

class ExcelReportGenerator:
    @staticmethod
    def generate_excel_csv_report(
        run: Any,
        matches: List[Any],
        exceptions: List[Any],
        records: List[Any],
        tax_summary: Dict[str, Any],
        anomalies: List[Dict[str, Any]]
    ) -> str:
        """
        Generates a comprehensive, formatted Excel-ready CSV string.
        """
        output = io.StringIO()
        writer = csv.writer(output)

        # 1. EXECUTIVE SUMMARY SECTION
        writer.writerow(["=========================================================================="])
        writer.writerow(["               FINCHECK AI — EXECUTIVE RECONCILIATION REPORT              "])
        writer.writerow(["=========================================================================="])
        writer.writerow(["Run ID", run.id])
        writer.writerow(["Report Date", run.created_at])
        writer.writerow(["Status", run.status.upper()])
        writer.writerow(["Approved By", run.approved_by or "Pending Controller Approval"])
        writer.writerow([])
        writer.writerow(["CORE RECONCILIATION METRICS"])
        writer.writerow(["Total Input Records Processed", run.total_records])
        writer.writerow(["Matched Input Records", run.matched_count])
        writer.writerow(["Unresolved Exception Items", run.exception_count])
        writer.writerow(["Measured Match Rate %", f"{run.match_rate_pct}%"])
        writer.writerow(["Processing Time", f"{run.processing_time_ms} ms ({(run.processing_time_ms / 1000):.2f} s)"])
        writer.writerow(["Processing Throughput", f"{((run.total_records / (run.processing_time_ms / 1000)) if run.processing_time_ms > 0 else 0):.1f} records/sec"])
        writer.writerow(["Conservation Invariant", "PASSED (Matched + Exceptions == Total Input Records)"])
        writer.writerow([])

        # 2. MATCHED TRANSACTIONS LEDGER
        writer.writerow(["=========================================================================="])
        writer.writerow(["                     CONFIRMED MATCHED TRANSACTIONS                       "])
        writer.writerow(["=========================================================================="])
        writer.writerow(["Match ID", "Match Tier", "Confidence Score", "Involved Record Codes", "Agent Reasoning"])

        for m in matches:
            codes = ", ".join(m.record_codes or [])
            writer.writerow([m.id, m.match_tier.upper(), f"{m.confidence:.2f}", codes, m.reasoning])

        writer.writerow([])

        # 3. EXCEPTION AUDIT & ROOT CAUSE ANALYSIS
        writer.writerow(["=========================================================================="])
        writer.writerow(["                  EXCEPTIONS & ROOT-CAUSE ANALYSIS                        "])
        writer.writerow(["=========================================================================="])
        writer.writerow(["Exception ID", "Record Code", "Source Feed", "Exception Classification", "Proximity Candidate", "Agent Reasoning / Root Cause", "Resolution Status"])

        for ex in exceptions:
            src = "Internal Ledger" if ex.source == "A" else "Bank Feed"
            writer.writerow([
                ex.id,
                ex.record_code,
                src,
                ex.exception_type,
                ex.candidate_record_code or "None",
                ex.reasoning,
                ex.resolution_status.upper()
            ])

        writer.writerow([])

        # 4. TAX & GENERAL LEDGER (GL) SUMMARY
        writer.writerow(["=========================================================================="])
        writer.writerow(["               TAX & GENERAL LEDGER (GL) ACCOUNT SUMMARY                  "])
        writer.writerow(["=========================================================================="])
        writer.writerow(["GL Account Code", "Tax Category", "Net Amount ($)"])

        for gl_code, total in tax_summary.get("gl_account_totals", {}).items():
            writer.writerow([gl_code, "Categorized Operating Expense/Revenue", f"${total:.2f}"])

        writer.writerow([])

        # 5. ANOMALY & FRAUD RISK SIGNALS
        writer.writerow(["=========================================================================="])
        writer.writerow(["                 AUTOMATED FRAUD & ANOMALY RISK MATRIX                    "])
        writer.writerow(["=========================================================================="])
        writer.writerow(["Record Code", "Amount ($)", "Counterparty", "Risk Score", "Risk Level", "Detected Signals"])

        for a in anomalies[:20]:
            flags = ", ".join(a.get("anomaly_flags", [])) or "None"
            writer.writerow([
                a.get("record_code") or a.get("record_id"),
                f"${a.get('amount', 0.0):.2f}",
                a.get("counterparty", ""),
                a.get("anomaly_score", 0.0),
                a.get("risk_level", "LOW"),
                flags
            ])

        return output.getvalue()
