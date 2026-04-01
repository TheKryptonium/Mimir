# API Reference Documentation

**Last Updated:** January 2024  
**API Version:** v1  
**Base URL:** `http://localhost:8000/api/v1`

---

## Table of Contents

1. [Authentication](#authentication)
2. [Response Format](#response-format)
3. [Error Handling](#error-handling)
4. [User Endpoints](#user-endpoints)
5. [Book Endpoints](#book-endpoints)
6. [Rate Limiting](#rate-limiting)
7. [Status Codes](#status-codes)

---

## Authentication

### Current Implementation
The API currently uses **no authentication** middleware on endpoints. All endpoints are publicly accessible.

### Future: JWT Implementation
When JWT authentication is added:

```bash
Authorization: Bearer <your_jwt_token_here>
```

All protected endpoints will require this header.

---

## Response Format

### Success Response (2xx)
All successful responses follow this format:

```json
{
  "data": { /* Response Object */ },
  "status": "success",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Single Resource
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "The Great Gatsby",
  "author": "F. Scott Fitzgerald",
  "year": 1925,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### Collection
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Book 1",
    ...
  },
  {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "title": "Book 2",
    ...
  }
]
```

---

## Error Handling

### Error Response Format (4xx, 5xx)

```json
{
  "detail": "Detailed error message",
  "status": "error",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Example Errors

**400 Bad Request - Validation Error:**
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "invalid email format",
      "type": "value_error.email"
    }
  ]
}
```

**403 Forbidden:**
```json
{
  "detail": "user with user@example.com already exists"
}
```

**404 Not Found:**
```json
{
  "detail": "Book not found"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Internal server error. Please try again later."
}
```

---

## User Endpoints

### 1. Register New User

**Endpoint:** `POST /auth/signup`

**Authentication:** None (Public)

**Request Body:**
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "firstname": "John",
  "lastname": "Doe",
  "password": "SecurePassword123"
}
```

**Field Validation:**
- `username` - Max 20 characters, required
- `email` - Valid email format, max 40 characters, required
- `firstname` - Max 20 characters, required
- `lastname` - Max 20 characters, required
- `password` - Minimum 6 characters, required

**Response:** `201 Created`
```json
{
  "uid": "550e8400-e29b-41d4-a716-446655440000",
  "username": "john_doe",
  "email": "john@example.com",
  "firstname": "John",
  "lastname": "Doe",
  "is_verified": false,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

**Errors:**
| Status | Error | Reason |
|--------|-------|--------|
| 400 | Validation Error | Invalid email format or field constraints violated |
| 403 | Forbidden | User with this email already exists |
| 500 | Server Error | Database error |

**cURL Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "firstname": "John",
    "lastname": "Doe",
    "password": "SecurePassword123"
  }'
```

**Python Example:**
```python
import requests

url = "http://localhost:8000/api/v1/auth/signup"
payload = {
    "username": "john_doe",
    "email": "john@example.com",
    "firstname": "John",
    "lastname": "Doe",
    "password": "SecurePassword123"
}

response = requests.post(url, json=payload)
user = response.json()
print(f"New user created: {user['uid']}")
```

---

## Book Endpoints

### 1. List All Books

**Endpoint:** `GET /books`

**Authentication:** None (Public)

**Query Parameters:** None

**Response:** `200 OK`
```json
[
  {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "title": "The Great Gatsby",
    "author": "F. Scott Fitzgerald",
    "year": 1925,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  },
  {
    "id": "223e4567-e89b-12d3-a456-426614174001",
    "title": "1984",
    "author": "George Orwell",
    "year": 1949,
    "created_at": "2024-01-15T10:35:00Z",
    "updated_at": "2024-01-15T10:35:00Z"
  }
]
```

**Notes:**
- Results sorted by `created_at` in descending order (newest first)
- Empty array returned if no books exist
- No pagination currently implemented

**cURL Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/books"
```

---

### 2. Get Single Book

**Endpoint:** `GET /books/{book_id}`

**Authentication:** None (Public)

**Path Parameters:**
- `book_id` (UUID, required) - Example: `123e4567-e89b-12d3-a456-426614174000`

**Response:** `200 OK`
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "title": "The Great Gatsby",
  "author": "F. Scott Fitzgerald",
  "year": 1925,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

**Errors:**
| Status | Error | Reason |
|--------|-------|--------|
| 404 | Not Found | Book with given ID doesn't exist |
| 400 | Bad Request | Invalid UUID format |

**cURL Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/books/123e4567-e89b-12d3-a456-426614174000"
```

---

### 3. Create Book

**Endpoint:** `POST /books`

**Authentication:** None (Public)

**Request Body:**
```json
{
  "title": "The Hobbit",
  "author": "J.R.R. Tolkien",
  "year": 1937
}
```

**Field Validation:**
- `title` - Required, string
- `author` - Required, string
- `year` - Required, integer (positive)

**Response:** `201 Created`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "title": "The Hobbit",
  "author": "J.R.R. Tolkien",
  "year": 1937,
  "created_at": "2024-01-15T11:00:00Z",
  "updated_at": "2024-01-15T11:00:00Z"
}
```

**Errors:**
| Status | Error | Reason |
|--------|-------|--------|
| 400 | Validation Error | Missing required fields or invalid data types |
| 500 | Server Error | Database error during creation |

**cURL Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/books" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "The Hobbit",
    "author": "J.R.R. Tolkien",
    "year": 1937
  }'
```

**Python Example:**
```python
import requests

url = "http://localhost:8000/api/v1/books"
book_data = {
    "title": "The Hobbit",
    "author": "J.R.R. Tolkien",
    "year": 1937
}

response = requests.post(url, json=book_data)
new_book = response.json()
print(f"Book created with ID: {new_book['id']}")
```

---

### 4. Update Book

**Endpoint:** `PATCH /books/{book_id}`

**Authentication:** None (Public)

**Path Parameters:**
- `book_id` (UUID, required)

**Request Body:**
```json
{
  "title": "The Hobbit: Revised Edition",
  "author": "J.R.R. Tolkien",
  "year": 1937
}
```

**Field Validation:**
- All fields optional but at least one required for update
- Unspecified fields remain unchanged

**Response:** `200 OK`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "title": "The Hobbit: Revised Edition",
  "author": "J.R.R. Tolkien",
  "year": 1937,
  "created_at": "2024-01-15T11:00:00Z",
  "updated_at": "2024-01-15T12:15:00Z"
}
```

**Errors:**
| Status | Error | Reason |
|--------|-------|--------|
| 404 | Not Found | Book doesn't exist |
| 400 | Bad Request | Invalid UUID format or no valid fields to update |

**cURL Example:**
```bash
curl -X PATCH "http://localhost:8000/api/v1/books/550e8400-e29b-41d4-a716-446655440001" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "The Hobbit: Revised Edition"
  }'
```

---

### 5. Delete Book

**Endpoint:** `DELETE /books/{book_id}`

**Authentication:** None (Public)

**Path Parameters:**
- `book_id` (UUID, required)

**Response:** `204 No Content`

No response body returned on success. The resource is deleted.

**Errors:**
| Status | Error | Reason |
|--------|-------|--------|
| 404 | Not Found | Book doesn't exist |
| 400 | Bad Request | Invalid UUID format |

**cURL Example:**
```bash
curl -X DELETE "http://localhost:8000/api/v1/books/550e8400-e29b-41d4-a716-446655440001"
```

**Python Example:**
```python
import requests

book_id = "550e8400-e29b-41d4-a716-446655440001"
url = f"http://localhost:8000/api/v1/books/{book_id}"

response = requests.delete(url)
if response.status_code == 204:
    print("Book deleted successfully")
```

---

## Rate Limiting

**Current Status:** Not implemented

**Future Implementation:**
When rate limiting is added, responses will include:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 99
X-RateLimit-Reset: 1705315800
```

---

## Status Codes

| Code | Name | Usage |
|------|------|-------|
| **200** | OK | Successful GET, successful PATCH |
| **201** | Created | Successful POST (resource created) |
| **204** | No Content | Successful DELETE |
| **400** | Bad Request | Invalid request body or parameters |
| **403** | Forbidden | Business logic violation (e.g., duplicate email) |
| **404** | Not Found | Resource doesn't exist |
| **422** | Unprocessable Entity | Validation error on request body |
| **500** | Server Error | Internal server error |
| **503** | Service Unavailable | Database connection failure |

---

## Request/Response Examples

### Complete Workflow

**1. Create User**
```bash
POST /api/v1/auth/signup
Request:
{
  "username": "jane_smith",
  "email": "jane@example.com",
  "firstname": "Jane",
  "lastname": "Smith",
  "password": "SecurePass123"
}

Response: 201
{
  "uid": "a1b2c3d4-e5f6-47a8-b9c0-d1e2f3a4b5c6",
  "username": "jane_smith",
  "email": "jane@example.com",
  "firstname": "Jane",
  "lastname": "Smith",
  "is_verified": false,
  "created_at": "2024-01-15T15:30:00Z",
  "updated_at": "2024-01-15T15:30:00Z"
}
```

**2. Create Book**
```bash
POST /api/v1/books
Request:
{
  "title": "Python Mastery",
  "author": "Expert Author",
  "year": 2023
}

Response: 201
{
  "id": "x1y2z3a4-b5c6-4def-8901-a2b3c4d5e6f7",
  "title": "Python Mastery",
  "author": "Expert Author",
  "year": 2023,
  "created_at": "2024-01-15T15:35:00Z",
  "updated_at": "2024-01-15T15:35:00Z"
}
```

**3. List Books**
```bash
GET /api/v1/books

Response: 200
[
  {
    "id": "x1y2z3a4-b5c6-4def-8901-a2b3c4d5e6f7",
    "title": "Python Mastery",
    "author": "Expert Author",
    "year": 2023,
    "created_at": "2024-01-15T15:35:00Z",
    "updated_at": "2024-01-15T15:35:00Z"
  }
]
```

---

## Testing API

### Using Swagger UI
Navigate to `http://localhost:8000/docs` for interactive API testing.

### Using Postman
1. Create new collection
2. Add requests with:
   - **Method:** GET/POST/PATCH/DELETE
   - **URL:** `http://localhost:8000/api/v1/...`
   - **Headers:** `Content-Type: application/json`
   - **Body:** JSON request format

### Using Python Requests
```python
import requests

# Get all books
response = requests.get("http://localhost:8000/api/v1/books")
books = response.json()

# Create book
new_book = {
    "title": "New Book",
    "author": "Author Name",
    "year": 2024
}
response = requests.post("http://localhost:8000/api/v1/books", json=new_book)
created = response.json()
```

---

## Changelog

### v1.0
- Initial release
- User registration endpoint
- Book CRUD endpoints
- UUID-based identification
- Automatic timestamps
