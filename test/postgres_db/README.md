# 💾 SearchBook - PostgreSQL Data Layer

Cette couche contient la base de données PostgreSQL, les scripts d'ingestion, le calcul Jaccard et PageRank.

## 📋 Structure

```
postgres_db/
├── migrations/
│   └── 001_init_schema.sql       # Schéma complet (tables, indexes, fonctions)
├── tools/
│   ├── import_books.py           # Ingestion + tokenization
│   ├── compute_jaccard.py        # Similarité Jaccard
│   └── compute_pagerank.py       # PageRank sur graphe Jaccard
├── docker-compose.yml            # Orchestration Postgres
├── .env.example                  # Variables d'environnement
├── requirements.txt              # Dépendances Python
└── README.md                     # Ce fichier
```

## 🚀 Démarrage rapide

### 1. Préparer l'environnement

```bash
cd postgres_db
cp .env.example .env
# Adapter .env si nécessaire (USER, PASSWORD, DB_DSN)

# Créer un virtualenv Python
python3 -m venv .venv
source .venv/bin/activate  # Linux/macOS
# ou
python -m venv .venv && .venv\Scripts\activate  # Windows

# Installer les dépendances
pip install -r requirements.txt
```

### 2. Lancer PostgreSQL

```bash
docker-compose up -d
# Vérifier que le conteneur est en bonne santé
docker-compose ps
```

Le serveur PostgreSQL est maintenant accessible sur `localhost:5432`.

### 3. Préparer les données

Placer vos fichiers `.txt` (livres) dans un répertoire, par exemple:
```
datasets/sample_books/
├── book1.txt
├── book2.txt
└── ...
```

### 4. Ingérer les livres

```bash
# Pour les 100 premiers fichiers (test):
python3 tools/import_books.py ../datasets/sample_books --limit 100

# Pour tous les fichiers:
python3 tools/import_books.py ../datasets/sample_books
```

**Résultat attendu**: 
- Table `documents` remplie
- Table `terms` contenant tous les termes uniques
- Table `inverted_index` mappant termes → documents

### 5. Calculer la similarité Jaccard

```bash
# Avec seuil τ=0.05 (par défaut)
python3 tools/compute_jaccard.py --tau 0.05

# Avec un seuil plus strict (ex. τ=0.1)
python3 tools/compute_jaccard.py --tau 0.1
```

**Justification du seuil τ** (à documenter dans le rapport):
- τ trop bas → graphe dense, ralentit les suggestions
- τ trop haut → graphe clairsemé, suggestions moins pertinentes
- Recommandé: 0.05-0.15 pour ~1664 documents

**Résultat attendu**: 
- Table `jaccard_edges` contenant les paires (doc_a, doc_b, jaccard_score)

### 6. Calculer le PageRank

```bash
# Avec paramètres par défaut (α=0.85)
python3 tools/compute_pagerank.py

# Avec facteur d'amortissement personnalisé
python3 tools/compute_pagerank.py --alpha 0.85 --max-iter 100
```

**Résultat attendu**: 
- Table `centrality_scores` remplie avec les scores PageRank
- Affichage des top 10 documents

---

## 📊 Schéma de la base de données

### Tables

| Nom | Description |
|-----|-------------|
| `documents` | Livres (titre, auteur, contenu, word_count) |
| `terms` | Termes uniques tokenisés |
| `inverted_index` | Mappe termes → documents + occurrences |
| `jaccard_edges` | Arêtes du graphe Jaccard (similarité) |
| `centrality_scores` | Scores PageRank pré-calculés |
| `popularity_doc` | Compteur de clics/popularité (optionnel) |

### Indexes

- `idx_terms_term_trgm` : Recherche approximative sur termes (trigram)
- `idx_inverted_index_*` : Accélère les jointures
- `idx_jaccard_edges_*` : Accélère les suggestions
- `idx_centrality_pagerank` : Triage rapide par PageRank

### Fonctions stockées

```sql
-- Recherche simple par terme exact
SELECT * FROM search_by_term('book');

-- Recherche par regex
SELECT * FROM search_by_regex('^th.*ing$');

-- Suggestions (5 voisins Jaccard par défaut)
SELECT * FROM get_suggestions('doc_uuid', p_limit => 10);
```

---

## 📈 Complexité et Performance

### Ingestion (import_books.py)
- **Complexité**: O(n × m) où n=nombre de livres, m=mots moyens/livre
- **Temps estimé**: ~5-10 min pour 1664 livres (10k mots chacun)

### Jaccard (compute_jaccard.py)
- **Complexité**: O(n² × m) pairwise comparison
- **Temps estimé**: ~30-60 min pour 1664 docs (n²/2 ≈ 1.38M paires)
- **Optimisation possible**: MinHash/LSH pour échelles supérieures

### PageRank (compute_pagerank.py)
- **Complexité**: O(e × iter) où e=nombre d'arêtes, iter≈100
- **Temps estimé**: ~1-5 min selon densité graphe

---

## 🔧 Dépannage

### Erreur de connexion DB
```
psycopg2.OperationalError: could not connect to server
```
→ Vérifier que Postgres est lancé: `docker-compose ps`

### Table déjà existante
Les migrations sont idempotentes (`IF NOT EXISTS`). Pour réinitialiser:
```bash
docker-compose down -v
docker-compose up -d
```

### Performance lente sur ingestion
→ Vérifier les indexes et la taille du corpus
→ Augmenter `shared_buffers` dans Postgres si nécessaire

---

## 🔗 Intégration avec le backend FastAPI

Le backend FastAPI interrogera ces tables via psycopg2:

```python
# Exemple endpoint /api/search/simple
def search_simple(query: str, ranking_by: str = "occurrences"):
    # Utiliser search_by_term(query) ou JOIN inverted_index
    # Trier par occurrences ou pagerank_score
    # Retourner JSON avec résultats + suggestions
```

---

## 📚 Références

- **Gutenberg Project**: https://www.gutenberg.org/
- **PostgreSQL**: https://www.postgresql.org/
- **NetworkX PageRank**: https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.pagerank.pagerank.html
- **Jaccard Similarity**: https://en.wikipedia.org/wiki/Jaccard_index

---

## 📝 Notes pour le rapport

Documenter dans le rapport:

1. **Stratégie d'ingestion**:
   - Tokenization: regex + stopwords
   - Extraction métadonnées: 2 premières lignes non vides
   - Lemmatization: non implémentée (amélioration possible)

2. **Choix du seuil Jaccard τ**:
   - Justifier le seuil choisi
   - Impact sur densité graphe et suggestions

3. **Indice de centralité PageRank**:
   - Définition: moyenne pondérée des PR des voisins
   - Calcul: algorithme itératif (α=0.85, ~100 itérations)
   - Résultats: afficher top 10 docs et leur contribution au classement

4. **Tests de performance**:
   - Temps ingestion/Jaccard/PageRank
   - Taille graphe (n nodes, e edges, densité)
   - Temps requêtes recherche (simple vs regex)
