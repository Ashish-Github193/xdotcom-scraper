import asyncio
import logging
import os
from dataclasses import dataclass
from typing import List, Optional

from pydoll.browser import Chrome
from pydoll.browser.options import ChromiumOptions
from pydoll.browser.tab import Tab, WebElement
from pydoll.constants import By

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class TweetData:
    datetime: str
    hashtag: Optional[str]
    details: Optional[str]
    content: Optional[str]
    link: str


class XComScraper:
    def __init__(self, account_name: str, headless: bool = False, timeout: int = 30):
        self.account_name = account_name
        self.headless = headless
        self.timeout = timeout
        self.account_url = f"https://x.com/{account_name}"

        # Chrome options
        self._headless = headless
        self._chrome_bin = self._find_chrome_binary()

    def _find_chrome_binary(self):
        """Find Chrome binary in common locations"""

        if chrome_bin := os.environ.get("CHROME_BIN"):
            if os.path.exists(chrome_bin):
                return chrome_bin

        # Common Chrome binary locations
        common_paths = [
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable",
            "/usr/bin/chromium",
            "/usr/bin/chromium-browser",
            "/snap/bin/chromium",
        ]

        for path in common_paths:
            if os.path.exists(path):
                return path

        return None

    def _get_chrome_options(self) -> ChromiumOptions:
        """Get Chrome options for browser configuration"""
        options = ChromiumOptions()

        if self.headless:
            options.add_argument("--headless")

        # Standard options for better compatibility
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-web-security")

        return options

    async def _scroll_until_tweets_loaded(self, tab: Tab, total_needed: int = 25) -> List:
        """Scroll down until required number of tweets are loaded"""
        seen_links = set()
        unique_articles = []
        scroll_attempts = 0
        max_scroll_attempts = 20

        while len(unique_articles) < total_needed and scroll_attempts < max_scroll_attempts:
            try:
                current_articles = await tab.query(expression="//article", find_all=True)
                if not current_articles or isinstance(current_articles, WebElement):
                    logger.warning("No articles found")
                    break

                # Track new unique articles by their links
                new_articles_count = 0
                for article in current_articles:
                    # Skip pinned tweets
                    if await self._is_tweet_pinned(article):
                        continue

                    # Get the tweet link as unique identifier
                    tweet_link = await self._find_tweet_link(article)
                    if tweet_link and tweet_link not in seen_links:
                        seen_links.add(tweet_link)
                        unique_articles.append(article)
                        new_articles_count += 1

                logger.info(
                    f"Found {new_articles_count} new articles, total unique: {len(unique_articles)}"
                )

                if len(unique_articles) >= total_needed:
                    logger.info(f"Collected {len(unique_articles)} unique articles")
                    break

                # If no new articles found, we've reached the end
                if new_articles_count == 0:
                    logger.info("No new articles found, stopping scroll")
                    break

                await tab.execute_script("window.scrollBy(0, 1000)")
                await asyncio.sleep(2)  # Increased sleep time for content loading
                scroll_attempts += 1

            except Exception as e:
                logger.error(f"Error during scrolling: {e}")
                break

        return unique_articles[:total_needed] if unique_articles else []

    async def _is_tweet_pinned(self, article: WebElement) -> bool:
        """Check if tweet is pinned"""
        try:
            pinned_elements = await article.query(expression="//div", find_all=True)
            if not pinned_elements or isinstance(pinned_elements, WebElement):
                logger.warning("No pinned elements found")
                return False

            for elem in pinned_elements:
                try:
                    text = await elem.text
                    if text and "pinned" in text.lower():
                        return True
                except:
                    continue
        except:
            pass
        return False

    async def _find_tweet_link(self, article: WebElement) -> Optional[str]:
        """Find the link to individual tweet"""
        try:
            links = await article.query(expression="//a", find_all=True)
            if not links or isinstance(links, WebElement):
                logger.warning("No links found")
                return None

            for link in links:
                try:
                    href = link.get_attribute(name="href")
                    if href and "/status/" in href and self.account_name in href:
                        if not href.startswith("http"):
                            href = f"https://x.com{href}"
                        return href
                except:
                    continue
        except Exception as e:
            logger.debug(f"Error finding tweet link: {e}")

        return None

    async def _extract_tweet_links(self, articles: List) -> List[str]:
        """Extract tweet links from articles"""
        links = set()

        for article in articles:
            try:
                if await self._is_tweet_pinned(article):
                    logger.debug("Skipping pinned tweet")
                    continue

                if link := await self._find_tweet_link(article):
                    links.add(link)
                    logger.debug(f"Found tweet link: {link}")

            except Exception as e:
                logger.error(f"Error extracting tweet link: {e}")
                continue

        return list(set(links))

    async def scrape_tweet_links(self, total_tweets: int = 25) -> List[str]:
        """Scrape tweet links from user profile"""
        try:
            chrome_options = self._get_chrome_options()
            async with Chrome(options=chrome_options) as browser:

                tab = await browser.start()
                logger.info(f"Navigating to {self.account_url}")

                await tab.go_to(self.account_url)
                await tab.find_or_wait_element(by=By.XPATH, value="//article", timeout=10)

                if not (articles := await self._scroll_until_tweets_loaded(tab, total_tweets)):
                    logger.warning("No articles found")
                    return []

                # Extract links from articles
                links = await self._extract_tweet_links(articles)
                logger.info(f"Collected {len(links)} tweet links")
                return links

        except Exception as e:
            logger.error(f"Error scraping tweet links: {e}")
            return []
