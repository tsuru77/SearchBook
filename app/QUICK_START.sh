#!/bin/bash
# SearchBook Ingestion Pipeline - Quick Start Guide

# =============================================================================
# QUICK START (Copy & Paste Ready)
# =============================================================================

# 1. Load first 10 books from Project Gutenberg (fastest test)
cd /path/to/SearchBook/app2
python ingestion/load_books.py --source gutenberg --start-id 1 --limit 10

# 2. Load 50 books and compute everything
python ingestion/load_books.py --source gutenberg --start-id 1 --limit 50

# 3. Load your local books
python ingestion/load_books.py --source local --corpus-path ./books

# =============================================================================
# REALISTIC EXAMPLES
# =============================================================================

# EXAMPLE 1: Initial corpus loading (classic literature)
# Load books 1-100 from Gutenberg (Alice, Pride and Prejudice, Sherlock, etc.)
python ingestion/load_books.py \
    --source gutenberg \
    --start-id 1 \
    --limit 100 \
    --phase 1

# Then compute graphs
python ingestion/load_books.py \
    --source gutenberg \
    --phase 2

# EXAMPLE 2: Add more books later
# Resume from book 101 (don't reload 1-100)
python ingestion/load_books.py \
    --source gutenberg \
    --start-id 101 \
    --limit 100 \
    --phase 1

# Recompute graphs (includes new books)
python ingestion/load_books.py \
    --source gutenberg \
    --phase 2

# EXAMPLE 3: Local corpus with filtering
# Load books from your directory, only those > 20,000 words
python ingestion/load_books.py \
    --source local \
    --corpus-path ./my_books \
    --min-words 20000 \
    --phase all

# EXAMPLE 4: Strict similarity threshold
# Only connect very similar books (Jaccard > 0.3)
python ingestion/load_books.py \
    --source gutenberg \
    --start-id 200 \
    --limit 30 \
    --jaccard-threshold 0.3

# EXAMPLE 5: Two-phase with different options
# Phase 1: Load 50 books
python ingestion/load_books.py \
    --source gutenberg \
    --start-id 1 \
    --limit 50 \
    --phase 1

# Phase 2: Compute with custom threshold
python ingestion/load_books.py \
    --source gutenberg \
    --phase 2 \
    --jaccard-threshold 0.15

# =============================================================================
# WHAT EACH OPTION DOES
# =============================================================================

# --source gutenberg          Load books from Project Gutenberg
# --source local              Load .txt files from local directory

# --start-id 1                Start at Project Gutenberg book ID 1
# --start-id 100              Start at book ID 100

# --limit 50                  Process maximum 50 books
# --limit 100                 Process maximum 100 books

# --min-words 10000           Only include books with 10,000+ words
# --min-words 5000            Lower threshold (include shorter books)

# --phase 1                   Load books only
# --phase 2                   Compute graphs only
# --phase all                 Load books AND compute graphs

# --jaccard-threshold 0.1     Connect books with 10%+ vocabulary overlap
# --jaccard-threshold 0.2     Stricter: only 20%+ overlap
# --jaccard-threshold 0.05    Looser: include 5%+ overlap

# =============================================================================
# COMMON WORKFLOWS
# =============================================================================

# WORKFLOW 1: Build corpus from scratch
echo "Building SearchBook corpus from Project Gutenberg..."
python ingestion/load_books.py --source gutenberg --start-id 1 --limit 100
echo "✅ Corpus complete with 100 books"

# WORKFLOW 2: Incremental loading
echo "Loading batch 101-200..."
python ingestion/load_books.py --source gutenberg --start-id 101 --limit 100
echo "Recomputing similarity graphs..."
python ingestion/load_books.py --source gutenberg --phase 2
echo "✅ Added 100 more books"

# WORKFLOW 3: Local corpus
echo "Loading from local directory..."
python ingestion/load_books.py --source local --corpus-path ./literature
echo "✅ Local books loaded"

# WORKFLOW 4: Testing with small dataset
echo "Loading 5 books for testing..."
python ingestion/load_books.py --source gutenberg --start-id 1 --limit 5
echo "✅ Ready for testing"

# =============================================================================
# MONITORING & VERIFICATION
# =============================================================================

# Check how many books are loaded
psql searchbook -c "SELECT COUNT(*) as books, COUNT(DISTINCT word) as unique_words FROM books, inverted_index;"

# Check top books by closeness
psql searchbook -c "SELECT id, title, author, closeness_score FROM books ORDER BY closeness_score DESC LIMIT 10;"

# Check Jaccard graph
psql searchbook -c "SELECT COUNT(*) as edges FROM jaccard_graph;"

# Check word statistics
psql searchbook -c "SELECT COUNT(DISTINCT word) as total_words, AVG(frequency) as avg_frequency FROM inverted_index;"

# =============================================================================
# PERFORMANCE TIPS
# =============================================================================

# Tip 1: Start small for testing
# Don't load 1000 books on first try. Test with 10 first.
python ingestion/load_books.py --source gutenberg --start-id 1 --limit 10

# Tip 2: Phase 1 and 2 can be separate
# Load all books first (Phase 1), then compute graphs later (Phase 2)
python ingestion/load_books.py --source gutenberg --start-id 1 --limit 100 --phase 1
# ... do other stuff ...
python ingestion/load_books.py --source gutenberg --phase 2

