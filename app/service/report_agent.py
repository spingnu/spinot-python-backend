from __future__ import annotations

MARKET_OVERVIEW_TEMPLATE = """
**Market Sentiment:** {{market_sentiment}}
**Current Trends:** {{key_market_trends}}

The market today is showing signs of {{market_trend_summary}}. Major movements are expected in sectors like {{hot_sectors}}. Here’s what this could mean for your investments and associated risks.

#### Sources:
{% for source in market_overview_sources %}
- [{{source.title}}]({{source.link}})
{% endfor %}
"""

PORTFOLIO_HIGHLIGHTS_TEMPLATE = """
Below are the standout movements in your portfolio along with a risk analysis.

| Asset          | Current Price | Change (%) | Forecast Direction | Risk Level |
|----------------|---------------|------------|---------------------|------------|
{% for asset in portfolio %}
| {{asset.name}} | {{asset.current_price}} | {{asset.change_percent}} | {{asset.trend}} | {{asset.risk_level}} |
{% endfor %}

> **Insight:** Assets in {{gaining_sectors}} show potential gains, driven by {{related_news_or_trend}}, but note that assets in {{losing_sectors}} come with elevated risk due to {{risk_factors}}.

#### Sources:
{% for source in portfolio_sources %}
- [{{source.title}}]({{source.link}})
{% endfor %}
"""

NEWS_HIGHLIGHTS_TEMPLATE = """
Stay informed about key news impacting your portfolio and the associated risks.

{% for news in relevant_news %}
#### {{news.title}}
**Source:** {{news.source}}
**Impact on Portfolio:** {{news.impact_on_portfolio}}
**Risk Assessment:** {{news.risk_level}}
**Summary:** {{news.summary}}

{% endfor %}

#### Sources:
{% for source in news_sources %}
- [{{source.title}}]({{source.link}})
{% endfor %}
"""

FORECAST_SUMMARY_TEMPLATE = """
**Top Gainers:**
{% for gainer in top_gainers %}
- **{{gainer.name}}**: Expected to rise due to {{gainer.reason}}, **Risk Level:** {{gainer.risk_level}}
{% endfor %}

**Top Losers:**
{% for loser in top_losers %}
- **{{loser.name}}**: Expected to fall due to {{loser.reason}}, **Risk Level:** {{loser.risk_level}}
{% endfor %}

#### Sources:
{% for source in forecast_sources %}
- [{{source.title}}]({{source.link}})
{% endfor %}
"""

ANALYST_INSIGHTS_TEMPLATE = """
1. **Sector Analysis:** {{sector_analysis_summary}}
2. **Noteworthy Movements:** {{significant_movement_details}}
3. **Risk Mitigation Recommendations:**
   - **Consider Reducing Exposure To:** {{high_risk_assets}}
   - **Diversification Opportunities:** {{diversification_suggestions}}
4. **Investment Suggestions:**
   - **Consider Buying:** {{buy_recommendations}}
   - **Consider Selling:** {{sell_recommendations}}

#### Sources:
{% for source in insights_sources %}
- [{{source.title}}]({{source.link}})
{% endfor %}
"""

RISK_ALERT_TEMPLATE = """
- **Volatility Warning:** Assets in sectors like {{volatile_sectors}} have been particularly volatile, increasing risk exposure.
- **Macro Risks:** Ongoing events in {{affected_countries_or_sectors}} could impact your portfolio's value.
- **Currency Risks:** Exchange rate fluctuations could affect assets in {{currency_sensitive_assets}}.

#### Sources:
{% for source in risk_sources %}
- [{{source.title}}]({{source.link}})
{% endfor %}
"""

UPCOMING_EVENTS_TEMPLATE = """
Keep an eye on these upcoming events and associated risks.

| Date       | Event                   | Impact                    | Risk Level |
|------------|-------------------------|---------------------------|------------|
{% for event in upcoming_events %}
| {{event.date}} | {{event.name}} | {{event.impact}} | {{event.risk_level}} |
{% endfor %}

#### Sources:
{% for source in events_sources %}
- [{{source.title}}]({{source.link}})
{% endfor %}
"""

FINANCIAL_ANALYST_TAKE_TEMPLATE = """
> Our AI's expert advice for you today:
> **"{{daily_advice}}"**

> **Risk Advisory:**
> **"{{risk_advice}}"**

#### Sources:
{% for source in advisory_sources %}
- [{{source.title}}]({{source.link}})
{% endfor %}
"""

SEPERATOR = "\n---\n"


def generate_report(user_id: str, date: str):
    report = f"## Daily Report for {user_id} on {date}"
    report += SEPERATOR
    report += "\n### 🔍 Market Overview\n"
    report += _generate_market_overview()
    report += SEPERATOR
    report += "\n### 📈 Portfolio Highlights\n"
    report += _generate_portfolio_highlights()
    report += SEPERATOR
    report += "\n### 📰 News & Social Media Highlights\n"
    report += _generate_news_highlights()
    report += SEPERATOR
    report += "\n### 📉 Forecast Summary\n"
    report += _generate_forecast_summary()
    report += SEPERATOR
    report += "\n### 💡 Analyst Insights\n"
    report += _generate_analyst_insights()
    report += SEPERATOR
    report += "\n### ⚠️ Risk Alert\n"
    report += _generate_risk_alert()
    report += SEPERATOR
    report += "\n### 📆 Upcoming Events\n"
    report += _generate_upcoming_events()
    report += SEPERATOR
    report += "\n### 🤖 Financial Analyst's Take\n"
    report += _generate_financial_analyst_take()

    return report


def _generate_market_overview():
    return "market_overview"


def _generate_portfolio_highlights():
    return "portfolio_highlights"


def _generate_news_highlights():
    return "news_highlights"


def _generate_forecast_summary():
    return "forecast_summary"


def _generate_analyst_insights():
    return "analyst_insights"


def _generate_risk_alert():
    return "risk_alert"


def _generate_upcoming_events():
    return "upcoming_events"


def _generate_financial_analyst_take():
    return "financial_analyst_take"
