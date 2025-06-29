#!/usr/bin/env python3
"""
Test script for X.com scraper
"""

import asyncio
import logging

from pydoll_scraper.core.xcom_scraper import XComScraper

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_basic_functionality():
    """Test basic X.com scraping functionality"""
    print("🧪 Testing X.com Scraper with PyDoll")
    print("=" * 50)

    # Test with a public account that likely has tweets
    test_account = "twitter"  # Official Twitter account

    try:
        scraper = XComScraper(test_account, headless=True)

        # Test 1: Scrape tweet links
        print(f"\n1️⃣ Testing tweet link collection for @{test_account}")
        links = await scraper.scrape_tweet_links(total_tweets=3)

        if links:
            print(f"✅ Successfully found {len(links)} tweet links")
            for i, link in enumerate(links[:3], 1):
                print(f"   {i}. {link}")
        else:
            print("❌ No tweet links found")
            return False

        # Test 2: Verify tweet links format
        print(f"\n2️⃣ Testing tweet link format validation")
        if links:
            valid_links = 0
            for link in links:
                if "/status/" in link and test_account in link:
                    valid_links += 1

            if valid_links == len(links):
                print(f"✅ All {len(links)} tweet links have valid format")
                print(f"   Example: {links[0]}")
            else:
                print(f"❌ Only {valid_links}/{len(links)} links have valid format")
                return False

        print(f"\n🎉 All tests passed!")
        return True

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False


async def test_cli_help():
    """Test CLI help functionality"""
    print(f"\n3️⃣ Testing CLI interface")
    import subprocess
    import sys

    try:
        # Test help command
        result = subprocess.run(
            [sys.executable, "/home/x/Projects/Experiments/cli_xcom_scraper.py", "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode == 0 and "X.com (Twitter) Scraper" in result.stdout:
            print("✅ CLI help command works")
            return True
        else:
            print("❌ CLI help command failed")
            return False

    except Exception as e:
        print(f"❌ CLI test failed: {e}")
        return False


async def main():
    """Run all tests"""
    print("🚀 Starting X.com Scraper Tests")
    print("=" * 60)

    success = True

    # Test basic functionality
    if not await test_basic_functionality():
        success = False

    # Test CLI
    if not await test_cli_help():
        success = False

    print("\n" + "=" * 60)
    if success:
        print("🎉 All tests completed successfully!")
        print("\nYou can now use the scraper with commands like:")
        print("python cli_xcom_scraper.py --account twitter --count 5 --visible")
    else:
        print("❌ Some tests failed. Check the logs above.")

    return success


if __name__ == "__main__":
    asyncio.run(main())
