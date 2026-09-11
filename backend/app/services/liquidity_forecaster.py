"""
Predictive Cash Flow & Liquidity Forecasting Engine for Fincheck AI.
Generates 30-day daily cash projections, working capital velocity, and exception impact models.
"""

from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any

class LiquidityForecaster:
    @staticmethod
    def generate_30day_forecast(
        current_balance: float,
        matched_records: List[Dict[str, Any]],
        open_exceptions_count: int = 0
    ) -> Dict[str, Any]:
        """
        Generates 30-day forward liquidity forecast curve and velocity metrics.
        """
        # Calculate daily velocity from historical matched records
        inflows = [r.get("amount", 0.0) for r in matched_records if r.get("amount", 0.0) > 0]
        outflows = [abs(r.get("amount", 0.0)) for r in matched_records if r.get("amount", 0.0) < 0]

        total_inflow = sum(inflows)
        total_outflow = sum(outflows)

        # Average daily velocity assuming 30-day window
        avg_daily_inflow = total_inflow / 30.0 if total_inflow > 0 else 450.0
        avg_daily_outflow = total_outflow / 30.0 if total_outflow > 0 else 320.0
        net_daily_velocity = avg_daily_inflow - avg_daily_outflow

        base_date = datetime.now(timezone.utc)
        timeline = []

        running_conservative = current_balance
        running_optimistic = current_balance + (open_exceptions_count * 250.0) # Estimate recoverable exception value

        for i in range(1, 31):
            day_date = (base_date + timedelta(days=i)).strftime("%Y-%m-%d")

            # Project daily movement
            running_conservative += net_daily_velocity
            running_optimistic += (net_daily_velocity * 1.05)

            timeline.append({
                "day": i,
                "date": day_date,
                "conservative_balance": round(running_conservative, 2),
                "optimistic_balance": round(running_optimistic, 2),
                "net_daily_flow": round(net_daily_velocity, 2)
            })

        return {
            "current_confirmed_balance": round(current_balance, 2),
            "projected_30d_balance": round(running_conservative, 2),
            "optimistic_30d_balance": round(running_optimistic, 2),
            "net_daily_velocity": round(net_daily_velocity, 2),
            "avg_daily_inflow": round(avg_daily_inflow, 2),
            "avg_daily_outflow": round(avg_daily_outflow, 2),
            "open_exceptions_held_out": open_exceptions_count,
            "timeline": timeline
        }
