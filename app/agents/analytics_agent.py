"""
Analytics AI Agent
Generates business reports and tracks KPIs with trend analysis and recommendations.
"""

import logging
import json
from datetime import datetime, timedelta
from typing import Optional, List
import anthropic

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AnalyticsAgent:
    """
    Autonomous analytics agent that:
    - Generates daily/weekly business reports
    - Tracks KPIs (MRR, churn, conversion, usage, CAC)
    - Identifies trends and anomalies
    - Sends weekly summary emails
    - Recommends actions based on data
    - Generates chart data for dashboards
    - Monitors API costs and usage
    """

    def __init__(self, config: Optional[dict] = None):
        """
        Initialize the Analytics Agent.

        Args:
            config: Configuration dictionary with API keys and settings
        """
        self.config = config or {}
        self.client = anthropic.Anthropic(
            api_key=self.config.get("anthropic_api_key", "")
        )
        self.model = "claude-3-5-sonnet-20241022"
        self.kpi_history = []
        self.reports = []
        logger.info("Analytics Agent initialized")

    def calculate_kpis(self, business_data: dict) -> dict:
        """
        Calculate key performance indicators from business data.

        Args:
            business_data: Dictionary with revenue, users, usage, and cost data

        Returns:
            Dictionary with calculated KPIs
        """
        kpi_prompt = f"""Analyze this business data and calculate KPIs.

Business Data:
{json.dumps(business_data, indent=2)}

Calculate and analyze:
1. MRR (Monthly Recurring Revenue)
2. Churn Rate (% customers lost)
3. Conversion Rate (free to paid)
4. Customer Acquisition Cost (CAC)
5. Customer Lifetime Value (LTV)
6. Usage Metrics (API calls, tokens used)
7. Growth Rate (month-over-month)

Format as JSON:
{{
    "mrr": {{"current": 0, "change_percent": 0.0, "status": "up|down|stable"}},
    "churn_rate": {{"percent": 0.0, "status": "high|medium|low"}},
    "conversion_rate": {{"percent": 0.0, "target": 0.0}},
    "cac": {{"amount": 0.0, "roi": 0.0}},
    "ltv": {{"amount": 0.0, "ltv_to_cac_ratio": 0.0}},
    "api_usage": {{"calls_this_month": 0, "percent_of_limit": 0.0}},
    "growth_rate": {{"percent": 0.0, "trend": "accelerating|stable|decelerating"}},
    "health_score": "0-100"
}}"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1500,
                messages=[{"role": "user", "content": kpi_prompt}]
            )

            result = json.loads(response.content[0].text)
            result["calculated_at"] = datetime.now().isoformat()
            self.kpi_history.append(result)

            logger.info("KPIs calculated successfully")
            return result
        except Exception as e:
            logger.error(f"KPI calculation error: {e}")
            return {"error": str(e)}

    def generate_daily_report(self, daily_metrics: dict) -> dict:
        """
        Generate a daily business report.

        Args:
            daily_metrics: Dictionary with daily metrics

        Returns:
            Dictionary with report content
        """
        report_prompt = f"""Generate a concise daily business report.

Daily Metrics:
{json.dumps(daily_metrics, indent=2)}

Include:
1. Executive Summary (key metrics and status)
2. Highlights (what went well)
3. Concerns (any issues or anomalies)
4. Daily Growth Metrics
5. API Health Status

