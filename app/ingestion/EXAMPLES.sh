#!/bin/bash
# Example commands for load_books.py ingestion pipeline

# ============================================================================
# EXAMPLE 1: Load from Project Gutenberg (most common use case)
# ============================================================================

# Load first 50 books from Project Gutenberg (IDs 1-50)
# This will download books, extract metadata, tokenize, and build graphs
python load_books.py --source gutenberg --start-id 1 --limit 50

# Load 20 books starting at ID 100
python load_books.py --source gutenberg --start-id 100 --limit 20

# Phase 1 only: Load books without computing graphs (faster)
python load_books.py --source gutenberg --start-id 1 --limit 50 --phase 1

# Phase 2 only: Compute graphs on already-loaded books
python load_books.py --source gutenberg --phase 2

# Custom Jaccard threshold (stricter similarity requirement)
python load_books.py --source gutenberg --start-id 1 --limit 50 \
    --jaccard-threshold 0.2

# ============================================================================
# EXAMPLE 2: Load from local directory
# ============================================================================

# Load all .txt files from ./corpus
python load_books.py --source local --corpus-path ./corpus

# Phase 1 only
python load_books.py --source local --corpus-path ./corpus --phase 1

# Custom minimum word count (include shorter books)
python load_books.py --source local --corpus-path ./corpus --min-words 5000

# Limit to first 10 books
python load_books.py --source local --corpus-path ./corpus --limit 10

# ============================================================================
# EXAMPLE 3: Mixed scenarios
# ============================================================================

# Load 100 books, stricter similarity (threshold 0.15)
python load_books.py --source gutenberg --start-id 1 --limit 100 \
    --jaccard-threshold 0.15

# Load from local corpus, custom minimum words
python load_books.py --source local --corpus-path ./books \
    --min-words 3000 --limit 30

# Compute graphs on already-loaded data (no loading)
python load_books.py --source gutenberg --phase 2

# ============================================================================
# EXAMPLE 4: For development/testing
# ============================================================================

# Load just a few books (quick test)
python load_books.py --source gutenberg --start-id 1 --limit 5

# Load from small local corpus
python load_books.py --source local --corpus-path ./test_books --limit 3

# ============================================================================
# NOTES
# ============================================================================

# Phase 1 (load books):
# - Downloads/reads books
# - Extracts metadata (title, author, language, publication_year)
# - Stores in lowercase in database
# - Builds inverted_index with word frequencies
# - Duration: ~1s per book (download + parsing)

# Phase 2 (compute graphs):
# - Computes Jaccard similarity between all pairs
# - Builds graph and computes Closeness centrality
# - Updates closeness_score in database
# - Duration: ~0.1s per book

# Total time for 50 books: ~60s (50s Phase1 + 5s Phase2)

# ============================================================================
# DATABASE SCHEMA
# ============================================================================

# Books are stored in PostgreSQL with:
# - title, author in ORIGINAL CASE (good for display)
# - content in LOWERCASE (efficient searching)
# - language as ISO 639-1 code (e.g., 'en' for English)
# - publication_year extracted from Gutenberg metadata
# - gutenberg_id for tracking (nullable for local files)

# Inverted index contains:
# - book_id, word (lowercase), frequency
# - Used for Jaccard similarity computation
# - Used for BM25 ranking in search

# Jaccard graph contains:
# - Edges between similar books (Jaccard score >= threshold)
# - Used for recommendations
# - Closeness centrality used for ranking
