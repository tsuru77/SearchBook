#!/usr/bin/env python3
"""
Calcule le PageRank sur le graphe de Jaccard.
Utilise networkx pour l'algorithme et stocke les résultats dans centrality_scores.
"""
import os
import sys
import psycopg2
import networkx as nx
import argparse

DB_DSN = os.environ.get("DB_DSN", "postgresql://searchbook:searchbookpass@localhost:5432/searchbook")

def build_graph_from_db(cur):
    """Construit un graphe NetworkX à partir des jaccard_edges."""
    cur.execute("SELECT doc_a, doc_b, jaccard_score FROM jaccard_edges")
    G = nx.Graph()
    
    for doc_a, doc_b, weight in cur:
        G.add_edge(str(doc_a), str(doc_b), weight=float(weight))
    
    return G

def compute_and_store_pagerank(alpha=0.85, max_iter=100):
    """
    Calcule PageRank avec paramètre d'amortissement alpha.
    Stocke les résultats dans centrality_scores.
    """
    try:
        with psycopg2.connect(DB_DSN) as conn:
            with conn.cursor() as cur:
                print("🔗 Construction du graphe à partir des jaccard_edges...")
                G = build_graph_from_db(cur)
                
                if G.number_of_nodes() == 0:
                    print("❌ Graphe vide. Avez-vous exécuté compute_jaccard.py ?")
                    return
                
                print(f"📈 Graphe: {G.number_of_nodes()} nœuds, {G.number_of_edges()} arêtes")
                
                print(f"⚙️  Calcul du PageRank (α={alpha}, max_iter={max_iter})...")
                pr = nx.pagerank(G, alpha=alpha, max_iter=max_iter, weight='weight')
                
                print(f"💾 Stockage des résultats dans centrality_scores...")
                
                # Clear existing scores
                cur.execute("TRUNCATE centrality_scores")
                
                # Insert new scores
                for doc_id, score in pr.items():
                    cur.execute("""
                        INSERT INTO centrality_scores (doc_id, pagerank_score)
                        VALUES (%s, %s)
                    """, (doc_id, float(score)))
                
                conn.commit()
                
                # Afficher quelques top documents
                top_docs = sorted(pr.items(), key=lambda x: x[1], reverse=True)[:10]
                print(f"\n🏆 Top 10 documents par PageRank:")
                
                cur.execute("""
                    SELECT id, title FROM documents WHERE id = ANY(%s)
                """, ([d[0] for d in top_docs],))
                doc_titles = {row[0]: row[1] for row in cur.fetchall()}
                
                for doc_id, score in top_docs:
                    title = doc_titles.get(doc_id, "Unknown")[:50]
                    print(f"   {title:<50} | PR={score:.6f}")
                
                print(f"\n✅ PageRank terminé ! {len(pr)} documents avec scores calculés")
    
    except Exception as e:
        print(f"❌ Erreur: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Calcule le PageRank sur le graphe de Jaccard et stocke les résultats."
    )
    parser.add_argument("--alpha", type=float, default=0.85,
                        help="Facteur d'amortissement (défaut: 0.85)")
    parser.add_argument("--max-iter", type=int, default=100,
                        help="Nombre maximal d'itérations (défaut: 100)")
    
    args = parser.parse_args()
    compute_and_store_pagerank(args.alpha, args.max_iter)
