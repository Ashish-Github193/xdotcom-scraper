#!/bin/bash
# Wait for noVNC display to be ready
sleep 5
# Run the FastAPI server
uv run uvicorn src.pydoll_scraper.api.main:app --host 0.0.0.0 --port 8000