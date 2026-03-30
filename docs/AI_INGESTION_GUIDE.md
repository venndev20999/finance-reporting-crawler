# Best Practices for crawl4ai & AI Ingestion

To get the most out of `crawl4ai` when integrating with **LangChain**, **n8n**, or other AI agents, follow these best practices for high-quality, structured, and cost-effective data.

## 1. Structured Data Extraction (The "Pro" Way)
Instead of just getting Markdown, you can provide `crawl4ai` with a schema to get structured JSON directly. This is ideal for **n8n** or **LangChain** tool-calling.

### Example: Extracting Stock Metrics
```python
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from pydantic import BaseModel, Field

class StockReport(BaseModel):
    ticker: str = Field(..., description="The stock ticker symbol")
    sentiment: str = Field(..., description="Bullish, Bearish, or Neutral")
    summary: str = Field(..., description="1-sentence summary of the news")

strategy = LLMExtractionStrategy(
    provider="openai/gpt-4o",
    api_token="YOUR_TOKEN",
    schema=StockReport.schema(),
    instruction="Extract stock information from the text."
)

result = await crawler.arun(url=url, extraction_strategy=strategy)
print(result.extracted_content) # Clean JSON!
```

## 2. Content Cleaning & Noise Reduction
Don't feed the LLM junk. Clean the DOM before conversion:
- **`exclude_tags`**: Remove `['nav', 'footer', 'script', 'style', 'header', 'aside']`.
- **`remove_overlay_elements`**: Set to `True` for modern sites with popups.
- **`word_count_threshold`**: Set (e.g., `200`) to avoid crawling short, useless sidebar snippets.
- **`fit_markdown`**: Use `result.markdown.fit_markdown` to get only the "main" content, excluding menus and sidebars.

## 3. Caching (Cost & Speed)
- Use `CacheMode.ENABLED` or `CacheMode.BYPASS` based on how frequently the source updates.
- In **n8n**, this prevents your workflow from hitting the website too hard and getting your IP blocked.

## 4. Integration Strategies

### n8n Workflow
1. **HTTP Request Node**: Call your FastAPI endpoint `/crawl/trigger`.
2. **Wait Node**: Wait for processing (or use a webhook callback if you implement one).
3. **HTTP Request Node**: Call `/reports` to get filenames.
4. **AI Agent Node**: Pass the Markdown content into the agent's context.

### LangChain
Use `crawl4ai` as a custom `BaseLoader`:
```python
from langchain.docstore.document import Document

# Process crawl4ai result
langchain_doc = Document(
    page_content=result.markdown.raw_markdown,
    metadata={
        "source": result.url,
        "title": article_title,
        "timestamp": crawl_time
    }
)
```

## 5. Handling Anti-Bot & Stealth
Cafef may eventually block basic crawlers.
- **`stealth=True`**: Always enable in `CrawlerRunConfig`.
- **`user_agent`**: Rotate user agents if crawling at high frequency.
- **`wait_for`**: Use CSS selectors to wait for the page to be fully loaded before extracting.

## 6. Recommendations for Stock Data
- **Metadata is King**: When saving to Markdown, keep the header with URL and Date (as implemented). This helps RAG (Retrieval-Augmented Generation) systems attribute information correctly.
- **Chunking**: For long reports, use LangChain's `MarkdownTextSplitter` instead of a generic recursive splitter to maintain document structure.
