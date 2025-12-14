# LinkedIn Insights Microservice
## Issue
 Businesses require current LinkedIn company data (followers, posts, employees), but static databases quickly become outdated and official APIs are frequently costly or restricted.


 ## Method
 A **Hybrid Real-Time Architecture** is implemented by this microservice:
 1. On-Demand Scraping: This method uses a headless browser to retrieve new data only as needed.
 2. Redis is used for "smart caching," which minimizes scraper load by instantly fulfilling frequent requests.
 3. Persistence: Maintains historical data in MongoDB for backup and analytics purposes.

## Architecture

```mermaid
graph TD
    Client[Client / API Consumer] -->|HTTP Request| API[FastAPI Service]
    API -->|1. Check| Redis[(Redis Cache)]
    API -->|2. Check| Mongo[(MongoDB)]
    API -->|3. Fallback| Scraper[Scraper Logic]
    Scraper -->|Fetch| LinkedIn[LinkedIn Website]
    Scraper -->|Store| Mongo
    Scraper -->|Cache| Redis
    API -->|Generate Summary| AI[Groq AI API]
```

**Core Components:**
*   **FastAPI**: Entry point, handles HTTP requests and routing.
*   **Redis**: In-memory cache for sub-millisecond data retrieval.
*   **MongoDB**: Persistent storage for scraped profiles and posts.
*   **Scraper**: Headless browser (Playwright) to fetch fresh data from LinkedIn.
*   **Groq AI**: Generates summaries using Llama-3 models.

## Data Flow

```mermaid
sequenceDiagram
    participant User
    participant API
    participant Cache as Redis
    participant DB as MongoDB
    participant Scraper
    
    User->>API: GET /pages/{id}
    API->>Cache: Check for {id}
    alt Cache Hit
        Cache-->>API: Return JSON
        API-->>User: Return Cached Data
    else Cache Miss
        API->>DB: Find {id}
        alt DB Hit
            DB-->>API: Return Doc
            API->>Cache: Set Cache for next time
            API-->>User: Return DB Data
        else DB Miss
            API->>Scraper: Trigger Scrape
            Scraper->>Scraper: Visit LinkedIn & Parse
            Scraper->>DB: Insert Data
            Scraper-->>API: Return New Data
            API->>Cache: Set Cache
            API-->>User: Return Scraped Data
        end
    end
```

**Strategy: "Cache First, Scrape Last"**
1.  **Cache**: Fastest. Checks memory first.
2.  **DB**: Reliable. Checks disk if cache is empty.
3.  **Scrape**: Fallback. Only connects to LinkedIn if data is completely missing.


## Setup

1.  **Install**:
    ```bash
    pip install -r requirements.txt
    playwright install
    ```
2.  **Run**:
    ```bash
    python run.py
    ```
3.  **Docs**: Visit `http://localhost:8000/docs`

## Tech Stack
*   **FastAPI** (Async API)
*   **MongoDB** (Storage)
*   **Redis** (Caching)
*   **Playwright** (Scraping)
*   **Groq AI** (Summaries)