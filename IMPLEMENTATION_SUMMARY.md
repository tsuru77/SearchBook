# SearchBook PostgreSQL Migration - Implementation Summary

## ✅ Project Complete

Successfully migrated SearchBook from **Elasticsearch** → **PostgreSQL** with **Okapi BM25** ranking and **Jaccard similarity graphs**.

---

## What Was Done

### 1. **Database Layer**
- ✅ Created PostgreSQL schema (`init_db.sql`) with 4 optimized tables:
  - `books` - Core document corpus
  - `jaccard_edges` - Pairwise similarity graph
  - `centrality_scores` - Closeness centrality metrics
  - `similar_books` - Top-K neighbors for fast suggestions
- ✅ Added indexed full-text search support
- ✅ Created `app/core/database.py` with connection pooling utilities

### 2. **Ingestion Pipeline (Two-Phase)**
- ✅ **Phase 1**: Load books from text files, filter by minimum word count (default 10,000)
  - Parameters: `--start`, `--limit`, `--min-words`
  - Resume support for interrupted loads
- ✅ **Phase 2**: Compute Jaccard similarity + Closeness centrality
  - Graph-based using NetworkX
  - Configurable threshold and top-K storage
  - Parameters: `--jaccard-threshold`, `--top-k-similar`

### 3. **Backend Services**
- ✅ `search_service.py` - Okapi BM25 ranking (using `rank-bm25` library)
  - Tokenization: Regex-based word extraction
  - Live ranking during query (no pre-indexing needed)
- ✅ `books_service.py` - Direct PostgreSQL queries
- ✅ `suggestions_service.py` - Jaccard-based neighbor recommendations
- ✅ Removed all Elasticsearch references

### 4. **Configuration**
- ✅ Updated `config.py` with PostgreSQL connection parameters
- ✅ Created `.env.example` with all required settings
- ✅ Environment-based configuration (Docker-friendly)

### 5. **Docker Compose**
- ✅ Replaced Elasticsearch with PostgreSQL 16 Alpine
- ✅ Added health checks for reliable service startup
- ✅ Auto-initialize database with `init_db.sql`
- ✅ Updated environment variable passing

### 6. **Dependencies**
- ✅ Replaced `elasticsearch` with `psycopg2-binary` and `rank-bm25`
- ✅ Kept `networkx` for graph algorithms
- ✅ Added `numpy` (BM25 dependency)

### 7. **Documentation**
- ✅ `POSTGRESQL_MIGRATION.md` - Complete architecture & API reference
- ✅ `QUICKSTART.md` - Quick start guide with examples
- ✅ `.env.example` - Configuration template

---

## File Structure (app2/)

```
app2/
├── backend/
│   ├── app/
│   │   ├── api/routes/
│   │   │   ├── books.py         ✓ Updated (PostgreSQL)
│   │   │   ├── search.py        ✓ Updated (BM25 + regex)
│   │   │   └── suggestions.py   ✓ Updated (Jaccard-based)
│   │   ├── core/
│   │   │   ├── config.py        ✓ PostgreSQL settings
│   │   │   └── database.py      ✓ New: DB utilities
│   │   ├── schemas/             ✓ Unchanged (compatible)
│   │   ├── services/
│   │   │   ├── search_service.py    ✓ BM25 implementation
│   │   │   ├── books_service.py     ✓ PostgreSQL queries
│   │   │   ├── suggestions_service.py ✓ Jaccard-based
│   │   │   └── elasticsearch.py     ✗ Removed
│   │   └── main.py              ✓ Unchanged
│   ├── init_db.sql              ✓ New: PostgreSQL schema
│   ├── requirements.txt          ✓ Updated
│   └── .env.example             ✓ New: Config template
├── frontend/                    ✓ Unchanged (works with new API)
├── ingestion/
│   └── load_books.py            ✓ Completely rewritten (2-phase)
├── docker-compose.yml           ✓ PostgreSQL instead of ES
├── POSTGRESQL_MIGRATION.md      ✓ New: Architecture docs
├── QUICKSTART.md                ✓ New: Quick start guide
└── [Dockerfile, nginx.conf, etc.] ✓ Unchanged
```

---

## Quick Start

### Using Docker
```bash
cd app2
docker compose up --build
```
- Frontend: http://localhost:8080
- API: http://localhost:8000/api
- Docs: http://localhost:8000/docs

### Manual Ingestion
```bash
cd app2/backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Load books from corpus (10,000+ words each)
python ../ingestion/load_books.py --corpus-path ../datasets/sample_books --phase all
```

---

## Key Features

### Search
- **BM25 Ranking**: Okapi BM25 algorithm (library: `rank-bm25`)
- **Regex Support**: Pattern matching on full text
- **Snippet Preview**: 280-character excerpts

### Suggestions
- **Jaccard Similarity**: Word-set overlap between books
- **Configurable**: Top-K neighbors per book (default 10)
- **Threshold-based**: Skip low-similarity pairs (default 0.1)

### Centrality Metrics
- **Closeness**: 1/(avg distance) in similarity graph
- **Pre-computed**: Calculated during Phase 2 ingestion
- **Extensible**: Ready for PageRank/Betweenness

---

## Configuration Parameters

### Ingestion Phase 1
```bash
--corpus-path   Directory with .txt files (required)
--start         Resume from index N (default: 0)
--limit         Max books to load (default: all)
--min-words     Minimum word count per book (default: 10000)
```

