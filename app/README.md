# SearchBook - app2 (PostgreSQL Version)

PostgreSQL-based search application with BM25 ranking and Jaccard similarity graph.

## Quick Start

### 1. Setup Environment
```bash
bash setup.sh          # Interactive setup (recommended)
# OR
cp .env.example .env   # Manual setup
```

### 2. Start Application
```bash
docker compose up --build
```

### 3. Access
- Frontend: http://localhost:8080
- API: http://localhost:8000/docs

## Architecture

```
app2/
├── backend/           # FastAPI application
├── frontend/          # React + TypeScript UI
├── ingestion/         # Data loading pipeline
├── database/          # PostgreSQL schema
├── docker-compose.yml # Service orchestration
└── .env               # Configuration
```

## Database

PostgreSQL 16 with:
- **inverted_index** - Term-based full-text search (BM25)
- **jaccard_edges** - Document similarity graph
- **centrality_scores** - PageRank/Closeness metrics

Auto-initialized from `database/migrations/001_init_schema.sql`

## Key Features

✅ **BM25 Ranking** - Relevance-based search  
✅ **Jaccard Similarity** - Find similar documents  
✅ **Graph Analysis** - Centrality metrics (PageRank, Closeness)  
✅ **Regex Search** - Pattern matching support  
✅ **Secure Configuration** - Environment-based secrets  

## Documentation

- `QUICKSTART.md` - Setup and ingestion guide
- `DATABASE.md` - Schema and architecture
- `SECURITY.md` - Security considerations
- `database/README.md` - Database quick reference
- `database/MIGRATION_NOTES.md` - Why inverted_index was restored

## Environment Variables

Required (set via `.env`):
```bash
POSTGRES_USER=searchbook
POSTGRES_PASSWORD=your_password
POSTGRES_DB=searchbook
SEARCHBOOK_DB_HOST=postgres
SEARCHBOOK_DB_PORT=5432
VITE_API_BASE_URL=http://localhost:8000/api
```

## Data Ingestion

Two-phase pipeline in `ingestion/load_books.py`:

**Phase 1:** Load documents, tokenize, populate inverted_index
```bash
python ingestion/load_books.py --corpus-path /path/to/books --phase 1
```

**Phase 2:** Compute Jaccard graph & centrality scores
```bash
python ingestion/load_books.py --corpus-path /path/to/books --phase 2
```

## API Endpoints

- `GET /api/search?query=...` - BM25 search
- `GET /api/books/{id}` - Get document
- `GET /api/suggestions?book_id=...` - Similar documents

Full docs at: http://localhost:8000/docs

## Technology Stack

- **Backend:** FastAPI (Python)
- **Frontend:** React + TypeScript + Vite
- **Database:** PostgreSQL 16
- **Search:** BM25 + Inverted Index
- **Graphs:** NetworkX (Jaccard, Centrality)
- **Orchestration:** Docker Compose

## Notes

- Uses `.env` for sensitive configuration (not committed to git)
- Database migrations auto-run on container startup
- All credentials externalized (no hardcoded secrets)
- Ready for development and testing

---

**For detailed information, see:**
- Setup guide: `QUICKSTART.md`
- Database design: `DATABASE.md`
- Security notes: `SECURITY.md`
