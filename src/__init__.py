from fastapi import FastAPI
from src.books.routes import book_router
from src.auth.routes import auth_router
from src.db.main import init_db
from contextlib import asynccontextmanager

"""Transform a simple generator function in a whole async context manager, which can be used in the lifespan parameter of FastAPI."""
@asynccontextmanager 
async def life_span(app: FastAPI):
    print("Server is running...")
    await init_db()
    yield
    print("Server has been stopped...")

version = "v1"

app = FastAPI(
    title="Mimir",
    description="A REST API for a book review web service",
    version = version,
    lifespan = life_span
)

app.include_router(book_router, prefix=f"/api/{version}/books", tags=['books'])
app.include_router(auth_router, prefix=f"/api/{version}/auth", tags=["auth"])