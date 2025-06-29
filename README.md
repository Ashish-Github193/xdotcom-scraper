# PyDoll Web Scraper

A modern web scraper built with PyDoll that can handle JavaScript-heavy websites, bypass Cloudflare protection, and run in Docker containers.

## Features

- **Modern Browser Automation**: Uses PyDoll with Chrome DevTools Protocol (no WebDriver needed)
- **Async/Await Support**: High-performance concurrent scraping
- **Dockerized**: Ready-to-run Docker container
- **X.com (Twitter) Scraping**: Specialized scraper for X.com/Twitter for tweet links extraction
- **FastAPI Interface**: REST API endpoints for web scraping operations

## Installation

### Prerequisites
- Python 3.10+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

### Local Installation with uv (Recommended)
```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv sync

# Activate the virtual environment
source .venv/bin/activate  # On Linux/macOS
# Or on Windows: .venv\Scripts\activate
```
### Docker Installation
```bash
# Build the Docker image
docker build -t pydoll-scraper .

# Or use docker-compose
docker-compose up --build
```

## Usage

### X.com (Twitter) Scraping

#### Using the Core Module:
```bash
# Run the X.com scraper module
uv run python -m src.pydoll_scraper.core.xcom_scraper

# Or run directly
uv run python src/pydoll_scraper/core/xcom_scraper.py
```

### Python API

#### X.com (Twitter) Scraping:
```python
import asyncio
from src.pydoll_scraper.core.xcom_scraper import XComScraper

async def twitter_example():
    scraper = XComScraper("elonmusk", headless=True)
    
    # Scrape tweet links from profile
    links = await scraper.scrape_tweet_links(total_tweets=10)
    
    # Scrape tweet content
    tweets = await scraper.scrape_tweets_content(links)
    
    # Save results
    scraper.save_to_json(tweets, "elon_tweets.json")

asyncio.run(twitter_example())
```

### FastAPI Interface

#### Start the API server:
```bash
# Run the API server locally
uv run uvicorn src.pydoll_scraper.api.main:app --reload

# Or with custom host/port
uv run uvicorn src.pydoll_scraper.api.main:app --host 0.0.0.0 --port 8000
```

#### API Endpoints:
```bash
# Get API information
curl http://localhost:8000/

# Scrape X.com links
curl -X POST "http://localhost:8000/xcom/links" \
     -H "Content-Type: application/json" \
     -d '{"account_name": "elonmusk", "total_tweets": 10}'

### Docker Usage

#### Using Docker directly:
```bash
# Build and run
docker build -t pydoll-scraper .
docker run -v $(pwd)/output:/app/output pydoll-scraper
```

## Configuration

### Environment Variables
- `CHROME_BIN`: Path to Chrome binary
- `CHROME_PATH`: Path to Chrome executable
- `DISPLAY`: Display for headless mode

### Docker Volumes
- `./output:/app/output`: Mount local output directory
- `./scraper.py:/app/scraper.py`: Mount scraper code for development

## Development

### Project Structure
```
├── src/
│   └── pydoll_scraper/          # Main package directory
│       ├── __init__.py
│       ├── core/                # Core scraping functionality
│       │   ├── __init__.py
│       │   ├── scraper.py       # General web scraper
│       │   └── xcom_scraper.py  # X.com/Twitter scraper
│       └── api/                 # FastAPI interface
│           ├── __init__.py
│           └── main.py          # API endpoints
├── tests/                       # Test files
│   ├── __init__.py
│   └── test_xcom_scraper.py
├── docker/                      # Docker configuration
│   ├── Dockerfile
│   └── scripts/
│       ├── run_api.sh
│       └── run_scraper.sh
├── output/                      # Scraper output files
├── pyproject.toml              # Project dependencies and config
├── docker-compose.yml          # Docker Compose setup
├── uv.lock                     # Dependency lock file
└── README.md                   # This file
```

### Running Tests
```bash
# Run all tests with pytest
uv run pytest

# Run specific test file
uv run pytest tests/test_xcom_scraper.py

# Test with Docker
docker-compose run web-scraper uv run pytest
```

### Development Commands
```bash
# Install development dependencies
uv sync --group dev

# Run linting
uv run ruff check .

# Run formatting
uv run black .

# Run type checking
uv run mypy .

# Run tests
uv run pytest
```

## Troubleshooting

### Common Issues

1. **Chrome not found**: Make sure Chrome/Chromium is installed:
   ```bash
   # Ubuntu/Debian
   sudo apt update && sudo apt install google-chrome-stable
   # Or use Chromium
   sudo apt install chromium-browser
   
   # On macOS with Homebrew
   brew install --cask google-chrome
   ```
2. **Permission denied**: Ensure scripts have execute permissions: `chmod +x cli_*.py`
3. **Display issues in Docker**: The container uses Xvfb for headless display
4. **X.com rate limiting**: If you get blocked, try reducing the --count or adding delays

### Debug Mode
Modify the scraper code to set `headless=False` for visible browser debugging:
```python
# In scraper.py or xcom_scraper.py
scraper = WebScraper(headless=False)  # Shows browser window
```

## License

MIT License - feel free to use and modify as needed.
