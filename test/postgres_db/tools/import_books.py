#!/usr/bin/env python3
"""
Script d'ingestion de livres dans PostgreSQL.
Tokenize le contenu, extrait métadonnées et remplit les tables:
- documents
- terms
- inverted_index
"""
import os
import re
import sys
import glob
import psycopg2
from collections import Counter
import argparse

# Configuration
DB_DSN = os.environ.get("DB_DSN", "postgresql://searchbook:searchbookpass@localhost:5432/searchbook")

# Stopwords français + anglais
STOPWORDS = set("""
a about above after again against all am an and any are aren't as at be because been before
being below between both but by can't could couldn't did didn't do does doesn't doing don't
down during each few for from further had hadn't has hasn't have haven't having he he'd he'll
he's her here here's hers herself him himself his how how's i i'd i'll i'm i've if in into
is isn't it it's its itself let's me more most mustn't my myself no nor not of off on once only
or other ought our ours ourselves out over own same shan't she she'd she'll she's should shouldn't
so some such than that that's the their theirs them themselves then there there's these they
they'd they'll they'm they're they've this those through to too under until up very was wasn't
we we'd we'll we're we've were weren't what what's when when's where where's which while who
who's whom why why's will with won't would wouldn't you you'd you'll you're you've your yours
yourself yourselves
le la les un une des du de et en à a être est sont dans que qui ne pas sur pour par avec se sa son
""".split())

# Tokenization regex: extraire mots (pas de chiffres, pas de ponctuation)
TOKEN_RE = re.compile(r"\b[^\W\d_]+\b", re.UNICODE)

def tokenize(text):
    """Tokenize, normalise et nettoie le texte."""
    toks = [t.lower() for t in TOKEN_RE.findall(text)]
    # Filtre: supprime stopwords et mots courts
    toks = [t for t in toks if t not in STOPWORDS and len(t) > 2]
    return toks

def insert_document(cur, filename, title, author, content):
    """Insère un document et retourne son ID."""
    cur.execute(
        """INSERT INTO documents (filename, title, author, word_count, content)
           VALUES (%s, %s, %s, %s, %s)
           RETURNING id""",
        (filename, title, author, len(content.split()), content)
    )
    return cur.fetchone()[0]

def insert_inverted_index(cur, doc_id, term_counts):
    """Insère les entrées de l'index inversé pour un document.
    
    Avec term TEXT en PRIMARY KEY, pas besoin de lookup dans une table terms séparée.
    On insère directement (term, doc_id, occurrences).
    """
    for term, count in term_counts.items():
        cur.execute(
            """INSERT INTO inverted_index (term, doc_id, occurrences)
               VALUES (%s, %s, %s)
               ON CONFLICT (term, doc_id) DO UPDATE SET occurrences = EXCLUDED.occurrences""",
            (term, doc_id, count)
        )

def ingest_directory(corpus_dir, limit=None):
    """Ingère tous les fichiers .txt d'un répertoire."""
    files = sorted(glob.glob(os.path.join(corpus_dir, "*.txt")))
    if limit:
        files = files[:limit]
    
    if not files:
        print(f"❌ Aucun fichier .txt trouvé dans {corpus_dir}")
        return
    
    print(f"📚 Ingestion de {len(files)} fichier(s) depuis {corpus_dir}")
    
    try:
        with psycopg2.connect(DB_DSN) as conn:
            with conn.cursor() as cur:
                for idx, filepath in enumerate(files, 1):
                    try:
                        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                            content = f.read()
                        
                        # Extraction basique des métadonnées (2 premières lignes non vides)
                        lines = [L.strip() for L in content.splitlines() if L.strip()]
                        title = lines[0] if lines else os.path.basename(filepath)
                        author = lines[1] if len(lines) > 1 else "Unknown"
                        
                        # Insérer le document
                        doc_id = insert_document(cur, os.path.basename(filepath), title, author, content)
                        
                        # Tokenize et compter les occurrences
                        tokens = tokenize(content)
                        term_counts = dict(Counter(tokens))
                        
                        # Insérer l'index inversé (plus besoin de ensure_terms_exist)
                        insert_inverted_index(cur, doc_id, term_counts)
                        
                        conn.commit()
                        print(f"  ✓ [{idx}/{len(files)}] {title[:50]:<50} | {len(term_counts)} termes uniques")
                    
                    except Exception as e:
                        conn.rollback()
                        print(f"  ❌ [{idx}/{len(files)}] Erreur avec {filepath}: {e}")
                        continue
            
            print(f"\n✅ Ingestion terminée !")
    
    except Exception as e:
        print(f"❌ Erreur de connexion DB: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Ingère des fichiers texte dans la base PostgreSQL et crée l'index inversé."
    )
    parser.add_argument("corpus_dir", help="Chemin du répertoire contenant les fichiers .txt")
    parser.add_argument("--limit", type=int, default=None, help="Limite le nombre de fichiers à ingérer")
    
    args = parser.parse_args()
    
    if not os.path.isdir(args.corpus_dir):
        print(f"❌ Répertoire non trouvé: {args.corpus_dir}")
        sys.exit(1)
    
    ingest_directory(args.corpus_dir, args.limit)
