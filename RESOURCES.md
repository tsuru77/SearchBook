# 📚 RESSOURCES & LIENS UTILES

## 🔗 Documentation Officielle

### Base de Données
- **PostgreSQL** : https://www.postgresql.org/docs/
  - Full-text search : https://www.postgresql.org/docs/current/textsearch.html
  - GIN indexes : https://www.postgresql.org/docs/current/indexes-types.html
  - Trigram (pg_trgm) : https://www.postgresql.org/docs/current/pgtrgm.html

- **psycopg2** (Python PostgreSQL adapter) : https://www.psycopg.org/
  - Connection pooling : https://www.psycopg.org/psycopg3/basic/index.html#connection-pools

### Backend
- **FastAPI** : https://fastapi.tiangolo.com/
  - Tutorial : https://fastapi.tiangolo.com/tutorial/
  - Pydantic : https://docs.pydantic.dev/latest/
  - Startup/shutdown events : https://fastapi.tiangolo.com/advanced/events/

- **Uvicorn** (ASGI server) : https://www.uvicorn.org/

### Frontend
- **React** : https://react.dev/
  - Hooks documentation : https://react.dev/reference/react
  - React TypeScript : https://react-typescript-cheatsheet.netlify.app/

- **Vite** : https://vitejs.dev/
  - Guide : https://vitejs.dev/guide/
  - Configuration : https://vitejs.dev/config/
  - HMR (Hot Module Replacement) : https://vitejs.dev/guide/hmr.html

- **TypeScript** : https://www.typescriptlang.org/docs/
  - React + TypeScript : https://www.typescriptlang.org/docs/handbook/2/narrowing.html

