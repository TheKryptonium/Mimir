from sqlmodel.ext.asyncio.session import AsyncSession
from .schemas import BookCreateModel, BookUpdateModel
from .models import Book
from sqlalchemy import desc
from sqlmodel import select

class BookService():
    async def get_all_books(self, session:AsyncSession):
        statement = select(Book).order_by(desc(Book.created_at))
        results = await session.execute(statement)
        return results.scalars().all()
    
    async def get_book(self, session: AsyncSession, book_uuid: str):
        statement = select(Book).where(Book.id == book_uuid)
        results = await session.execute(statement)
        book = results.scalars().first()
        
        return book if book is not None else None
    
    async def create_book(self, session: AsyncSession, book_data: BookCreateModel):
        book_dict  = book_data.model_dump()
        new_book = Book(
            **book_dict
        )
        
        session.add(new_book)
        await session.commit()
        
        return new_book
    
    async def update_book(self, session: AsyncSession, book_uuid: str, book_data: BookUpdateModel):
        book_update = await self.get_book(session, book_uuid)
        
        if book_update is not None:
            book_update_data_dict = book_data.model_dump(exclude_unset=True)
            for key, value in book_update_data_dict.items():
                setattr(book_update, key, value)
            
            await session.commit()
            
            await session.refresh(book_update)
            
            return book_update
        else:
            return None
    
    async def delete_book(self, session: AsyncSession, book_uuid: str):
        book_to_delete = await self.get_book(session, book_uuid)
    
        if book_to_delete:
            try:
                await session.delete(book_to_delete)
                await session.commit()
                return book_to_delete
            except Exception as e:
                await session.rollback() 
                raise e
        return None