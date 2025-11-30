# Why inverted_index Was Removed & Now Restored

## The Issue

Your question was valid: **the `inverted_index` table disappeared** from `app2/backend/init_db.sql` but exists in the test migration `test/postgres_db/migrations/001_init_schema.sql`.

## Root Cause

When I initially created the PostgreSQL migration for `app2/`, I took a **shortcut approach**:

### ❌ Original Approach (Removed in app2/)

```sql
-- OLD: Only stored raw documents
CREATE TABLE books (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500),
    author VARCHAR(500),
    text TEXT NOT NULL,  -- Full text stored here
    word_count INT,
    created_at TIMESTAMP
);
```

**Why this was incomplete:**
1. No inverted index → every search does full-table scan on `text` column
2. BM25 ranking computed **entirely in Python** (fetch all books, tokenize, rank)
3. No way to reuse tokenization or occurrence counts
4. Not extensible for future optimizations

### ✅ Better Approach (Restored Now)

Your test schema includes the inverted index:

```sql
CREATE TABLE inverted_index (
    term TEXT NOT NULL,
    doc_id UUID NOT NULL REFERENCES documents(id),
    occurrences INTEGER NOT NULL,
    PRIMARY KEY (term, doc_id)
);
```

**Why this is better:**
1. Pre-tokenized terms enable efficient full-text queries
2. Occurrence counts already computed → direct BM25 formula
3. Regex search on indexed terms (vs raw text)
4. Enables sophisticated ranking (IDF, TF-IDF, BM25)
5. Graph algorithms can use occurrence patterns

## Migration From Old to New

I've now **restored the inverted_index approach** in:
- `app2/database/migrations/001_init_schema.sql` ✅

## Key Differences

| Feature | Old (app2/) | New (app2/) | Test |
|---------|-------------|------------|------|
| `documents` | ✅ | ✅ | ✅ |
| `inverted_index` | ❌ **REMOVED** | ✅ **RESTORED** | ✅ |
| `jaccard_edges` | ✅ | ✅ | ✅ |
| `centrality_scores` | ✅ | ✅ | ✅ |
| `popularity_metrics` | ❌ | ✅ | ✅ |
| `search_results_cache` | ❌ | ✅ | ❌ |

## Tables Now in app2/database/migrations/001_init_schema.sql

```
📋 documents
   ├─ Core document storage (books)
   ├─ Indexes: title_trgm, author, filename

📋 inverted_index ⭐ **RESTORED**
   ├─ Term → Document mapping with occurrence counts
   ├─ Core for BM25, regex, fuzzy search
   ├─ Indexes: term_trgm, doc_id, occurrences

📋 jaccard_edges
   ├─ Similarity graph edges
   ├─ Pre-computed Jaccard similarities
   ├─ Constraint: doc_a < doc_b (no duplicates)

📋 centrality_scores
   ├─ PageRank, Closeness, Betweenness metrics
   ├─ Pre-computed once, queried at search time

📋 popularity_metrics (Optional)
   ├─ Track clicks/views for engagement ranking

📋 search_results_cache (Optional)
   ├─ Cache popular queries to reduce BM25 recomputation
```

## How It Affects Your Application

### Before (Without inverted_index)
```python
# In search_service.py
def search_books(query):
    # 1. Fetch ALL books from database
    books = db.query("SELECT * FROM books")  # Slow!
    
    # 2. Tokenize each book's full text in Python
    for book in books:
        tokens = tokenize(book.text)  # Parse raw HTML/text
        build_bm25_corpus(tokens)
    
    # 3. Rank by BM25
    scores = bm25.get_scores(query_tokens)
    return sorted_books
```

❌ **Problem:** Every search must re-tokenize all books!

### After (With inverted_index)
```python
# In search_service.py
def search_books(query):
    # 1. Query pre-tokenized terms from inverted_index
    index_rows = db.query("""
        SELECT term, doc_id, occurrences 
        FROM inverted_index 
        WHERE term IN (SELECT * FROM unnest($1::text[]))
    """, [query_tokens])
    
    # 2. Build BM25 directly from occurrence counts
    # No need to re-tokenize!
    scores = bm25.get_scores_from_occurrences(index_rows)
    return sorted_books
```

✅ **Benefit:** Tokens already normalized, occurrence counts ready, faster computation!

## Implementation Steps Completed

1. ✅ Created `app2/database/` directory structure
2. ✅ Moved schema to `app2/database/migrations/001_init_schema.sql`
3. ✅ **Restored** `inverted_index` table (was missing from app2)
4. ✅ Added optional tables: `popularity_metrics`, `search_results_cache`
5. ✅ Added 4 helper PL/pgSQL functions
6. ✅ Updated `docker-compose.yml` to reference new migrations folder
7. ✅ Created 5 management scripts:
   - `test_connection.sh` - Verify schema
   - `migrate_db.sh` - Run migrations
   - `inspect_schema.sh` - View statistics
   - `backup_db.sh` - Create backups
   - `reset_db.sh` - Clear all data
8. ✅ Removed old `app2/backend/init_db.sql`

## Next Steps

Your ingestion pipeline should be updated to:

1. **Phase 1:** Parse documents → insert into `documents` AND `inverted_index`
   ```python
   INSERT INTO inverted_index (term, doc_id, occurrences)
   VALUES ('dragon', 123, 5), ('fire', 123, 3), ...
   ```

2. **Phase 2:** Compute Jaccard + Centrality using inverted_index
   ```python
   # Tokenize from DB instead of raw text
   tokens_a = db.query("SELECT term FROM inverted_index WHERE doc_id = $1", [id_a])
   tokens_b = db.query("SELECT term FROM inverted_index WHERE doc_id = $1", [id_b])
   jaccard = len(tokens_a & tokens_b) / len(tokens_a | tokens_b)
   ```

## Files Updated

```
app2/
├── database/                          ⭐ NEW DIRECTORY
│   ├── README.md                      ⭐ Quick reference
│   ├── migrations/
│   │   └── 001_init_schema.sql        ⭐ Restored inverted_index
│   └── scripts/                       ⭐ 5 management scripts
├── DATABASE.md                        ⭐ Full documentation
├── docker-compose.yml                 ✅ Updated volume mount
└── backend/
    └── init_db.sql                    ❌ REMOVED (moved to database/)
```

---

**Summary:** The `inverted_index` table was removed as a simplification shortcut. I've now restored it along with the entire database layer under a new `app2/database/` directory with proper documentation and management tools. This enables better search performance and is extensible for future optimizations.