Format as JSON:
{{
    "date": "YYYY-MM-DD",
    "type": "daily",
    "executive_summary": "Brief overview",
    "highlights": ["Achievement 1", "Achievement 2"],
    "concerns": ["Issue 1", "Issue 2"],
    "metrics": {{
        "new_signups": 0,
        "api_calls": 0,
        "active_users": 0,
        "revenue": 0.0
    }},
    "api_health": "healthy|degraded|down"
}}"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1500,
                messages=[{"role": "user", "content": report_prompt}]
            )

            result = json.loads(response.content[0].text)
            self.reports.append(result)
            logger.info("Daily report generated")
            return result
        except Exception as e:
            logger.error(f"Daily report generation error: {e}")
            return {"error": str(e)}

    def generate_weekly_report(self, weekly_data: dict) -> dict:
        """
        Generate a comprehensive weekly business report.

        Args:
            weekly_data: Dictionary with weekly metrics and data

        Returns:
            Dictionary with weekly report and recommendations
        """
        report_prompt = f"""Generate a comprehensive weekly business report with strategic recommendations.

Weekly Data:
{json.dumps(weekly_data, indent=2)}

Analyze:
1. Revenue Trends (MRR movement)
2. Growth Metrics (new customers, signups)
3. Churn Analysis (lost customers, reasons)
4. Product Usage Patterns
5. Customer Satisfaction (support tickets, NPS)
6. Operational Metrics (API usage, costs)

For each section, provide:
- Current Performance
- Week-over-Week Change
- Status (target exceeded, on track, below target)
- Recommended Actions

Format as JSON:
{{
    "week": "2026-W12",
    "period": "2026-03-16 to 2026-03-22",
    "summary": "Overall business summary",
    "sections": {{
        "revenue": {{"mrr": 0, "growth": "0%", "status": "on_track"}},
        "growth": {{"new_customers": 0, "signups": 0, "conversion": "0%"}},
        "churn": {{"customers_lost": 0, "rate": "0%", "main_reasons": []}},
        "product_usage": {{"daily_active_users": 0, "api_calls": 0, "avg_session_duration": "mins"}},
        "support": {{"tickets": 0, "avg_response_time": "hrs", "nps_score": 0}},
        "operations": {{"api_costs": 0.0, "uptime": "99.9%", "error_rate": "0%"}}
    }},
    "recommendations": [
        {{"priority": "high", "action": "Action to take"}},
        {{"priority": "medium", "action": "Action to take"}}
    ]
}}"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2500,
                messages=[{"role": "user", "content": report_prompt}]
            )

            result = json.loads(response.content[0].text)
            self.reports.append(result)
            logger.info("Weekly report generated")
            return result
        except Exception as e:
            logger.error(f"Weekly report generation error: {e}")
            return {"error": str(e)}

    def identify_trends_and_anomalies(self, historical_data: List[dict]) -> dict:
        """
        Identify trends and anomalies in historical data.

        Args:
            historical_data: List of historical metrics

        Returns:
            Dictionary with trend and anomaly analysis
        """
        analysis_prompt = f"""Analyze this historical business data for trends and anomalies.

Historical Data (last 30 days):
{json.dumps(historical_data, indent=2)}

Identify:
1. Trends (increasing, decreasing, stable for each metric)
2. Anomalies (unusual spikes or drops)
3. Correlation Patterns (which metrics move together)
4. Forecast (next week prediction for key metrics)

Format as JSON:
{{
    "trends": [
        {{"metric": "MRR", "direction": "increasing", "rate": "5% per week"}},
        {{"metric": "Churn Rate", "direction": "decreasing", "rate": "0.5% reduction"}}
    ],
    "anomalies": [
        {{"date": "2026-03-20", "metric": "API Calls", "value": 0, "deviation": "50% above average", "possible_cause": "Marketing campaign"}}
    ],
    "correlations": [
        {{"metric1": "New Signups", "metric2": "API Calls", "correlation": "0.85 (strong positive)"}}
    ],
    "forecast": {{
        "mrr_next_week": 0.0,
        "churn_next_week": "0%",
        "confidence": "85%"
    }}
}}"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1500,
                messages=[{"role": "user", "content": analysis_prompt}]
            )

            result = json.loads(response.content[0].text)
            logger.info("Trend and anomaly analysis completed")
            return result
        except Exception as e:
            logger.error(f"Trend analysis error: {e}")
            return {"error": str(e)}

    def generate_recommendations(self, current_kpis: dict, trends: dict) -> List[dict]:
        """
        Generate data-driven business recommendations.

        Args:
            current_kpis: Current KPI values
            trends: Trend analysis data

        Returns:
            List of recommendations with priority and expected impact
        """
        recommendation_prompt = f"""Based on these KPIs and trends, generate strategic business recommendations.

Current KPIs:
{json.dumps(current_kpis, indent=2)}

Trends:
{json.dumps(trends, indent=2)}

Generate 5-7 actionable recommendations that:
1. Address underperforming metrics
2. Double down on what's working
3. Address emerging concerns
4. Capitalize on opportunities

For each recommendation include:
- Title and description
- Priority (high, medium, low)
- Expected impact on key metrics
- Implementation effort (low, medium, high)
- Timeline

Format as JSON array:
[
    {{
        "title": "Action Title",
        "description": "Detailed description",
        "priority": "high",
        "expected_impact": {{"metric": "MRR", "change": "+10%"}},
        "effort": "medium",
        "timeline": "2 weeks"
    }}
]"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[{"role": "user", "content": recommendation_prompt}]
            )

            recommendations = json.loads(response.content[0].text)
            logger.info(f"Generated {len(recommendations)} recommendations")
            return recommendations
        except Exception as e:
            logger.error(f"Recommendation generation error: {e}")
            return []

    def generate_dashboard_data(self, kpis: dict, historical_data: List[dict]) -> dict:
        """
        Generate data formatted for dashboard visualization.

        Args:
            kpis: Current KPI values
            historical_data: Historical data for charts

        Returns:
            Dictionary with chart-ready data
        """
        dashboard_prompt = f"""Format this business data for dashboard visualizations.

Current KPIs:
{json.dumps(kpis, indent=2)}

