-- Function to increment click count
CREATE OR REPLACE FUNCTION increment_book_click(p_book_id INTEGER)
RETURNS VOID AS $$
BEGIN
    UPDATE books
    SET click_count = click_count + 1
    WHERE id = p_book_id;
END;
$$ LANGUAGE plpgsql;

-- Redefine get_suggestions to use click_count (popularity)
-- Must DROP first because return type changed (FLOAT -> BIGINT, +image_url)
DROP FUNCTION IF EXISTS get_suggestions(INTEGER, INTEGER);

CREATE OR REPLACE FUNCTION get_suggestions(p_book_id INTEGER, p_limit INTEGER DEFAULT 5)
RETURNS TABLE(similar_book_id INTEGER, title TEXT, author TEXT, similarity_score BIGINT, image_url TEXT) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        b.id as similar_book_id,
        b.title, 
        b.author, 
        b.click_count as similarity_score,
        b.image_url
    FROM books b
    WHERE b.id != p_book_id
    ORDER BY b.click_count DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql STABLE;
