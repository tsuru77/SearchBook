# Quick Start - PostgreSQL Edition (app2)

This directory contains the refactored SearchBook backend using **PostgreSQL**, **Okapi BM25**, and **Jaccard similarity** graphs instead of Elasticsearch.

## Key Differences from Original (`app/`)

| Component | Original (`app/`) | PostgreSQL (`app2/`) |
|-----------|-------------------|----------------------|
| Database | Elasticsearch 9.2 | PostgreSQL 16 |
| Search Ranking | Elasticsearch BM25 | Okapi BM25 (Python lib) |
| Graph Storage | In-memory | PostgreSQL tables |
| Ingestion | Single-phase | **Two-phase** (load → compute) |

## Setup (Docker)

### Option 1: Interactive Setup (Recommended)
```bash
cd app2

# Run setup script to create .env interactively
bash setup.sh

# Start services (PostgreSQL + Backend + Frontend)
docker compose up --build
```

### Option 2: Manual Setup
```bash
cd app2

# Copy and customize environment file
cp .env.example .env
# Edit .env with your desired values
nano .env

# Start services
docker compose up --build
```

**Services:**
- Frontend: http://localhost:8080
- Backend API: http://localhost:8000/api
- API Documentation: http://localhost:8000/docs
- PostgreSQL: localhost:5432

### Security Notes
- ✅ `.env` file is in `.gitignore` and will NOT be committed
- ✅ Credentials are loaded from environment variables
- ✅ No hardcoded secrets in docker-compose.yml
- 🔒 In production, use strong passwords and external secret management

## Manual Ingestion

```bash
cd app2/backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# PHASE 1: Load books from corpus
python ../ingestion/load_books.py \
  --corpus-path ../datasets/sample_books \
  --phase 1 \
  --limit 50 \
  --min-words 10000

# PHASE 2: Compute Jaccard & Closeness scores
python ../ingestion/load_books.py \
  --corpus-path ../datasets/sample_books \
  --phase 2 \
  --jaccard-threshold 0.1 \
  --top-k-similar 10

# OR do both phases at once:
python ../ingestion/load_books.py \
  --corpus-path ../datasets/sample_books \
  --phase all \
  --limit 50
```

## Ingestion Parameters Reference

**Phase 1 (Book Loading):**
- `--corpus-path`: Directory with `.txt` files (**required**)
- `--phase`: `1`, `2`, or `all` (default: `all`)
- `--start`: Resume from index N (for interrupted loads)
- `--limit`: Max books to load
- `--min-words`: Minimum word count per book (default: 10000)

**Phase 2 (Graph Computation):**
- `--jaccard-threshold`: Store edges ≥ this similarity (default: 0.1, range 0-1)
- `--top-k-similar`: Store top-K neighbors per book (default: 10)

**Examples:**

```bash
# Load all books with defaults
python ../ingestion/load_books.py --corpus-path ../datasets/books --phase all

# Load only 100 books, then compute
python ../ingestion/load_books.py --corpus-path ../datasets/books --phase 1 --limit 100
python ../ingestion/load_books.py --corpus-path ../datasets/books --phase 2

# Load high-quality corpus (>20k words), strict similarity threshold
python ../ingestion/load_books.py \
  --corpus-path ../datasets/books \
  --phase all \
  --min-words 20000 \
  --jaccard-threshold 0.25
```

## Database Structure

Three main tables:

1. **books** - Document corpus
2. **jaccard_edges** - Pairwise similarities (book_id_1, book_id_2, similarity)
3. **centrality_scores** - Closeness centrality per book
4. **similar_books** - Top-K neighbors (for fast suggestions)

Schema initialized automatically via `init_db.sql`.

## API Usage

```bash
# Full-text search (BM25 ranked)
curl "http://localhost:8000/api/search?query=dragon&size=10"

# Regex search
curl "http://localhost:8000/api/search/advanced?regex=.*sword.*&size=10"

# Get book details
curl "http://localhost:8000/api/books/1"

# Get similar books (from Jaccard graph)
curl "http://localhost:8000/api/suggestions?book_id=1&limit=5"
```

## File Structure

```
app2/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes/          # API endpoints
│   │   ├── core/
│   │   │   ├── config.py        # Settings (PostgreSQL URLs)
│   │   │   └── database.py      # DB connection utilities
│   │   ├── schemas/             # Pydantic models
│   │   ├── services/
│   │   │   ├── search_service.py   # BM25 ranking logic
│   │   │   ├── books_service.py
│   │   │   └── suggestions_service.py
│   │   └── main.py              # FastAPI app
│   ├── init_db.sql              # PostgreSQL schema (auto-initialized)
│   ├── requirements.txt          # Dependencies (psycopg2, rank-bm25, networkx)
│   └── .env.example
├── frontend/                    # Unchanged (Vite + React)
├── ingestion/
│   └── load_books.py            # Two-phase ingestion script
├── docker-compose.yml           # PostgreSQL + Backend + Frontend
├── POSTGRESQL_MIGRATION.md      # Detailed architecture docs
└── QUICKSTART.md                # This file
```

## Troubleshooting

**PostgreSQL connection error:**
```bash
# Ensure database is running
docker compose ps
docker compose logs postgres

# Try reconnecting after waiting a few seconds
docker compose up postgres
```

**No books found after ingestion:**
```bash
# Check word count filtering
python ../ingestion/load_books.py --corpus-path ../datasets/books --phase 1 --min-words 5000
```

**BM25 giving unexpected results:**
- Results are based on **term frequency** in each book
- No traditional TF-IDF weighting (uses BM25 algorithm instead)
- Increase `--limit` for more training data

## Next Steps

1. **Place your corpus**: Add `.txt` files to `datasets/sample_books/`
2. **Run ingestion**: `python ../ingestion/load_books.py --corpus-path ../datasets/sample_books --phase all`
3. **Test API**: Visit http://localhost:8000/docs
4. **Use frontend**: http://localhost:8080

---

For full documentation, see `POSTGRESQL_MIGRATION.md`.
