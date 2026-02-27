from fastapi import FastAPI
from routes import router
from database import fake_db
from models import Item

app = FastAPI(title="Мое простое приложение")

app.include_router(router)

@app.get("/")
async def root():
    return {
        "message": "Добро пожаловать!",
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/items/")
async def create_item(item: Item):
    fake_db.append(item.dict())
    return {"item": item.dict(), "message": "Item created"}

@app.get("/items/")
async def get_items():
    return {"items": fake_db}