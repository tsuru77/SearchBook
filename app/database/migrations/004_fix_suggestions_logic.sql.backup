-- Fix get_suggestions to return neighbors from Jaccard graph
-- Sorted by popularity (click_count) then similarity
CREATE OR REPLACE FUNCTION get_suggestions(p_book_id INTEGER, p_limit INTEGER DEFAULT 5) RETURNS TABLE(
        similar_book_id INTEGER,
        title TEXT,
        author TEXT,
        similarity_score BIGINT,
        image_url TEXT
    ) AS $$ BEGIN RETURN QUERY
SELECT b.id as similar_book_id,
    b.title,
    b.author,
    b.click_count as similarity_score,
    b.image_url
FROM books b -- Join with jaccard_graph to find neighbors (undirected graph logic)
    JOIN jaccard_graph j ON (
        j.book_a_id = p_book_id
        AND j.book_b_id = b.id
    )
    OR (
        j.book_b_id = p_book_id
        AND j.book_a_id = b.id
    )
WHERE b.id != p_book_id
ORDER BY b.click_count DESC,
    j.similarity_score DESC
LIMIT p_limit;
END;
$$ LANGUAGE plpgsql STABLE;