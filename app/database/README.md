# Database Directory

PostgreSQL schema and initialization files.

## Structure

```
database/
├── migrations/                # SQL schema files (auto-run by Docker)
│   └── 001_init_schema.sql   # Complete schema with tables, indexes, functions
├── backups/                  # (for future backups if needed)
├── README.md                 # This file
└── MIGRATION_NOTES.md        # Technical notes about inverted_index restoration
```

## How It Works

When the application starts with `docker compose up`:

1. PostgreSQL container runs and mounts `database/migrations/` 
2. All `.sql` files in `migrations/` are executed automatically
3. Schema is created: tables, indexes, and helper functions
4. Ready to use!

No manual setup needed.

## Schema Overview

| Table | Purpose |
|-------|---------|
| `documents` | Books/documents |
| `inverted_index` | Term → Document mapping for BM25 search |
| `jaccard_edges` | Similarity graph edges |
| `centrality_scores` | PageRank, Closeness, Betweenness scores |

For full architecture details, see: [`../DATABASE.md`](../DATABASE.md)

## Key Tables

### `inverted_index` (Restored ⭐)

Maps terms to documents with occurrence counts:

```sql
CREATE TABLE inverted_index (
    term TEXT NOT NULL,
    doc_id UUID NOT NULL REFERENCES documents(id),
    occurrences INTEGER NOT NULL,
    PRIMARY KEY (term, doc_id)
);
```

Enables:
- ✅ Efficient BM25 ranking
- ✅ Regex pattern matching
- ✅ Jaccard similarity computation
- ✅ Future optimizations (IDF, analytics)

See `MIGRATION_NOTES.md` for why this table was restored.

## What's Auto-Run on Startup

✅ All table creation  
✅ All indexes  
✅ All helper functions  
✅ Environment-based configuration  

Nothing to do manually!
