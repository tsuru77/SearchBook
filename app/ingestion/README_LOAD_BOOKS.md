# SearchBook Ingestion Pipeline - `load_books.py`

## Overview

`load_books.py` is a two-phase ingestion pipeline that loads books into the SearchBook database and computes similarity graphs for recommendations.

**Two book sources are supported:**
- **Local**: Load `.txt` files from a directory
- **Project Gutenberg**: Download books directly from https://www.gutenberg.org/

## Phase 1: Load Books & Build Inverted Index

### What it does:
1. Loads books (from local files or Project Gutenberg)
2. Extracts metadata: `title`, `author`, `language`, `publication_year`
3. Converts content to **lowercase** for consistency
4. Tokenizes: removes stopwords, punctuation, keeps only words ≥3 chars
5. Inserts into `books` table and `inverted_index` table

### Key design decisions:

#### 1. Content storage: **LOWERCASE**
- **Why?** One-time normalization at ingestion saves computation at query time
- No need for `LOWER()` function calls during searches
- Query function `search_by_word()` uses direct string comparison

```python
# Content stored lowercase
content_lower = content.lower()  # "The quick BROWN fox" → "the quick brown fox"

# Tokenization extracts words: no punctuation, no separators
tokens = re.findall(r'\b[a-z]+\b', content_lower)
# "the-quick_brown... fox?" → ["the", "quick", "brown", "fox"]
```

#### 2. Metadata: **ORIGINAL CASE**
- **Why?** Better UX - display titles and authors in natural formatting
- Title: "Alice's Adventures in Wonderland" (readable)
- Author: "Lewis Carroll" (proper naming)
- Language: Normalized to ISO 639-1 codes (e.g., "English" → "en")

#### 3. Gutenberg ID: **INTEGER**
- **Why?** Project Gutenberg uses simple numeric IDs (1, 11, 1661, etc.)
- More efficient than TEXT
- Unique constraint on `books.gutenberg_id`

#### 4. Project Gutenberg metadata extraction
Regex patterns to parse metadata from Gutenberg header:
```
Title: Alice's Adventures in Wonderland
Author: Lewis Carroll
Language: English
Release date: June 27, 2008 [eBook #11]
```

Language mapping: "English" → "en", "French" → "fr", etc. (ISO 639-1)

## Phase 2: Compute Jaccard Graph & Closeness Centrality

### What it does:
1. Loads all books and their word sets (from `inverted_index`)
2. Computes **Jaccard similarity** between all book pairs
3. Stores edges in `jaccard_graph` (above threshold)
4. Computes **Closeness centrality** using NetworkX
5. Updates `closeness_score` in `books` table

### Algorithms:

#### Jaccard Similarity
```
Jaccard(A, B) = |A ∩ B| / |A ∪ B|
```
Where A and B are sets of words in two books.

**Example:**
- Book A words: {the, quick, brown, fox}
- Book B words: {the, quick, red, fox}
- Intersection: {the, quick, fox} = 3
- Union: {the, quick, brown, red, fox} = 5
- Jaccard = 3/5 = 0.6

Only edges with score ≥ `jaccard_threshold` (default 0.1) are stored.

#### Closeness Centrality
```
Closeness(v) = 1 / (average shortest path distance to all nodes)
```

Computed using NetworkX on the Jaccard graph. Books that are "close" to many other books (high similarity) get higher scores.

## Usage

### Local Directory

```bash
# Load all .txt files from ./corpus
python load_books.py --source local --corpus-path ./corpus --phase all

# Phase 1 only (load without computing graphs)
python load_books.py --source local --corpus-path ./corpus --phase 1

# With custom minimum word count
python load_books.py --source local --corpus-path ./corpus --min-words 5000

# Limit to first 10 books
python load_books.py --source local --corpus-path ./corpus --limit 10
```

### Project Gutenberg

```bash
# Load books 1-50 from Project Gutenberg
python load_books.py --source gutenberg --start-id 1 --limit 50

# Load 20 books starting at ID 100
python load_books.py --source gutenberg --start-id 100 --limit 20

# Phase 2 only (compute graphs on already-loaded books)
python load_books.py --source gutenberg --phase 2

# Adjust Jaccard threshold
python load_books.py --source gutenberg --limit 30 --jaccard-threshold 0.2
```

## Options

```
--source {local, gutenberg}        REQUIRED. Where to load books from
--corpus-path PATH                 Required if --source local. Directory with .txt files
--start-id ID                      Starting Project Gutenberg ID (default: 1)
--limit N                          Max books to process (default: 50)
--phase {1, 2, all}               Which phase to run (default: all)
--min-words N                      Minimum words per book (default: 10000)
--jaccard-threshold FLOAT          Min Jaccard score to store edge (default: 0.1)
```

## Data Flow