Historical Data:
{json.dumps(historical_data[:7], indent=2)}

Generate data for:
1. MRR Chart (line chart showing monthly trend)
2. Churn Rate Gauge (0-10% scale)
3. Conversion Funnel (free to paid breakdown)
4. Customer Growth (new vs total)
5. API Usage (current vs limit)
6. Revenue Breakdown (by plan tier)

Format as JSON:
{{
    "mrr_chart": {{"labels": ["date"], "data": [0]}},
    "churn_gauge": {{"value": 0.0, "target": 0.0}},
    "conversion_funnel": {{"free": 0, "trial": 0, "paid": 0}},
    "customer_growth": {{"new": 0, "total": 0, "growth_rate": "0%"}},
    "api_usage": {{"current": 0, "limit": 0, "percent": 0.0}},
    "revenue_breakdown": {{"starter": 0, "pro": 0, "agency": 0}}
}}"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1500,
                messages=[{"role": "user", "content": dashboard_prompt}]
            )

            dashboard_data = json.loads(response.content[0].text)
            logger.info("Dashboard data generated")
            return dashboard_data
        except Exception as e:
            logger.error(f"Dashboard data generation error: {e}")
            return {"error": str(e)}

    def monitor_api_costs(self, usage_data: dict) -> dict:
        """
        Monitor API costs and usage patterns.

        Args:
            usage_data: Dictionary with API usage and cost data

        Returns:
            Dictionary with cost analysis and alerts
        """
        cost_prompt = f"""Analyze API usage and costs.

Usage Data:
{json.dumps(usage_data, indent=2)}

Analyze:
1. Daily API Costs
2. Cost Trend (increasing, stable, decreasing)
3. Cost per Customer
4. Usage Patterns (peak times, heavy users)
5. Budget Status (% of monthly budget used)
6. Cost Optimization Opportunities

Format as JSON:
{{
    "daily_cost": 0.0,
    "monthly_projected": 0.0,
    "monthly_budget": 0.0,
    "budget_percent_used": 0.0,
    "cost_trend": "increasing|stable|decreasing",
    "cost_per_customer": 0.0,
    "alerts": [
        {{"type": "budget_warning", "message": "X% of monthly budget spent"}}
    ],
    "optimization_opportunities": [
        {{"suggestion": "Opportunity", "potential_savings": "0%"}}
    ]
}}"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1500,
                messages=[{"role": "user", "content": cost_prompt}]
            )

            cost_analysis = json.loads(response.content[0].text)
            logger.info("API cost analysis completed")
            return cost_analysis
        except Exception as e:
            logger.error(f"Cost monitoring error: {e}")
            return {"error": str(e)}

    def run(self, report_type: str = "weekly", data: dict = None) -> dict:
        """
        Run the analytics agent.

        Args:
            report_type: Type of report ('daily', 'weekly', 'summary')
            data: Business data dictionary

        Returns:
            Dictionary with analytics results
        """
        logger.info(f"Running analytics agent - report type: {report_type}")

        if data is None:
            data = {}

        results = {}

        # Calculate KPIs
        kpis = self.calculate_kpis(data.get("business_data", {}))
        results["kpis"] = kpis

        # Generate appropriate report
        if report_type == "daily":
            results["report"] = self.generate_daily_report(data.get("daily_metrics", {}))
        elif report_type == "weekly":
            results["report"] = self.generate_weekly_report(data.get("weekly_data", {}))

        # Trend analysis
        if "historical_data" in data:
            results["trends"] = self.identify_trends_and_anomalies(data["historical_data"])
            results["recommendations"] = self.generate_recommendations(kpis, results["trends"])

        # Dashboard data
        if "historical_data" in data:
            results["dashboard"] = self.generate_dashboard_data(kpis, data["historical_data"])

        # API cost monitoring
        if "api_usage" in data:
            results["cost_analysis"] = self.monitor_api_costs(data["api_usage"])

        logger.info("Analytics agent run completed")
        return results


if __name__ == "__main__":
    # Example usage
    agent = AnalyticsAgent()

    print("=== Analytics Agent Demo ===\n")

    # Sample data
    business_data = {
        "mrr": 50000,
        "total_customers": 500,
        "new_customers_this_month": 45,
        "churned_customers": 8,
        "free_to_paid_conversions": 25,
        "cac": 300,
        "ltv": 3000,
        "api_calls_this_month": 5000000,
        "api_limit": 10000000,
        "api_cost": 1500
    }

    kpis = agent.calculate_kpis(business_data)
    print(f"MRR: ${kpis.get('mrr', {}).get('current', 'N/A')}")
    print(f"Churn Rate: {kpis.get('churn_rate', {}).get('percent', 'N/A')}%")
    print(f"Health Score: {kpis.get('health_score', 'N/A')}")
