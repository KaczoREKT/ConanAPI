from app.controllers.main import Controller
from app.models.main import Model
from app.views.main import View
from ToSort.fandom_downloader import FandomDownloader
from ToSort.web_scraper import WebScraper


def main2():
    fd = FandomDownloader()
    ws = WebScraper()

    url_list = fd.get_pages_urls()
    ws.load_from_url(url_list)

if __name__ == "__main__":
    model = Model()
    view = View()
    controller = Controller(model, view)
    controller.start()