### Phase 1:
```
Input Files (.txt)
       ↓
   Load & Parse
       ↓
  Extract Metadata (title, author, language, year)
       ↓
  Convert to lowercase
       ↓
  Tokenize (remove stopwords, punctuation)
       ↓
  Count word frequencies
       ↓
INSERT books (title, author, content_lowercase, ...)
INSERT inverted_index (book_id, word, frequency)
```

### Phase 2:
```
inverted_index (loaded)
       ↓
  Build word sets per book
       ↓
  Compute Jaccard(A, B) for all pairs
       ↓
INSERT jaccard_graph (if score ≥ threshold)
       ↓
  Build NetworkX graph
       ↓
  Compute Closeness centrality
       ↓
UPDATE books.closeness_score
```

## Example: Loading from Project Gutenberg

```bash
# Load first 50 books from Project Gutenberg
python load_books.py --source gutenberg --start-id 1 --limit 50

# Output:
# ======================================================================
# SearchBook Ingestion Pipeline
# ======================================================================
# Source: gutenberg
# Project Gutenberg IDs: 1 to 50
# Minimum words: 10000
# Phase: all
# ======================================================================
#
# 📚 Phase 1: Loading books from gutenberg
#    Min word count: 10000
#
#    Found 50 books to process
#
#    [1/50] ⏭️  Gutenberg #1 (not found)
#    [2/50] 📖 Alice's Adventures in Wonderland (29446 words)
#           ✅ Inserted (2456 unique terms)
#    [3/50] 📖 The Gutenberg Bible (25000 words)
#           ✅ Inserted (1845 unique terms)
#    ...
#
# ✅ Phase 1 complete
#    Loaded: 45, Skipped: 3, Errors: 2
#
# 🔗 Phase 2: Computing Jaccard graph and Closeness centrality
#    Jaccard threshold: 0.1
#
#    1️⃣  Loading book vocabularies...
#       Found 45 books
#    2️⃣  Computing Jaccard similarities...
#       Found 892 edges (threshold=0.1)
#    3️⃣  Inserting Jaccard edges...
#    4️⃣  Computing Closeness centrality (NetworkX)...
#    5️⃣  Updating closeness scores...
#
# ✅ Phase 2 complete
#
#    📊 Top 5 books by Closeness centrality:
#       1. Alice's Adventures in Wonderland by Lewis Carroll - 0.8234
#       2. The Picture of Dorian Gray by Oscar Wilde - 0.7156
#       ...
#
# ======================================================================
# ✅ Pipeline completed successfully in 127.3s
# ======================================================================
```

## Implementation Details

### Tokenization
```python
def tokenize(text: str) -> List[str]:
    # Extract words: only lowercase letters
    tokens = re.findall(r'\b[a-z]+\b', text.lower())
    
    # Filter stopwords, min length 3
    cleaned = [t for t in tokens if len(t) >= 3 and t not in STOP_WORDS]
    
    return cleaned
```

### Stopwords (50 common English words)
```python
{'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
 'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'been', 'be',
 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
 ...}
```

### Database Schema
```sql
CREATE TABLE books (
    id SERIAL PRIMARY KEY,
    gutenberg_id INTEGER UNIQUE,
    title TEXT,                    -- Original case
    author TEXT,                   -- Original case
    language TEXT,                 -- ISO 639-1 (e.g., 'en')
    publication_year INTEGER,
    content TEXT,                  -- LOWERCASE
    word_count INTEGER,
    closeness_score FLOAT,
    ...
);

CREATE TABLE inverted_index (
    book_id INTEGER,
    word TEXT,                     -- LOWERCASE (from tokenization)
    frequency INTEGER,             -- Word count in book
    PRIMARY KEY (book_id, word)
);

CREATE TABLE jaccard_graph (
    book_a_id INTEGER,
    book_b_id INTEGER,
    similarity_score FLOAT,        -- Jaccard similarity [0, 1]
    ...
);
```

## Performance Notes

- **Phase 1** (loading 50 books): ~30-60s (depends on download speed)
- **Phase 2** (computing graphs on 50 books): ~5-10s
- Tokenization: ~50,000 words/second
- Jaccard computation: O(n²) where n = number of books

## Troubleshooting

### Connection failed
```
❌ Database connection failed: ...
```
Ensure PostgreSQL is running and credentials are correct in `load_books.py`.

### Project Gutenberg book not found
```
[1/50] ⏭️  Gutenberg #1 (not found)
```
Some IDs may not exist. This is normal. The script continues with the next ID.

### Books skipped (word count filter)
```
[5/50] ⏭️  Gutenberg #1661 (8234 words, min=10000)
```
Book is too short. Increase `--min-words` to include it.

## Future Improvements

- [ ] Resume functionality (track which books were loaded)
- [ ] Download multiple books in parallel
- [ ] Support for other metadata sources (RDF catalog)
- [ ] Caching downloaded texts
- [ ] BM25 ranking precomputation
