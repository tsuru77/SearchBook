-- SearchBook PostgreSQL Schema
-- Centralized database schema for document indexing, similarity graph, and ranking
-- Created: 2025-11-29

-- ============================================================================
-- EXTENSIONS
-- ============================================================================
CREATE EXTENSION IF NOT EXISTS pg_trgm;      -- Trigram text search
CREATE EXTENSION IF NOT EXISTS unaccent;     -- Accent-insensitive search
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";  -- UUID generation


-- ============================================================================
-- TABLE: documents
-- Description: Core document storage (books)
-- Indexes: Trigram on title/author for similarity search
-- ============================================================================
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    filename TEXT NOT NULL UNIQUE,
    title TEXT,
    author TEXT,
    word_count INTEGER CHECK (word_count > 0),
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_documents_title_trgm ON documents USING gin (title gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_documents_author ON documents(author);
CREATE INDEX IF NOT EXISTS idx_documents_filename ON documents(filename);


-- ============================================================================
-- TABLE: inverted_index
-- Description: Inverted index mapping terms to documents with occurrence counts
-- Purpose: Core index for term-based search, BM25 ranking, and regex matching
-- Note: term TEXT as PRIMARY KEY for denormalization + performance
--       Avoids 1 JOIN on every search (vs separate terms table)
-- Indexes: Trigram for fuzzy/prefix search, doc_id for reverse lookups
-- ============================================================================
CREATE TABLE IF NOT EXISTS inverted_index (
    term TEXT NOT NULL,
    doc_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    occurrences INTEGER NOT NULL DEFAULT 1 CHECK (occurrences > 0),
    PRIMARY KEY (term, doc_id)
);

CREATE INDEX IF NOT EXISTS idx_inverted_index_term_trgm ON inverted_index USING gin (term gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_inverted_index_doc_id ON inverted_index(doc_id);
CREATE INDEX IF NOT EXISTS idx_inverted_index_occurrences ON inverted_index(occurrences DESC);


-- ============================================================================
-- TABLE: jaccard_edges
-- Description: Jaccard similarity graph edges between documents
-- Purpose: Store pre-computed Jaccard similarities for semantic linking
-- Constraint: doc_a < doc_b to avoid duplicate edges (a,b) and (b,a)
-- ============================================================================
CREATE TABLE IF NOT EXISTS jaccard_edges (
    doc_a UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    doc_b UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    jaccard_score DOUBLE PRECISION NOT NULL CHECK (jaccard_score >= 0 AND jaccard_score <= 1),
    created_at TIMESTAMPTZ DEFAULT now(),
    PRIMARY KEY (doc_a, doc_b),
    CHECK (doc_a < doc_b)
);

CREATE INDEX IF NOT EXISTS idx_jaccard_edges_doc_a ON jaccard_edges(doc_a);
CREATE INDEX IF NOT EXISTS idx_jaccard_edges_doc_b ON jaccard_edges(doc_b);
CREATE INDEX IF NOT EXISTS idx_jaccard_edges_score ON jaccard_edges(jaccard_score DESC);


-- ============================================================================
-- TABLE: centrality_scores
-- Description: Pre-computed graph centrality metrics for each document
-- Purpose: PageRank, closeness centrality, and other ranking signals
-- Extensible: Can store multiple centrality measures in one row
-- ============================================================================
CREATE TABLE IF NOT EXISTS centrality_scores (
    doc_id UUID PRIMARY KEY REFERENCES documents(id) ON DELETE CASCADE,
    pagerank_score DOUBLE PRECISION,
    closeness_score DOUBLE PRECISION,
    betweenness_score DOUBLE PRECISION,
    computed_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_centrality_pagerank ON centrality_scores(pagerank_score DESC NULLS LAST);
CREATE INDEX IF NOT EXISTS idx_centrality_closeness ON centrality_scores(closeness_score DESC NULLS LAST);
CREATE INDEX IF NOT EXISTS idx_centrality_betweenness ON centrality_scores(betweenness_score DESC NULLS LAST);


-- ============================================================================
-- TABLE: search_results_cache (Optional - for performance)
-- Description: Cache popular search queries and their ranked results
-- Purpose: Reduce repeated BM25 computation for trending searches
-- TTL: Application level (can add created_at + INTERVAL check)
-- ============================================================================
CREATE TABLE IF NOT EXISTS search_results_cache (
    query_hash VARCHAR(64) NOT NULL PRIMARY KEY,
    query_text TEXT NOT NULL,
    results JSONB NOT NULL,  -- Array of {doc_id, score, rank}
    created_at TIMESTAMPTZ DEFAULT now(),
    hit_count INTEGER DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_search_cache_popularity ON search_results_cache(hit_count DESC);


-- ============================================================================
-- TABLE: popularity_metrics (Optional - for click tracking)
-- Description: Track document popularity based on clicks/views
-- Purpose: Combine with BM25/Jaccard for multi-factor ranking
-- ============================================================================
CREATE TABLE IF NOT EXISTS popularity_metrics (
    doc_id UUID PRIMARY KEY REFERENCES documents(id) ON DELETE CASCADE,
    click_count BIGINT DEFAULT 0,
    view_count BIGINT DEFAULT 0,
    last_accessed TIMESTAMPTZ,
    last_clicked TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_popularity_clicks ON popularity_metrics(click_count DESC);
CREATE INDEX IF NOT EXISTS idx_popularity_views ON popularity_metrics(view_count DESC);


-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

-- Function: Search documents by exact term
CREATE OR REPLACE FUNCTION search_by_term(p_term TEXT)
RETURNS TABLE(doc_id UUID, title TEXT, author TEXT, word_count INTEGER, occurrences INTEGER) AS $$
BEGIN
    RETURN QUERY
    SELECT ii.doc_id, d.title, d.author, d.word_count, ii.occurrences
    FROM inverted_index ii
    JOIN documents d ON d.id = ii.doc_id
    WHERE LOWER(ii.term) = LOWER(p_term)
    ORDER BY ii.occurrences DESC;
END;
$$ LANGUAGE plpgsql STABLE;


-- Function: Search documents by regex pattern on terms
CREATE OR REPLACE FUNCTION search_by_regex(p_regex TEXT)
RETURNS TABLE(doc_id UUID, title TEXT, author TEXT, word_count INTEGER, occurrences INTEGER) AS $$
BEGIN
    RETURN QUERY
    SELECT ii.doc_id, d.title, d.author, d.word_count, ii.occurrences
    FROM inverted_index ii
    JOIN documents d ON d.id = ii.doc_id
    WHERE ii.term ~ p_regex
    ORDER BY ii.occurrences DESC;
END;
$$ LANGUAGE plpgsql STABLE;


-- Function: Get Jaccard neighbors of a document
CREATE OR REPLACE FUNCTION get_jaccard_neighbors(p_doc_id UUID, p_limit INT DEFAULT 5)
RETURNS TABLE(doc_id UUID, title TEXT, author TEXT, jaccard_score DOUBLE PRECISION) AS $$
BEGIN
    RETURN QUERY
    SELECT DISTINCT
        CASE WHEN je.doc_a = p_doc_id THEN je.doc_b ELSE je.doc_a END as neighbor_id,
        d.title, d.author, je.jaccard_score
    FROM jaccard_edges je
    JOIN documents d ON d.id = (CASE WHEN je.doc_a = p_doc_id THEN je.doc_b ELSE je.doc_a END)
    WHERE je.doc_a = p_doc_id OR je.doc_b = p_doc_id
    ORDER BY je.jaccard_score DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql STABLE;


-- Function: Get centrality-ranked documents
CREATE OR REPLACE FUNCTION get_top_by_centrality(p_metric TEXT, p_limit INT DEFAULT 10)
RETURNS TABLE(doc_id UUID, title TEXT, author TEXT, score DOUBLE PRECISION) AS $$
BEGIN
    IF p_metric = 'pagerank' THEN
        RETURN QUERY
        SELECT cs.doc_id, d.title, d.author, cs.pagerank_score
        FROM centrality_scores cs
        JOIN documents d ON d.id = cs.doc_id
        WHERE cs.pagerank_score IS NOT NULL
        ORDER BY cs.pagerank_score DESC
        LIMIT p_limit;
    ELSIF p_metric = 'closeness' THEN
        RETURN QUERY
        SELECT cs.doc_id, d.title, d.author, cs.closeness_score
        FROM centrality_scores cs
        JOIN documents d ON d.id = cs.doc_id
        WHERE cs.closeness_score IS NOT NULL
        ORDER BY cs.closeness_score DESC
        LIMIT p_limit;
    ELSIF p_metric = 'betweenness' THEN
        RETURN QUERY
        SELECT cs.doc_id, d.title, d.author, cs.betweenness_score
        FROM centrality_scores cs
        JOIN documents d ON d.id = cs.doc_id
        WHERE cs.betweenness_score IS NOT NULL
        ORDER BY cs.betweenness_score DESC
        LIMIT p_limit;
    END IF;
END;
$$ LANGUAGE plpgsql STABLE;
