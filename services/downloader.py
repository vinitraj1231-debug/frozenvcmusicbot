import asyncio
import os
import logging
import yt_dlp
from config.config import config

logger = logging.getLogger(__name__)

class Downloader:
    def __init__(self):
        self.ydl_opts = config.YDL_OPTS.copy()
        # Check if cookiefile exists, if not remove it from opts
        cookie_path = self.ydl_opts.get("cookiefile", "cookies.txt")
        if not os.path.exists(cookie_path):
            self.ydl_opts.pop("cookiefile", None)
            logger.warning(f"Cookie file not found at {cookie_path}. Proceeding without it.")

        self.ydl_opts.update({
            'outtmpl': os.path.join('downloads', 'frozen_%(id)s.%(ext)s'),
            'cachedir': False,
            'logger': logger,
            'compat_opts': {'no-direct-merge': True},
        })

        if not os.path.exists('downloads'):
            os.makedirs('downloads')

    async def download(self, url: str, retries: int = 2):
        loop = asyncio.get_event_loop()

        # Try different player client combinations if it fails
        fallback_strategies = [
            # Strategy 1: Default (usually with cookies if available)
            {"youtube": {"player_client": ["web", "android"], "player_skip": ["webpage"]}},
            # Strategy 2: No cookies (often avoids 403 on some clients)
            {"youtube": {"player_client": ["web", "android"], "player_skip": ["webpage"]}, "cookiefile": None},
            # Strategy 3: Web client only
            {"youtube": {"player_client": ["web"]}},
            # Strategy 4: iOS client (sometimes works when others fail)
            {"youtube": {"player_client": ["ios"]}},
        ]

        last_error = None
        for attempt in range(retries + 1):
            strategy = fallback_strategies[min(attempt, len(fallback_strategies) - 1)]
            current_opts = self.ydl_opts.copy()
            current_opts["extractor_args"] = strategy

            try:
                if "cookiefile" in strategy:
                    if strategy["cookiefile"] is None:
                        current_opts.pop("cookiefile", None)
                    else:
                        current_opts["cookiefile"] = strategy["cookiefile"]

                def get_info_sync():
                    with yt_dlp.YoutubeDL(current_opts) as ydl:
                        try:
                            info = ydl.extract_info(url, download=False)
                        except Exception as e:
                            logger.error(f"Extraction error (attempt {attempt+1}) for {url}: {e}")
                            raise e

                        if info is None:
                            raise Exception("Failed to extract video info")

                        # Validate formats
                        formats = info.get('formats', [])
                        if not formats and not info.get('url'):
                             raise Exception("Only images or restricted content available for download")

                        return info

                info = await loop.run_in_executor(None, get_info_sync)
                video_id = info.get('id')

                # Check for already downloaded file
                possible_extensions = ['m4a', 'webm', 'mp3', 'mp4', 'opus']
                for ext in possible_extensions:
                    expected_filename = os.path.join('downloads', f"frozen_{video_id}.{ext}")
                    if os.path.exists(expected_filename):
                        logger.info(f"Using cached file: {expected_filename}")
                        return expected_filename

                def download_sync():
                    with yt_dlp.YoutubeDL(current_opts) as ydl:
                        try:
                            info_res = ydl.extract_info(url, download=True)
                            if info_res is None:
                                 raise Exception("Download failed, no info returned")
                            return ydl.prepare_filename(info_res)
                        except Exception as e:
                            logger.error(f"Download error (attempt {attempt+1}) for {url}: {e}")
                            raise e

                file_path = await loop.run_in_executor(None, download_sync)

                # Post-processing might change extension to .m4a
                if os.path.exists(file_path):
                    return file_path

                base_path = os.path.join('downloads', f"frozen_{video_id}")
                for ext in possible_extensions:
                    if os.path.exists(f"{base_path}.{ext}"):
                        return f"{base_path}.{ext}"

                return file_path

            except Exception as e:
                last_error = e
                if attempt < retries:
                    wait_time = 2 ** attempt
                    logger.info(f"Retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                continue

        raise Exception(f"Download failed after {retries+1} attempts: {str(last_error)}")

    async def search(self, query: str):
        loop = asyncio.get_event_loop()
        def search_sync():
            opts = self.ydl_opts.copy()
            is_link = query.startswith(("http://", "https://"))
            opts['extract_flat'] = "in_playlist" if is_link else True
            opts['download'] = False

            with yt_dlp.YoutubeDL(opts) as ydl:
                try:
                    search_query = f"ytsearch1:{query}" if not is_link else query
                    info = ydl.extract_info(search_query, download=False)

                    if info is None:
                        return []

                    if 'entries' in info:
                        return [e for e in info['entries'] if e is not None]
                    return [info]
                except Exception as e:
                    logger.error(f"Search error for {query}: {e}")
                    return []

        return await loop.run_in_executor(None, search_sync)

downloader = Downloader()
