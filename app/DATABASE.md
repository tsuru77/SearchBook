# Database Architecture & Management

## Overview

All PostgreSQL database components are now organized under `app2/database/`:

```
database/
├── migrations/           # SQL migration files
│   └── 001_init_schema.sql
├── scripts/              # Utility scripts for DB management
│   ├── test_connection.sh
│   ├── migrate_db.sh
│   ├── reset_db.sh
│   ├── inspect_schema.sh
│   └── backup_db.sh
└── backups/              # Auto-created by backup_db.sh
    └── searchbook_backup_YYYYMMDD_HHMMSS.sql
```

---

## Schema Design

### 1. **documents** - Core Document Storage

Stores the books/documents to be indexed and ranked.

```sql
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    filename TEXT NOT NULL UNIQUE,
    title TEXT,
    author TEXT,
    word_count INTEGER CHECK (word_count > 0),
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);
```

**Indexes:**
- `idx_documents_title_trgm` - Trigram on title (fuzzy search)
- `idx_documents_author` - On author (faceted filtering)
- `idx_documents_filename` - On filename (uniqueness)

**Use Case:** Direct document retrieval by ID, filtering by author, full-text search via inverted index.

---

### 2. **inverted_index** - Term-Based Full-Text Index

Maps terms to documents with occurrence counts. Core table for BM25 ranking and regex pattern matching.

```sql
CREATE TABLE inverted_index (
    term TEXT NOT NULL,
    doc_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    occurrences INTEGER NOT NULL DEFAULT 1 CHECK (occurrences > 0),
    PRIMARY KEY (term, doc_id)
);
```

**Why this design?**
- **Denormalization:** Term stored directly (vs separate terms table)
- **Performance:** Avoids 1 JOIN per search query
- **Scalability:** Can partition by term range in large deployments

**Indexes:**
- `idx_inverted_index_term_trgm` - Trigram on term (prefix search, fuzzy matching)
- `idx_inverted_index_doc_id` - On doc_id (reverse lookups)
- `idx_inverted_index_occurrences` - On occurrence count (BM25 ranking)

**Use Cases:**
- `search_by_term()` - Exact term search
- `search_by_regex()` - Pattern matching on terms
- BM25 ranking computation (in-memory, using this table as corpus)
- Document frequency (DF) for IDF calculations

**Scalability Note:**
For 1M+ documents with 10K average unique terms per document, consider:
```sql
-- Partition by term first letter
CREATE TABLE inverted_index_a PARTITION OF inverted_index FOR VALUES FROM ('a') TO ('b');
```

---

### 3. **jaccard_edges** - Similarity Graph

Pre-computed Jaccard similarity edges between document pairs.

```sql
CREATE TABLE jaccard_edges (
    doc_a UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    doc_b UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    jaccard_score DOUBLE PRECISION NOT NULL CHECK (0 <= jaccard_score <= 1),
    created_at TIMESTAMPTZ DEFAULT now(),
    PRIMARY KEY (doc_a, doc_b),
    CHECK (doc_a < doc_b)  -- Prevent duplicates (a,b) and (b,a)
);
```

**Why ordered constraint?**
- Jaccard(A, B) = Jaccard(B, A) (symmetric)
- Storing only `doc_a < doc_b` saves 50% space
- Query both directions: `WHERE doc_a = ID OR doc_b = ID`

**Indexes:**
- Primary key acts as main index
- `idx_jaccard_edges_doc_a`, `idx_jaccard_edges_doc_b` - For neighborhood queries
- `idx_jaccard_edges_score` - For top-K similar documents

**Use Case:** Get K-nearest neighbors of a document via Jaccard similarity.

**Computing Jaccard:**
```
Jaccard(A, B) = |tokens_A ∩ tokens_B| / |tokens_A ∪ tokens_B|
```

---

### 4. **centrality_scores** - Graph Ranking Metrics

Pre-computed centrality measures for all documents (extensible for PageRank, Closeness, Betweenness).

```sql
CREATE TABLE centrality_scores (
    doc_id UUID PRIMARY KEY REFERENCES documents(id) ON DELETE CASCADE,
    pagerank_score DOUBLE PRECISION,
    closeness_score DOUBLE PRECISION,
    betweenness_score DOUBLE PRECISION,
    computed_at TIMESTAMPTZ DEFAULT now()
);
```

**Why pre-computed?**
- Graph algorithms (PageRank, Closeness) are O(V³) in worst case
- Pre-compute once during ingestion, query instantly at search time
- Can update asynchronously every N hours

**Indexes:**
- `idx_centrality_pagerank` - For PageRank-based ranking
- `idx_centrality_closeness` - For Closeness-based ranking
- `idx_centrality_betweenness` - For Betweenness-based ranking

**Extensibility:**
Can add more columns as needed:
```sql
ALTER TABLE centrality_scores
ADD COLUMN eigenvector_centrality DOUBLE PRECISION,
ADD COLUMN harmonic_centrality DOUBLE PRECISION;
```

---

