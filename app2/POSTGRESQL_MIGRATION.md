# SearchBook - PostgreSQL + BM25 Edition

This is the redesigned SearchBook backend using PostgreSQL with Okapi BM25 full-text search ranking, Jaccard similarity graphs, and Closeness centrality metrics.

## Architecture Overview

### Components
- **Frontend**: Vite + React SPA (served by Nginx)
- **Backend**: FastAPI REST API
- **Database**: PostgreSQL with full-text search indexing
- **Search Algorithm**: Okapi BM25 for ranking
- **Graph Analysis**: Jaccard similarity + Closeness centrality (pre-computed during ingestion)

### Two-Phase Ingestion Pipeline

#### Phase 1: Book Loading
- Load all `.txt` files from corpus directory
- Filter by minimum word count (default: 10,000 words)
- Store in PostgreSQL `books` table with normalized metadata
- Parameters: `--start`, `--limit`, `--min-words`

#### Phase 2: Graph Computation
- Build Jaccard similarity graph between all book pairs
- Compute Closeness centrality for each book in the graph
- Store top-K similar books for fast suggestions retrieval
- Parameters: `--jaccard-threshold`, `--top-k-similar`

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 20+
- Docker Desktop with Compose v2

### Quick Start

#### 1. Initialize Database
```bash
cd app2
docker compose up postgres -d
```

#### 2. Prepare Sample Dataset
```bash
mkdir -p datasets/sample_books
# Place your .txt files (>10k words each) in datasets/sample_books/
```

#### 3. Run Ingestion
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Phase 1: Load books from corpus
python ../ingestion/load_books.py --corpus-path ../datasets/sample_books --phase 1 --limit 100

# Phase 2: Compute Jaccard & Closeness
python ../ingestion/load_books.py --corpus-path ../datasets/sample_books --phase 2

# Or both phases at once:
python ../ingestion/load_books.py --corpus-path ../datasets/sample_books --phase all --limit 100
```

#### 4. Start Full Stack
```bash
docker compose up --build
```

- Frontend: http://localhost:8080
- Backend API: http://localhost:8000/api
- API Docs: http://localhost:8000/docs
- PostgreSQL: localhost:5432

## Database Schema

### Tables

**books** - Core book documents
```sql
id (SERIAL PRIMARY KEY)
title (VARCHAR)
author (VARCHAR)
text (TEXT)
word_count (INT)
created_at (TIMESTAMP)
```

**jaccard_edges** - Pairwise Jaccard similarities
```sql
id (SERIAL PRIMARY KEY)
book_id_1, book_id_2 (INT, FOREIGN KEY)
jaccard_similarity (FLOAT, 0-1)
UNIQUE(book_id_1, book_id_2) with book_id_1 < book_id_2
```

**centrality_scores** - Pre-computed Closeness centrality
```sql
id (SERIAL PRIMARY KEY)
book_id (INT, UNIQUE FOREIGN KEY)
closeness_score (FLOAT)
betweenness_score (FLOAT, nullable)
pagerank_score (FLOAT, nullable)
updated_at (TIMESTAMP)
```

**similar_books** - Top-K neighbors for each book
```sql
id (SERIAL PRIMARY KEY)
book_id, similar_book_id (INT, FOREIGN KEY)
similarity_score (FLOAT)
rank (INT, 1 to K)
UNIQUE(book_id, similar_book_id)
```

## Ingestion Script Reference

### Usage Examples

**Load all books with default settings:**
```bash
python load_books.py --corpus-path ../datasets/books --phase all
```

**Load with custom filtering (books ≥20k words):**
```bash
python load_books.py --corpus-path ../datasets/books --phase 1 --min-words 20000
```

**Resume from a specific index (useful if interrupted):**
```bash
python load_books.py --corpus-path ../datasets/books --phase 1 --start 500 --limit 100
```

**Compute similarity with custom thresholds:**
```bash
python load_books.py --corpus-path ../datasets/books --phase 2 --jaccard-threshold 0.2 --top-k-similar 20
```

### Parameters

| Argument | Default | Description |
|----------|---------|-------------|
| `--corpus-path` | (required) | Directory containing `.txt` files |
| `--phase` | `all` | `1` = load, `2` = compute, `all` = both |
| `--start` | `0` | Start index for Phase 1 |
| `--limit` | `None` | Max books to load in Phase 1 |
| `--min-words` | `10000` | Minimum word count per book |
| `--jaccard-threshold` | `0.1` | Only store edges above this similarity |
| `--top-k-similar` | `10` | Number of neighbors per book |

## API Endpoints

### Search
- **GET** `/api/search?query={text}&size=10`
  - Returns top results ranked by BM25
  - Response: `SearchResponse` with total count and ranked results

### Advanced Search (Regex)
- **GET** `/api/search/advanced?regex={pattern}&size=10`
  - Returns books matching regex pattern
  - Response: `AdvancedSearchResponse` with regex and results

### Book Details
- **GET** `/api/books/{book_id}`
  - Returns full book document
  - Response: `BookResponse`

### Suggestions
- **GET** `/api/suggestions?book_id={id}&limit=5`
  - Returns similar books from Jaccard graph
  - Response: `SuggestionsResponse` with ranked suggestions

## Search Algorithm Details

### BM25 Okapi
- **Library**: `rank-bm25` (Python implementation)
- **Tokenization**: Regex-based word splitting (case-insensitive)
- **Ranking**: Relevance-based scoring during query execution
- **Performance**: O(N) per query where N = total books

### Jaccard Similarity
- **Computation**: Set intersection / union of tokenized words
- **Storage**: Only edges ≥ threshold are stored (configurable)
- **Graph**: NetworkX-based representation

### Closeness Centrality
- **Definition**: 1 / (average distance to all other nodes)
- **Range**: 0 (isolated) to 1 (central in graph)
- **Usage**: Can be incorporated into final ranking if desired

## Configuration

Environment variables (set in `.env` or docker-compose):

```bash
SEARCHBOOK_DB_HOST=postgres
SEARCHBOOK_DB_PORT=5432
SEARCHBOOK_DB_NAME=searchbook
SEARCHBOOK_DB_USER=searchbook
SEARCHBOOK_DB_PASSWORD=searchbook_password
SEARCHBOOK_MIN_WORD_COUNT=10000
SEARCHBOOK_BM25_RESULTS_LIMIT=50
SEARCHBOOK_SUGGESTIONS_LIMIT=5
```

## Troubleshooting

### "psycopg2" import error
```bash
# Install from requirements
pip install -r requirements.txt
```

### Database connection refused
```bash
# Ensure PostgreSQL is running
docker compose ps
docker compose up postgres -d
```

### No books after ingestion
```bash
# Check word count filtering
python load_books.py --corpus-path ../datasets/books --phase 1 --min-words 5000
```

### Graph computation taking too long
- Start with smaller dataset (`--limit 100`)
- Increase `--jaccard-threshold` to skip low-similarity pairs

## Next Steps / TODOs

- [ ] Implement PageRank centrality scoring
- [ ] Cache BM25 results for frequent queries
- [ ] Add Betweenness centrality computation
- [ ] Optimize regex search with indexed patterns
- [ ] Add user search history tracking
- [ ] Implement interactive ranking tuning UI

---

**Branch**: `users/LBI`  
**Project**: DAAR Project 3 (Sorbonne Université)