### Ingestion Phase 2
```bash
--jaccard-threshold   Store edges ≥ this similarity (default: 0.1)
--top-k-similar       Neighbors to store per book (default: 10)
```

### Example
```bash
# Load 500 books, compute strict Jaccard with top 5 neighbors
python load_books.py \
  --corpus-path ../datasets/books \
  --phase all \
  --limit 500 \
  --min-words 15000 \
  --jaccard-threshold 0.25 \
  --top-k-similar 5
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/search?query={text}&size=10` | BM25 search |
| GET | `/api/search/advanced?regex={pat}&size=10` | Regex search |
| GET | `/api/books/{id}` | Book details |
| GET | `/api/suggestions?book_id={id}&limit=5` | Similar books |

**Example Responses:**
```json
{
  "total": 5,
  "results": [
    {
      "id": "1",
      "title": "The Great Gatsby",
      "author": "Unknown",
      "score": 45.2,
      "snippet": "In my younger and more vulnerable years..."
    }
  ]
}
```

---

## Database Schema Highlights

### books
```sql
id (SERIAL PRIMARY KEY)
title, author (VARCHAR)
text (TEXT)
word_count (INT)
created_at (TIMESTAMP)
-- Indexed: title, text (GIN)
```

### jaccard_edges
```sql
book_id_1, book_id_2 (FOREIGN KEY books)
jaccard_similarity (FLOAT 0-1)
-- UNIQUE constraint ensures single edge per pair
```

### centrality_scores
```sql
book_id (UNIQUE FOREIGN KEY)
closeness_score (FLOAT)
betweenness_score, pagerank_score (FLOAT, nullable)
-- Ready for future expansion
```

### similar_books (pre-computed)
```sql
book_id, similar_book_id
similarity_score (FLOAT)
rank (INT 1 to K)
-- Fast suggestions via index on book_id
```

---

## Performance Characteristics

| Operation | Complexity | Notes |
|-----------|-----------|-------|
| Search (BM25) | O(N × T) | N = books, T = tokens in query |
| Regex Search | O(N × M) | N = books, M = text size |
| Suggestions | O(1) | Pre-computed at ingest time |
| Closeness Centrality | O(V² + E) | V = books, E = edges |

**Optimization Opportunities:**
- Cache frequent BM25 searches
- Add TF-IDF pre-computation for faster ranking
- Implement incremental graph updates
- Use PostgreSQL FTS for regex acceleration

---

## Troubleshooting

### Database won't connect
```bash
# Check PostgreSQL logs
docker compose logs postgres

# Verify health
docker compose ps postgres
```

### Books not loading
```bash
# Check word count filtering
python load_books.py --corpus-path ../datasets/books --phase 1 --min-words 5000

# Verify corpus files exist
ls -lh ../datasets/sample_books/*.txt
```

### Search returns empty results
- Ensure Phase 1 & 2 completed successfully
- Check `docker compose logs backend`
- Verify database connection in API logs

---

## Files Changed/Created

### Created
- `app2/backend/app/core/database.py` - DB utilities
- `app2/backend/init_db.sql` - PostgreSQL schema
- `app2/backend/.env.example` - Config template
- `app2/POSTGRESQL_MIGRATION.md` - Architecture docs
- `app2/QUICKSTART.md` - Quick start guide

### Modified
- `app2/backend/requirements.txt` - Dependencies
- `app2/backend/app/core/config.py` - PostgreSQL settings
- `app2/backend/app/services/search_service.py` - BM25 ranking
- `app2/backend/app/services/books_service.py` - PostgreSQL queries
- `app2/backend/app/services/suggestions_service.py` - Jaccard suggestions
- `app2/backend/app/api/routes/search.py` - Updated descriptions
- `app2/backend/app/api/routes/books.py` - Updated descriptions
- `app2/docker-compose.yml` - PostgreSQL instead of ES

### Deleted
- `app2/backend/app/services/elasticsearch.py` - No longer needed

---

## Next Steps (Optional Enhancements)

- [ ] Implement PageRank centrality scoring
- [ ] Add Betweenness centrality computation
- [ ] Cache BM25 results for frequent queries
- [ ] Optimize regex search with indexed patterns
- [ ] Add user search history tracking
- [ ] Implement TF-IDF pre-computation for faster BM25
- [ ] Create admin endpoint for re-ingestion
- [ ] Add query logging & analytics
- [ ] Implement result re-ranking based on centrality scores

---

## Testing Checklist

- [x] PostgreSQL schema initializes correctly
- [x] Phase 1 ingestion filters by word count
- [x] Phase 2 builds Jaccard graph correctly
- [x] BM25 search returns ranked results
- [x] Regex search matches patterns
- [x] Suggestions return similar books
- [x] API endpoints return correct schemas
- [x] Docker compose orchestration works
- [x] Database health checks pass

---

## References

- **Okapi BM25**: https://en.wikipedia.org/wiki/Okapi_BM25
- **Jaccard Similarity**: https://en.wikipedia.org/wiki/Jaccard_index
- **Closeness Centrality**: https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.centrality.closeness_centrality.html
- **rank-bm25**: https://github.com/dorianbrown/rank_bm25
- **NetworkX**: https://networkx.org/

---

**Status**: ✅ Complete  
**Branch**: `users/LBI`  
**Project**: DAAR Project 3 (Sorbonne Université)  
**Date**: November 29, 2025
