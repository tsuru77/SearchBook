# 📚 SearchBook - Moteur de Recherche pour Bibliothèque

Une application **web/mobile** complète pour la recherche et la suggestion de livres basée sur :
- **Index Inversé** : tokenisation + recherche par mot-clé et RegEx
- **Graphe de Jaccard** : similarité entre documents
- **PageRank** : classement des résultats par importance
- **Stack Moderne** : PostgreSQL + FastAPI + React/Vite

---

## 📋 Architecture Globale

```
SearchBook/
│
├── postgres_db/                  ⭐ COUCHE DATA
│   ├── migrations/001_init_schema.sql
│   ├── tools/
│   │   ├── import_books.py       (Ingestion + tokenization)
│   │   ├── compute_jaccard.py    (Similarité Jaccard)
│   │   └── compute_pagerank.py   (PageRank)
│   ├── docker-compose.yml
│   ├── requirements.txt
│   └── README.md
│
├── backend/                       ⭐ COUCHE SERVEUR
│   ├── app/
│   │   ├── main.py               (FastAPI app + startup)
│   │   ├── db/__init__.py        (Pool de connexions)
│   │   ├── models/schemas.py     (Pydantic schemas)
│   │   ├── services/search_service.py  (Logique métier)
│   │   └── api/routes/search.py  (Endpoints POST)
│   ├── requirements.txt
│   ├── .env.example
│   └── Dockerfile (optionnel)
│
├── frontend/                      ⭐ COUCHE CLIENT
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── components/
│   │   │   ├── SearchBar.tsx     (Barre de recherche)
│   │   │   ├── SearchResultCard.tsx
│   │   │   └── SuggestionsList.tsx
│   │   ├── lib/api.ts            (Service API client)
│   │   ├── types/api.ts          (Types TypeScript)
│   │   ├── index.css             (Styles globaux)
│   │   └── views/
│   │       ├── HomeSearchView.tsx
│   │       └── BookDetailsView.tsx
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── Dockerfile (optionnel)
│
└── README.md (ce fichier)
```

---

## 🚀 Démarrage Complet (5 étapes)

### 1️⃣ **Lancer PostgreSQL**

```bash
cd postgres_db
docker-compose up -d
# Vérifier: docker-compose ps
```

### 2️⃣ **Ingérer les Livres**

```bash
# Créer un virtualenv
cd postgres_db
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Placer les fichiers .txt dans ../datasets/sample_books/
# Puis lancer l'ingestion
python3 tools/import_books.py ../datasets/sample_books --limit 100  # Test
python3 tools/import_books.py ../datasets/sample_books              # Complet (1664+)
```

### 3️⃣ **Calculer Jaccard et PageRank**

```bash
# Toujours dans postgres_db/.venv
python3 tools/compute_jaccard.py --tau 0.05
python3 tools/compute_pagerank.py --alpha 0.85
```

### 4️⃣ **Lancer le Backend FastAPI**

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

# Démarrer le serveur (http://localhost:8000)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5️⃣ **Lancer le Frontend React**

```bash
cd frontend
npm install
npm run dev
# Accédez à http://localhost:5173
```

---

## 📊 Fonctionnalités Implémentées

### ✅ Phase 1 : Couche Data (Obligatoire)

| Tâche | Description | Fichiers |
|-------|-------------|----------|
| **1.1 Indexation** | Index inversé + tokenization | `postgres_db/migrations/001_init_schema.sql`, `tools/import_books.py` |
| **1.2 Jaccard** | Graphe de similarité | `tools/compute_jaccard.py` |
| **1.3 Centralité** | PageRank (choix retenu) | `tools/compute_pagerank.py` |

### ✅ Phase 2 : Backend (Obligatoire)

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/search/simple` | POST | Recherche par mot-clé |
| `/api/search/advanced` | POST | Recherche par RegEx |
| (Implicit) Ranking | - | Tri par occurrences ou PageRank |
| (Implicit) Suggestions | - | Voisins Jaccard des top résultats |

### ✅ Phase 3 : Frontend (Obligatoire)

| Composant | Description |
|-----------|-------------|
| SearchBar | Champ de saisie + toggle RegEx + sélection critère tri |
| SearchResultCard | Affichage titre/auteur/occurrences/PageRank avec badge |
| SuggestionsList | Suggestions sous forme de grille (voisins Jaccard) |

---

## 📡 Exemples d'Utilisation API

### Recherche Simple

```bash
curl -X POST http://localhost:8000/api/search/simple \
  -H "Content-Type: application/json" \
  -d '{
    "query": "book",
    "ranking_by": "occurrences",
    "limit": 20
  }'
