from __future__ import annotations

import xml.etree.ElementTree as ET
from datetime import datetime

import requests

URL = "https://www.coindesk.com/arc/outboundfeeds/rss/"


def parse_rss_date(date_str):
    # Define the date format
    date_format = "%a, %d %b %Y %H:%M:%S %z"
    # Parse the date string into a datetime object
    parsed_date = datetime.strptime(date_str, date_format)
    return parsed_date.isoformat()


def fetch_and_parse_rss():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
    }
    response = requests.get(URL, headers=headers)
    response.raise_for_status()  # Check if the request was successful
    xml_data = response.text
    return parse_rss_news_with_media(xml_data)


def parse_rss_news_with_media(xml_data):
    namespaces = {
        "dc": "http://purl.org/dc/elements/1.1/",
        "media": "http://search.yahoo.com/mrss/",
    }

    root = ET.fromstring(xml_data)
    news_list = []

    # Find all <item> elements within the <channel>
    for item in root.find("channel").findall("item"):
        # Get the media content URL if available
        media_content = item.find("media:content", namespaces)
        media_url = media_content.get("url") if media_content is not None else None

        # Get the author from the dc:creator tag
        author = item.find("dc:creator", namespaces)
        author_text = author.text.strip() if author is not None else None

        news = {
            "title": item.find("title").text.strip(),
            "link": item.find("link").text,
            "author": author_text,
            "description": item.find("description").text
            if item.find("description") is not None
            else None,
            "pubDate": parse_rss_date(item.find("pubDate").text)
            if item.find("pubDate") is not None
            else None,
            "categories": ", ".join(
                [category.text.strip() for category in item.findall("category")]
            )
            if item.findall("category")
            else None,
            "media_url": media_url,  # Add media URL to the dictionary
        }

        news_list.append(news)

    return news_list


if __name__ == "__main__":
    # Fetch and parse the RSS feed
    news_list = fetch_and_parse_rss()

    # Print each news item
    for news in news_list:
        print(news)

    print(f"Total news items: {len(news_list)}")
