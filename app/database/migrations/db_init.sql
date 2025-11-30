-- Nettoyage préalable (pour le développement)
DROP TABLE IF EXISTS jaccard_graph CASCADE;
DROP TABLE IF EXISTS inverted_index CASCADE;
DROP TABLE IF EXISTS books CASCADE;

-- ==========================================
-- 1. TABLE PRINCIPALE : LES LIVRES
-- ==========================================
CREATE TABLE books (
    id                  SERIAL PRIMARY KEY, -- ID du livre
    gutenberg_id        INTEGER UNIQUE,     -- ID Gutenberg unique
    title               TEXT NOT NULL,      -- Titre du livre 
    author              TEXT,               -- Auteur du livre
    language            TEXT,               -- Langue du document
    content             TEXT NOT NULL,      -- Le contenu brut du livre
    word_count          INTEGER DEFAULT 0,  -- Nombre de mot dans le document
    publication_year    INTEGER,            -- Année de publication

    click_count         BIGINT DEFAULT 0,   -- Nombre de clics (popularité)
    closeness_score     FLOAT DEFAULT 0,    -- Le score de centralité (closeness)

    inserted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index pour accélérer le tri par centralité
CREATE INDEX idx_books_closeness ON books(closeness_score DESC);

-- ==========================================
-- 2. INDEX INVERSÉ (POUR LA RECHERCHE TEXTUELLE & BM25)
-- ==========================================
CREATE TABLE inverted_index (
    book_id     INTEGER REFERENCES books(id) ON DELETE CASCADE,
    word        TEXT NOT NULL,  
    frequency   INTEGER NOT NULL, 
    
    PRIMARY KEY (book_id, word) 
);

-- Index pour trouver rapidement les livres contenant un mot
CREATE INDEX idx_inv_word_book ON inverted_index(word);

-- Index CRITIQUE pour compter le nombre de documents contenant un mot (calcul de l'IDF)
CREATE INDEX idx_inv_word_count ON inverted_index(word, book_id);


-- ==========================================
-- 3. GRAPHE JACCARD (POUR LA SUGGESTION)
-- ==========================================
CREATE TABLE jaccard_graph (
    book_a_id INTEGER REFERENCES books(id) ON DELETE CASCADE,
    book_b_id INTEGER REFERENCES books(id) ON DELETE CASCADE,
    similarity_score FLOAT NOT NULL,
    
    PRIMARY KEY (book_a_id, book_b_id),
    -- Création d'une contrainte pour : 
    -- 1. Empêcher l'auto-référence (A != B).
    -- 2. Garantir l'unicité de la paire (A-B et non B-A) pour éviter la redondance.
    CHECK (book_a_id < book_b_id)
);

-- Index pour les requêtes de suggestion (voisins)
CREATE INDEX idx_jaccard_lookup_a ON jaccard_graph(book_a_id, similarity_score DESC);
CREATE INDEX idx_jaccard_lookup_b ON jaccard_graph(book_b_id, similarity_score DESC);


-- ==========================================
-- 4. FONCTIONS UTILITAIRES
-- ==========================================

-- FONCTION 1: search_by_word
-- Utilité: Trouver tous les livres contenant un mot spécifique
-- Cas d'usage: Recherche simple par terme (ex: "dragon")
-- Retour: Liste de livres avec titre, auteur, fréquence du mot
-- Note: Les mots sont déjà en minuscules (tokenization en Python)
CREATE OR REPLACE FUNCTION search_by_word(p_word TEXT)
RETURNS TABLE(book_id INTEGER, title TEXT, author TEXT, frequency INTEGER) AS $$
BEGIN
    RETURN QUERY
    SELECT ii.book_id, b.title, b.author, ii.frequency
    FROM inverted_index ii
    JOIN books b ON b.id = ii.book_id
    WHERE ii.word = p_word
    ORDER BY ii.frequency DESC;
END;
$$ LANGUAGE plpgsql STABLE;


-- FONCTION 2: search_by_regex
-- Utilité: Rechercher des livres avec des mots correspondant à un pattern regex
-- Cas d'usage: Recherche avancée (ex: "drag.*" pour "dragon", "dragonfly", etc.)
-- Retour: Liste de livres avec titre, auteur, fréquence agrégée
CREATE OR REPLACE FUNCTION search_by_regex(p_regex TEXT)
RETURNS TABLE(book_id INTEGER, title TEXT, author TEXT, total_frequency INTEGER) AS $$
BEGIN
    RETURN QUERY
    SELECT ii.book_id, b.title, b.author, SUM(ii.frequency)::INTEGER
    FROM inverted_index ii
    JOIN books b ON b.id = ii.book_id
    WHERE ii.word ~ p_regex
    GROUP BY ii.book_id, b.title, b.author
    ORDER BY SUM(ii.frequency) DESC;
END;
$$ LANGUAGE plpgsql STABLE;


-- FONCTION 3: get_suggestions
-- Utilité: Obtenir les K livres les plus similaires à un livre donné
-- Cas d'usage: "Livres similaires" - afficher les voisins Jaccard
-- Retour: Liste de livres avec titre, auteur, score Jaccard
CREATE OR REPLACE FUNCTION get_suggestions(p_book_id INTEGER, p_limit INTEGER DEFAULT 5)
RETURNS TABLE(similar_book_id INTEGER, title TEXT, author TEXT, similarity_score FLOAT) AS $$
BEGIN
    RETURN QUERY
    SELECT DISTINCT
        CASE WHEN jg.book_a_id = p_book_id THEN jg.book_b_id ELSE jg.book_a_id END as neighbor_id,
        b.title, b.author, jg.similarity_score
    FROM jaccard_graph jg
    JOIN books b ON b.id = (CASE WHEN jg.book_a_id = p_book_id THEN jg.book_b_id ELSE jg.book_a_id END)
    WHERE jg.book_a_id = p_book_id OR jg.book_b_id = p_book_id
    ORDER BY jg.similarity_score DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql STABLE;


-- FONCTION 4: get_top_books_by_closeness
-- Utilité: Obtenir les K livres les plus importants du graphe (par closeness centrality)
-- Cas d'usage: Afficher les livres "centraux" - les plus connectés aux autres
-- Retour: Liste de livres triés par score de centralité décroissant
CREATE OR REPLACE FUNCTION get_top_books_by_closeness(p_limit INTEGER DEFAULT 10)
RETURNS TABLE(book_id INTEGER, title TEXT, author TEXT, closeness_score FLOAT) AS $$
BEGIN
    RETURN QUERY
    SELECT b.id, b.title, b.author, b.closeness_score
    FROM books b
    WHERE b.closeness_score > 0
    ORDER BY b.closeness_score DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql STABLE;