# Tip 3: Monitor database disk usage
du -sh /var/lib/postgresql/data/  # If local PostgreSQL
# Or check with: psql searchbook -c "SELECT pg_size_pretty(pg_database_size('searchbook'));"

# Tip 4: Use --limit wisely
# 10 books = ~10 seconds
# 50 books = ~60 seconds
# 100 books = ~120 seconds
# 1000 books = ~20-30 minutes

# =============================================================================
# DATABASE QUERIES FOR ANALYSIS
# =============================================================================

# Most common words
psql searchbook -c "
SELECT word, COUNT(*) as book_count, AVG(frequency) as avg_freq
FROM inverted_index
GROUP BY word
ORDER BY book_count DESC
LIMIT 20;
"

# Books with most similar neighbors
psql searchbook -c "
SELECT b.id, b.title, COUNT(jg.*) as similar_books
FROM books b
LEFT JOIN jaccard_graph jg ON (b.id = jg.book_a_id OR b.id = jg.book_b_id)
GROUP BY b.id
ORDER BY similar_books DESC
LIMIT 10;
"

# Similarity graph connectivity
psql searchbook -c "
SELECT 
    COUNT(*) as total_edges,
    MIN(similarity_score) as min_similarity,
    MAX(similarity_score) as max_similarity,
    AVG(similarity_score) as avg_similarity
FROM jaccard_graph;
"

# Books with highest closeness centrality
psql searchbook -c "
SELECT 
    id, 
    title, 
    author, 
    closeness_score,
    word_count
FROM books
WHERE closeness_score > 0
ORDER BY closeness_score DESC
LIMIT 10;
"

# =============================================================================
# TROUBLESHOOTING
# =============================================================================

# Q: Books not loading from Gutenberg?
# A: Check internet connection. Some IDs may not exist (normal).

# Q: "Database connection failed"?
# A: Check PostgreSQL is running: systemctl status postgresql

# Q: Too slow?
# A: Use --phase 1 first (skip graph computation), then --phase 2 later

# Q: Out of disk space?
# A: Check database size and delete old books if needed

# Q: Want to reload everything?
# A: The database script (db_init.sql) has DROP TABLE IF EXISTS at top
#    So you can restart with fresh tables

# =============================================================================
# ADVANCED: BATCH PROCESSING
# =============================================================================

# Load 1000 books in batches
for batch in {0..9}; do
    start_id=$((batch * 100 + 1))
    echo "Loading batch $batch (IDs $start_id to $((start_id+99)))..."
    python ingestion/load_books.py \
        --source gutenberg \
        --start-id $start_id \
        --limit 100 \
        --phase 1
done

# After all batches loaded, compute graphs once
echo "Computing similarity graphs..."
python ingestion/load_books.py --source gutenberg --phase 2

# =============================================================================
# EXPECTED OUTPUT
# =============================================================================

# Successful run should show:
# ======================================================================
# SearchBook Ingestion Pipeline
# ======================================================================
# Source: gutenberg
# Project Gutenberg IDs: 1 to 10
# Minimum words: 10000
# Phase: all
# ======================================================================
#
# 📚 Phase 1: Loading books from gutenberg
#    Min word count: 10000
#
#    Found 10 books to process
#
#    [1/10] ⏭️  Gutenberg #1 (not found)
#    [2/10] 📖 Alice's Adventures in Wonderland (29446 words)
#           ✅ Inserted (2456 unique terms)
#    [3/10] 📖 Pride and Prejudice (28432 words)
#           ✅ Inserted (2234 unique terms)
#    [4/10] 📖 The Picture of Dorian Gray (24267 words)
#           ✅ Inserted (1894 unique terms)
#    ...
#
# ✅ Phase 1 complete
#    Loaded: 8, Skipped: 1, Errors: 1
#
# 🔗 Phase 2: Computing Jaccard graph and Closeness centrality
#    Jaccard threshold: 0.1
#
#    1️⃣  Loading book vocabularies...
#       Found 8 books
#    2️⃣  Computing Jaccard similarities...
#       Found 18 edges (threshold=0.1)
#    3️⃣  Inserting Jaccard edges...
#    4️⃣  Computing Closeness centrality (NetworkX)...
#    5️⃣  Updating closeness scores...
#
# ✅ Phase 2 complete
#
#    📊 Top 5 books by Closeness centrality:
#       1. Alice's Adventures in Wonderland by Lewis Carroll - 0.8234
#       2. Pride and Prejudice by Jane Austen - 0.7856
#       3. The Picture of Dorian Gray by Oscar Wilde - 0.7234
#       4. Jane Eyre by Charlotte Brontë - 0.6890
#       5. Great Expectations by Charles Dickens - 0.6412
#
# ======================================================================
# ✅ Pipeline completed successfully in 127.3s
# ======================================================================

# =============================================================================
# NEXT STEPS AFTER INGESTION
# =============================================================================

# 1. Test search API with loaded books
#    curl http://localhost:5000/api/search?q=alice

# 2. Test recommendations
#    curl http://localhost:5000/api/suggestions?book_id=1

# 3. Check frontend displays books correctly
#    Open http://localhost:3000 in browser

# 4. Monitor performance
#    Query response times, database size, etc.

# 5. Gradually add more books
#    Use --start-id to resume from where you left off
