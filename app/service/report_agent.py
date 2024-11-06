from __future__ import annotations

from datetime import datetime

from app.db.news import get_news_in_time_range
from app.db.portfolio import filter_out_user_without_portfolio
from app.db.portfolio import get_user_portfolio
from app.db.report import update_report_for_user_on_date
from app.db.source import update_coindesk_db
from app.db.tweet import get_user_tweets_in_time_range
from app.db.user import get_all_user_ids
from app.logger import logger
from app.service.twitter_batch_service import batch_update_all_user_timelines
from app.utils import get_response
from app.utils.llm_apis.openai_api import generate_text


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

SYSTEM_PROMPT = """
You are a professional financial analyst writing a concise, data-driven daily report for the user. The report should focus on key insights relevant to the user’s portfolio, recent market trends, significant news events, and notable social media highlights. Your writing should be fact-based, actionable, and organized in a clear and structured format. Ensure that the language is professional, concise, and easy to read.
"""

USER_PROMPT = """
Do not include any meta comments or instructions—only the report content.

Important Guidelines:

	•	Content Focus: Only include information that directly pertains to the specified section of the report. Avoid including unrelated topics or sections.
	•	Structure and Clarity: Write in a structured, bullet-point format or short paragraphs for easy readability.
	•	Relevance: Ensure that each point is relevant to the user’s investment strategy or decision-making.
    •	Reference: Include sources by its number and type (tweet or news) for all data points, news, and insights provided in the report.
                    Link of the reference should be #news1 or #tweet1 etc.
    •	Conciseness: Keep the report concise and to the point, do not use general statements or filler content.

Only provide content that adheres to these instructions and fits the specified report template.
"""


def crawl_data_generate_report():
    try:
        update_coindesk_db()
        logger.info("Successfully updated coindesk news")
    except Exception as e:
        logger.error(f"Failed to update coindesk news: {e}")
        return get_response(500, {"error": str(e)})

    try:
        batch_update_all_user_timelines(24)
        logger.info("Successfully updated all user timelines")
    except Exception as e:
        logger.error(f"Failed to update all user timelines: {e}")
        return get_response(500, {"error": str(e)})

    date = datetime.now()
    try:
        generate_report_for_every_user(date)
        logger.info("Successfully generated reports for all users")
    except Exception as e:
        logger.error(f"Failed to generate reports for all users: {e}")
        return get_response(500, {"error": str(e)})


def generate_report_for_every_user(date: datetime) -> dict:
    all_user_ids = get_all_user_ids()
    user_ids_with_portfolio = filter_out_user_without_portfolio(all_user_ids)

    for user_id in user_ids_with_portfolio:
        report, reference = generate_report(user_id, date)
        update_report_for_user_on_date(user_id, date, report, reference)


def generate_report(user_id: str, date: datetime) -> str:
    """
    Generate a daily report for a user based on the given date.

    Args:
    - user_id (str): The ID of the user for whom the report is generated.
    - date (datetime): The date for which the report is generated.

    Returns:
    - str: Markdown-formatted daily report
    """

    tweets = get_user_tweets_in_time_range(user_id, date, 1)
    tweet_contents = [tweet["content"] for tweet in tweets]
    tweet_prompt = "\n".join(
        [f"{i+1}. {tweet}" for i, tweet in enumerate(tweet_contents)]
    )
    tweet_prompt = "Here are some tweets from your network:\n" + tweet_prompt

    news = get_news_in_time_range(date, 1)
    news_contents = [f"{news['title']}: {news['description']}" for news in news]
    news_prompt = "\n".join([f"{i+1}. {news}" for i, news in enumerate(news_contents)])
    news_prompt = "Here are some news highlights for you:\n" + news_prompt

    portfolio = get_user_portfolio(user_id)
    portfolio_contents = [f"{asset['name']} ({asset['symbol']})" for asset in portfolio]
    portfolio_prompt = "\n".join(
        [f"{i+1}. {asset}" for i, asset in enumerate(portfolio_contents)]
    )
    portfolio_prompt = "Here are some assets in your portfolio:\n" + portfolio_prompt

    report = SEPERATOR
    report += "\n### 🔍 Market Overview\n"
    report += _generate_market_overview(tweet_prompt, news_prompt, portfolio_prompt)
    report += SEPERATOR
    report += "\n### 📈 Portfolio Highlights\n"
    report += _generate_portfolio_highlights(
        tweet_prompt, news_prompt, portfolio_prompt
    )
    report += SEPERATOR
    report += "\n### 📰 News & Social Media Highlights\n"
    report += _generate_news_highlights(tweet_prompt, news_prompt, portfolio_prompt)
    report += SEPERATOR
    report += "\n### 📉 Forecast Summary\n"
    report += _generate_forecast_summary(tweet_prompt, news_prompt, portfolio_prompt)
    report += SEPERATOR
    report += "\n### 💡 Analyst Insights\n"
    report += _generate_analyst_insights(tweet_prompt, news_prompt, portfolio_prompt)
    report += SEPERATOR
    report += "\n### ⚠️ Risk Alert\n"
    report += _generate_risk_alert(tweet_prompt, news_prompt, portfolio_prompt)
    report += SEPERATOR
    report += "\n### 📆 Upcoming Events\n"
    report += _generate_upcoming_events(tweet_prompt, news_prompt, portfolio_prompt)
    report += SEPERATOR
    report += "\n### 🤖 Financial Analyst's Take\n"
    report += _generate_financial_analyst_take(
        tweet_prompt, news_prompt, portfolio_prompt
    )

    reference = {
        "news": news_contents,
        "tweet": tweet_contents,
    }

    return report, reference


