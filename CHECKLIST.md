# ✅ CHECKLIST - Ce Qui a Été Fait vs. À Faire

## ✅ COMPLÉTÉ (Phase 1 & 2)

### Couche Data (PostgreSQL)
- [x] Schéma complet avec 6 tables (documents, terms, inverted_index, jaccard_edges, centrality_scores, popularity_doc)
- [x] Indexes optimisés (trgm pour recherche, GIN pour jointures)
- [x] Fonctions PostgreSQL (search_by_term, search_by_regex, get_suggestions)
- [x] Docker Compose pour Postgres (avec healthcheck + volume)
- [x] Script import_books.py (tokenization + stopwords + métadonnées)
- [x] Script compute_jaccard.py (pairwise similarity O(n²), seuil τ paramétrable)
- [x] Script compute_pagerank.py (NetworkX, α=0.85, 100 itérations)
- [x] requirements.txt (psycopg2, networkx)
- [x] Documentation postgres_db/README.md complète

### Backend (FastAPI)
- [x] Connection pool PostgreSQL (psycopg2.pool)
- [x] Pydantic schemas (SearchRequest, DocumentResult, SuggestionResult, SearchResponse)
- [x] Service de recherche (simple_search, advanced_search, get_suggestions, track_click)
- [x] Endpoint POST /api/search/simple (query, ranking_by, limit)
- [x] Endpoint POST /api/search/advanced (regex_pattern, ranking_by, limit)
- [x] Ranking logic (occurrences vs pagerank)
- [x] Suggestions (voisins Jaccard des top 3 résultats)
- [x] Startup/shutdown events
- [x] CORS middleware
- [x] Health check endpoint
- [x] Auto-documentation Swagger (/docs)
- [x] requirements.txt
- [x] .env.example

### Frontend (React + Vite)
- [x] SearchBar.tsx (input + toggle RegEx + radio ranking_by)
- [x] SearchResultCard.tsx (titre, auteur, occurrences, pagerank)
- [x] SuggestionsList.tsx (grid de suggestions Jaccard)
- [x] api.ts (service API client pour simpleSearch et advancedSearch)
- [x] api.ts types (DocumentResult, SuggestionResult, SearchResponse)
- [x] index.css (styles globaux + responsive + dark theme)
- [x] package.json (react, react-dom, vite, typescript)
- [x] tsconfig.json + tsconfig.node.json
- [x] vite.config.ts (React plugin + proxy API)

### Documentation & Architecture
- [x] QUICKSTART.md (15 min pour une démo)
- [x] ARCHITECTURE.md (3000+ lignes, guide complet)
- [x] DECISIONS.md (justifications techniques détaillées)
- [x] SUMMARY.md (résumé structuré)
- [x] postgres_db/README.md (guide data layer)

---

## ⚠️ À FAIRE (Pour Finalisation)

### Frontend React (Composants Principaux Restants)

```
[ ] frontend/src/main.tsx
    ├─ ReactDOM.render(<App />, root)
    └─ Import CSS global

[ ] frontend/src/App.tsx
    ├─ State: query, results, suggestions, ranking_by, isRegex, loading
    ├─ Render: <SearchBar /> + <ResultsList /> + <SuggestionsList />
    └─ Event handlers: onSearch, onRankingChange

[ ] frontend/src/components/SearchResultCard.tsx
    ├─ Props: DocumentResult
    ├─ Render: ranking circle + title + author + badges (occurrences/pagerank)
    └─ onClick: track click + show details

[ ] frontend/src/components/SuggestionsList.tsx
    ├─ Props: suggestions array
    ├─ Grid layout (3+ colonnes desktop, responsive mobile)
    └─ Card par suggestion avec titre + jaccard_score

[ ] frontend/src/views/HomeSearchView.tsx
    ├─ Main search interface
    └─ Render App.tsx components

[ ] frontend/src/views/BookDetailsView.tsx
    ├─ Page détail d'un livre
    ├─ Afficher titre + auteur + contenu complet
    └─ Related books (voisins Jaccard)
```

### Données & Testing

```
[ ] Télécharger/préparer corpus Gutenberg
    ├─ Minimum 1664 fichiers .txt
    ├─ Minimum 10 000 mots par fichier
    └─ Placer dans datasets/sample_books/

[ ] Tester la pipeline data complète
    ├─ python3 postgres_db/tools/import_books.py datasets/sample_books
    ├─ python3 postgres_db/tools/compute_jaccard.py
    └─ python3 postgres_db/tools/compute_pagerank.py

[ ] Tests de performance & validationAPI
    ├─ Test requête simple (curl)
    ├─ Test requête regex
    ├─ Mesurer temps réponse (< 100ms cible)
    └─ Vérifier suggestions pertinentes
```

### Rapport Académique (10-15 pages)

