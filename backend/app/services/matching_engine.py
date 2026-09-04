"""
Pure deterministic matching engine (Tier 1).
No database dependencies — pure data structures in, matches and remaining unmatched records out.
"""

from typing import List, Dict, Any, Tuple, Set
from datetime import datetime
from rapidfuzz import fuzz

def parse_date(date_str: str) -> datetime:
    return datetime.strptime(date_str, "%Y-%m-%d")

def clean_str(s: str) -> str:
    if not s:
        return ""
    return str(s).strip().upper()

def days_diff(d1: str, d2: str) -> int:
    try:
        return abs((parse_date(d1) - parse_date(d2)).days)
    except Exception:
        return 999

class Tier1DeterministicMatcher:
    def __init__(
        self,
        amount_tolerance: float = 0.50,
        date_tolerance_days: int = 3,
        fuzzy_threshold: float = 0.85
    ):
        self.amount_tolerance = amount_tolerance
        self.date_tolerance_days = date_tolerance_days
        self.fuzzy_threshold = fuzzy_threshold

    def run(
        self,
        records_a: List[Dict[str, Any]],
        records_b: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Executes Tier 1 deterministic passes.
        Returns:
            (matches, duplicates, remaining_a, remaining_b)
        """
        matched_a_ids: Set[str] = set()
        matched_b_ids: Set[str] = set()
        matches: List[Dict[str, Any]] = []
        duplicates: List[Dict[str, Any]] = []

        # Pass 0: Detect Duplicates within Source B
        b_seen: Dict[Tuple[str, float], List[Dict[str, Any]]] = {}
        for r_b in records_b:
            key = (clean_str(r_b.get("reference_id")), round(r_b.get("amount", 0.0), 2))
            if key[0]:
                b_seen.setdefault(key, []).append(r_b)

        for key, r_list in b_seen.items():
            if len(r_list) > 1:
                # Keep the first one as primary, mark others as duplicate suspects
                for dup_rec in r_list[1:]:
                    duplicates.append({
                        "record": dup_rec,
                        "primary_record": r_list[0],
                        "reasoning": f"Duplicate transaction detected in Bank Feed matching reference '{key[0]}' and amount ${key[1]:.2f}"
                    })

        # Pass 1: Exact Reference + Exact Amount (±$0.01)
        for r_a in records_a:
            if r_a["id"] in matched_a_ids:
                continue
            ref_a = clean_str(r_a.get("reference_id"))
            amt_a = r_a.get("amount", 0.0)

            if not ref_a:
                continue

            for r_b in records_b:
                if r_b["id"] in matched_b_ids:
                    continue

                ref_b = clean_str(r_b.get("reference_id"))
                amt_b = r_b.get("amount", 0.0)

                if ref_a == ref_b and abs(amt_a - amt_b) <= 0.01:
                    matched_a_ids.add(r_a["id"])
                    matched_b_ids.add(r_b["id"])
                    matches.append({
                        "record_ids": [r_a["id"], r_b["id"]],
                        "record_codes": [r_a["record_id"], r_b["record_id"]],
                        "match_tier": "exact",
                        "confidence": 1.0,
                        "reasoning": f"Exact match on reference '{r_a.get('reference_id')}' and amount ${amt_a:.2f}"
                    })
                    break

        # Pass 2: Split Transaction Match (1 Ledger record = 2 Bank records)
        for r_a in records_a:
            if r_a["id"] in matched_a_ids:
                continue
            amt_a = r_a.get("amount", 0.0)
            ref_a = clean_str(r_a.get("reference_id"))

            unmatched_b_avail = [r for r in records_b if r["id"] not in matched_b_ids]
            n_avail = len(unmatched_b_avail)

            found_split = False
            for i in range(n_avail):
                for j in range(i + 1, n_avail):
                    rb1 = unmatched_b_avail[i]
                    rb2 = unmatched_b_avail[j]
                    sum_b = rb1.get("amount", 0.0) + rb2.get("amount", 0.0)

                    if abs(amt_a - sum_b) <= 0.05:
                        # Check reference similarity or prefix match
                        ref_b1 = clean_str(rb1.get("reference_id"))
                        ref_b2 = clean_str(rb2.get("reference_id"))

                        if ref_a in ref_b1 or ref_a in ref_b2 or "SPLIT" in ref_a or "PART" in ref_b1 or "PART" in ref_b2:
                            matched_a_ids.add(r_a["id"])
                            matched_b_ids.add(rb1["id"])
                            matched_b_ids.add(rb2["id"])
                            matches.append({
                                "record_ids": [r_a["id"], rb1["id"], rb2["id"]],
                                "record_codes": [r_a["record_id"], rb1["record_id"], rb2["record_id"]],
                                "match_tier": "split",
                                "confidence": 0.95,
                                "reasoning": f"Split transaction match: Ledger record ${amt_a:.2f} matches bank items ${rb1.get('amount'):.2f} + ${rb2.get('amount'):.2f}"
                            })
                            found_split = True
                            break
                if found_split:
                    break

        # Pass 3: Tolerant Match (Amount within tolerance OR date within tolerance AND fuzzy reference match)
        for r_a in records_a:
            if r_a["id"] in matched_a_ids:
                continue
            amt_a = r_a.get("amount", 0.0)
            date_a = r_a.get("transaction_date", "")
            ref_a = clean_str(r_a.get("reference_id"))
            cp_a = clean_str(r_a.get("counterparty"))

            best_candidate = None
            best_score = 0.0
            best_reason = ""

            for r_b in records_b:
                if r_b["id"] in matched_b_ids:
                    continue

                amt_b = r_b.get("amount", 0.0)
                date_b = r_b.get("transaction_date", "")
                ref_b = clean_str(r_b.get("reference_id"))
                cp_b = clean_str(r_b.get("counterparty"))

                amt_diff = abs(amt_a - amt_b)
                d_diff = days_diff(date_a, date_b)

                ref_sim = fuzz.token_sort_ratio(ref_a, ref_b) / 100.0 if ref_a and ref_b else 0.0
                cp_sim = fuzz.token_sort_ratio(cp_a, cp_b) / 100.0 if cp_a and cp_b else 0.0

                combined_sim = max(ref_sim, cp_sim)

                if amt_diff <= self.amount_tolerance and d_diff <= self.date_tolerance_days and combined_sim >= self.fuzzy_threshold:
                    score = 0.90 + (0.10 * combined_sim)
                    reason = f"Tolerant match: amount diff ${amt_diff:.2f}, date diff {d_diff} days, text similarity {combined_sim*100:.1f}%"

                    if score > best_score:
                        best_score = score
                        best_candidate = r_b
                        best_reason = reason

            if best_candidate and best_score >= 0.85:
                matched_a_ids.add(r_a["id"])
                matched_b_ids.add(best_candidate["id"])
                matches.append({
                    "record_ids": [r_a["id"], best_candidate["id"]],
                    "record_codes": [r_a["record_id"], best_candidate["record_id"]],
                    "match_tier": "tolerant",
                    "confidence": round(best_score, 2),
                    "reasoning": best_reason
                })

        remaining_a = [r for r in records_a if r["id"] not in matched_a_ids]
        remaining_b = [r for r in records_b if r["id"] not in matched_b_ids]

        return matches, duplicates, remaining_a, remaining_b
