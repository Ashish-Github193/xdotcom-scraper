from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

from ..core.xcom_scraper import XComScraper

app = FastAPI(
    title="Web Scraper API",
    description="FastAPI endpoints for web scraping and social media data extraction",
    version="1.0.0",
)


class XComScrapeRequest(BaseModel):
    account_name: str
    total_tweets: int = 25


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Web Scraper API",
        "version": "1.0.0",
        "endpoints": {
            "xcom_links": "/xcom/links",
            "xcom_content": "/xcom/content",
        },
    }


@app.post("/xcom/links")
async def scrape_xcom_links(request: XComScrapeRequest):
    """Scrape tweet links from an X.com account"""
    try:
        scraper = XComScraper(request.account_name)
        links = await scraper.scrape_tweet_links(request.total_tweets)

        return {
            "success": True,
            "account": request.account_name,
            "count": len(links),
            "links": links,
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"X.com scraping error: {str(e)}",
        )
