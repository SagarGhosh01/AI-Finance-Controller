"""
Tax Category & General Ledger (GL) Auto-Classifier Module.
Maps transactions to standard GL chart of accounts and IRS tax schedule categories.
"""

from typing import Dict, Any

class TaxGLClassifier:
    TAX_GL_MAP = [
        (["CLOUDSCALE", "SAAS", "SOFTWARE", "AWS", "HOSTING"], "6010-SOFTWARE_SAAS", "Software & Cloud Infrastructure"),
        (["LOGISTICS", "FREIGHT", "SHIPPING", "DELTA FREIGHT"], "6020-LOGISTICS_FREIGHT", "Freight & Delivery Expenses"),
        (["SUPPLIES", "APEX", "MATERIALS", "OFFICE"], "6030-OFFICE_SUPPLIES", "Office & Operating Supplies"),
        (["LEGAL", "LAW", "ATTORNEY", "PINNACLE"], "6040-LEGAL_PROFESSIONAL", "Legal & Professional Services"),
        (["REAL ESTATE", "LEASE", "RENT", "SUMMIT"], "6050-REAL_ESTATE_LEASE", "Occupancy & Facility Rent"),
        (["TELECOM", "TEL", "COMM", "HORIZON"], "6060-TELECOM_UTILITIES", "Utilities & Communications"),
        (["MARKETING", "MKTG", "ADVERTISING", "VANGUARD"], "6070-MARKETING_ADVERTISING", "Marketing & Growth"),
        (["ACME", "CLIENT", "PAYMENT", "INVOICE"], "4010-REVENUE_SALES", "Gross Commercial Revenue"),
    ]

    @staticmethod
    def classify(counterparty: str, description: str, amount: float) -> Dict[str, str]:
        text = f"{str(counterparty).upper()} {str(description).upper()}"

        for keywords, gl_code, tax_cat in TaxGLClassifier.TAX_GL_MAP:
            if any(kw in text for kw in keywords):
                return {
                    "gl_account_code": gl_code,
                    "tax_category": tax_cat,
                    "schedule_line": "Form 1120 / Schedule C - Operating Expenses" if amount < 0 else "Form 1120 - Gross Receipts"
                }

        # Default fallback
        if amount >= 0:
            return {
                "gl_account_code": "4090-MISC_REVENUE",
                "tax_category": "Other Commercial Income",
                "schedule_line": "Form 1120 - Gross Income"
            }
        else:
            return {
                "gl_account_code": "6090-MISC_OPERATING_EXPENSE",
                "tax_category": "General & Administrative Expense",
                "schedule_line": "Form 1120 - Other Deductions"
            }
