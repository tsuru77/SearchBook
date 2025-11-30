-- SearchBook PostgreSQL Schema
-- Initializes tables for books, Jaccard graph edges, and centrality scores

CREATE EXTENSION IF NOT EXISTS pg_trgm;  -- For text search indexing
CREATE EXTENSION IF NOT EXISTS unaccent;

-- Books table
CREATE TABLE IF NOT EXISTS books (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    author VARCHAR(500),
    text TEXT NOT NULL,
    word_count INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Full-text search index for BM25 ranking
CREATE INDEX IF NOT EXISTS idx_books_text_trgm ON books USING GIN (text gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_books_title ON books (title);

-- Jaccard similarity graph edges
-- Stores pairs of similar books with their Jaccard similarity score
CREATE TABLE IF NOT EXISTS jaccard_edges (
    id SERIAL PRIMARY KEY,
    book_id_1 INT NOT NULL REFERENCES books(id) ON DELETE CASCADE,
    book_id_2 INT NOT NULL REFERENCES books(id) ON DELETE CASCADE,
    jaccard_similarity FLOAT NOT NULL CHECK (jaccard_similarity >= 0 AND jaccard_similarity <= 1),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(book_id_1, book_id_2),
    CHECK (book_id_1 < book_id_2)
);

CREATE INDEX IF NOT EXISTS idx_jaccard_edges_book_id_1 ON jaccard_edges(book_id_1);
CREATE INDEX IF NOT EXISTS idx_jaccard_edges_book_id_2 ON jaccard_edges(book_id_2);

-- Centrality scores (closeness)
CREATE TABLE IF NOT EXISTS centrality_scores (
    id SERIAL PRIMARY KEY,
    book_id INT NOT NULL UNIQUE REFERENCES books(id) ON DELETE CASCADE,
    closeness_score FLOAT NOT NULL,
    betweenness_score FLOAT,
    pagerank_score FLOAT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_centrality_scores_closeness ON centrality_scores(closeness_score DESC);
CREATE INDEX IF NOT EXISTS idx_centrality_scores_pagerank ON centrality_scores(pagerank_score DESC);

-- Book pairs suggestions (pre-computed neighbors for each book)
CREATE TABLE IF NOT EXISTS similar_books (
    id SERIAL PRIMARY KEY,
    book_id INT NOT NULL REFERENCES books(id) ON DELETE CASCADE,
    similar_book_id INT NOT NULL REFERENCES books(id) ON DELETE CASCADE,
    similarity_score FLOAT NOT NULL,
    rank INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(book_id, similar_book_id),
    CHECK (rank > 0)
);

CREATE INDEX IF NOT EXISTS idx_similar_books_book_id ON similar_books(book_id);
CREATE INDEX IF NOT EXISTS idx_similar_books_rank ON similar_books(book_id, rank);
