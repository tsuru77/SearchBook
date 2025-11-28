#!/usr/bin/env python3
"""
Calcule la similarité de Jaccard entre toutes les paires de documents.
Stocke les arêtes dans la table jaccard_edges (seuil tau configurable).
"""
import os
import sys
import psycopg2
from collections import defaultdict
import argparse
from itertools import combinations

DB_DSN = os.environ.get("DB_DSN", "postgresql://searchbook:searchbookpass@localhost:5432/searchbook")

def load_doc_terms(cur):
    """Charge pour chaque document la liste de ses termes.
    
    Directement depuis inverted_index (plus besoin de JOIN terms).
    """
    cur.execute("""
        SELECT ii.doc_id, array_agg(ii.term) AS terms
        FROM inverted_index ii
        GROUP BY ii.doc_id
    """)
    return {row[0]: set(row[1]) for row in cur.fetchall()}

def compute_and_store_jaccard(tau=0.05):
    """
    Calcule Jaccard(Di, Dj) = |Di ∩ Dj| / |Di ∪ Dj|
    Stocke les arêtes si Jaccard(Di, Dj) >= tau.
    """
    try:
        with psycopg2.connect(DB_DSN) as conn:
            with conn.cursor() as cur:
                print("📊 Chargement des documents et termes...")
                docs_terms = load_doc_terms(cur)
                doc_ids = sorted(docs_terms.keys())
                n = len(doc_ids)
                
                if n == 0:
                    print("❌ Aucun document trouvé dans la base de données.")
                    return
                
                print(f"📈 Calcul de Jaccard pour {n} documents (seuil τ={tau})")
                print(f"   Nombre de paires à calculer: {n * (n - 1) // 2}")
                
                edges_count = 0
                
                # Calcul pairwise (O(n²) mais acceptable pour ~1664 docs)
                for i in range(n):
                    for j in range(i + 1, n):
                        di, dj = doc_ids[i], doc_ids[j]
                        ti, tj = docs_terms[di], docs_terms[dj]
                        
                        # Jaccard = |intersection| / |union|
                        intersection = len(ti & tj)
                        if intersection == 0:
                            continue
                        
                        union = len(ti | tj)
                        jscore = intersection / union
                        
                        # Insérer seulement si >= seuil
                        if jscore >= tau:
                            cur.execute("""
                                INSERT INTO jaccard_edges (doc_a, doc_b, jaccard_score)
                                VALUES (%s, %s, %s)
                                ON CONFLICT (doc_a, doc_b) DO UPDATE SET jaccard_score = EXCLUDED.jaccard_score
                            """, (str(di), str(dj), float(jscore)))
                            edges_count += 1
                    
                    if (i + 1) % max(1, n // 10) == 0:
                        print(f"   ... {i + 1}/{n} documents traités")
                
                conn.commit()
                print(f"\n✅ Jaccard terminé ! {edges_count} arêtes créées (τ={tau})")
    
    except Exception as e:
        print(f"❌ Erreur: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Calcule la similarité de Jaccard et crée le graphe de similarité."
    )
    parser.add_argument("--tau", type=float, default=0.05,
                        help="Seuil de similarité Jaccard (défaut: 0.05)")
    
    args = parser.parse_args()
    compute_and_store_jaccard(args.tau)
