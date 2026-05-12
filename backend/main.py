# backend/main.py
from fastapi import FastAPI

# If you have DB init code, import and run it here
# Example: from .database import init_db
# init_db()

# If you have routers, import and include them
# Example: from .routers import items_router
# app.include_router(items_router)

app = FastAPI(title="ueba-backend")

@app.get("/")
async def root():
    return {"status": "ok"}
