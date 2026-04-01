# Database Documentation

**Last Updated:** January 2024  
**Database:** PostgreSQL 12+  
**ORM:** SQLAlchemy 2.0 with SQLModel  
**Migrations:** Alembic

---

## Table of Contents

1. [Database Setup](#database-setup)
2. [Schema Overview](#schema-overview)
3. [Tables](#tables)
4. [Relationships](#relationships)
5. [Indexes](#indexes)
6. [Migrations](#migrations)
7. [Backup & Recovery](#backup--recovery)
8. [Performance Tuning](#performance-tuning)
9. [SQL Queries](#sql-queries)

---

## Database Setup

### Prerequisites

1. **PostgreSQL Installation**
   ```bash
   # macOS
   brew install postgresql
   
   # Ubuntu/Debian
   sudo apt-get install postgresql postgresql-contrib
   
   # Windows
   # Download from https://www.postgresql.org/download/windows/
   ```

2. **Create Database**
   ```bash
   psql -U postgres
   CREATE DATABASE mimir;
   \q
   ```

3. **Environment Configuration**
   ```bash
   # .env file
   DATABASE_URL = postgresql+asyncpg://postgres:password@localhost:5432/mimir
   ```

### Connection String Format

```
postgresql+asyncpg://username:password@host:port/database_name
                    ^^^^^^^^ ^^^^^^^^  ^^^^ ^^^^
                    user     pass      host port
```

**Example Variations:**
```
# Local development
postgresql+asyncpg://postgres:password@localhost:5432/mimir

# Remote server
postgresql+asyncpg://user:pass@db.example.com:5432/mimir

# Docker container
postgresql+asyncpg://postgres:password@db:5432/mimir
```

---

## Schema Overview

### Entity Relationship Diagram

```
┌─────────────────────────────────────┐
│ USERS                               │
├─────────────────────────────────────┤
│ UID (UUID) [PK]                     │
│ USERNAME (VARCHAR)                  │
│ EMAIL (VARCHAR) [UNIQUE]            │
│ FIRSTNAME (VARCHAR)                 │
│ LASTNAME (VARCHAR)                  │
│ PASSWORD_HASH (VARCHAR)             │
│ IS_VERIFIED (BOOLEAN)               │
│ CREATED_AT (TIMESTAMP)              │
│ UPDATED_AT (TIMESTAMP)              │
└─────────────────────────────────────┘
            (Standalone)

┌─────────────────────────────────────┐
│ BOOKS                               │
├─────────────────────────────────────┤
│ ID (UUID) [PK]                      │
│ TITLE (VARCHAR)                     │
│ AUTHOR (VARCHAR)                    │
│ YEAR (INTEGER)                      │
│ CREATED_AT (TIMESTAMP)              │
│ UPDATED_AT (TIMESTAMP)              │
└─────────────────────────────────────┘
            (Standalone)
```

**Current Status:** Two independent entities with no foreign key relationships.

**Future Relationships:**
```
USERS → BOOK_REVIEWS ← BOOKS
        (Many-to-Many junction table)
```

---

## Tables

### 1. USERS Table

**Purpose:** Store user account information

**Table Definition:**
```sql
CREATE TABLE users (
    uid UUID NOT NULL PRIMARY KEY,
    username VARCHAR NOT NULL,
    email VARCHAR NOT NULL UNIQUE,
    firstname VARCHAR NOT NULL,
    lastname VARCHAR NOT NULL,
    password_hash VARCHAR NOT NULL,
    is_verified BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

**Column Details:**

| Column | Type | Constraints | Default | Purpose |
|--------|------|-----------|---------|---------|
| `uid` | UUID | PK, NOT NULL | Generated | Unique user identifier |
| `username` | VARCHAR | NOT NULL | - | Login username |
| `email` | VARCHAR | UNIQUE, NOT NULL | - | Contact email |
| `firstname` | VARCHAR | NOT NULL | - | User first name |
| `lastname` | VARCHAR | NOT NULL | - | User last name |
| `password_hash` | VARCHAR | NOT NULL | - | Bcrypt hashed password |
| `is_verified` | BOOLEAN | NOT NULL | FALSE | Email verification flag |
| `created_at` | TIMESTAMP TZ | NOT NULL | NOW() | Account creation time |
| `updated_at` | TIMESTAMP TZ | NOT NULL | NOW() | Last update time |

**Sample Data:**
```sql
INSERT INTO users (uid, username, email, firstname, lastname, password_hash, is_verified, created_at, updated_at)
VALUES (
    '550e8400-e29b-41d4-a716-446655440000',
    'john_doe',
    'john@example.com',
    'John',
    'Doe',
    '$2b$12$R9h7cIPz0gi.URNNX3kh', -- Hashed password
    FALSE,
    '2024-01-15 10:30:00+00:00',
    '2024-01-15 10:30:00+00:00'
);
```

**Data Size:**
- Per record: ~500 bytes
- 1 million users: ~500 MB

---

### 2. BOOKS Table

**Purpose:** Store book information and metadata

**Table Definition:**
```sql
CREATE TABLE books (
    id UUID NOT NULL PRIMARY KEY,
    title VARCHAR NOT NULL,
    author VARCHAR NOT NULL,
    year INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

**Column Details:**

| Column | Type | Constraints | Default | Purpose |
|--------|------|-----------|---------|---------|
| `id` | UUID | PK, NOT NULL | Generated | Unique book identifier |
| `title` | VARCHAR | NOT NULL | - | Book title |
| `author` | VARCHAR | NOT NULL | - | Author name |
| `year` | INTEGER | NOT NULL | - | Publication year |
| `created_at` | TIMESTAMP TZ | NOT NULL | NOW() | Record creation time |
| `updated_at` | TIMESTAMP TZ | NOT NULL | NOW() | Last modification time |

**Sample Data:**
```sql
INSERT INTO books (id, title, author, year, created_at, updated_at)
VALUES (
    '123e4567-e89b-12d3-a456-426614174000',
    'The Great Gatsby',
    'F. Scott Fitzgerald',
    1925,
    '2024-01-15 10:30:00+00:00',
    '2024-01-15 10:30:00+00:00'
);
```

**Data Size:**
- Per record: ~300 bytes
- 1 million books: ~300 MB

---

## Relationships

### Current State

**Independent Tables:** Users and Books have no relationships.

### Future: Many-to-Many Relationship

**Scenario:** Users can review books.

**Implementation:**

1. **Create Review Junction Table**
```sql
CREATE TABLE book_reviews (
    id UUID NOT NULL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(uid) ON DELETE CASCADE,
    book_id UUID NOT NULL REFERENCES books(id) ON DELETE CASCADE,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    review_text TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, book_id) -- One review per user per book
);
```

2. **Create Indexes for Foreign Keys**
```sql
CREATE INDEX idx_book_reviews_user_id ON book_reviews(user_id);
CREATE INDEX idx_book_reviews_book_id ON book_reviews(book_id);
```

3. **Migration Command**
```bash
alembic revision --autogenerate -m "Add book_reviews table with relationships"
alembic upgrade head
```

---

## Indexes

### Current Indexes

**USERS Table:**
```sql
-- Primary Key (implicit)
CREATE INDEX idx_users_uid ON users(uid);

-- Unique constraint (implicit)
CREATE UNIQUE INDEX idx_users_email ON users(email);
```

**BOOKS Table:**
```sql
-- Primary Key (implicit)
CREATE INDEX idx_books_id ON books(id);

-- Query optimization (for sorting)
CREATE INDEX idx_books_created_at ON books(created_at DESC);
```

### Query Performance Impact

**Without Index:**
```sql
SELECT * FROM books 
WHERE created_at > '2024-01-01'
ORDER BY created_at DESC;
-- Full table scan: ~100ms for 1M rows
```

**With Index:**
```sql
SELECT * FROM books 
WHERE created_at > '2024-01-01'
ORDER BY created_at DESC;
-- Index scan: ~10ms for 1M rows (10x faster)
```

### Future Indexes

**Full-Text Search (when needed):**
```sql
CREATE INDEX idx_books_title_gin ON books USING GIN(to_tsvector('english', title));
CREATE INDEX idx_books_author_gin ON books USING GIN(to_tsvector('english', author));
```

**Composite Indexes:**
```sql
CREATE INDEX idx_users_email_verified ON users(email, is_verified);
```

### Index Maintenance

**Check Index Usage:**
```sql
SELECT schemaname, tablename, indexname, idx_scan
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;
```

**Rebuild Indexes:**
```sql
REINDEX INDEX idx_books_created_at;
REINDEX TABLE books;
```

---

## Migrations

### Alembic Configuration

**alembic.ini:**
```ini
sqlalchemy.url = driver://user:password@localhost/dbname
script_location = %(here)s/migrations
versions_locations = %(here)s/migrations/versions
```

**migrations/env.py:**
Sets up migration environment to use the Config.DATABASE_URL

### Migration Workflow

#### 1. Create Migration

**Option A: Auto-generate (Recommended)**
```bash
alembic revision --autogenerate -m "Add password_hash column"
```

This compares current models against database and generates migration automatically.

**Option B: Manual migration**
```bash
alembic revision -m "Manual migration description"
```

#### 2. Review Migration File

**Generated File:** `migrations/versions/xxxxx_message.py`

```python
def upgrade() -> None:
    op.add_column(
        'users',
        sa.Column('password_hash', sa.String(), nullable=False)
    )

def downgrade() -> None:
    op.drop_column('users', 'password_hash')
```

#### 3. Apply Migration

**Upgrade to Latest:**
```bash
alembic upgrade head
```

**Upgrade to Specific Version:**
```bash
alembic upgrade ae1027a6acf
```

**Downgrade One Version:**
```bash
alembic downgrade -1
```

**Downgrade to Specific Version:**
```bash
alembic downgrade ae1027a
```

### Migration History

**View All Migrations:**
```bash
alembic history
```

**Output:**
```
<base> -> ae1027a6acf (head), Initial migration
```

**Current Database Version:**
```bash
alembic current
```

### Migration Best Practices

1. **Test Migrations Locally First**
```bash
# Development
alembic upgrade head

# Verify
alembic current
```

2. **Keep Migrations Small**
   - One logical change per migration
   - Easier to debug and rollback

3. **Write Reversible Migrations**
   - Always define both `upgrade()` and `downgrade()`
   - Test rollback: `alembic downgrade -1` then `alembic upgrade head`

4. **Add Data Migration When Needed**
```python
def upgrade() -> None:
    # Structural change
    op.add_column('books', sa.Column('rating', sa.Integer))
    
    # Data migration
    op.execute("UPDATE books SET rating = 0")

def downgrade() -> None:
    op.drop_column('books', 'rating')
```

---

## Backup & Recovery

### Backup Strategies

#### 1. Full Database Backup

**Using pg_dump:**
```bash
# Backup entire database
pg_dump -U postgres -h localhost mimir > backup_2024_01_15.sql

# With compression
pg_dump -U postgres -h localhost -Fc mimir > backup_2024_01_15.dump
```

**Example Output:**
```sql
-- PostgreSQL database dump
-- ...
CREATE TABLE users (...)
CREATE TABLE books (...)
INSERT INTO users VALUES (...)
-- ...
```

#### 2. Incremental Backup (with WAL)

**Enable WAL archiving:**
```bash
# postgresql.conf
wal_level = replica
max_wal_senders = 3
wal_keep_size = 1GB
```

#### 3. Automated Backup Script

**backup.sh:**
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"
DB_NAME="mimir"

pg_dump -U postgres $DB_NAME > $BACKUP_DIR/mimir_$DATE.sql
gzip $BACKUP_DIR/mimir_$DATE.sql

# Keep only last 7 days
find $BACKUP_DIR -name "mimir_*.sql.gz" -mtime +7 -delete
```

**Cron Job (daily backup at 2 AM):**
```bash
0 2 * * * /scripts/backup.sh
```

### Recovery Procedures

#### 1. Full Database Restore

```bash
# From SQL file
psql -U postgres -d mimir < backup_2024_01_15.sql

# From compressed dump
pg_restore -U postgres -d mimir backup_2024_01_15.dump
```

#### 2. Point-in-Time Recovery (PITR)

```bash
# 1. Stop application
# 2. Copy base backup
# 3. Restore WAL files up to specific time

pg_restore -d mimir base_backup.dump

# Then restore WAL files with recovery_target_timeline
```

#### 3. Selective Table Restore

```bash
# Restore specific table
pg_restore -d mimir -t books backup_2024_01_15.dump
```

---

## Performance Tuning

### Query Performance Analysis

**EXPLAIN ANALYZE:**
```sql
EXPLAIN ANALYZE
SELECT * FROM books 
WHERE created_at > '2024-01-01'
ORDER BY created_at DESC LIMIT 10;
```

**Output Interpretation:**
```
Limit (cost=0.42..0.57 rows=10 width=52) (actual time=0.034..0.041 rows=10)
  -> Index Scan Backward using idx_books_created_at...
```

- **cost:** Query planner estimate
- **time:** Actual execution time
- **rows:** Number of rows returned

### Connection Pooling

**Current Configuration:**
```python
engine = create_engine(
    Config.DATABASE_URL,
    echo=True,
    pool_size=5,           # Number of connections to keep
    max_overflow=10,       # Additional connections allowed
    pool_timeout=30,       # Timeout waiting for connection
    pool_pre_ping=True     # Test connections before using
)
```

**Tuning for Production:**
```python
engine = create_engine(
    Config.DATABASE_URL,
    echo=False,
    pool_size=20,          # More connections
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=3600,     # Recycle stale connections
    pool_pre_ping=True
)
```

### Query Optimization Tips

1. **Use Specific Columns**
```python
# ✅ Good
statement = select(Book.id, Book.title, Book.author)

# ❌ Wasteful
statement = select(Book)  # Gets all columns
```

2. **Add Filters Early**
```python
# ✅ Good - Filters in database
select(Book).where(Book.year > 1920)

# ❌ Inefficient - Filter in Python
[book for book in all_books if book.year > 1920]
```

3. **Use Pagination**
```python
# ✅ Good
select(Book).offset(0).limit(20)

# ❌ Slow - Loads entire table
select(Book).all()
```

### Monitoring

**Check Active Queries:**
```sql
SELECT pid, query, state FROM pg_stat_activity;
```

**Check Table Sizes:**
```sql
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE schemaname != 'pg_catalog'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

**Check Index Effectiveness:**
```sql
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;
```

---

## SQL Queries

### Common Queries

**1. Get User by Email**
```sql
SELECT * FROM users WHERE email = 'john@example.com';
```

**2. Get All Books Sorted by Date**
```sql
SELECT * FROM books ORDER BY created_at DESC;
```

**3. Get Books by Author**
```sql
SELECT * FROM books WHERE author = 'George Orwell';
```

**4. Get Recently Updated Books**
```sql
SELECT * FROM books 
WHERE updated_at > NOW() - INTERVAL '7 days'
ORDER BY updated_at DESC;
```

**5. Count Books by Year**
```sql
SELECT year, COUNT(*) as count
FROM books
GROUP BY year
ORDER BY year DESC;
```

### Statistical Queries

**1. User Registration Trend**
```sql
SELECT 
    DATE(created_at) as date,
    COUNT(*) as new_users
FROM users
GROUP BY DATE(created_at)
ORDER BY date DESC;
```

**2. Average Books per Query**
```sql
SELECT COUNT(*) / (SELECT COUNT(DISTINCT 1) FROM books) as avg;
```

---

## Conclusion

The Mimir database is designed for:
- **Simplicity:** Straightforward schema with minimal complexity
- **Growth:** Ready to scale with proper indexing and partitioning
- **Reliability:** Regular backups and migration control
- **Performance:** Optimized queries and connection pooling

As the application grows, monitoring and optimization will become increasingly important.
