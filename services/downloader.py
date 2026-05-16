import asyncio
import os
import tempfile
import yt_dlp
from config.config import config

class Downloader:
    def __init__(self):
        self.ydl_opts = config.YDL_OPTS.copy()
        # Check if cookiefile exists, if not remove it from opts
        if not os.path.exists(self.ydl_opts.get("cookiefile", "cookies.txt")):
            self.ydl_opts.pop("cookiefile", None)

        self.ydl_opts.update({
            'outtmpl': os.path.join('downloads', 'frozen_%(id)s.%(ext)s'),
            'cachedir': False
        })
        if not os.path.exists('downloads'):
            os.makedirs('downloads')

    async def download(self, url: str):
        loop = asyncio.get_event_loop()

        def get_info_sync():
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if info is None:
                    raise Exception("Failed to extract video info")

                # Check if it's just an image or thumbnail (happens sometimes with YouTube music)
                formats = info.get('formats', [])
                if not formats and not info.get('url'):
                     raise Exception("Only images are available for download")

                return info

        info = await loop.run_in_executor(None, get_info_sync)
        video_id = info.get('id')

        # Check all possible extensions that might have been downloaded previously
        # since yt-dlp might choose a different one depending on available formats
        possible_extensions = ['webm', 'm4a', 'mp3', 'mp4', 'opus']
        for ext in possible_extensions:
            expected_filename = os.path.join('downloads', f"frozen_{video_id}.{ext}")
            if os.path.exists(expected_filename):
                return expected_filename

        def download_sync():
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info_res = ydl.extract_info(url, download=True)
                if info_res is None:
                     raise Exception("Download failed, no info returned")
                return ydl.prepare_filename(info_res)

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