```

**Réponse** :
```json
{
  "query": "book",
  "ranking_by": "occurrences",
  "total_results": 150,
  "results": [
    {
      "doc_id": "uuid-1",
      "title": "Les Misérables",
      "author": "Victor Hugo",
      "word_count": 545000,
      "occurrences": 245,
      "pagerank_score": 0.0045,
      "ranking_position": 1
    },
    ...
  ],
  "suggestions": [
    {
      "doc_id": "uuid-2",
      "title": "Notre-Dame de Paris",
      "author": "Victor Hugo",
      "jaccard_score": 0.142
    },
    ...
  ],
  "execution_time_ms": 45.3
}
```

### Recherche Avancée (RegEx)

```bash
curl -X POST "http://localhost:8000/api/search/advanced?regex_pattern=^th.*ing&ranking_by=pagerank&limit=20"
```

---

## 🗄️ Schéma PostgreSQL (Clés)

| Table | Colonnes |
|-------|----------|
| `documents` | id (uuid), title, author, content, word_count |
| `terms` | id (bigserial), term (unique) |
| `inverted_index` | (term_id, doc_id, occurrences) |
| `jaccard_edges` | (doc_a, doc_b, jaccard_score) |
| `centrality_scores` | (doc_id, pagerank_score) |
| `popularity_doc` | (doc_id, clicks) |

### Indexes
- `idx_terms_term_trgm` : Recherche approximative (trigram)
- `idx_inverted_index_*` : Jointures rapides
- `idx_centrality_pagerank` : Tri PageRank O(1)

---

## ⚙️ Configuration

### Variables d'Environnement

**postgres_db/.env** :
```bash
POSTGRES_USER=searchbook
POSTGRES_PASSWORD=searchbookpass
POSTGRES_DB=searchbook
DB_DSN=postgresql://searchbook:searchbookpass@localhost:5432/searchbook
```

**backend/.env** :
```bash
DB_DSN=postgresql://searchbook:searchbookpass@localhost:5432/searchbook
```

**frontend/.env** (optionnel) :
```bash
VITE_API_URL=http://localhost:8000
```

---

## 📈 Performance & Complexité

### Ingestion
- **Complexité** : O(n × m) où n=docs, m=mots/doc
- **Temps** : ~5-10 min pour 1664 livres

### Jaccard
- **Complexité** : O(n² × m) pairwise
- **Temps** : ~30-60 min pour 1664 docs
- **Optimisation** : MinHash/LSH pour > 10k docs

### PageRank
- **Complexité** : O(e × iter) où e=arêtes
- **Temps** : ~1-5 min

### Requête de Recherche
- **Simple** : O(log n) lookup term + O(r) résultats
- **Regex** : O(t) où t=nombre de termes
- **Temps** : < 100ms (avec indexes)

---

## 🧪 Tests

### Test unitaire des scripts data

```bash
cd postgres_db
python3 -m pytest tests/ -v
```

### Test de load du frontend

Ouvrir plusieurs onglets/appareils et effectuer des recherches simultanées.

### Benchmark API

```bash
# Avec Apache Bench
ab -n 100 -c 10 -p query.json http://localhost:8000/api/search/simple
```

---

## 📝 Pour le Rapport

### Sections à Documenter

1. **Algorithmes** :
   - Index Inversé : définition, structure de données, complexité
   - Tokenization : regex + stopwords + nettoyage
   - Jaccard : définition, seuil τ justifié
   - PageRank : formule itérative, α=0.85, convergence

2. **Data** :
   - Source : Gutenberg (ou autre), nombre de docs, taille corpus
   - Métadonnées : extraction titre/auteur
   - Nettoyage : stopwords français/anglais, min length=3

3. **Tests** :
   - Temps ingestion/Jaccard/PageRank (graphiques)
   - Temps requêtes par taille résultats
   - Temps PageRank en fonction du nombre d'arêtes

4. **Indice Jaccard** :
   - Justifier le seuil τ=0.05
   - Exemple de paire : doc_a (termes={...}), doc_b (termes={...})
   - Calcul : |intersection| / |union| = ...
   - Résultats : densité graphe, nombre d'arêtes

---

## 🎤 Pour la Présentation (20 min)

### Partie Introductive (7 min)
- Objectif : moteur de recherche pour 1664+ livres
- Cas d'usage : recherche simple, avancée, suggestions
- Wireframe : barre recherche → résultats → suggestions
- Stack : PostgreSQL + FastAPI + React (justifié vs Elasticsearch)

### Partie Technique (10 min)
- Architecture : Data → Backend → Frontend
- Index Inversé : tables terms + inverted_index
- Jaccard : graphe de similarité (seuil τ)
- PageRank : scores centrality
- Endpoints : /api/search/{simple,advanced}
- React : composants SearchBar, Results, Suggestions

### Démo (3 min)
- 🖥️ Machine serveur : Postgres + FastAPI
- 📱 Machine client 1 : navigateur (recherche "book")
- 📱 Machine client 2 : smartphone (même recherche, suggestions différentes)
- Vérifier : résultats synchronisés, temps de réponse

---

## 🐛 Troubleshooting

### Postgres ne démarre pas
```bash
docker-compose down -v
docker-compose up -d
```

### Recherche vide
- Vérifier : `SELECT COUNT(*) FROM documents;`
- Relancer : `python3 tools/import_books.py ...`

### Backend erreur 500
- Vérifier : `DB_DSN` correct dans `.env`
- Logs : `docker logs searchbook_postgres`

### Frontend affiche "API down"
- Vérifier : backend lancé sur port 8000
- CORS : `add_middleware(CORSMiddleware, allow_origins=["*"])`

---

## 📚 Ressources

- **PostgreSQL** : https://www.postgresql.org/
- **FastAPI** : https://fastapi.tiangolo.com/
- **React** : https://react.dev/
- **Vite** : https://vitejs.dev/
- **NetworkX PageRank** : https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.pagerank.pagerank.html
- **Gutenberg Project** : https://www.gutenberg.org/

---

## 📦 Livrable Final

Archivez :
```
daar-projet3-NOM1-NOM2-NOM3.zip
├── rapport.pdf                   (10-15 pages)
├── code/
│   ├── postgres_db/
│   ├── backend/
│   └── frontend/
├── video_pitch.mp4              (optionnel, 5 min)
└── README.md                     (ce fichier)
```

**Format** : 30 Mo max.

**Deadline** : 23 Nov 2025, 23h59.

---

## ✨ Équipe

À remplir avec les noms et emails des contributeurs.

---

**Dernière mise à jour** : 28 novembre 2025
