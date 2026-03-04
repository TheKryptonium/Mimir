from fastapi import APIRouter, status, HTTPException
from typing import Optional, List
from src.books.data import books_collection
from src.books.schemas import Book, BookUpdateModel

book_router = APIRouter()

@book_router.get('/')
def read_books()-> List[Book]:
    return books_collection[::-1]


@book_router.get('/{book_id}')
def read_book(book_id: int)->dict:
    for book in books_collection:
        if book["id"]==book_id:
            return book
    raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail="Book not found")
    

@book_router.post('/', status_code = status.HTTP_201_CREATED)
def create_book(book: Book)->Book:
    books_collection.append(book.model_dump())
    return book


@book_router.patch('/{book_id}')
def update_book(book_id: int, book_updates: BookUpdateModel):
    for book in books_collection:
        if book["id"] == book_id:
            book['title'] = book_updates.title
            book['author'] = book_updates.author
            book['year'] = book_updates.year
            
            return book
    
    raise HTTPException(status.HTTP_404_NOT_FOUND, detail = 'Book not found')


@book_router.delete('/{book_id}', status_code = status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int):
    for book in books_collection:
        if book['id'] == book_id:
            books_collection.remove(book)
            return books_collection
    
    raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Book not found")