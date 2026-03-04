from fastapi import FastAPI
from src.books.routes import book_router
from src.db.main import init_db
from contextlib import asynccontextmanager

@asynccontextmanager
async def life_span(app: FastAPI):
    print(f"{app} server is running...")
    await init_db()
    yield
    print(f'{app} has been stopped...')

version = "v1"

app = FastAPI(
    title="Mimir",
    description="A REST API for a book review web service",
    version = version,
    lifespan = life_span
)

app.include_router(book_router, prefix=f"/api/{version}/books", tags=['books'])