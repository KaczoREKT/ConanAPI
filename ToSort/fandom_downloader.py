import os
import time
import json
import pathlib
import requests


class FandomDownloader:

    def __init__(self):
        self.base_url = "https://conanexiles.fandom.com"
        self.api_url = f"{self.base_url}/api.php"
        self.session = self._create_session()
        self.images_out_dir = None

    def _create_session(self):
        session = requests.Session()
        UA = "GameVPR-HealthCheck/1.0 (research; contact: email@example.com)"
        session.headers.update({"User-Agent": UA})
        session.timeout = 30
        return session

    def _mw_query(self, params):
        """
        MediaWiki query with continuation handling.
        """
        last_continue = {}
        while True:
            req = params.copy()
            req.update(last_continue)
            r = self.session.get(self.api_url, params=req)
            r.raise_for_status()
            data = r.json()

            if 'error' in data:
                raise RuntimeError(f"API error: {data['error']}")

            if 'warnings' in data:
                LOGGER.info("API warnings:", json.dumps(data['warnings'], ensure_ascii=False))

            yield data

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
        for pages in self._mw_query(params):
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

    def download_images(self, image_map, delay=0.0):
        saved = []
        for file_title, url in image_map.items():
            try:
                dest = os.path.join(self.images_out_dir, file_title.replace("File:", ""))
                if os.path.exists(dest):
                    saved.append(dest)
                    LOGGER.error(f"File {dest} already exists, skipping")
                    continue
                with self.session.get(url, stream=True) as r:
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

    def get_pages_id(self):
        all_pids = []
        params = {
            "action": "query",
            "format": "json",
            "list": "allpages",
            "aplimit": "500"
        }

        for data in self._mw_query(params):
            for query in data['query']['allpages']:
                all_pids.append(query["pageid"])
        return all_pids

    def get_pages_urls(self):
        all_urls = []
        params = {
            "action": "query",
            "format": "json",
            "generator": "allpages",
            "gapnamespace": "0",
            "gaplimit": "500",
            "prop": "info",
            "inprop": "url",
        }
        for data in self._mw_query(params):
            pages = data.get("query", {}).get("pages", {})
            for page in pages.values():
                all_urls.append(page.get("fullurl"))
        return all_urls

    def download_entire_fandom_text(self):
        all_urls = self.get_pages_urls()
        print(all_urls[:20])


if __name__ == "__main__":
    fd = FandomDownloader()
    fd.download_entire_fandom_text()
