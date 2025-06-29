# PyDoll Scraper Project

A modern web scraper built with PyDoll that provides both CLI and API interfaces for web scraping and social media data extraction.

## Project Structure

- **src/pydoll_scraper/**: Main package directory
  - **core/**: Core scraping functionality (`scraper.py`, `xcom_scraper.py`)
  - **api/**: FastAPI interface (`main.py`)
- **tests/**: All test files
- **docker/**: Docker configuration
  - **Dockerfile**: Container definition
  - **scripts/**: Runtime scripts for containerized execution
- **output/**: Scraper output files
- **docker-compose.yml**: Container orchestration

## Key Technologies

- **PyDoll**: Main web scraping library
- **FastAPI**: API framework
- **Pydantic**: Data validation and serialization
- **Chrome/Chromium**: Browser automation via PyDoll
- **Docker**: Containerization with Chrome support
- **uv**: Python package manager and dependency resolver

## Development Standards

### Code Style
- Use **Black** formatter with 100 character line length
- Follow **Ruff** linting rules (configured in pyproject.toml)
- Use **MyPy** for type checking
- Python 3.10+ compatibility required

### Import Organization
- Standard library imports first
- Third-party imports second  
- Local imports last
- Use relative imports within the package

### Data Classes & Models
- Use `@dataclass` for simple data structures
- Use Pydantic `BaseModel` for API request/response models
- Include type hints for all function parameters and returns

### Async/Await Patterns
- Core scrapers use async/await extensively
- Always handle browser cleanup in try/finally blocks
- Use `asyncio.gather()` for concurrent operations

## Common Commands

### Development
```bash
# Install dependencies
uv sync

# Run tests
uv run pytest

# Lint and format
uv run ruff check src/ tests/
uv run black src/ tests/
uv run mypy src/

# Run API server locally
uv run uvicorn src.pydoll_scraper.api.main:app --reload

# Run CLI scraper
uv run python -m src.pydoll_scraper.core.scraper
```

### Docker
```bash
# Build and run with docker-compose
docker-compose up --build

# Run CLI scraper in container
docker-compose --profile cli up web-scraper

# View logs
docker-compose logs scraper-api
```

## Architecture Notes

### Browser Configuration
- Chrome runs in headless mode by default in containers
- Xvfb virtual display used for containerized Chrome
- Chrome binary path configurable via `CHROME_BIN` environment variable
- Specific Chrome flags for Docker compatibility (--no-sandbox, --disable-dev-shm-usage)

### API Design
- RESTful endpoints with proper HTTP status codes
- Background job processing for long-running scrape operations
- In-memory job storage (consider Redis for production)
- Comprehensive error handling and logging

### Data Flow
1. **Input**: URLs, selectors, or search queries
2. **Processing**: PyDoll browser automation extracts data
3. **Output**: Structured JSON with metadata and timestamps
4. **Storage**: Files in `output/` directory, API responses via JSON

## Environment Variables

- `CHROME_BIN`: Path to Chrome binary (default: `/usr/bin/google-chrome`)
- `CHROME_PATH`: Alternative Chrome path
- `DISPLAY`: X11 display for containerized Chrome (`:99`)

## Testing Strategy

- Unit tests for core scraping logic
- Integration tests for API endpoints
- Test files follow `test_*.py` naming convention
- Use pytest with asyncio support

## Deployment Considerations

- Docker containers include Chrome and all dependencies
- Volume mounts for persistent output storage
- Redis service available for caching (optional)
- Health checks and proper container restart policies

## Common Patterns

### Error Handling
```python
try:
    # Browser operations
    result = await scraper.scrape_url(url)
except Exception as e:
    logger.error(f"Scraping failed: {e}")
    raise HTTPException(status_code=500, detail=str(e))
```

### Data Validation
```python
class ScrapeRequest(BaseModel):
    url: HttpUrl
    selectors: Optional[Dict[str, str]] = None
```

### Async Context Management
```python
async with Chrome(options=options) as browser:
    # Browser operations
    page = await browser.get(url)
```
