# ⚡ QUICKSTART - SearchBook en 15 minutes

Suivez ces étapes simples pour avoir une démo fonctionnelle.

## 🎯 Objectif Final

À la fin, vous aurez :
- PostgreSQL remplie avec des livres
- Backend FastAPI qui répond aux requêtes de recherche
- Frontend React qui affiche les résultats et suggestions

## ⏱️ Chronologie (15-20 min total)

### 1. Lancer PostgreSQL (2 min)

```bash
cd postgres_db
docker-compose up -d
sleep 5  # Attendre que Postgres initialise
docker-compose ps  # Vérifier que 'postgres' est 'Up'
```

✅ PostgreSQL écoute sur `localhost:5432`

### 2. Préparer Python et Ingérer les Données (5 min)

```bash
cd postgres_db

# Créer virtualenv
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou: .venv\Scripts\activate  # Windows

# Installer dépendances
pip install -r requirements.txt

# Télécharger/placer des livres dans ../datasets/sample_books/
# Pour le test rapide: téléchargez juste 5-10 fichiers .txt depuis:
# https://www.gutenberg.org/cache/epub/

# Lancer ingestion (start with 10 files for speed)
python3 tools/import_books.py ../datasets/sample_books --limit 10
# Ou complet:
# python3 tools/import_books.py ../datasets/sample_books
```

✅ Les livres sont indexés dans `documents`, `terms`, `inverted_index`

### 3. Calculer Jaccard et PageRank (5-10 min)

```bash
# Toujours dans postgres_db/.venv

# Jaccard (3-5 min pour 10 docs)
python3 tools/compute_jaccard.py --tau 0.05

# PageRank (1 min)
python3 tools/compute_pagerank.py
```

✅ Tables `jaccard_edges` et `centrality_scores` remplies

### 4. Lancer le Backend FastAPI (2 min)

```bash
cd ../../backend  # Retour à la racine, puis dans backend

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

# Démarrer (écoute sur http://localhost:8000)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

✅ Docs API disponible sur http://localhost:8000/docs

### 5. Lancer le Frontend React (2 min)

**Dans un autre terminal** :

```bash
cd frontend

npm install
npm run dev
```

✅ Accédez à http://localhost:5173

---

## 🧪 Test Rapide

### Via Swagger (http://localhost:8000/docs)

1. Allez sur http://localhost:8000/docs
2. Cliquez sur `POST /api/search/simple`
3. Essayez avec `{"query": "the", "ranking_by": "occurrences", "limit": 10}`
4. Cliquez **Execute**

Vous devez voir une réponse JSON avec les résultats.

### Via le Frontend

1. Ouvrez http://localhost:5173
2. Tapez un mot dans la barre de recherche (ex: "the")
3. Cliquez **Chercher**
4. Voyez les résultats et suggestions

---

## 📊 Vérifier que tout marche

```bash
# Terminal 1: Postgres
cd postgres_db && docker-compose ps
# Doit afficher: postgres | Up

# Terminal 2: Backend logs
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
# Doit afficher: Uvicorn running on http://0.0.0.0:8000

# Terminal 3: Frontend logs
npm run dev
# Doit afficher: VITE v... Local: http://localhost:5173

# Terminal 4: Test une requête
curl -X POST http://localhost:8000/api/search/simple \
  -H "Content-Type: application/json" \
  -d '{"query":"the","ranking_by":"occurrences","limit":10}'
```

✅ Tous les services répondent

---

## 🎬 Prochaines Étapes

### Ingérer plus de livres

```bash
# Télécharger ~100 livres depuis Gutenberg
# Puis:
python3 postgres_db/tools/import_books.py datasets/sample_books

# Recalculer Jaccard et PageRank
python3 postgres_db/tools/compute_jaccard.py
python3 postgres_db/tools/compute_pagerank.py
```

### Développer le Frontend

Ajouter :
- Page détail d'un livre
- Historique de recherche
- Filtres avancés
- Design responsive

### Tests de Performance

```bash
# Benchmark simple search (100 requêtes, 10 parallèles)
ab -n 100 -c 10 -p query.json http://localhost:8000/api/search/simple
```

### Multi-client Demo

Ouvrir le frontend sur 2 navigateurs/appareils différents et effectuer des recherches simultanées.

---

## ❌ Si quelque chose ne marche pas

### Postgres ne démarre pas
```bash
cd postgres_db
docker-compose down -v
docker-compose up -d
```

### Import échoue
```bash
# Vérifier la variable DB_DSN
echo $DB_DSN
# Doit afficher: postgresql://...

# Relancer
python3 tools/import_books.py ../datasets/sample_books --limit 5
```

### Backend répond pas
```bash
# Vérifier .env
cat backend/.env
# Doit avoir DB_DSN correct

# Relancer
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend affiche erreur API
```bash
# Vérifier que backend écoute sur :8000
curl http://localhost:8000/health
# Doit afficher: {"status":"healthy"}
```

---

## 📚 Documentation Complète

Pour les détails, voir :
- `postgres_db/README.md` → Configuration Data
- `ARCHITECTURE.md` → Architecture complète
- `backend/requirements.txt` + `frontend/package.json` → Dépendances

---

**Temps estimé : 15-20 minutes**

Enjoy! 🚀
