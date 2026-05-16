import asyncio
import os
import tempfile
import yt_dlp
from config.config import config

class Downloader:
    def __init__(self):
        self.ydl_opts = config.YDL_OPTS.copy()
        self.ydl_opts.update({
            'outtmpl': os.path.join('downloads', 'frozen_%(id)s.%(ext)s'),
            'cachedir': False
        })
        if not os.path.exists('downloads'):
            os.makedirs('downloads')

    async def download(self, url: str):
        # Generate a unique filename based on URL or ID
        # Simple hash or use yt-dlp to get ID first
        loop = asyncio.get_event_loop()

        def get_info_sync():
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                return ydl.extract_info(url, download=False)

        info = await loop.run_in_executor(None, get_info_sync)
        video_id = info.get('id')
        ext = info.get('ext', 'webm')
        expected_filename = os.path.join('downloads', f"frozen_{video_id}.{ext}")

        if os.path.exists(expected_filename):
            return expected_filename

        def download_sync():
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                return ydl.prepare_filename(info)

        return await loop.run_in_executor(None, download_sync)

    async def search(self, query: str):
        loop = asyncio.get_event_loop()
        def search_sync():
            opts = self.ydl_opts.copy()
            # If it's a playlist link, don't use flat extract if we want all entries
            # but for a quick search, flat is better.
            is_link = query.startswith("http")
            opts['extract_flat'] = "in_playlist" if is_link else True

            with yt_dlp.YoutubeDL(opts) as ydl:
                search_query = f"ytsearch1:{query}" if not is_link else query
                info = ydl.extract_info(search_query, download=False)

                if 'entries' in info:
                    # It could be a search result or a playlist
                    return info['entries']
                return [info]

        return await loop.run_in_executor(None, search_sync)

downloader = Downloader()
