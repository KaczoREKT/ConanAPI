import os
import time
import json
import pathlib
import requests
import logging
LOGGER = logging.getLogger(__name__)

BASE = "https://zelda.fandom.com"
API = f"{BASE}/api.php"

UA = "GameVPR-HealthCheck/1.0 (research; contact: email@example.com)"
S = requests.Session()
S.headers.update({"User-Agent": UA})
S.timeout = 30

OUT_DIR = "zelda_items_images"
pathlib.Path(OUT_DIR).mkdir(parents=True, exist_ok=True)

class FandomDownloader:

    def __init__(self):
        pass

    def mw_query(self, params, base_api=API, session=S):
        """
        MediaWiki query with continuation handling.
        Yields 'pages' dicts until continuation ends.
        """
        last_continue = {}
        while True:
            req = params.copy()
            req.update(last_continue)
            r = session.get(base_api, params=req)
            r.raise_for_status()
            data = r.json()

            if 'error' in data:
                raise RuntimeError(f"API error: {data['error']}")

            if 'warnings' in data:
                LOGGER.info("API warnings:", json.dumps(data['warnings'], ensure_ascii=False))

            if 'query' in data and 'pages' in data['query']:
                yield data['query']['pages']

            if 'continue' not in data:
                break

            last_continue = data['continue']

    def get_titles_and_urls(self, title, thumb_width=None):
        params = {
            "action": "query",
            "format": "json",
            "generator": "images",
            "titles": title,
            "prop": "imageinfo",
            "iilimit": "1",
            "iiprop": "url"
        }
        if thumb_width:
            params["iiurlwidth"] = str(thumb_width)

        result_map = {}
        for pages in self.mw_query(params):
            for _, page in pages.items():
                file_title = page.get("title")
                ii = page.get("imageinfo")
                if not file_title or not ii:
                    continue
                info = ii
                url = info[0].get("thumburl") if thumb_width else info[0].get("url")
                if url:
                    result_map[file_title] = url
        return result_map

    def download_images(self, image_map, out_dir=OUT_DIR, session=S, delay=0.0):
        saved = []
        for file_title, url in image_map.items():
            try:
                dest = os.path.join(out_dir, file_title.replace("File:", ""))
                if os.path.exists(dest):
                    saved.append(dest)
                    LOGGER.error(f"File {dest} already exists, skipping")
                    continue
                with session.get(url, stream=True) as r:
                    r.raise_for_status()
                    with open(dest, "wb") as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                saved.append(dest)
                if delay:
                    time.sleep(delay)
            except Exception as e:
                LOGGER.error(f"Failed {url}: {e}")
        return saved


    def download_from_page(self, page_title):
        image_map = self.get_titles_and_urls(page_title, thumb_width=None)
        LOGGER.info(f"Found {len(image_map)} images with URLs")

        files = self.download_images(image_map)
        LOGGER.info(f"Downloaded {len(files)} images to {OUT_DIR}")

if __name__ == "__main__":
    fd = FandomDownloader()
    page_title = "Enemies_in_The_Legend_of_Zelda"
    fd.download_from_page(page_title)
