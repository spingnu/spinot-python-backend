from __future__ import annotations

import requests

from app.s3 import upload_asset_image_to_s3
from app.supabase_client import supabase

# Replace with your CoinMarketCap API key
API_KEY = "e3de57d1-3713-4cce-8fbe-d3027cb49e48"
URL = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"


def fetch_tickers():
    headers = {
        "Accepts": "application/json",
        "X-CMC_PRO_API_KEY": API_KEY,
    }

    start = 1  # Starting index
    limit = 5000  # Number of items per request

    while True:
        params = {"start": start, "limit": limit}
        response = requests.get(URL, headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()
            tickers = data.get("data", [])

            if not tickers:
                # If no more data, break out of the loop
                break

            # Print tickers information
            for ticker in tickers:
                name = ticker["name"]
                symbol = ticker["symbol"]
                ticker_id = ticker["id"]
                img_url = f"https://s2.coinmarketcap.com/static/img/coins/64x64/{ticker_id}.png"

                # check if symbol already exists in the database
                existing_symbol = (
                    supabase.table("assets")
                    .select("symbol")
                    .eq("symbol", symbol)
                    .execute()
                )
                if existing_symbol.data:
                    print(f"{name} ({symbol}) already exists")
                    continue

                upload_asset_image_to_s3(img_url, symbol)
                supabase.table("assets").insert(
                    [
                        {
                            "name": name,
                            "symbol": symbol,
                            "img_url": img_url,
                            "from": "cmc",
                        }
                    ]
                ).execute()

                print(f"{name} ({symbol}): {img_url}")

            if len(tickers) < limit:
                # If the number of tickers fetched is less than the limit, break out of the loop
                break
            # Increment start to get the next page
            start += limit
        else:
            print(f"Failed to fetch data. HTTP status code: {response.status_code}")
            print(f"Error content: {response.text}")
            break


if __name__ == "__main__":
    fetch_tickers()
