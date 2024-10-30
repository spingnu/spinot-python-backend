from __future__ import annotations

import xml.etree.ElementTree as ET

import requests


def fetch_and_parse_rss(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Check if the request was successful
    xml_data = response.text
    return parse_rss_news_with_media(xml_data)


def parse_rss_news_with_media(xml_data):
    root = ET.fromstring(xml_data)
    news_list = []

    # Find all <item> elements within the <channel>
    for item in root.find("channel").findall("item"):
        # Get the media content URL if available
        media_content = item.find("{http://search.yahoo.com/mrss/}content")
        media_url = media_content.get("url") if media_content is not None else None

        news = {
            "title": item.find("title").text.strip(),
            "link": item.find("link").text,
            "author": item.find("dc:creator").text.strip()
            if item.find("dc:creator") is not None
            else None,
            "description": item.find("description").text
            if item.find("description") is not None
            else None,
            "pubDate": item.find("pubDate").text
            if item.find("pubDate") is not None
            else None,
            "categories": [
                category.text.strip() for category in item.findall("category")
            ]
            if item.findall("category")
            else [],
            "media_url": media_url,  # Add media URL to the dictionary
        }

        news_list.append(news)

    return news_list


if __name__ == "__main__":
    # Fetch and parse the RSS feed
    url = "https://www.coindesk.com/arc/outboundfeeds/rss/"
    news_list = fetch_and_parse_rss(url)

    # Print each news item
    for news in news_list:
        print(news)

    print(f"Total news items: {len(news_list)}")
