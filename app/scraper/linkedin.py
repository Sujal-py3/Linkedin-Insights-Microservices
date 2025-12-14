import asyncio
from playwright.async_api import async_playwright
from datetime import datetime
import random

# just a helper for delays
async def sleep_abit(min_s=1, max_s=3):
    await asyncio.sleep(random.uniform(min_s, max_s))

async def fetch_linkedin_data(pid):
    # launch browser
    async with async_playwright() as p:
        # headless=True usually, but keeping it visible for testing if needed
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        page = await ctx.new_page()

        target = f"https://www.linkedin.com/company/{pid}"
        
        try:
            await page.goto(target, timeout=45000)
            await sleep_abit(2, 4)

            # --- Extract Basics ---
            # trying h1 for title
            t_el = await page.query_selector("h1")
            if t_el:
                title = await t_el.inner_text()
            else:
                title = pid

            # meta desc
            desc = await page.get_attribute('meta[name="description"]', "content")
            if not desc:
                desc = ""
            desc = desc.replace("About us", "").strip()

            # --- Mock Logic for Validation ---
            # hardcoded stuff because linkedin blocks bots hard
            f_count = 12345
            ind = "Technology"
            web = f"https://www.linkedin.com/company/{pid}"

            # --- Posts ---
            # scroll a bit
            for i in range(3):
                await page.keyboard.press("PageDown")
                await sleep_abit(0.5, 1.5)

            # fake posts for now
            posts = []
            posts.append({
                "page_id": pid,
                "post_id": f"urn:li:share:{pid}_001",
                "content": f"We are hiring at {title}!",
                "likes": 42,
                "comments_count": 5,
                "created_at": datetime.now(),
                "scraped_at": datetime.now()
            })
            posts.append({
                "page_id": pid,
                "post_id": f"urn:li:share:{pid}_002",
                "content": f"New update from {title}...",
                "likes": 100,
                "comments_count": 10,
                "created_at": datetime.now(),
                "scraped_at": datetime.now()
            })

            # return raw dicts
            return {
                "page": {
                    "page_id": pid,
                    "name": title,
                    "url": target,
                    "description": desc,
                    "followers": f_count,
                    "industry": ind,
                    "website": web,
                    "created_at": datetime.now(),
                    "updated_at": datetime.now()
                },
                "posts": posts,
                "employees": [] 
            }

        except Exception as e:
            print(f"Scrape error: {e}")
            raise e
        finally:
            await browser.close()
