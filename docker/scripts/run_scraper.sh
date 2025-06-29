#!/bin/bash

# Start virtual display
Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &

# Start x11vnc attached to the X display
x11vnc -display :99 -nopw -forever -shared -bg > /dev/null 2>&1

# Wait for display to start
sleep 5

# Run the scraper
uv run uvicorn src.pydoll_scraper.api.main:app --host 0.0.0.0 --port 8000