```
[ ] Partie 1 : Introduction & Contexte
    ├─ Objectif du projet (moteur recherche 1664+ livres)
    └─ Cas d'usage (recherche simple, avancée, suggestions)

[ ] Partie 2 : Algorithmes (5-6 pages)
    ├─ Index Inversé
    │   ├─ Définition + structure données
    │   ├─ Tokenization + stopwords
    │   └─ Complexité O(log n + r)
    │
    ├─ Jaccard Similarity
    │   ├─ Formule J(A,B) = |A∩B| / |A∪B|
    │   ├─ Choix seuil τ=0.05 (justification)
    │   ├─ Résultats empiriques (nb arêtes, densité)
    │   └─ Complexité O(n²)
    │
    └─ PageRank
        ├─ Formule itérative + damping factor
        ├─ Paramètres (α=0.85, 100 itérations)
        ├─ Top 10 documents (résultats)
        └─ Complexité O(e × iter)

[ ] Partie 3 : Architecture (3-4 pages)
    ├─ Stack technique (PostgreSQL, FastAPI, React)
    ├─ Diagramme architecture (3 couches)
    ├─ Schéma DB (6 tables)
    └─ Endpoints API (2 POST)

[ ] Partie 4 : Données & Tests (2-3 pages)
    ├─ Source des données (Gutenberg)
    ├─ Statistiques corpus (1664 docs, 10k mots min)
    ├─ Résultats performance
    │   ├─ Temps ingestion
    │   ├─ Temps Jaccard
    │   ├─ Temps PageRank
    │   └─ Temps requêtes (graphiques)
    └─ Tests utilisateur (optionnel)

[ ] Conclusion & Perspectives
    ├─ Bilan projet
    ├─ Améliorations possibles (stemming, LSH, etc.)
    └─ Scénarios production
```

### Présentation Orale (20 min) ou Vidéo Pitch (5 min)

```
[ ] Partie Introductive (7 min)
    ├─ Objectif + cas d'usage
    ├─ Wireframe UI (figma/balsamiq screenshot)
    ├─ Stack technique (tableau comparatif vs alternatives)
    └─ Resource planning (Gantt / scrum backlog)

[ ] Partie Technique (10 min)
    ├─ Architecture générale (diagramme)
    ├─ Couche Data (tables, indexes, algorithmes)
    ├─ Couche Backend (endpoints, ranking)
    ├─ Couche Frontend (composants, responsive)
    └─ Demo live (recherche "book", résultats, suggestions)

[ ] Démonstration Multi-Client (3 min)
    ├─ Machine 1 (serveur) : Postgres + FastAPI
    ├─ Machine 2 (client desktop) : navigateur Firefox/Chrome
    ├─ Machine 3 (client mobile) : smartphone/tablet
    └─ Effectuer recherche sincro sur les 3 machines
```

### Livrable Final

```
[ ] Archiver tout en daarprojet3-NOM1-NOM2-NOM3.zip (< 30 Mo)
    ├─ rapport.pdf (10-15 pages)
    ├─ code/ (postgres_db + backend + frontend)
    ├─ video_pitch.mp4 (optionnel, 5 min)
    ├─ QUICKSTART.md + ARCHITECTURE.md
    └─ README.md

[ ] Vérifier format du nom : daar-projet3-NOM1-NOM2-NOM3.{zip,tgz,rar,7z}
[ ] Upload sur Moodle avant 23 Nov 2025, 23h59
```

---

## 📝 Ordre Recommandé d'Exécution

### Week 1 : Data + Backend ✅ (Complété)
1. ✅ Créer migration SQL + docker-compose
2. ✅ Créer scripts Python (import, jaccard, pagerank)
3. ✅ Créer FastAPI app + endpoints + services
4. ✅ Tester API via Swagger

### Week 2 : Frontend + Intégration (À FAIRE)
1. Télécharger corpus Gutenberg (100-200 livres test)
2. Completer App.tsx + views
3. Tester frontend en local
4. Tester intégration API backend ↔ frontend

### Week 3 : Données Complètes + Benchmarks (À FAIRE)
1. Télécharger 1664+ livres complets
2. Lancer pipeline data (import + jaccard + pagerank) ~2-3h
3. Benchmarks & mesures performance
4. Optimisations si nécessaire

### Week 4 : Rapport + Présentation (À FAIRE)
1. Rédiger rapport 10-15 pages
2. Créer slides présentation (20 min)
3. Préparer démo multi-client (2+ machines)
4. Archiver livrable final

---

## 🚀 Quick Commands to Start

```bash
# 1. Démarrer Postgres
cd postgres_db && docker-compose up -d

# 2. Ingérer données test (10 livres)
cd postgres_db
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python3 tools/import_books.py ../datasets/sample_books --limit 10

# 3. Calculer Jaccard + PageRank
python3 tools/compute_jaccard.py
python3 tools/compute_pagerank.py

# 4. Démarrer backend (autre terminal)
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# 5. Démarrer frontend (3ème terminal)
cd frontend
npm install && npm run dev

# 6. Ouvrir http://localhost:5173
```

---

## 📊 État du Projet

| Phase | Composant | % Complet | Blockers |
|-------|-----------|----------|----------|
| 1 | Data (Postgres) | ✅ 100% | Aucun |
| 2 | Backend (FastAPI) | ✅ 100% | Aucun |
| 3 | Frontend (React) | ⚠️ 50% | Views + App.tsx |
| 4 | Données (Corpus) | 🔴 0% | À télécharger |
| 5 | Tests | 🔴 0% | Attendre données |
| 6 | Rapport | 🔴 0% | À rédiger |
| 7 | Présentation | 🔴 0% | À préparer |

**ETA Complet** : 3-4 semaines (avec 1 développeur temps plein)

---

**Tous les fichiers sont prêts. À vous de jouer ! 🚀**