### 5. **search_results_cache** (Optional) - Query Cache

Cache popular search queries and their ranked results to reduce computation.

```sql
CREATE TABLE search_results_cache (
    query_hash VARCHAR(64) PRIMARY KEY,
    query_text TEXT NOT NULL,
    results JSONB,  -- [{doc_id, score, rank}, ...]
    created_at TIMESTAMPTZ DEFAULT now(),
    hit_count INTEGER DEFAULT 0
);
```

**TTL Strategy:**
- Application-level: Delete cached results older than 24 hours
- Or: Use PostgreSQL `pg_cron` extension for automatic cleanup

**Use Case:** Reduce repeated BM25 computation for trending queries.

---

### 6. **popularity_metrics** (Optional) - Click Tracking

Track user engagement for multi-factor ranking.

```sql
CREATE TABLE popularity_metrics (
    doc_id UUID PRIMARY KEY REFERENCES documents(id) ON DELETE CASCADE,
    click_count BIGINT DEFAULT 0,
    view_count BIGINT DEFAULT 0,
    last_accessed TIMESTAMPTZ,
    last_clicked TIMESTAMPTZ
);
```

**Ranking Formula:**
```
final_score = 0.5 * bm25_score + 0.3 * jaccard_score + 0.2 * popularity_score
```

---

## Helper Functions

### `search_by_term(p_term TEXT)`
Find documents containing exact term.

```sql
SELECT * FROM search_by_term('dragon');
-- Returns: (doc_id, title, author, word_count, occurrences)
```

### `search_by_regex(p_regex TEXT)`
Find documents matching regex pattern on terms.

```sql
SELECT * FROM search_by_regex('drag.*');
-- Returns terms starting with 'drag': dragon, dragonfly, etc.
```

### `get_jaccard_neighbors(p_doc_id UUID, p_limit INT)`
Get K most similar documents based on Jaccard similarity.

```sql
SELECT * FROM get_jaccard_neighbors('550e8400-e29b-41d4-a716-446655440000'::UUID, 5);
-- Returns top 5 neighbors with similarity scores
```

### `get_top_by_centrality(p_metric TEXT, p_limit INT)`
Get top documents by centrality metric (pagerank, closeness, or betweenness).

```sql
SELECT * FROM get_top_by_centrality('pagerank', 10);
SELECT * FROM get_top_by_centrality('closeness', 10);
SELECT * FROM get_top_by_centrality('betweenness', 10);
```

---

## Database Scripts

All scripts use environment variables from `.env`:

| Variable | Default | Purpose |
|----------|---------|---------|
| `SEARCHBOOK_DB_HOST` | `postgres` | PostgreSQL hostname |
| `SEARCHBOOK_DB_PORT` | `5432` | PostgreSQL port |
| `SEARCHBOOK_DB_NAME` | `searchbook` | Database name |
| `SEARCHBOOK_DB_USER` | `searchbook` | Database user |

### 1. **test_connection.sh**

Verify database connection and schema completeness.

```bash
cd app2
bash database/scripts/test_connection.sh
```

**Checks:**
- ✅ PostgreSQL connection
- ✅ Required tables exist
- ✅ Required functions exist
- ✅ Required extensions loaded

### 2. **migrate_db.sh**

Run all SQL migrations from `database/migrations/` folder.

```bash
bash database/scripts/migrate_db.sh
```

**Behavior:**
- Finds all `.sql` files in migrations directory (alphabetically sorted)
- Executes them sequentially
- Outputs CREATE/DROP/INDEX operations for verification

**Future:** Can add version tracking for incremental migrations.

### 3. **inspect_schema.sh**

Inspect database schema, table sizes, and index performance.

```bash
bash database/scripts/inspect_schema.sh
```

**Output:**
- Table sizes (with total relation size)
- Row counts per table
- Index usage statistics (scans, tuples read/fetched)

### 4. **reset_db.sh** ⚠️

**DANGER:** Reset database to empty state (deletes ALL data).

```bash
bash database/scripts/reset_db.sh
# Type 'yes' to confirm
```

**Use Case:** 
- Dev environment recovery
- Testing ingestion pipeline from scratch
- Removing corrupt data

### 5. **backup_db.sh**

Create SQL dump of entire database to `database/backups/`.

```bash
bash database/scripts/backup_db.sh
# Creates: database/backups/searchbook_backup_20251129_185900.sql
```

**Restore:**
```bash
psql -h postgres -U searchbook -d searchbook < database/backups/searchbook_backup_20251129_185900.sql
```

---

## Workflow Examples

### Setup Fresh Database

```bash
cd app2

# 1. Start PostgreSQL container
docker compose up -d postgres

# 2. Wait for health check
sleep 10

# 3. Test connection (includes running migrations)
bash database/scripts/test_connection.sh
```

### Ingest Data

```bash
# Phase 1: Load documents into inverted_index
python ingestion/load_books.py --corpus-path /path/to/books --phase 1

# Phase 2: Compute Jaccard graph and centrality scores
python ingestion/load_books.py --corpus-path /path/to/books --phase 2

# Inspect results
bash database/scripts/inspect_schema.sh
```

