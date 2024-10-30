"""Fetches the latest cryptocurrency tickers from CoinMarketCap API asynchronously using aiohttp."""
import json
import asyncio
import aiohttp
import os

from absl import app
from absl import flags
from absl import logging

flags.DEFINE_string('output_dir', 'ticker_imgs/', 'Directory to save the tickers and images')
flags.DEFINE_string('out_file', 'tickers.json', 'Path to save the tickers in JSON format')
flags.DEFINE_string('api_key', None, 'CoinMarketCap API key')

FLAGS = flags.FLAGS

URL = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'


async def download_image(session, url, save_path):
    """Asynchronously downloads an image from the given URL and saves it to the specified path."""
    try:
        async with session.get(url) as resp:
            if resp.status == 200:
                content = await resp.read()
                with open(save_path, 'wb') as f:
                    f.write(content)
            else:
                logging.error(f'Failed to download image from {url}. Status code: {resp.status}')
    except Exception as e:
        logging.error(f'Exception occurred while downloading image from {url}: {e}')


async def main(_):
    os.makedirs(FLAGS.output_dir, exist_ok=True)
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': FLAGS.api_key,
    }
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(URL, params={'start': 1, 'limit': 5000}) as response:
            if response.status == 200:
                data = await response.json()
                tasks = []
                logging.info("Number of data: %d", len(data['data']))
                for ticker in data['data']:
                    ticker_id = ticker['id']
                    img_url = f'https://s2.coinmarketcap.com/static/img/coins/64x64/{ticker_id}.png'
                    tasks.append(download_image(session, img_url, os.path.join(FLAGS.output_dir, f'{ticker_id}.png')))
                await asyncio.gather(*tasks)
                logging.info("All images downloaded successfully")
                with open('tickers.json', 'w') as f:
                    json.dump(data['data'], f, indent=2)
            else:
                logging.error(f'Failed to fetch data. HTTP status code: {response.status}')
                content = await response.text()
                logging.error(f'Error content: {content}')


if __name__ == '__main__':
    flags.mark_flag_as_required('api_key')
    app.run(lambda argv: asyncio.run(main(argv)))
