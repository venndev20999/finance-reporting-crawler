.PHONY: help install run trigger-crawl list-latest get-json list-md clean

# Variables
PORT ?= 8000
HOST ?= 0.0.0.0
LIMIT ?= 5

help:
	@echo "Finance Stock Reporting Crawler - Makefile"
	@echo ""
	@echo "Usage:"
	@echo "  make install         Install dependencies and playwright browsers"
	@echo "  make run             Start the FastAPI server"
	@echo "  make trigger-crawl   Trigger background crawling (Markdown generation)"
	@echo "  make list-latest     List metadata for latest available stock news"
	@echo "  make get-json        Fetch full content as JSON (LIMIT=$(LIMIT))"
	@echo "  make list-md         List all generated Markdown report files"
	@echo "  make clean           Remove all generated Markdown reports"

install:
	uv sync
	uv run playwright install --with-deps chromium

run:
	uv run uvicorn app.main:app --host $(HOST) --port $(PORT) --reload

trigger-crawl:
	curl -X POST http://localhost:$(PORT)/crawl/trigger

list-latest:
	curl http://localhost:$(PORT)/crawl/latest-articles

get-json:
	curl "http://localhost:$(PORT)/crawl/content-json?limit=$(LIMIT)"

list-md:
	curl http://localhost:$(PORT)/reports

clean:
	rm -rf data/reports/*.md
	@echo "Cleaned generated reports."
