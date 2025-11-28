-- CreateExtensions
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Table Documents : stocke les livres
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    filename TEXT NOT NULL,
    title TEXT,
    author TEXT,
    word_count INTEGER,
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Table IndexInversé : mappe termes -> documents avec occurrences
-- Note: term TEXT en PRIMARY KEY pour dénormalisation + performance
-- Évite 1 JOIN à chaque recherche (terms.id → inverted_index)
CREATE TABLE IF NOT EXISTS inverted_index (
    term TEXT NOT NULL,
    doc_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    occurrences INTEGER NOT NULL DEFAULT 1,
    PRIMARY KEY (term, doc_id)
);

-- Table ArêtesJaccard : graphe de similarité Jaccard
CREATE TABLE IF NOT EXISTS jaccard_edges (
    doc_a UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    doc_b UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    jaccard_score DOUBLE PRECISION NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    PRIMARY KEY (doc_a, doc_b),
    CHECK (doc_a < doc_b)  -- Évite les doublons (a,b) et (b,a)
);

-- Table IndicesCentralité : stocke les scores PageRank pré-calculés
CREATE TABLE IF NOT EXISTS centrality_scores (
    doc_id UUID PRIMARY KEY REFERENCES documents(id) ON DELETE CASCADE,
    pagerank_score DOUBLE PRECISION NOT NULL,
    computed_at TIMESTAMPTZ DEFAULT now()
);

-- Table PopularitéDoc : track des clics/popularité
CREATE TABLE IF NOT EXISTS popularity_doc (
    doc_id UUID PRIMARY KEY REFERENCES documents(id) ON DELETE CASCADE,
    clicks BIGINT DEFAULT 0,
    last_clicked TIMESTAMPTZ
);

-- Indexes pour la performance
CREATE INDEX IF NOT EXISTS idx_inverted_index_term_trgm ON inverted_index USING gin (term gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_inverted_index_doc_id ON inverted_index(doc_id);
CREATE INDEX IF NOT EXISTS idx_documents_title_trgm ON documents USING gin (title gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_documents_author ON documents(author);
CREATE INDEX IF NOT EXISTS idx_jaccard_edges_doc_a ON jaccard_edges(doc_a);
CREATE INDEX IF NOT EXISTS idx_jaccard_edges_doc_b ON jaccard_edges(doc_b);
CREATE INDEX IF NOT EXISTS idx_centrality_pagerank ON centrality_scores(pagerank_score DESC);
CREATE INDEX IF NOT EXISTS idx_popularity_clicks ON popularity_doc(clicks DESC);

-- Fonction utilitaire : recherche par terme simple
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

-- Fonction : recherche par expression régulière sur les termes
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

-- Fonction : suggestions basées sur les voisins Jaccard
CREATE OR REPLACE FUNCTION get_suggestions(p_doc_id UUID, p_limit INT DEFAULT 5)
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
