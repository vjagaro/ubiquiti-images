#!/usr/bin/env python

import argparse
import aiofiles
import aiohttp
import asyncio
import json
from pathlib import Path
import re

MARKETING_URL = 'https://www.ui.com/marketing/'


def get_args():
    parser = argparse.ArgumentParser(
        description='Download Ubiquiti marketing images.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('directory', type=Path, nargs='?',
                        default=Path.cwd(), help='Output directory')
    parser.add_argument('-f', '--format', type=str, default='best',
                        help='Format (e.g., png, jpg, tif, ai, all)')
    parser.add_argument('-p', '--position', type=str, default='front',
                        help='Position (e.g., front, bottom, all)')
    parser.add_argument('-c', '--concurrent', type=int, default=5,
                        help='Number of concurrent downloads')
    return parser.parse_args()


async def download(session, item, dir):
    print(f'Downloading {item["url"]}')
    async with session.get(item['url']) as response:
        if response.status == 200:
            item_dir = Path(dir) / item['group']
            item_dir.mkdir(parents=True, exist_ok=True)
            f = await aiofiles.open(item_dir / item['filename'], mode='wb')
            await f.write(await response.read())
        else:
            print(
                f'Error downloading {item["url"]}, status = {response.status}')


async def fetch_marketing_page(session):
    print(f'Downloading Ubiquiti marketing JSON from {MARKETING_URL}')
    async with session.get(MARKETING_URL) as response:
        if response.status != 200:
            raise Exception(f'Could not download {MARKETING_URL}')
        return await response.text()


async def get_marketing_data(session):
    html = await fetch_marketing_page(session)
    m = re.search(r'var marketingCategories = JSON.parse\("(.+)"\)', html)
    if not m:
        raise Exception(f'Cannot find data from {UBIQUITI_MARKETING_URL}')
    text = m.group(1)
    # Replace all instances of \u0022 with "
    text = text.replace('\\u0022', '"')
    return json.loads(text)


async def get_items(session, format, position):
    for group, values in (await get_marketing_data(session)).items():
        for item in values['items']:
            if position != 'all' and position != item['position_slug']:
                continue
            downloads = {}
            for item_download in item['itemdownload_set']:
                ext = item_download['file_extension'].strip()
                downloads[ext] = item_download['download_url'].strip()
            if format != 'all':
                if format == 'best':
                    if 'png' in downloads:
                        downloads = {'png': downloads['png']}
                    elif 'jpg' in downloads:
                        downloads = {'jpg': downloads['jpg']}
                    elif 'tif' in downloads:
                        downloads = {'tif': downloads['tif']}
                    else:
                        downloads = {}
                elif format in downloads:
                    downloads = {format: downloads[format]}
                else:
                    downloads = {}
            for ext, url in downloads.items():
                yield {
                    'group': group,
                    'filename': Path(url).name,
                    'url': url,
                }


async def run(args):
    async with aiohttp.ClientSession() as session:
        semaphore = asyncio.Semaphore(args.concurrent)

        async def concurrent_download(item):
            async with semaphore:
                await download(session, item, args.directory)

        tasks = [
            asyncio.create_task(concurrent_download(item))
            async for item in get_items(session, args.format, args.position)
        ]
        await asyncio.gather(*tasks)


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(get_args()))


if __name__ == '__main__':
    main()
