from app.config import settings
from app.db.mongodb import get_db
from groq import AsyncGroq

from app.config import settings
from app.db.mongodb import get_db
from groq import AsyncGroq

# simple setup
api_key = settings.GROQ_API_KEY
client = AsyncGroq(api_key=api_key) if api_key else None

async def generate_summary(page_id: str):
    # lazy fetch db
    db = get_db()
    if db is None:
        from app.db.mongodb import mongodb
        db = mongodb.db

    # Fetch data
    page_data = await db.pages.find_one({"page_id": page_id})
    if not page_data:
        return {"error": "Page not found"}

    # If no key, return mock
    if not client:
        return {
            "summary": f"[MOCK AI SUMMARY] {page_data.get('name')} is a company in {page_data.get('industry')}. (Groq API Key missing)",
            "note": "Groq API Key not provided."
        }

    # Construct prompt
    context = f"""
    Page Name: {page_data.get('name')}
    Description: {page_data.get('description')}
    Industry: {page_data.get('industry')}
    Followers: {page_data.get('followers')}
    Specialities: {', '.join(page_data.get('specialities', []))}
    """
    
    try:
        chat_completion = await client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional business analyst. specific concise summary of the company based on the provided details."
                },
                {
                    "role": "user",
                    "content": f"Summarize this company profile:\n{context}"
                }
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.5,
            max_tokens=500,
        )
        
        summary = chat_completion.choices[0].message.content
        return {
            "summary": summary
        }
    except Exception as e:
        print(f"Groq API Error: {e}")
        return {
            "summary": "Error generating summary.",
            "error": str(e)
        }

# keeping the object wrapper just for compatibility if imports elsewhere expect it
class SimpleAI:
    async def generate_summary(self, pid):
        return await generate_summary(pid)

ai_service = SimpleAI()