### Algorithmes
- **Jaccard Similarity** : https://en.wikipedia.org/wiki/Jaccard_index
  - Explication : https://en.wikipedia.org/wiki/Jaccard_index
  - Implémentation optimisée : MinHash (https://en.wikipedia.org/wiki/MinHash)

- **PageRank** : https://en.wikipedia.org/wiki/PageRank
  - Formule originale : https://en.wikipedia.org/wiki/PageRank#Algorithm
  - NetworkX implementation : https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.pagerank.pagerank.html

- **Index Inversé** : https://en.wikipedia.org/wiki/Inverted_index
  - Full-text indexing : https://en.wikipedia.org/wiki/Full-text_search

---

## 📦 Données & Corpus

### Project Gutenberg
- **Site** : https://www.gutenberg.org/
- **Catalogue** : https://www.gutenberg.org/browse/
- **Téléchargement en masse** : https://www.gutenberg.org/cache/epub/
  - Format : EPUB, Kindle, HTML, plain text, etc.
  - Licence : Domaine public (gratuit)
  
- **API Gutenberg** : https://gutendex.com/ (API JSON)
  ```bash
  # Exemple : récupérer infos d'un livre
  curl https://gutendex.com/books/1  # Les Misérables
  ```

### Autres corpus
- **LibriVox** : https://librivox.org/ (Audio books)
- **Open Library** : https://openlibrary.org/ (Millions de livres)
- **Standard Ebooks** : https://standardebooks.org/ (Libres, bien formatés)

---

## 🛠️ Outils & Services

### Développement Local
- **Docker** : https://www.docker.com/
- **Docker Compose** : https://docs.docker.com/compose/

### Éditeurs & IDEs
- **VS Code** : https://code.visualstudio.com/
  - Extensions recommandées :
    - Python (Microsoft)
    - Pylance (Microsoft)
    - ESLint (Microsoft)
    - Prettier (Code formatter)
    - REST Client (tester API)

- **PyCharm** : https://www.jetbrains.com/pycharm/
- **WebStorm** : https://www.jetbrains.com/webstorm/

### Testing & Benchmarking
- **Postman** : https://www.postman.com/ (Tester API)
- **Apache Bench** : `ab -n 100 -c 10 http://localhost:8000/api/search/simple`
- **pytest** (Python tests) : https://docs.pytest.org/
- **Jest** (JavaScript tests) : https://jestjs.io/

### Visualization
- **Graphviz** (diagrammes) : https://graphviz.org/
- **PlantUML** (UML) : https://plantuml.com/
- **Excalidraw** (wireframes) : https://excalidraw.com/
- **Figma** (design) : https://www.figma.com/

---

## 📊 Analyse de Performance

### Load Testing
```bash
# Apache Bench
ab -n 100 -c 10 http://localhost:8000/health

# Sysbench
sysbench --help

# Locust (Python)
pip install locust
```

### Database Performance
```bash
# PostgreSQL explain
EXPLAIN ANALYZE SELECT ...

# Slow query log
SET log_min_duration_statement = 100;
```

### Frontend Performance
- **Chrome DevTools** : Onglet "Performance" (profiling)
- **Lighthouse** : Vérifier scores performance/accessibilité
- **Web Vitals** : https://web.dev/vitals/

---

## 📖 Tutoriels & Articles

### PostgreSQL + Python
- **Real Python - Database Connections** : https://realpython.com/intro-to-python-sqlite/
- **PostgreSQL + psycopg2 Tutorial** : https://www.guru99.com/postgresql-python.html

### Full-Text Search
- **Medium - Building a Search Engine** : https://medium.com/search/q=building%20search%20engine
- **Blog PostgreSQL FTS** : https://www.postgresql.org/about/news/2045/

### FastAPI + React
- **Full-Stack with FastAPI + React** : https://taoofcode.dev/
- **Real-time web apps with FastAPI + WebSockets** : https://fastapi.tiangolo.com/advanced/websockets/

### Graph Algorithms
- **NetworkX Tutorial** : https://networkx.org/documentation/stable/tutorial.html
- **PageRank Visualization** : https://www.google.com/search?q=pagerank+visualization+python

---

## 🎓 Cours & Learning

### Gratuit
- **Coursera - Data Structures & Algorithms** : https://www.coursera.org/
- **MIT OpenCourseWare** : https://ocw.mit.edu/
- **YouTube - Algorithms by Errichto** : https://www.youtube.com/c/Errichto

### Payant
- **Udemy - FastAPI Course** : https://www.udemy.com/
- **DataCamp - Python for Data Science** : https://www.datacamp.com/

---

## 📚 Livres de Référence

### Algorithmes
- **Introduction to Algorithms (CLRS)** : Cormen, Leiserson, Rivest, Stein
- **Algorithm Design Manual** : Steven Skiena
- **Thinking in Algorithms** : Bhargava

### Bases de Données
- **SQL Performance Explained** : Markus Winand
- **PostgreSQL: The Comprehensive Guide** : Peter Eisentraut

### Web Development
- **Web Performance Action Guide** : Daniel Fleck
- **Real-time Web Development with Node.js** : Les Tyrrell

---

## 🔍 Benchmarking Resources

### Public Datasets
- **UCI Machine Learning Repository** : https://archive.ics.uci.edu/ml/
- **Kaggle Datasets** : https://www.kaggle.com/datasets
- **Google Dataset Search** : https://datasetsearch.research.google.com/

### Performance Metrics
- **NDCG (Normalized DCG)** : Metric pour pertinence recherche
  - Paper : https://www.microsoft.com/en-us/research/publication/ndcg/
- **Mean Average Precision (MAP)** : https://en.wikipedia.org/wiki/Evaluation_measures_(information_retrieval)

---

## 🌐 Community & Support

### Stack Overflow
- Search : `[postgresql]`, `[fastapi]`, `[react]`, `[algorithms]`
- https://stackoverflow.com/

### Reddit
- **r/learnprogramming** : https://www.reddit.com/r/learnprogramming/
- **r/PostgreSQL** : https://www.reddit.com/r/PostgreSQL/
- **r/FastAPI** : https://www.reddit.com/r/FastAPI/
- **r/reactjs** : https://www.reddit.com/r/reactjs/

### GitHub
- **Search open-source projects** : https://github.com/search
- **Awesome Lists** : https://github.com/awesome-lists/awesome (collections de ressources)

---

## 🎯 Résources Projet-Spécifiques

### Recherche d'Information
- **Okapi BM25** (ranking algorithm) : https://en.wikipedia.org/wiki/Okapi_BM25
- **TF-IDF** : https://en.wikipedia.org/wiki/Tf%E2%80%93idf
- **Vector Space Model** : https://en.wikipedia.org/wiki/Vector_space_model

### Graphes de Similarité
- **Similarity Measures** : https://en.wikipedia.org/wiki/Similarity_measure
- **Graph-based recommendations** : https://en.wikipedia.org/wiki/Collaborative_filtering

### Centarlité dans Graphes
- **Closeness Centrality** : https://en.wikipedia.org/wiki/Closeness_centrality
- **Betweenness Centrality** : https://en.wikipedia.org/wiki/Betweenness_centrality
- **Eigenvector Centrality** : https://en.wikipedia.org/wiki/Eigenvector_centrality

---

## 💾 Installation & Setup

### Macros Commands

```bash
# Setup PostgreSQL avec Docker
docker run --name postgres-searchbook \
  -e POSTGRES_USER=searchbook \
  -e POSTGRES_PASSWORD=searchbookpass \
  -e POSTGRES_DB=searchbook \
  -p 5432:5432 \
  -d postgres:15

# Setup Python
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt

# Setup Node
npm install -g npm
npm --version

# Test connectivity
psql -h localhost -U searchbook -d searchbook -c "SELECT 1;"
```

---

## 🚀 Deployment (Optional)

### Docker
- **Docker Hub** : https://hub.docker.com/
- **Image PostgreSQL** : https://hub.docker.com/_/postgres

### Cloud Platforms
- **Heroku** : https://www.heroku.com/ (free tier exhausted)
- **Railway** : https://railway.app/ (free tier)
- **Render** : https://render.com/
- **Vercel** (frontend) : https://vercel.com/
- **AWS** : https://aws.amazon.com/
- **Azure** : https://azure.microsoft.com/

---

## 📝 Note Finale

Tous ces liens sont valides au moment de la création de ce document. En cas de lien cassé, cherchez directement sur Google ou le GitHub du projet.

**Bonne chance avec votre SearchBook ! 🚀📚**
