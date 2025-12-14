from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
import json
from app.models.page import Page, Post, Employee
# removing the service pattern to make it less "generic"
from app.db.mongodb import get_db
from app.db.redis import get_redis, redis_client 
# using our new simple scraper function
from app.scraper.linkedin import fetch_linkedin_data

router = APIRouter()

# direct db access here
db = get_db()

@router.get("/pages/{page_id}", response_model=Page)
async def get_page_details(page_id: str):
    """
    Get details of a LinkedIn Page by its ID (e.g., deepsolv).
    Fetches from DB or scrapes if missing.
    """
    # 1. try cache
    # accessing global client directly if possible or getting it
    r = redis_client.client
    if r:
        try:
            cached = await r.get(f"page:{page_id}")
            if cached:
                print(f"CACHE HIT: {page_id}")
                return Page.model_validate_json(cached)
        except Exception as e:
            print(f"redis error: {e}")

    # 2. try mongo
    # lazy load db if global var is None (it might be depending on import order/init)
    local_db = get_db()
    if local_db is None:
        from app.db.mongodb import mongodb
        local_db = mongodb.db

    exists = await local_db.pages.find_one({"page_id": page_id})
    if exists:
        print(f"DB HIT: {page_id}")
        p = Page(**exists)
        # set cache
        if r:
            await r.setex(f"page:{page_id}", 300, p.model_dump_json())
        return p

    # 3. scrape
    print(f"SCRAPING: {page_id}")
    try:
        data = await fetch_linkedin_data(page_id)
        
        # save stuff
        p_data = data["page"]
        await local_db.pages.insert_one(p_data)
        
        posts = data["posts"]
        if posts:
            await local_db.posts.insert_many(posts)
            
        emps = data["employees"]
        if emps:
            await local_db.employees.insert_many(emps)

        # return obj
        final_page = Page(**p_data)
        
        # cache
        if r:
            await r.setex(f"page:{page_id}", 300, final_page.model_dump_json())
            
        return final_page

    except Exception as e:
        print(f"Scrape failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/pages", response_model=List[Page])
async def search_pages(
    min_followers: Optional[int] = Query(None, description="Minimum followers count"),
    max_followers: Optional[int] = Query(None, description="Maximum followers count"),
    industry: Optional[str] = Query(None, description="Filter by industry (regex)"),
    name: Optional[str] = Query(None, description="Search by name (regex)"),
    limit: int = Query(10, ge=1, le=100),
    page: int = Query(1, ge=1, description="Page number for pagination")
):
    skip = (page - 1) * limit
    local_db = get_db()
    if local_db is None:
        from app.db.mongodb import mongodb
        local_db = mongodb.db

    q = {}
    if min_followers: q["followers"] = {"$gte": min_followers}
    if max_followers: 
        if "followers" in q:
            q["followers"]["$lte"] = max_followers
        else:
            q["followers"] = {"$lte": max_followers}
            
    if industry: q["industry"] = {"$regex": industry, "$options": "i"}
    if name: q["name"] = {"$regex": name, "$options": "i"}

    cursor = local_db.pages.find(q).skip(skip).limit(limit)
    out = await cursor.to_list(length=limit)
    return [Page(**x) for x in out]


@router.get("/pages/{page_id}/posts", response_model=List[Post])
async def get_page_posts(page_id: str):
    local_db = get_db()
    if local_db is None:
        from app.db.mongodb import mongodb
        local_db = mongodb.db
        
    c = local_db.posts.find({"page_id": page_id}).sort("created_at", -1).limit(20)
    res = await c.to_list(length=20)
    return [Post(**x) for x in res]

@router.get("/pages/{page_id}/employees", response_model=List[Employee])
async def get_page_employees(page_id: str):
    return []

@router.get("/pages/{page_id}/summary")
async def get_page_summary(page_id: str):
    # just import here, messy style
    from app.services.ai_service import ai_service
    return await ai_service.generate_summary(page_id)
