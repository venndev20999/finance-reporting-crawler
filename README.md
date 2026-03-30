# Finance Stock Reporting Crawler

A Python-based web crawler for Vietnamese stock market news from CafeF and CafeBiz, built with `FastAPI` and `crawl4ai`.

## Features
- **Daily Crawling**: Automatically identifies and fetches the latest stock market news (within last 24h).
- **Markdown Export**: Converts crawled articles into clean Markdown files for easy reading and future processing.
- **RESTful API**: Expose endpoints to trigger crawls and list available reports.
- **Modern Stack**: Powered by `uv` for package management, `crawl4ai` for extraction, and `FastAPI` for the web interface.

## Project Structure
```text
.
├── app/
│   ├── main.py      # FastAPI application & API endpoints
│   └── crawler.py   # Crawl4AI logic and website parsers
├── data/
│   └── reports/     # Generated Markdown files
├── pyproject.toml   # Project dependencies
└── .python-version  # Python version (3.13)
```

## Setup & Run

### 1. Prerequisites
Ensure you have `uv` installed.

### 2. Install Dependencies
```bash
uv sync
uv run playwright install --with-deps chromium
```

### 3. Run the API Server
```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## API Endpoints

- `GET /`: Health check.
- `GET /crawl/latest-articles`: Lists the latest news titles and URLs without fetching full content.
- `POST /crawl/trigger`: Triggers a background job to crawl all recent articles and save them to `data/reports/`.
- `GET /reports`: Lists all saved `.md` files in the reports directory.

## Current Sources
- **CafeF**: [Thị trường chứng khoán](https://cafef.vn/thi-truong-chung-khoan.chn)
- **CafeBiz**: [Tài chính](https://cafebiz.vn/tai-chinh.chn)

## Future Work
- Ingest data into PostgreSQL.
- Add more news sources.
- Implement scheduled crawling with APScheduler.

How to Run:
Sync dependencies: uv sync
Install Playwright browser: uv run playwright install --with-deps chromium
Start the server: uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
Trigger a crawl: curl -X POST http://localhost:8000/crawl/trigger