import asyncio
import os
from datetime import datetime, timedelta
import re
from typing import List, Optional
from urllib.parse import urljoin

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from pydantic import BaseModel

class ArticleMetadata(BaseModel):
    title: str
    url: str
    timestamp: str
    source: str

class CrawlerService:
    def __init__(self, output_dir: str = "data/reports"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def _is_recent(self, timestamp_str: str) -> bool:
        """
        Heuristic to check if the article is from today or yesterday.
        Cafef often uses "giờ trước", "phút trước" or "DD/MM/YYYY".
        Cafebiz uses "HH:mm".
        """
        now = datetime.now()
        
        # Check for relative time
        if any(keyword in timestamp_str for keyword in ["giờ trước", "phút trước", "ngay bây giờ"]):
            return True
            
        # Check for HH:mm (Cafebiz style)
        if re.match(r"^\d{1,2}:\d{2}$", timestamp_str.strip()):
            return True
            
        # Check for DD/MM/YYYY
        date_match = re.search(r"(\d{1,2})/(\d{1,2})/(\d{4})", timestamp_str)
        if date_match:
            day, month, year = map(int, date_match.groups())
            article_date = datetime(year, month, day)
            if (now - article_date).days <= 1:
                return True
                
        return False

    async def get_latest_articles(self, source_url: str, source_name: str) -> List[ArticleMetadata]:
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(url=source_url)
            if not result.success:
                print(f"Failed to crawl {source_url}")
                return []

            articles = []
            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(result.html, 'html.parser')
            
            if source_name == "cafef":
                # Cafef listing: items are div.tlitem
                items = soup.select("div.tlitem")
                for item in items:
                    title_tag = item.select_one("h3 a")
                    time_tag = item.select_one(".knswli-time") or item.select_one(".time-ago")
                    
                    if title_tag and time_tag:
                        title = title_tag.get_text(strip=True)
                        link = urljoin(source_url, title_tag['href'])
                        timestamp = time_tag.get_text(strip=True)
                        
                        if self._is_recent(timestamp):
                            articles.append(ArticleMetadata(
                                title=title,
                                url=link,
                                timestamp=timestamp,
                                source=source_name
                            ))
                            
            return articles

    async def crawl_article_to_md(self, article: ArticleMetadata):
        async with AsyncWebCrawler() as crawler:
            # Configure crawler for better article extraction
            config = CrawlerRunConfig(
                cache_mode=CacheMode.BYPASS,
                word_count_threshold=200,
                remove_overlay_elements=True
            )
            
            result = await crawler.arun(url=article.url, config=config)
            
            if result.success:
                # Sanitize title for filename
                safe_title = re.sub(r'[\\/*?:"<>|]', "", article.title)[:50]
                filename = f"{article.source}_{datetime.now().strftime('%Y%m%d')}_{safe_title}.md"
                filepath = os.path.join(self.output_dir, filename)
                
                content = f"# {article.title}\n\n"
                content += f"**Source:** {article.source}\n"
                content += f"**URL:** {article.url}\n"
                content += f"**Date:** {article.timestamp}\n\n"
                content += "---\n\n"
                # Updated for latest crawl4ai version
                if hasattr(result.markdown, 'raw_markdown'):
                    content += result.markdown.raw_markdown
                else:
                    content += result.markdown
                
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(content)
                
                return filepath
            return None

    async def crawl_article_to_dict(self, article: ArticleMetadata) -> Optional[dict]:
        """
        Crawls a single article and returns its content as a clean dictionary (JSON-friendly).
        No LLM/API token required.
        """
        async with AsyncWebCrawler() as crawler:
            config = CrawlerRunConfig(
                cache_mode=CacheMode.BYPASS,
                word_count_threshold=200,
                remove_overlay_elements=True
            )
            
            result = await crawler.arun(url=article.url, config=config)
            
            if result.success:
                content = result.markdown.raw_markdown if hasattr(result.markdown, 'raw_markdown') else result.markdown
                
                return {
                    "title": article.title,
                    "url": article.url,
                    "date": article.timestamp,
                    "source": article.source,
                    "content": content,
                    "crawled_at": datetime.now().isoformat()
                }
            return None

    async def run_daily_crawl(self):
        sources = [
            ("https://cafef.vn/thi-truong-chung-khoan.chn", "cafef"),
        ]
        
        all_new_articles = []
        for url, name in sources:
            articles = await self.get_latest_articles(url, name)
            all_new_articles.extend(articles)
            
        saved_files = []
        for article in all_new_articles:
            print(f"Crawling: {article.title}")
            path = await self.crawl_article_to_md(article)
            if path:
                saved_files.append(path)
                
        return saved_files
