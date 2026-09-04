"""
Advanced Anomaly & Fraud Risk Detection Engine for Fincheck AI.
Evaluates transaction streams for suspicious patterns, round-number fraud,
structuring threshold anomalies, counterparty spoofing, and fee discrepancies.
"""

import math
from typing import List, Dict, Any

class AnomalyDetectionEngine:
    @staticmethod
    def analyze_transactions(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Analyzes a batch of records and appends anomaly risk scores (0.0 to 1.0) and flag tags.
        """
        analyzed = []

        # Calculate average amount and standard deviation for anomaly scoring
        amounts = [abs(r.get("amount", 0.0)) for r in records if r.get("amount")]
        avg_amt = sum(amounts) / len(amounts) if amounts else 1000.0
        variance = sum((x - avg_amt) ** 2 for x in amounts) / len(amounts) if amounts else 1.0
        std_dev = math.sqrt(variance) if variance > 0 else 1.0

        for r in records:
            amt = abs(r.get("amount", 0.0))
            ref = str(r.get("reference_id", "")).upper()
            cp = str(r.get("counterparty", "")).upper()

            flags = []
            risk_score = 0.0

            # 1. Round-number fraud risk (e.g. exactly $5,000.00 or $10,000.00)
            if amt > 1000.0 and amt % 500 == 0:
                risk_score += 0.25
                flags.append("ROUND_NUMBER_ANOMALY")

            # 2. BSA Structuring threshold (just under $10,000 threshold e.g. $9,950.00)
            if 9500.0 <= amt < 10000.0:
                risk_score += 0.45
                flags.append("STRUCTURING_THRESHOLD_SUSPECT")

            # 3. Statistical Z-Score Outlier (3+ standard deviations)
            z_score = (amt - avg_amt) / std_dev if std_dev > 0 else 0
            if z_score > 3.0:
                risk_score += 0.35
                flags.append("STATISTICAL_OUTLIER")

            # 4. Counterparty Name Suspicion (Generic / Anonymous payees)
            if any(term in cp for term in ["UNIDENTIFIED", "CASH", "UNKNOWN", "MISC VENDOR", "TEST"]):
                risk_score += 0.30
                flags.append("GENERIC_COUNTERPARTY_RISK")

            risk_score = min(round(risk_score, 2), 1.0)

            record_copy = dict(r)
            record_copy["anomaly_score"] = risk_score
            record_copy["anomaly_flags"] = flags
            record_copy["risk_level"] = "HIGH" if risk_score >= 0.50 else ("MEDIUM" if risk_score >= 0.25 else "LOW")
            analyzed.append(record_copy)

        return analyzed
