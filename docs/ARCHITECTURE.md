# Architecture Guide

**Document Purpose:** Understand the system design, patterns, and decision rationale for Mimir API

---

## Table of Contents

1. [High-Level Architecture](#high-level-architecture)
2. [Design Patterns](#design-patterns)
3. [Module Organization](#module-organization)
4. [Data Flow](#data-flow)
5. [Dependency Injection](#dependency-injection)
6. [Error Handling Strategy](#error-handling-strategy)
7. [Scalability Considerations](#scalability-considerations)
8. [Future Architecture](#future-architecture)

---

## High-Level Architecture

### System Overview Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    API Client Layer                          │
│        (Web Browser, Mobile App, External Services)         │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           │ HTTP/HTTPS
                           ▼
┌─────────────────────────────────────────────────────────────┐
│               FastAPI Application Layer                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Routes (API Endpoints)                             │  │
│  │  - /api/v1/auth/signup                              │  │
│  │  - /api/v1/books/*                                  │  │
│  └──────────────────────────────────────────────────────┘  │
│                           │                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Pydantic Schemas Layer (Validation)                │  │
│  │  - Request/Response contracts                        │  │
│  │  - Data validation                                   │  │
│  └──────────────────────────────────────────────────────┘  │
│                           │                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Service Layer (Business Logic)                     │  │
│  │  - UserService                                       │  │
│  │  - BookService                                       │  │
│  └──────────────────────────────────────────────────────┘  │
│                           │                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  SQLModel ORM Layer (Data Access)                   │  │
│  │  - User model                                        │  │
│  │  - Book model                                        │  │
│  └──────────────────────────────────────────────────────┘  │
└──────────────────────────┬──────────────────────────────────┘
                           │
        ┌──────────────────┴──────────────────┐
        │                                     │
        ▼                                     ▼
┌──────────────────────┐          ┌──────────────────────┐
│  PostgreSQL Database │          │  Connection Pool     │
│                      │          │  (asyncpg)           │
│  - Users Table       │          │  - Async connections │
│  - Books Table       │          │  - Connection reuse  │
└──────────────────────┘          └──────────────────────┘
```

---

## Design Patterns

### 1. Layered Architecture (3-Tier)

**Purpose:** Separation of concerns, testability, and maintainability

```
┌─────────────────────┐
│  Routes Layer       │  ← Handles HTTP requests/responses
├─────────────────────┤
│  Service Layer      │  ← Contains business logic
├─────────────────────┤
│  Data Access Layer  │  ← ORM and database operations
└─────────────────────┘
```

**Benefits:**
- Each layer has single responsibility
- Easy to test each layer independently
- Can modify one layer without affecting others
- Clear separation between API contract and implementation

### 2. Repository Pattern (Implicit)

Although not explicitly implemented as a separate repository class, each service acts as a repository:

```python
class BookService:
    async def get_all_books(self, session: AsyncSession):
        return await fetch_from_database()
    
    async def create_book(self, session: AsyncSession, book_data):
        return await persist_to_database()
```

**Future Enhancement:** Could extract into explicit `Repository` classes for better testability.

### 3. Dependency Injection

**Pattern:** Constructor/Method injection using FastAPI's `Depends()`

```python
@router.get("/")
async def get_books(session: AsyncSession = Depends(get_session)):
    # session is injected automatically
    await book_service.get_all_books(session)
```

**Benefits:**
- Loose coupling between components
- Easy to mock for testing
- Automatic resource lifecycle management
- Declarative dependencies

### 4. Factory Pattern

Database session creation uses factory pattern:

```python
def get_session() -> AsyncSession:
    # Creates and yields a new session
    # Automatically closes after use (context manager)
    Session = sessionmaker(bind=engine, class_=AsyncSession)
    async with Session() as session:
        yield session
```

### 5. Async/Await Pattern

**Pattern:** Asynchronous I/O for non-blocking operations

```python
async def create_book(self, session: AsyncSession, book_data):
    book = Book(**book_data)
    session.add(book)
    await session.commit()  # Non-blocking database write
    await session.refresh(book)
    return book
```

**Benefits:**
- Handle thousands of concurrent connections
- Improved throughput
- Better resource utilization
- Non-blocking I/O operations

---

## Module Organization

### Directory Structure Philosophy

```
src/
├── __init__.py          # Application entry point
├── config.py            # Configuration management
├── auth/                # Authentication Feature Module
│   ├── __init__.py
│   ├── models.py        # SQLModel definitions
│   ├── schemas.py       # Pydantic schemas
│   ├── routes.py        # FastAPI routes
│   ├── service.py       # Business logic
│   └── utils.py         # Helper functions
├── books/               # Books Feature Module (same structure)
│   ├── models.py
│   ├── schemas.py
│   ├── routes.py
│   ├── service.py
│   ├── data.py          # Mock data
│   └── __init__.py
└── db/                  # Database Configuration
    ├── __init__.py
    └── main.py          # Connection & session setup
```

### Feature Module Structure

Each feature module follows this pattern:

```
feature/
├── models.py          # ORM Models (SQLModel)
│   └── DatabaseModel class
├── schemas.py         # Request/Response schemas (Pydantic)
│   ├── CreateModel
│   ├── ResponseModel
│   └── UpdateModel
├── routes.py          # API Endpoints
│   ├── @router.get
│   ├── @router.post
│   ├── @router.patch
│   └── @router.delete
├── service.py         # Business Logic
│   ├── get_all()
│   ├── create()
│   ├── update()
│   └── delete()
└── utils.py           # Helpers
    └── Helper functions specific to this feature
```

### Configuration Module

```python
# config.py
class Settings(BaseSettings):
    DATABASE_URL: str  # From environment
    
    model_config = SettingsConfigDict(
        env_file='.env'
    )

Config = Settings()  # Global config instance
```

**Used throughout:**
```python
from src.config import Config

engine = create_engine(Config.DATABASE_URL)
```

---

## Data Flow

### User Registration Flow

```
1. Client POST /api/v1/auth/signup
   │
2. routes.py: create_user()
   ├─ Validates request with UserCreateModel
   ├─ Checks if user exists
   │
3. service.py: create_user()
   ├─ Hashes password using bcrypt
   ├─ Creates User model instance
   ├─ Commits to database
   │
4. Database Write
   ├─ User record inserted into users table
   │
5. Response
   └─ Return UserModel (201 Created)
```

### Book CRUD Flow

**Read (Get All Books):**
```
GET /api/v1/books
   │
1. routes.py: get_all_books()
   │
2. service.py: get_all_books()
   ├─ Build SQL SELECT statement
   ├─ Order by created_at DESC
   │
3. Database Query
   ├─ Execute async query
   │
4. Response
   └─ Return List[Book]
```

**Create (Post Book):**
```
POST /api/v1/books
   │
1. routes.py: create_book()
   ├─ Validates request with BookCreateModel
   │
2. service.py: create_book()
   ├─ Create Book instance
   ├─ Add to session
   ├─ Commit transaction
   │
3. Database Write
   ├─ Generate UUID for ID
   ├─ Set created_at/updated_at timestamps
   ├─ Insert record
   │
4. Response
   └─ Return created Book (201 Created)
```

**Update (Patch Book):**
```
PATCH /api/v1/books/{id}
   │
1. routes.py: update_book()
   ├─ Validates request with BookUpdateModel
   │
2. service.py: update_book()
   ├─ Find existing book by ID
   ├─ Update fields (exclude_unset=True)
   ├─ Set updated_at timestamp
   ├─ Commit transaction
   │
3. Database Update
   ├─ Execute UPDATE statement
   │
4. Response
   └─ Return updated Book
```

**Delete (Delete Book):**
```
DELETE /api/v1/books/{id}
   │
1. routes.py: delete_book()
   │
2. service.py: delete_book()
   ├─ Find book by ID
   ├─ Delete from session
   ├─ Commit transaction
   │
3. Database Delete
   ├─ Execute DELETE statement
   │
4. Response
   └─ Return 204 No Content
```

---

## Dependency Injection

### FastAPI Dependency System

```python
# Definition
async def get_session() -> AsyncSession:
    """Dependency that provides database session"""
    Session = sessionmaker(bind=engine, class_=AsyncSession)
    async with Session() as session:
        yield session  # Provide session
                       # Cleanup happens automatically
```

### Usage in Routes

```python
@router.get("/")
async def get_books(
    session: AsyncSession = Depends(get_session)
) -> List[Book]:
    # session is automatically injected
    # session is automatically cleaned up after request
    return await book_service.get_all_books(session)
```

### Dependency Tree

```
HTTP Request
   │
   ├─ FastAPI detects Depends(get_session)
   │
   ├─ Calls get_session()
   │
   ├─ Creates AsyncSession
   │
   ├─ Yields session to route handler
   │
   ├─ Route handler executes
   │
   └─ Session cleanup and return
      (finally block in context manager)
```

---

## Error Handling Strategy

### Current Implementation

**Route-level Error Handling:**
```python
@router.get("/{book_id}")
async def get_book(book_id: str, session: AsyncSession = Depends(get_session)):
    book = await book_service.get_book(session, book_id)
    
    if book:
        return book
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
```

**Service-level Error Handling:**
```python
async def delete_book(self, session: AsyncSession, book_uuid: str):
    book_to_delete = await self.get_book(session, book_uuid)

    if book_to_delete:
        try:
            await session.delete(book_to_delete)
            await session.commit()
            return book_to_delete
        except Exception as e:
            await session.rollback()  # Rollback on error
            raise e
    return None
```

### Error Types Handled

1. **Resource Not Found** → 404 HTTPException
2. **Validation Error** → 422 Automatic (Pydantic)
3. **Duplicate Resource** → 403 Forbidden (UserService)
4. **Database Error** → 500 Server Error

### Future: Global Exception Handler

```python
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    # Log error
    # Return formatted error response
    # Track in error monitoring (Sentry)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )
```

---

## Scalability Considerations

### Current Scalability

**Horizontal Scaling:**
- ✅ Stateless application design
- ✅ Can run multiple instances behind load balancer
- ✅ No session affinity required
- ✅ Can scale independently

**Vertical Scaling:**
- ✅ Async/await allows high concurrency per instance
- ✅ Connection pooling optimizes database usage
- ✅ Efficient memory footprint (~150MB base)

### Database Scalability

**Current Approach:**
- Single PostgreSQL instance
- Connection pooling (via asyncpg)
- Max connections configurable

**Future Improvements:**
```python
# Connection pool optimization
engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_size=20,           # Max pool size
    max_overflow=10,        # Overflow connections
    pool_timeout=30,        # Timeout
    pool_recycle=3600       # Recycle connections
)
```

### Caching Strategy

**Future Redis Integration:**
```python
# Cache frequently accessed books
cache.get(f"book:{book_id}")
cache.set(f"book:{book_id}", book_data, ttl=3600)

# Cache all books list
cache.get("books:all")
```

### Rate Limiting

**Future Implementation:**
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.get("/books")
@limiter.limit("100/minute")
async def get_books():
    pass
```

### Query Optimization

1. **Index Strategy:**
   ```sql
   CREATE INDEX idx_books_created_at ON books(created_at DESC);
   CREATE INDEX idx_users_email ON users(email);
   ```

2. **N+1 Query Prevention:**
   - Current: Minimal N+1 risk (simple relationships)
   - Future: Use SQLAlchemy selectinload() for relationships

3. **Batch Operations:**
   ```python
   # Instead of loop creating books
   # Use bulk_insert for efficiency
   ```

---

## Future Architecture

### Planned Enhancements

#### 1. Authentication & Authorization
```python
# JWT Token-based auth
from fastapi.security import HTTPBearer, HTTPAuthCredentials

@app.get("/protected")
async def protected_route(credentials: HTTPAuthCredentials = Depends(HTTPBearer())):
    # Verify JWT token
    # Extract user info
    # Check permissions
    pass
```

#### 2. Message Queue (Celery + Redis)
```python
# Async background tasks
from celery import Celery

celery_app = Celery("mimir")

@celery_app.task
def send_verification_email(user_id):
    # Send email async
    pass
```

#### 3. API Versioning Strategy
```
/api/v1/books          # Current
/api/v2/books          # Future improvements
/api/v3/books          # Further enhancements
```

#### 4. GraphQL Support
```python
from strawberry import Schema, ObjectType

@ObjectType
class Book:
    id: str
    title: str
    author: str
```

#### 5. WebSocket Real-time Updates
```python
from fastapi import WebSocket

@app.websocket("/ws/books")
async def websocket_endpoint(websocket: WebSocket):
    # Real-time book updates
    pass
```

#### 6. Microservices Separation
```
mimir/
├── api-service/          # REST API
├── auth-service/         # Authentication
├── notification-service/ # Email/SMS
├── search-service/       # Elasticsearch
└── analytics-service/    # Usage analytics
```

### Monitoring & Observability

**Planned Additions:**
- Application Performance Monitoring (APM) - New Relic
- Error Tracking - Sentry
- Logging - Structured logging
- Metrics - Prometheus
- Tracing - OpenTelemetry

---

## Technology Evolution Path

```
Current (v1)
├─ REST API with SQLAlchemy
├─ PostgreSQL single instance
├─ Basic error handling
│
Next (v2)
├─ JWT Authentication
├─ Caching layer (Redis)
├─ Rate limiting
├─ Advanced error tracking
│
Future (v3)
├─ GraphQL support
├─ Microservices
├─ Real-time WebSocket
├─ Elasticsearch integration
└─ Advanced analytics
```

---

## ConCLUSION

The Mimir architecture is designed with:
- **Simplicity:** Easy to understand and maintain
- **Scalability:** Ready for horizontal scaling
- **Extensibility:** Clear patterns for adding features
- **Testability:** Loosely coupled components
- **Performance:** Async-first design

This foundation allows for confident evolution as requirements grow.
