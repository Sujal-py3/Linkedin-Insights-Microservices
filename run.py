import sys
import asyncio
import uvicorn

if __name__ == "__main__":
    # Enforce ProactorEventLoopPolicy on Windows for Playwright/Subprocess support
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    # Run Uvicorn programmatically
    # loop="asyncio" is crucial to respect the set_event_loop_policy above
    # reload=False is safer on Windows with Playwright to avoid subprocess loop conflicts
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=False, loop="asyncio")
