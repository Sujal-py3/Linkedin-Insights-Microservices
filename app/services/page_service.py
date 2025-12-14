import json
from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import HTTPException
from app.db.mongodb import get_db
from app.db.redis import get_redis
from app.scraper.linkedin import scraper_service
from app.models.page import Page, Post, Employee

class PageService:
    @property
    def db(self):
        result = get_db()
        if result is None:
            # Fallback or just let it fail naturally if connection issues
            from app.db.mongodb import mongodb
            return mongodb.db
        return result

    @property
    def redis(self):
        result = get_redis()
        if result is None:
           from app.db.redis import redis_client
           return redis_client.client
        return result
    
    async def get_page(self, page_id: str) -> Page:
        # 1. Check Redis Cache
        if self.redis:
            cached_page = await self.redis.get(f"page:{page_id}")
            if cached_page:
                print(f"Cache Hit for {page_id}")
                return Page.model_validate_json(cached_page)
        
        # 2. Check Database
        db_page = await self.db.pages.find_one({"page_id": page_id})
        if db_page:
            print(f"DB Hit for {page_id}")
            page_obj = Page(**db_page)
            # Cache it for next time
            if self.redis:
                await self.redis.setex(f"page:{page_id}", 300, page_obj.model_dump_json())
            return page_obj
        
        # 3. Scrape if not found
        print(f"Scraping {page_id}...")
        try:
            page_data, posts_data, employees_data = await scraper_service.scrape_page(page_id)
            
            # Save to DB
            await self.db.pages.insert_one(page_data.model_dump(by_alias=True))
            
            if posts_data:
                await self.db.posts.insert_many([p.model_dump(by_alias=True) for p in posts_data])
                
            if employees_data:
                await self.db.employees.insert_many([e.model_dump(by_alias=True) for e in employees_data])
            
            # Cache it
            if self.redis:
                await self.redis.setex(f"page:{page_id}", 300, page_data.model_dump_json())
            
            return page_data
        except Exception as e:
            # If scraping fails, and we have nothing, raise 404 or 500
            # Ideally we might have a "ScrapeFailed" status in DB
            raise HTTPException(status_code=500, detail=f"Failed to fetch page data: {str(e)}")

    async def list_pages(self, min_followers: Optional[int] = None, 
                         max_followers: Optional[int] = None, 
                         industry: Optional[str] = None,
                         name: Optional[str] = None,
                         limit: int = 10, skip: int = 0) -> List[Page]:
        
        query = {}
        if min_followers is not None and max_followers is not None:
            query["followers"] = {"$gte": min_followers, "$lte": max_followers}
        elif min_followers is not None:
            query["followers"] = {"$gte": min_followers}
        elif max_followers is not None:
            query["followers"] = {"$lte": max_followers}
            
        if industry:
            query["industry"] = {"$regex": industry, "$options": "i"}
            
        if name:
            query["name"] = {"$regex": name, "$options": "i"}

        cursor = self.db.pages.find(query).skip(skip).limit(limit)
        pages = await cursor.to_list(length=limit)
        return [Page(**p) for p in pages]

    async def get_posts(self, page_id: str, limit: int = 10) -> List[Post]:
        cursor = self.db.posts.find({"page_id": page_id}).sort("created_at", -1).limit(limit)
        posts = await cursor.to_list(length=limit)
        return [Post(**p) for p in posts]

    async def get_employees(self, page_id: str) -> List[Employee]:
        cursor = self.db.employees.find({"page_id": page_id})
        employees = await cursor.to_list(length=100) # Cap at 100 for now
        return [Employee(**e) for e in employees]

page_service = PageService()
