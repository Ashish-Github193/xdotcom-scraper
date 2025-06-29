import asyncio
import json
import logging
import os
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Dict, List, Optional

from pydoll.browser import Chrome
from pydoll.browser.options import ChromiumOptions
from pydoll.constants import Key

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ScrapedData:
    url: str
    title: str
    content: str
    timestamp: str
    metadata: Dict[str, str]


class WebScraper:
    def __init__(self, headless: bool = False, timeout: int = 30):
        self.timeout = timeout
        self.scraped_data: List[ScrapedData] = []

        # Setup Chrome options - create fresh each time to avoid conflicts
        self._headless = headless
        self._chrome_bin = os.environ.get("CHROME_BIN", "/usr/bin/google-chrome")

    def _create_chrome_options(self):
        """Create fresh Chrome options to avoid argument conflicts"""
        options = ChromiumOptions()

        options.add_argument("--no-sandbox")

        # Set Chrome binary path (for Docker)
        if os.path.exists(self._chrome_bin):
            options.binary_location = self._chrome_bin

        return options

    async def scrape_url(self, url: str, selectors: Dict[str, str] = None) -> Optional[ScrapedData]:
        """
        Scrape a single URL using PyDoll

        Args:
            url: URL to scrape
            selectors: Dictionary of CSS selectors for specific elements

        Returns:
            ScrapedData object or None if scraping fails
        """
        if selectors is None:
            selectors = {"title": "title", "content": "body"}

        try:
            async with Chrome(options=self._create_chrome_options()) as browser:
                tab = await browser.start(headless=self._headless)
                logger.info(f"Navigating to {url}")

                await tab.go_to(url)
                await asyncio.sleep(2)  # Wait for page to load

                # Extract title
                try:
                    title = await tab.get_title()
                except:
                    try:
                        title_element = await tab.find(tag_name="title")
                        title = (
                            await title_element.get_text() if title_element else "No title found"
                        )
                    except:
                        title = "No title found"

                # Extract content
                try:
                    content_element = await tab.find(tag_name="body")
                    content = (
                        await content_element.get_text() if content_element else "No content found"
                    )
                except:
                    content = "No content found"

                # Extract metadata
                metadata = {}
                try:
                    # Get page description
                    desc_elements = await tab.select_all("meta")
                    for elem in desc_elements:
                        name_attr = await elem.get_attribute("name")
                        if name_attr == "description":
                            content_attr = await elem.get_attribute("content")
                            if content_attr:
                                metadata["description"] = content_attr
                        elif name_attr == "keywords":
                            content_attr = await elem.get_attribute("content")
                            if content_attr:
                                metadata["keywords"] = content_attr
                except:
                    pass

                scraped_data = ScrapedData(
                    url=url,
                    title=title.strip(),
                    content=content.strip()[:1000],  # Limit content length
                    timestamp=datetime.now().isoformat(),
                    metadata=metadata,
                )

                self.scraped_data.append(scraped_data)
                logger.info(f"Successfully scraped {url}")
                return scraped_data

        except Exception as e:
            logger.error(f"Error scraping {url}: {str(e)}")
            return None

    async def scrape_multiple_urls(
        self, urls: List[str], selectors: Dict[str, str] = None
    ) -> List[ScrapedData]:
        """
        Scrape multiple URLs concurrently

        Args:
            urls: List of URLs to scrape
            selectors: Dictionary of CSS selectors for specific elements

        Returns:
            List of ScrapedData objects
        """
        tasks = [self.scrape_url(url, selectors) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        successful_results = []
        for result in results:
            if isinstance(result, ScrapedData):
                successful_results.append(result)
            elif isinstance(result, Exception):
                logger.error(f"Error in concurrent scraping: {str(result)}")

        return successful_results

    async def search_and_scrape(self, query: str, max_results: int = 5) -> List[ScrapedData]:
        """
        Search Google and scrape the first few results

        Args:
            query: Search query
            max_results: Maximum number of results to scrape

        Returns:
            List of ScrapedData objects
        """
        try:
            async with Chrome(options=self._create_chrome_options()) as browser:
                logger.debug(f"Display: {os.getenv('DISPLAY')}")
                tab = await browser.start()
                logger.info(f"Searching for: {query}")

                # Go to Google
                await tab.go_to("https://www.google.com")
                await asyncio.sleep(2)

                # Find search box and enter query
                search_box = None
                try:
                    search_box = await tab.find(tag_name="textarea", name="q")
                except:
                    try:
                        search_box = await tab.find(tag_name="input", name="q")
                    except:
                        pass

                if search_box:
                    await search_box.insert_text(query)
                    await search_box.press_keyboard_key(Key.ENTER)
                    await asyncio.sleep(3)

                    # Extract search result URLs
                    try:
                        result_links = await tab.select_all("a")
                        urls = []

                        for link in result_links[: max_results * 3]:  # Get more links to filter
                            try:
                                href = await link.get_attribute("href")
                                if href and href.startswith("http") and "google.com" not in href:
                                    urls.append(href)
                                    if len(urls) >= max_results:
                                        break
                            except:
                                continue
                    except:
                        urls = []

                    logger.info(f"Found {len(urls)} URLs to scrape")

                    # Scrape each URL
                    scraped_results = []
                    for url in urls:
                        result = await self.scrape_url(url)
                        if result:
                            scraped_results.append(result)

                    return scraped_results

        except Exception as e:
            logger.error(f"Error in search and scrape: {str(e)}")
            return []

    def save_to_json(self, filename: str = "scraped_data.json"):
        """Save scraped data to JSON file"""
        try:
            data = [asdict(item) for item in self.scraped_data]
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"Data saved to {filename}")
        except Exception as e:
            logger.error(f"Error saving data: {str(e)}")

    def get_scraped_data(self) -> List[Dict]:
        """Return scraped data as list of dictionaries"""
        return [asdict(item) for item in self.scraped_data]
