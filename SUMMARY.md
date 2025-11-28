📚 SearchBook - Résumé Complet de la Structure

================================================================================
FICHIERS CRÉÉS (COUCHE DATA)
================================================================================

postgres_db/
├── migrations/
│   └── 001_init_schema.sql              ✅ Schéma complet
│       ├─ CREATE TABLE documents
│       ├─ CREATE TABLE terms
│       ├─ CREATE TABLE inverted_index
│       ├─ CREATE TABLE jaccard_edges
│       ├─ CREATE TABLE centrality_scores
│       ├─ CREATE TABLE popularity_doc
│       ├─ CREATE INDEX (optimisations)
│       └─ CREATE FUNCTION (recherche, suggestions)
│
├── tools/
│   ├── import_books.py                  ✅ Ingestion + tokenization
│   │   ├─ Tokenize + stopwords
│   │   ├─ Extract metadata (titre, auteur)
│   │   └─ Populate documents, terms, inverted_index
│   │
│   ├── compute_jaccard.py               ✅ Similarité Jaccard
│   │   ├─ O(n²) pairwise comparison
│   │   ├─ Seuil τ paramétrable (défaut 0.05)
│   │   └─ Populate jaccard_edges
│   │
│   └── compute_pagerank.py              ✅ PageRank
│       ├─ Build graph from jaccard_edges
│       ├─ NetworkX pagerank algorithm
│       ├─ α=0.85, max_iter=100
│       └─ Populate centrality_scores
│
├── docker-compose.yml                   ✅ Postgres + volume + healthcheck
├── .env.example                         ✅ Variables DB
├── requirements.txt                     ✅ psycopg2, networkx
└── README.md                            ✅ Guide complet d'utilisation

================================================================================
FICHIERS CRÉÉS (BACKEND FASTAPI)
================================================================================

backend/
├── app/
│   ├── __init__.py                      ✅ Package init
│   │
│   ├── main.py                          ✅ FastAPI app + startup/shutdown
│   │   ├─ Initialize pool on startup
│   │   ├─ CORS middleware
│   │   └─ Health check endpoint
│   │
│   ├── db/
│   │   └── __init__.py                  ✅ Connection pool management
│   │       ├─ initialize_pool()
│   │       ├─ close_pool()
│   │       └─ get_db_cursor() context manager
│   │
│   ├── models/
│   │   ├── __init__.py                  ✅ Package init
│   │   └── schemas.py                   ✅ Pydantic schemas
│   │       ├─ SearchRequest
│   │       ├─ AdvancedSearchRequest
│   │       ├─ DocumentResult
│   │       ├─ SuggestionResult
│   │       ├─ SearchResponse
│   │       └─ ErrorResponse
│   │
│   ├── services/
│   │   ├── __init__.py                  ✅ Package init
│   │   └── search_service.py            ✅ Business logic
│   │       ├─ simple_search(query, ranking_by, limit)
│   │       ├─ advanced_search(regex, ranking_by, limit)
│   │       ├─ get_suggestions(doc_ids, limit, use_popularity)
│   │       └─ track_click(doc_id)
│   │
│   ├── api/
│   │   ├── __init__.py                  ✅ Package init
│   │   └── routes/
│   │       ├── __init__.py              ✅ Package init
│   │       └── search.py                ✅ Endpoints
│   │           ├─ POST /api/search/simple
│   │           └─ POST /api/search/advanced
│   │
├── requirements.txt                     ✅ fastapi, uvicorn, pydantic, psycopg2
├── .env.example                         ✅ DB_DSN example
└── Dockerfile (optionnel)

================================================================================
FICHIERS CRÉÉS (FRONTEND REACT)
================================================================================

