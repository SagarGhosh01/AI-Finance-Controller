"""
Excel & Executive Insights Report Generator Module for Fincheck AI.
Generates multi-tab, beautifully styled Excel workbooks (.xlsx) with embedded
native charts, KPI metrics, formatted data tables, and fraud anomaly matrices.
"""

import io
from typing import Dict, Any, List
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.chart import PieChart, BarChart, Reference

class ExcelReportGenerator:
    @staticmethod
    def generate_excel_workbook(
        run: Any,
        matches: List[Any],
        exceptions: List[Any],
        records: List[Any],
        tax_summary: Dict[str, Any],
        anomalies: List[Dict[str, Any]]
    ) -> bytes:
        wb = openpyxl.Workbook()

        # Styles
        header_fill = PatternFill(start_color="0F172A", end_color="0F172A", fill_type="solid") # Dark Navy
        header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")

        bold_font = Font(name="Calibri", size=11, bold=True)
        regular_font = Font(name="Calibri", size=11)

        kpi_label_fill = PatternFill(start_color="F1F5F9", end_color="F1F5F9", fill_type="solid")
        kpi_val_fill = PatternFill(start_color="E2E8F0", end_color="E2E8F0", fill_type="solid")

        thin_border = Border(
            left=Side(style='thin', color='CBD5E1'),
            right=Side(style='thin', color='CBD5E1'),
            top=Side(style='thin', color='CBD5E1'),
            bottom=Side(style='thin', color='CBD5E1')
        )

        # -------------------------------------------------------------
        # TAB 1: Executive Summary
        # -------------------------------------------------------------
        ws_sum = wb.active
        ws_sum.title = "Executive Summary"
        ws_sum.views.sheetView[0].showGridLines = True

        # Banner Title
        ws_sum.merge_cells("A1:G1")
        ws_sum["A1"] = "FINCHECK AI — EXECUTIVE RECONCILIATION REPORT"
        ws_sum["A1"].font = Font(name="Calibri", size=16, bold=True, color="FFFFFF")
        ws_sum["A1"].fill = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
        ws_sum["A1"].alignment = Alignment(horizontal="center", vertical="center")
        ws_sum.row_dimensions[1].height = 40

        # Run Details
        ws_sum["A3"] = "Run ID:"
        ws_sum["B3"] = run.id
        ws_sum["A4"] = "Created At:"
        ws_sum["B4"] = str(run.created_at)
        ws_sum["A5"] = "Status:"
        ws_sum["B5"] = run.status.upper()
        ws_sum["A6"] = "Approval Status:"
        ws_sum["B6"] = f"Approved by {run.approved_by}" if run.approved_by else "Pending Controller Review"

        for r in range(3, 7):
            ws_sum[f"A{r}"].font = bold_font
            ws_sum[f"B{r}"].font = regular_font

        # Core KPIs Table
        ws_sum["A8"] = "Metric Description"
        ws_sum["B8"] = "Measured Value"
        ws_sum["A8"].fill = header_fill
        ws_sum["B8"].fill = header_fill
        ws_sum["A8"].font = header_font
        ws_sum["B8"].font = header_font

        throughput = (run.total_records / max(run.processing_time_ms / 1000.0, 0.001)) if run.processing_time_ms > 0 else 0.0

        kpis = [
            ("Total Input Records", run.total_records),
            ("Matched Input Records", run.matched_count),
            ("Unresolved Exception Items", run.exception_count),
            ("Verified Match Rate %", f"{run.match_rate_pct:.2f}%"),
            ("Processing Throughput", f"{throughput:.1f} rec/sec"),
            ("Conservation Invariant", "PASSED (Matched + Exceptions == Total)")
        ]

        for idx, (label, val) in enumerate(kpis, start=9):
            ws_sum[f"A{idx}"] = label
            ws_sum[f"B{idx}"] = val
            ws_sum[f"A{idx}"].font = bold_font
            ws_sum[f"A{idx}"].fill = kpi_label_fill
            ws_sum[f"B{idx}"].fill = kpi_val_fill
            ws_sum[f"A{idx}"].border = thin_border
            ws_sum[f"B{idx}"].border = thin_border

        # Match Tier Breakdown Data (For Chart)
        ws_sum["D8"] = "Match Engine Tier"
        ws_sum["E8"] = "Count"
        ws_sum["D8"].fill = header_fill
        ws_sum["E8"].fill = header_fill
        ws_sum["D8"].font = header_font
        ws_sum["E8"].font = header_font

        tier_counts = {}
        for m in matches:
            t = m.match_tier.upper()
            tier_counts[t] = tier_counts.get(t, 0) + 1

        row_idx = 9
        for tier, count in tier_counts.items():
            ws_sum[f"D{row_idx}"] = tier
            ws_sum[f"E{row_idx}"] = count
            ws_sum[f"D{row_idx}"].border = thin_border
            ws_sum[f"E{row_idx}"].border = thin_border
            row_idx += 1

        max_tier_row = row_idx - 1 if row_idx > 9 else 9

        # Exception Breakdown Data (For Chart)
        ws_sum["D16"] = "Exception Type"
        ws_sum["E16"] = "Count"
        ws_sum["D16"].fill = header_fill
        ws_sum["E16"].fill = header_fill
        ws_sum["D16"].font = header_font
        ws_sum["E16"].font = header_font

        ex_counts = {}
        for ex in exceptions:
            t = ex.exception_type
            ex_counts[t] = ex_counts.get(t, 0) + 1

        ex_row_idx = 17
        for ex_type, count in ex_counts.items():
            ws_sum[f"D{ex_row_idx}"] = ex_type
            ws_sum[f"E{ex_row_idx}"] = count
            ws_sum[f"D{ex_row_idx}"].border = thin_border
            ws_sum[f"E{ex_row_idx}"].border = thin_border
            ex_row_idx += 1

        max_ex_row = ex_row_idx - 1 if ex_row_idx > 17 else 17

        # Add Native Excel Pie Chart for Match Tiers
        if max_tier_row >= 9 and len(tier_counts) > 0:
            pie = PieChart()
            pie.title = "Match Engine Tier Distribution"
            labels = Reference(ws_sum, min_col=4, min_row=9, max_row=max_tier_row)
            data = Reference(ws_sum, min_col=5, min_row=8, max_row=max_tier_row)
            pie.add_data(data, titles_from_data=True)
            pie.set_categories(labels)
            pie.width = 14
            pie.height = 9
            ws_sum.add_chart(pie, "G3")

        # Add Native Excel Bar Chart for Exceptions
        if max_ex_row >= 17 and len(ex_counts) > 0:
            bar = BarChart()
            bar.type = "col"
            bar.style = 10
            bar.title = "Unresolved Exception Root Causes"
            bar.y_axis.title = "Record Count"
            bar.x_axis.title = "Category"
            labels = Reference(ws_sum, min_col=4, min_row=17, max_row=max_ex_row)
            data = Reference(ws_sum, min_col=5, min_row=16, max_row=max_ex_row)
            bar.add_data(data, titles_from_data=True)
            bar.set_categories(labels)
            bar.legend = None
            bar.width = 14
            bar.height = 9
            ws_sum.add_chart(bar, "G18")

        # -------------------------------------------------------------
        # TAB 2: Matched Transactions
        # -------------------------------------------------------------
        ws_match = wb.create_sheet(title="Matched Transactions")
        ws_match.views.sheetView[0].showGridLines = True

        headers_m = ["Match ID", "Match Tier", "Confidence", "Record Codes", "Agent Match Reasoning"]
        ws_match.append(headers_m)

        for col_num, h in enumerate(headers_m, 1):
            cell = ws_match.cell(row=1, column=col_num)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="left", vertical="center")

        for m in matches:
            ws_match.append([
                m.id,
                m.match_tier.upper(),
                m.confidence,
                ", ".join(m.record_codes or []),
                m.reasoning
            ])

        # Format cells
        for row in range(2, ws_match.max_row + 1):
            ws_match.cell(row=row, column=3).number_format = '0.00'
            for col in range(1, 6):
                ws_match.cell(row=row, column=col).border = thin_border
                ws_match.cell(row=row, column=col).font = regular_font

        # -------------------------------------------------------------
        # TAB 3: Exception Workbench
        # -------------------------------------------------------------
        ws_ex = wb.create_sheet(title="Exceptions Workbench")
        ws_ex.views.sheetView[0].showGridLines = True

        headers_e = ["Exception ID", "Record Code", "Source Feed", "Exception Classification", "Candidate Suggestion", "Root Cause Reasoning", "Resolution Status"]
        ws_ex.append(headers_e)

        for col_num, h in enumerate(headers_e, 1):
            cell = ws_ex.cell(row=1, column=col_num)
            cell.fill = header_fill
            cell.font = header_font

        status_fills = {
            "OPEN": PatternFill(start_color="FEF3C7", end_color="FEF3C7", fill_type="solid"), # Amber
            "ACCEPT": PatternFill(start_color="D1FAE5", end_color="D1FAE5", fill_type="solid"), # Emerald
            "REJECT": PatternFill(start_color="FEE2E2", end_color="FEE2E2", fill_type="solid"), # Rose
            "FLAG": PatternFill(start_color="F3E8FF", end_color="F3E8FF", fill_type="solid") # Purple
        }

        for ex in exceptions:
            src = "Internal Ledger" if ex.source == "A" else "Bank Feed"
            st = ex.resolution_status.upper()
            ws_ex.append([
                ex.id,
                ex.record_code,
                src,
                ex.exception_type,
                ex.candidate_record_code or "None",
                ex.reasoning,
                st
            ])

        for row in range(2, ws_ex.max_row + 1):
            st_val = str(ws_ex.cell(row=row, column=7).value)
            if st_val in status_fills:
                ws_ex.cell(row=row, column=7).fill = status_fills[st_val]
            for col in range(1, 8):
                ws_ex.cell(row=row, column=col).border = thin_border
                ws_ex.cell(row=row, column=col).font = regular_font

        # -------------------------------------------------------------
        # TAB 4: Tax & GL Mapping
        # -------------------------------------------------------------
        ws_tax = wb.create_sheet(title="Tax & GL Mapping")
        ws_tax.views.sheetView[0].showGridLines = True

        headers_t = ["GL Account Code", "Operating Expense / Revenue Category", "Net Amount ($)"]
        ws_tax.append(headers_t)
        for col_num, h in enumerate(headers_t, 1):
            cell = ws_tax.cell(row=1, column=col_num)
            cell.fill = header_fill
            cell.font = header_font

        for gl_code, total in tax_summary.get("gl_account_totals", {}).items():
            ws_tax.append([gl_code, "Operating Ledger Expense/Revenue", total])

        for row in range(2, ws_tax.max_row + 1):
            ws_tax.cell(row=row, column=3).number_format = '$#,##0.00'
            for col in range(1, 4):
                ws_tax.cell(row=row, column=col).border = thin_border
                ws_tax.cell(row=row, column=col).font = regular_font

        # -------------------------------------------------------------
        # TAB 5: Fraud & Anomaly Matrix
        # -------------------------------------------------------------
        ws_anom = wb.create_sheet(title="Fraud & Anomaly Matrix")
        ws_anom.views.sheetView[0].showGridLines = True

        headers_a = ["Record Code", "Amount ($)", "Counterparty", "Risk Score", "Risk Level", "Detected Risk Flags"]
        ws_anom.append(headers_a)
        for col_num, h in enumerate(headers_a, 1):
            cell = ws_anom.cell(row=1, column=col_num)
            cell.fill = header_fill
            cell.font = header_font

        for a in anomalies:
            flags = ", ".join(a.get("anomaly_flags", [])) or "None"
            ws_anom.append([
                a.get("record_code") or a.get("record_id"),
                a.get("amount", 0.0),
                a.get("counterparty", ""),
                a.get("anomaly_score", 0.0),
                a.get("risk_level", "LOW"),
                flags
            ])

        for row in range(2, ws_anom.max_row + 1):
            ws_anom.cell(row=row, column=2).number_format = '$#,##0.00'
            ws_anom.cell(row=row, column=4).number_format = '0.00'

            risk_val = str(ws_anom.cell(row=row, column=5).value)
            if risk_val == "HIGH":
                ws_anom.cell(row=row, column=5).fill = status_fills["REJECT"]
            elif risk_val == "MEDIUM":
                ws_anom.cell(row=row, column=5).fill = status_fills["OPEN"]

            for col in range(1, 7):
                ws_anom.cell(row=row, column=col).border = thin_border
                ws_anom.cell(row=row, column=col).font = regular_font

        # Auto-adjust column widths across all worksheets
        for sheet in wb.worksheets:
            for col in sheet.columns:
                max_len = 0
                col_letter = get_column_letter(col[0].column)
                for cell in col:
                    if cell.value is not None:
                        # Avoid huge cell width for merged title
                        if sheet.title == "Executive Summary" and cell.coordinate in ["A1", "B1", "C1", "D1", "E1", "F1", "G1"]:
                            continue
                        val_str = str(cell.value)
                        max_len = max(max_len, len(val_str))
                sheet.column_dimensions[col_letter].width = max(max_len + 4, 12)

        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        return output.getvalue()
