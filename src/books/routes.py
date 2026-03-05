from fastapi import APIRouter, status, HTTPException, Depends
from typing import Optional, List
from sqlmodel.ext.asyncio.session import AsyncSession
from src.books.data import books_collection
from src.db.main import get_session
from .service import BookService
from src.books.schemas import Book, BookUpdateModel, BookCreateModel

book_router = APIRouter()
book_service = BookService()

@book_router.get('/', response_model = List[Book])
async def get_all_books(session: AsyncSession = Depends(get_session))-> List[Book]:
    books = await book_service.get_all_books(session)
    return books

@book_router.get('/{book_id}', response_model=Book)
async def get_book(book_id: str, session: AsyncSession=Depends(get_session))->dict:
    book = await book_service.get_book(session, book_id)
    if book:
        return book
    else:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail="Book not found")
    

@book_router.post('/', status_code = status.HTTP_201_CREATED, response_model = Book)
async def create_book(book: BookCreateModel, session: AsyncSession=Depends(get_session))->Book:
    new_book = await book_service.create_book(session, book)
    return new_book

@book_router.patch('/{book_id}')
async def update_book(book_id: str, book_updates: BookUpdateModel, session: AsyncSession=Depends(get_session)):
    update_book = await book_service.update_book(session, book_id, book_updates)
    if update_book:
        return update_book
    else:    
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail = 'Book not found')


@book_router.delete('/{book_id}', status_code = status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: str, session: AsyncSession = Depends(get_session)):
    book_to_detele = await book_service.delete_book(session, book_id)

    if book_to_detele:
        return book_to_detele
    else:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Book not found")