def _generate_market_overview(
    tweet_prompt: str, news_prompt: str, portfolio_prompt: str
):
    prompt = tweet_prompt + news_prompt + portfolio_prompt
    prompt += "\n"
    prompt += f"""Fill the template below with the latest market overview information:
    {MARKET_OVERVIEW_TEMPLATE}"""
    prompt += "\n"
    prompt += USER_PROMPT
    return generate_text(prompt, system_prompt=SYSTEM_PROMPT)


def _generate_portfolio_highlights(
    tweet_prompt: str, news_prompt: str, portfolio_prompt: str
):
    prompt = tweet_prompt + news_prompt + portfolio_prompt
    prompt += "\n"
    prompt += f"""Fill the template below with the latest portfolio highlights information. For the price and change just fill any imaginery number:
    {PORTFOLIO_HIGHLIGHTS_TEMPLATE}"""
    prompt += "\n"
    prompt += USER_PROMPT
    return generate_text(prompt)


def _generate_news_highlights(
    tweet_prompt: str, news_prompt: str, portfolio_prompt: str
):
    prompt = tweet_prompt + news_prompt + portfolio_prompt
    prompt += "\n"
    prompt += f"""Fill the template below with the latest news highlights information:
    {NEWS_HIGHLIGHTS_TEMPLATE}"""
    prompt += "\n"
    prompt += USER_PROMPT
    return generate_text(prompt)


def _generate_forecast_summary(
    tweet_prompt: str, news_prompt: str, portfolio_prompt: str
):
    prompt = tweet_prompt + news_prompt + portfolio_prompt
    prompt += "\n"
    prompt += f"""Fill the template below with the latest forecast summary information:
    {FORECAST_SUMMARY_TEMPLATE}"""
    prompt += "\n"
    prompt += USER_PROMPT
    return generate_text(prompt)


def _generate_analyst_insights(
    tweet_prompt: str, news_prompt: str, portfolio_prompt: str
):
    prompt = tweet_prompt + news_prompt + portfolio_prompt
    prompt += "\n"
    prompt += f"""Fill the template below with the latest analyst insights information:
    {ANALYST_INSIGHTS_TEMPLATE}"""
    prompt += "\n"
    prompt += USER_PROMPT

    return generate_text(prompt)


def _generate_risk_alert(tweet_prompt: str, news_prompt: str, portfolio_prompt: str):
    prompt = tweet_prompt + news_prompt + portfolio_prompt
    prompt += "\n"
    prompt += f"""Fill the template below with the latest risk alert information:
    {RISK_ALERT_TEMPLATE}"""
    prompt += "\n"
    prompt += USER_PROMPT

    return generate_text(prompt)


def _generate_upcoming_events(
    tweet_prompt: str, news_prompt: str, portfolio_prompt: str
):
    prompt = tweet_prompt + news_prompt + portfolio_prompt
    prompt += "\n"
    prompt += f"""Fill the template below with the latest upcoming events information:
    {UPCOMING_EVENTS_TEMPLATE}"""
    prompt += "\n"
    prompt += USER_PROMPT

    return generate_text(prompt)


def _generate_financial_analyst_take(
    tweet_prompt: str, news_prompt: str, portfolio_prompt: str
):
    prompt = tweet_prompt + news_prompt + portfolio_prompt
    prompt += "\n"
    prompt += f"""Fill the template below with the latest financial analyst take information:
    {FINANCIAL_ANALYST_TAKE_TEMPLATE}"""
    prompt += "\n"
    prompt += USER_PROMPT

    return generate_text(prompt)


if __name__ == "__main__":
    user_id = "b447cb9c-39f3-4e72-82bf-932dbf9204a5"
    date = datetime.now()
    # report = generate_report(user_id, date)
    # print(report)
    generate_report_for_every_user(date)
