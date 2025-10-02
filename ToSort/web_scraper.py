import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import urllib.parse


class WebScraper:
    def __init__(self):
        self.web_paths = [
            # 'https://gamefaqs.gamespot.com/nes/563433-the-legend-of-zelda/faqs/78634',
            # 'https://gamefaqs.gamespot.com/ps2/582958-shin-megami-tensei-nocturne/faqs/23739'
            # 'https://gamefaqs.gamespot.com/n64/197771-the-legend-of-zelda-ocarina-of-time/faqs/39038'
        #self.find_tutorial_link("The Legend of Zelda", "nes"),
            "https://conanexiles.fandom.com/wiki/Hide"
        ]
        if self.web_paths == [None]:
            print("Znaleźli nas. Włączam tutorial dla Zeldy")
            self.web_paths[0] = 'https://gamefaqs.gamespot.com/nes/563433-the-legend-of-zelda/faqs/78634&rut=e3c3e04ebb035d47bfe79f8210f582ab32efd670685b6fd4b5db746f1ffebae8'
        for web_path in self.web_paths:
            web_path += '?print=1'

    def _scrape(self, url: str) -> BeautifulSoup:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10.0)
        return BeautifulSoup(response.text, "html.parser")

    def scrape(self, url: str) -> BeautifulSoup:
        """Scrape the webpage at the given url."""
        return self._scrape(url)

    def _build_metadata(self, soup, url: str) -> dict:
        metadata = {"source": url}
        if title := soup.find("title"):
            metadata["title"] = title.get_text()
        if description := soup.find("meta", attrs={"name": "description"}):
            metadata["description"] = description.get("content", "No description found.")
        if html := soup.find("html"):
            metadata["language"] = html.get("lang", "No language found.")
        if notes := soup.find("notes"):
            metadata["notes"] = notes.get("base", {}).get("href")
        return metadata

    def build_metadata(self, soup, url: str) -> dict:
        """Build metadata from BeautifulSoup output."""
        return self._build_metadata(soup, url)

    def _load_from_url(self, web_paths):

        soup = self.scrape(web_paths[0])
        print(soup)


    def load_from_url(self, url_list):
        return self._load_from_url(url_list)

    def find_tutorial_link(self, game_name="The Legend of Zelda", platform="nes") -> str or None:
        """
        Finds a tutorial link for a specific game on GameFAQs using the DuckDuckGo search engine.

        This function constructs a search query for the specified game on GameFAQs, performs a web
        search using a headless browser, and parses the search results to locate a valid tutorial link.

        :param game_name: The name of the game for which the tutorial link is required.
        :type game_name: str
        :param platform: The platform of the game (e.g., "ps4", "xbox", etc.). Default is an empty string.
        :return: The URL of the tutorial page if found, otherwise None.
        :rtype: str or None
        """
        print(f"Looking for tutorial link for: {game_name} on platform: {platform}")
        query = f"{game_name} tutorial site:gamefaqs.gamespot.com"
        search_url = f"https://duckduckgo.com/html/?q={urllib.parse.quote_plus(query)}"

        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")

        driver = webdriver.Chrome(options=options)
        driver.get(search_url)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        driver.quit()
        for a in soup.find_all('a', href=True):
            href = a['href']
            if "uddg=" in href and "gamefaqs.gamespot.com" in href:
                true_link = href.split("uddg=")[-1]
                decoded_link = urllib.parse.unquote(true_link)
                if decoded_link.startswith(
                        "https://gamefaqs.gamespot.com") and f"/{platform}/" in decoded_link and f"/faqs/" in decoded_link:
                    return decoded_link
        return None

if __name__ == "__main__":
    tws = WebScraper()
