from fandom_downloader import FandomDownloader
from web_scraper import WebScraper

if __name__ == "__main__":
    fd = FandomDownloader()
    ws = WebScraper()

    url_list = fd.get_pages_urls()
    ws.load_from_url(url_list)
