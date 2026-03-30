from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os
from datetime import datetime

from .crawler import CrawlerService

app = FastAPI(
    title="Stock News Crawler",
    description="Crawls Cafef and Cafebiz for stock reports/news and saves them as Markdown files.",
    version="1.0.0"
)

# Initialize crawler service
crawler_service = CrawlerService(output_dir="data/reports")

class CrawlStatus(BaseModel):
    status: str
    message: str
    job_id: Optional[str] = None
    timestamp: datetime = datetime.now()

class ArticleInfo(BaseModel):
    title: str
    url: str
    source: str
    date: str

@app.get("/")
async def root():
    return {"message": "Finance Stock Reporting Crawler API is running."}

@app.post("/crawl/trigger", response_model=CrawlStatus)
async def trigger_crawl(background_tasks: BackgroundTasks):
    """
    Triggers a manual crawl for the latest stock reports.
    Runs in the background.
    """
    job_id = f"crawl_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    background_tasks.add_task(crawler_service.run_daily_crawl)
    
    return CrawlStatus(
        status="started",
        message="Crawler job has been triggered in the background.",
        job_id=job_id
    )

@app.get("/crawl/latest-articles", response_model=List[ArticleInfo])
async def list_latest_articles():
    """
    Lists only the metadata of the latest articles without crawling full content.
    Useful for seeing what's available before triggering a full crawl.
    """
    cafef_articles = await crawler_service.get_latest_articles("https://cafef.vn/thi-truong-chung-khoan.chn", "cafef")
    
    all_articles = cafef_articles
    
    return [
        ArticleInfo(
            title=a.title,
            url=a.url,
            source=a.source,
            date=a.timestamp
        ) for a in all_articles
    ]

@app.get("/reports", response_model=List[str])
async def list_reports():
    """
    Lists all saved markdown report files.
    """
    if not os.path.exists("data/reports"):
        return []
    
    files = [f for f in os.listdir("data/reports") if f.endswith(".md")]
    return sorted(files, reverse=True)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