### Backup Before Major Changes

```bash
# Backup current state
bash database/scripts/backup_db.sh

# Make changes (add index, modify function, etc.)
psql -h postgres -U searchbook -d searchbook -c "CREATE INDEX ..."

# If something breaks, restore
bash database/scripts/reset_db.sh
psql -h postgres -U searchbook -d searchbook < database/backups/searchbook_backup_20251129_185900.sql
```

### Development Workflow

```bash
# Start all services
docker compose up --build

# In another terminal, run DB management tasks
bash database/scripts/test_connection.sh     # Verify setup
python ingestion/load_books.py ...           # Load data
bash database/scripts/inspect_schema.sh      # Check results
```

---

## Performance Considerations

### Query Optimization

**Finding terms by prefix (trigram index):**
```sql
-- ✅ FAST: Uses idx_inverted_index_term_trgm
SELECT * FROM inverted_index WHERE term LIKE 'drag%';

-- ❌ SLOW: Full table scan
SELECT * FROM inverted_index WHERE term LIKE '%dragon';
```

**Jaccard neighborhood query:**
```sql
-- ✅ FAST: Uses indexes on doc_a, doc_b
SELECT * FROM jaccard_edges 
WHERE doc_a = $1 OR doc_b = $1
ORDER BY jaccard_score DESC
LIMIT 5;
```

### Index Maintenance

Monitor index bloat:
```sql
SELECT schemaname, tablename, indexname, idx_scan
FROM pg_stat_user_indexes
WHERE idx_scan = 0  -- Unused indexes
ORDER BY pg_relation_size(indexrelid) DESC;
```

Rebuild large indexes:
```sql
REINDEX INDEX CONCURRENTLY idx_inverted_index_term_trgm;
```

### Connection Pooling

In production, use PgBouncer or pgpool-II to manage connections:

```ini
# pgbouncer.ini
[databases]
searchbook = host=postgres port=5432 dbname=searchbook user=searchbook password=secret
```

---

## Migration Strategy

For large schema changes without downtime:

### 1. **Non-blocking column addition:**
```sql
ALTER TABLE documents ADD COLUMN language VARCHAR(10) DEFAULT 'en';
```

### 2. **Non-blocking index creation:**
```sql
CREATE INDEX CONCURRENTLY idx_new_column ON documents(language);
```

### 3. **Function updates (zero downtime):**
```sql
CREATE OR REPLACE FUNCTION search_by_term(...)
-- Old function still serves queries during update
-- New function replaces it atomically
```

### 4. **Table partitioning (future):**
```sql
-- For 100M+ documents, partition by date or term range
CREATE TABLE inverted_index_2025_01 
PARTITION OF inverted_index
FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');
```

---

## Disaster Recovery

### Automated Backups

Set up cron jobs:
```bash
# crontab -e
0 2 * * * /home/leo/Bureau/.../app2/database/scripts/backup_db.sh

# Keeps last 7 days of backups
find /home/leo/Bureau/.../app2/database/backups -mtime +7 -delete
```

### Point-in-Time Recovery

Enable archiving:
```sql
-- In postgresql.conf
wal_level = replica
archive_mode = on
archive_command = 'cp %p /backups/wal/%f'
```

Then restore to specific timestamp:
```sql
-- Create recovery.conf with recovery_target_timeline = 'latest'
-- Restore from backup and replay WAL logs up to target time
```

---

## Monitoring

### Table Growth

```sql
SELECT schemaname, tablename, 
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### Slow Queries

```sql
-- Enable query logging
ALTER SYSTEM SET log_min_duration_statement = 100;  -- Log queries > 100ms
SELECT pg_reload_conf();

-- View logs
tail -f /var/lib/postgresql/data/log/postgresql.log
```

### Replication Status (if applicable)

```sql
SELECT slot_name, slot_type, active, restart_lsn 
FROM pg_replication_slots;
```

---

## FAQs

**Q: Why not use Elasticsearch instead of PostgreSQL?**  
A: We need SQL joins, ACID transactions, and graph algorithms (NetworkX). PostgreSQL provides better query flexibility and operational simplicity for this use case.

**Q: Should I use BM25 in PostgreSQL or in-memory?**  
A: Hybrid approach: Store inverted_index in PostgreSQL, compute BM25 scores in Python (rank-bm25 library). PostgreSQL doesn't have native BM25, so in-memory computation is simpler than custom triggers.

**Q: How often should I recompute centrality scores?**  
A: Depends on ingestion rate. For static corpus: once during setup. For growing corpus: weekly or when doc count changes > 10%.

**Q: Can I use this with Redis caching?**  
A: Yes! Cache popular query results in Redis (with TTL), fall back to PostgreSQL for cold queries.

---

**Last Updated:** 2025-11-29  
**Database Version:** PostgreSQL 16-Alpine  
**Schema Version:** 001