frontend/
├── src/
│   ├── components/
│   │   ├── SearchBar.tsx                ✅ Barre recherche + toggle RegEx
│   │   │   ├─ Input field
│   │   │   ├─ Checkbox mode RegEx
│   │   │   └─ Radio buttons ranking_by (occurrences/pagerank)
│   │   │
│   │   ├── SearchResultCard.tsx         ✅ Résultat unique (à compléter)
│   │   │   ├─ Title, author
│   │   │   ├─ Occurrences badge
│   │   │   ├─ PageRank score
│   │   │   └─ Ranking position circle
│   │   │
│   │   └── SuggestionsList.tsx          ✅ Liste suggestions (à compléter)
│   │       └─ Grid de cartes suggestion
│   │
│   ├── lib/
│   │   └── api.ts                       ✅ Service API client
│   │       ├─ simpleSearch()
│   │       └─ advancedSearch()
│   │
│   ├── types/
│   │   └── api.ts                       ✅ TypeScript types
│   │       ├─ DocumentResult
│   │       ├─ SuggestionResult
│   │       ├─ SearchResponse
│   │       └─ RankingType
│   │
│   ├── index.css                        ✅ Styles globaux + responsive
│   │
│   └── views/
│       ├── HomeSearchView.tsx           (à créer)
│       └── BookDetailsView.tsx          (à créer)
│
├── package.json                         ✅ react, react-dom, vite, typescript
├── tsconfig.json                        ✅ Config TS
├── tsconfig.node.json                   ✅ Config TS pour Vite
├── vite.config.ts                       ✅ Vite + React plugin + proxy API
└── Dockerfile (optionnel)

================================================================================
DOCUMENTATION
================================================================================

📄 QUICKSTART.md                         ✅ 15 min pour une démo
📄 ARCHITECTURE.md                       ✅ Architecture + guide complet (3k lignes)
📄 DECISIONS.md                          ✅ Justifications des choix tech
📄 postgres_db/README.md                 ✅ Guide Data layer + troubleshooting

================================================================================
PROCHAINES ÉTAPES (À COMPLÉTER)
================================================================================

Frontend à compléter:
  ☐ App.tsx (composant principal)
  ☐ SearchResultCard.tsx (rendu résultat)
  ☐ SuggestionsList.tsx (rendu suggestions)
  ☐ HomeSearchView.tsx (page accueil)
  ☐ BookDetailsView.tsx (page détail)
  ☐ main.tsx (entry point React)

Tests & validation:
  ☐ Télécharger 10-100 livres Gutenberg
  ☐ Exécuter import_books.py
  ☐ Exécuter compute_jaccard.py
  ☐ Exécuter compute_pagerank.py
  ☐ Lancer backend + frontend
  ☐ Tester recherches (simple + regex)
  ☐ Vérifier suggestions

Rapport & présentation:
  ☐ Écrire rapport 10-15 pages
  ☐ Créer slides présentation (20 min)
  ☐ Préparer démo multi-client
  ☐ Archiver en daar-projet3-NOM1-NOM2-NOM3.zip

================================================================================
COMMANDES RAPIDES
================================================================================

# Démarrer PostgreSQL
cd postgres_db && docker-compose up -d

# Ingérer livres
python3 postgres_db/tools/import_books.py datasets/sample_books --limit 100

# Calculer Jaccard
python3 postgres_db/tools/compute_jaccard.py --tau 0.05

# Calculer PageRank
python3 postgres_db/tools/compute_pagerank.py

# Démarrer backend
cd backend && pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Démarrer frontend
cd frontend && npm install && npm run dev

# Tester API
curl -X POST http://localhost:8000/api/search/simple \
  -H "Content-Type: application/json" \
  -d '{"query":"the","ranking_by":"occurrences","limit":10}'

================================================================================
RÉSUMÉ DES FONCTIONNALITÉS
================================================================================

✅ Phase 1 - Data :
  ✓ Index inversé (terms + inverted_index)
  ✓ Tokenization + stopwords
  ✓ Jaccard similarity (τ=0.05)
  ✓ PageRank (α=0.85)

✅ Phase 2 - Backend :
  ✓ POST /api/search/simple
  ✓ POST /api/search/advanced (regex)
  ✓ Ranking by occurrences ou pagerank
  ✓ Suggestions (voisins Jaccard)

⚠️  Phase 3 - Frontend :
  ~ 50% complet (composants créés, views à faire)
  ~ Styles CSS complets et responsive
  ~ TypeScript types et API client

================================================================================
ESTIMATIONS DE TEMPS TOTAL
================================================================================

Development:
  Data layer: ✅ 2h (migration + scripts + docker)
  Backend: ✅ 2h (API + services)
  Frontend: ⚠️  4-6h (composants + views + intégration)
  Testing & docs: ⚠️  3-4h

Data ingestion & processing:
  Télécharger 1664 livres: ~30 min
  Import livres: ~10 min
  Jaccard: ~45-75 min (O(n²))
  PageRank: ~2-5 min
  Total: ~2-3 heures (une fois lancé, pas de supervision)

Report & presentation:
  Rapport (10-15 pages): ~8h
  Slides présentation (20 min): ~4h
  Démo multi-client: ~1h

TOTAL PROJET: ~30-35 heures team

================================================================================
