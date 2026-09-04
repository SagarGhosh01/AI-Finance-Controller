"""
Tier 2 LLM-assisted matching layer.
Uses Anthropic Claude Messages API (or structured fallback if API key unavailable)
with input caching, concurrency control, and low-temperature structured output.
"""

import os
import json
import hashlib
import asyncio
from typing import List, Dict, Any, Optional
from app.core.config import settings

class LLMMatcher:
    def __init__(self):
        self.api_key = settings.ANTHROPIC_API_KEY or os.getenv("ANTHROPIC_API_KEY")
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.semaphore = asyncio.Semaphore(settings.LLM_MAX_CONCURRENCY)

    def _hash_input(self, record_a: Dict[str, Any], candidates_b: List[Dict[str, Any]]) -> str:
        key_str = f"{record_a.get('id')}:{record_a.get('amount')}:{record_a.get('reference_id')}_"
        cand_keys = "-".join([f"{c.get('id')}:{c.get('amount')}" for c in candidates_b])
        return hashlib.sha256((key_str + cand_keys).encode("utf-8")).hexdigest()

    async def evaluate_pair(
        self,
        record_a: Dict[str, Any],
        candidates_b: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Evaluates an unmatched ledger record against top candidate bank feed records.
        Returns:
            {
                "match": bool,
                "matched_record_id": str | None,
                "confidence": float,
                "reasoning": str,
                "tokens_used": int,
                "llm_called": bool
            }
        """
        if not candidates_b:
            return {
                "match": False,
                "matched_record_id": None,
                "confidence": 0.0,
                "reasoning": "No candidate bank records found within Proximity window.",
                "tokens_used": 0,
                "llm_called": False
            }

        cache_key = self._hash_input(record_a, candidates_b)
        if cache_key in self.cache:
            res = dict(self.cache[cache_key])
            res["llm_called"] = False
            return res

        # Fallback if no API key
        if not self.api_key:
            fallback = {
                "match": False,
                "matched_record_id": None,
                "confidence": 0.0,
                "reasoning": "Anthropic API key not configured — record escalated to human review.",
                "tokens_used": 0,
                "llm_called": False
            }
            self.cache[cache_key] = fallback
            return fallback

        async with self.semaphore:
            try:
                import anthropic

                client = anthropic.AsyncAnthropic(api_key=self.api_key)

                candidates_text = json.dumps([
                    {
                        "candidate_id": c.get("id"),
                        "record_code": c.get("record_id"),
                        "reference_id": c.get("reference_id"),
                        "amount": c.get("amount"),
                        "date": c.get("transaction_date"),
                        "counterparty": c.get("counterparty"),
                        "description": c.get("description")
                    } for c in candidates_b
                ], indent=2)

                prompt = f"""You are an expert AI Finance Controller specializing in transaction reconciliation.
Evaluate this UNMATCHED LEDGER TRANSACTION against the candidate BANK FEED TRANSACTIONS.

LEDGER TRANSACTION:
- Record Code: {record_a.get("record_id")}
- Reference ID: {record_a.get("reference_id")}
- Amount: ${record_a.get("amount")}
- Date: {record_a.get("transaction_date")}
- Counterparty: {record_a.get("counterparty")}
- Description: {record_a.get("description")}

CANDIDATE BANK FEED TRANSACTIONS:
{candidates_text}

INSTRUCTIONS:
1. Determine if any candidate matches the ledger transaction despite minor noise (e.g. typos in reference, minor fee deductions, date shifts).
2. If confident match (confidence >= 0.75), set "match": true, specify "matched_record_id" (candidate_id), "confidence" (0.0 to 1.0), and concise "reasoning".
3. If no match is confident, set "match": false, "matched_record_id": null, "confidence": 0.0, and state reasoning.
4. Output MUST be strictly valid JSON matching this schema:
{{
  "match": boolean,
  "matched_record_id": string or null,
  "confidence": float,
  "reasoning": string
}}"""

                response = await client.messages.create(
                    model="claude-3-haiku-20240307",
                    max_tokens=300,
                    temperature=0.1,
                    messages=[{"role": "user", "content": prompt}]
                )

                content_text = response.content[0].text.strip()
                # Parse JSON response
                if "```json" in content_text:
                    content_text = content_text.split("```json")[1].split("```")[0].strip()
                elif "```" in content_text:
                    content_text = content_text.split("```")[1].split("```")[0].strip()

                parsed = json.loads(content_text)
                tokens_used = (response.usage.input_tokens + response.usage.output_tokens) if response.usage else 150

                result = {
                    "match": bool(parsed.get("match", False)),
                    "matched_record_id": parsed.get("matched_record_id"),
                    "confidence": float(parsed.get("confidence", 0.0)),
                    "reasoning": parsed.get("reasoning", "LLM evaluation completed."),
                    "tokens_used": tokens_used,
                    "llm_called": True
                }

                self.cache[cache_key] = result
                return result

            except Exception as e:
                error_fallback = {
                    "match": False,
                    "matched_record_id": None,
                    "confidence": 0.0,
                    "reasoning": f"LLM matching error ({type(e).__name__}): {str(e)}",
                    "tokens_used": 0,
                    "llm_called": True
                }
                return error_fallback
