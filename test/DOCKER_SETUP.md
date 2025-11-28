# 🐳 Docker Setup - SearchBook Complete Architecture

## Architecture Globale

```
┌─────────────────────────────────────────────────────────────────┐
│                        INTERNET CLIENT                          │
└────────────────────────────┬────────────────────────────────────┘
                             │
                    HTTP/HTTPS :80/:443
                             │
        ┌────────────────────▼────────────────────┐
        │     NGINX Reverse Proxy (Port 80)       │
        │  ✓ Route /api → Backend FastAPI        │
        │  ✓ Route /  → Frontend React (SPA)     │
        │  ✓ Health checks                        │
        │  ✓ Rate limiting                        │
        │  ✓ Gzip compression                     │
        └────┬─────────────────────────────────┬──┘
             │                                 │
        :8000│ (internal)              (internal)│ :80
             │                                 │
    ┌────────▼──────────┐        ┌────────────▼───────┐
    │  FastAPI Backend  │        │  React Frontend    │
    │  (Python 3.11)    │        │  (Node.js + Nginx) │
    │                   │        │                    │
    │  ✓ API endpoints  │        │  ✓ SPA app        │
    │  ✓ Database ORM   │        │  ✓ Static assets  │
    │  ✓ Auth/validation│        │  ✓ Routing        │
    └────────┬──────────┘        └────────────────────┘
             │
             │ :5432 (internal)
             │
        ┌────▼──────────────┐
        │   PostgreSQL 15   │
        │   (Alpine 3.18)   │
        │                   │
        │  ✓ Migrations     │
        │  ✓ Persistent vol │
        │  ✓ Health checks  │
        └───────────────────┘
```

---

## 📋 Fichiers Créés

```
test/
├── docker-compose.yml          ← Configuration Docker Compose (4 services)
├── nginx.conf                  ← Nginx reverse proxy config
├── .env.example                ← Variables d'environnement
│
├── backend/
│   └── Dockerfile              ← Multi-stage FastAPI build
│
├── frontend/
│   └── Dockerfile              ← Multi-stage React + Nginx build
│
└── postgres_db/
    ├── docker-compose.yml      ← (legacy) peut être supprimé
    ├── migrations/
    │   └── 001_init_schema.sql
    └── tools/
        ├── import_books.py
        ├── compute_jaccard.py
        └── compute_pagerank.py
```

---

## 🚀 Démarrage Rapide

### Prérequis
- Docker >= 20.10
- Docker Compose >= 2.0
- Espace disque : ~5 GB (PostgreSQL + images)

### Étapes

1. **Cloner/Navigator vers le répertoire test**
   ```bash
   cd SearchBook/test
   ```

2. **Créer le fichier .env**
   ```bash
   cp .env.example .env
   # Optionnel: Éditer .env pour modifier les variables
   ```

3. **Démarrer tous les services**
   ```bash
   docker-compose up -d
   ```
   
   Logs en temps réel:
   ```bash
   docker-compose logs -f
   ```

4. **Attendre que tous les services soient healthy**
   ```bash
   docker-compose ps
   
   # Attendez que tous les containers affichent "healthy"
   # STATUS colonne: "healthy", "Up"
   ```

5. **Accéder à l'application**
   - Frontend: http://localhost/
   - API Swagger: http://localhost/docs
   - API REST: http://localhost/api/search/simple

---

## 📡 Architecture des Requêtes

### Frontend → Backend

```mermaid
Client Browser
    ↓
    HTTP GET http://localhost/
    ↓
Nginx (Port 80)
    ├─ Reçoit requête
    ├─ Route → frontend:80 (location /)
    ↓
React App (SPA)
    ├─ Charge index.html
    ├─ Charge JS/CSS assets (cached)
    ↓
Navigateur exécute JavaScript
    ├─ Utilisateur tapeLe une recherche
    ├─ JavaScript → POST http://localhost/api/search/simple
    ↓
Nginx (interception /api/)
    ├─ Route → backend:8000
    ↓
FastAPI
    ├─ Traite requête
    ├─ Query PostgreSQL
    ├─ Retourne JSON
    ↓
Nginx (relais réponse)
    ↓
React App (update state)
    ↓
Affiche résultats utilisateur
```

### Flux détaillé par endpoint

#### GET / (Frontend)
```
Browser → Nginx:80
Nginx → frontend:80 (SPA root location /)
Frontend → serve /dist/index.html + static assets
Nginx → Browser (HTTP 200)
```

#### POST /api/search/simple (Backend)
```
Browser → Nginx:80 (location /api/)
Nginx → backend:8000 (proxy_pass http://backend_api)
Backend → PostgreSQL:5432 (SQL query)
Backend → Nginx (JSON response)
Nginx → Browser (HTTP 200 + JSON)
```

#### GET /docs (Swagger UI)
```
Browser → Nginx:80 (location /docs)
Nginx → backend:8000/docs
Backend → serve Swagger docs
Nginx → Browser
```

---

## 🔧 Services Docker

### 1. PostgreSQL (postgres)

| Param | Valeur |
|-------|--------|
| Image | postgres:15-alpine |
| Port | 5432 (interne: 5432) |
| Healthcheck | pg_isready |
| Volume | pgdata (persistent) |
| Init Script | migrations/001_init_schema.sql |

**Env vars** (depuis .env):
```
POSTGRES_USER=searchbook
POSTGRES_PASSWORD=searchbookpass
POSTGRES_DB=searchbook
```

### 2. Backend FastAPI (backend)

| Param | Valeur |
|-------|--------|
| Build | ./backend/Dockerfile (multi-stage) |
| Port | 8000 (interne) → 8000 (host pour dev) |
| Healthcheck | curl http://localhost:8000/health |
| Depends on | postgres (service_healthy) |
| Network | searchbook-network |

**Dockerfile stratégie**:
- Stage 1 (builder): pip install -r requirements.txt
- Stage 2 (runtime): copy wheels from stage 1, minimal image
- Result: ~150 MB image

### 3. Frontend React (frontend)

| Param | Valeur |
|-------|--------|
| Build | ./frontend/Dockerfile (multi-stage) |
| Port | 80 (interne) → 3000 (host pour dev) |
| Healthcheck | wget http://localhost/ |
| Depends on | backend (for API availability) |
| Network | searchbook-network |

**Dockerfile stratégie**:
- Stage 1 (builder): npm ci + npm run build
- Stage 2 (runtime): nginx:1.25-alpine serving dist/
- Result: ~40 MB image

**Nginx config interne**:
```nginx
location / { try_files $uri $uri/ /index.html; }  # SPA routing
location ~* \.(js|css|...)$ { expires 1y; }        # Cache assets
gzip on;                                            # Compression
```

### 4. Nginx Reverse Proxy (nginx)

| Param | Valeur |
|-------|--------|
| Image | nginx:1.25-alpine |
| Port | 80 (public), 443 (future) |
| Config | ./nginx.conf |
| Depends on | backend, frontend |
| Healthcheck | wget http://localhost/health |

**Routes**:
```
/health          → return "OK" (health check)
/api/*           → proxy_pass http://backend:8000
/docs            → proxy_pass http://backend:8000/docs
/openapi.json    → proxy_pass http://backend:8000/openapi.json
/                → proxy_pass http://frontend:80 (SPA)
```

---

## 💾 Volumes et Persistence

| Volume | Montage | Usage |
|--------|---------|-------|
| `pgdata` | `/var/lib/postgresql/data` | Données PostgreSQL persistentes |

Les données persistent même après `docker-compose down` !

---

## 🔗 Network

Tous les services sont connectés au réseau `searchbook-network`:
```
- postgres (interne: postgres:5432)
- backend (interne: backend:8000)
- frontend (interne: frontend:80)
- nginx (interne, expose: 80, 443)
```

Communication réseau interne (pas d'exposition direct) :
```
nginx → backend:8000 (internal)
nginx → frontend:80 (internal)
backend → postgres:5432 (internal)
```

Seule Nginx expose les ports vers l'hôte :
```
Host :80 → Nginx:80 (HTTP)
Host :5432 → PostgreSQL:5432 (dev seulement)
```

---

## 📝 Commandes Courantes

### Démarrer
```bash
# Tous les services en arrière-plan
docker-compose up -d

# Avec logs en temps réel
docker-compose up

# Rebuild images et démarrer
docker-compose up -d --build
```

### Arrêter
```bash
# Arrêter tous les services
docker-compose down

# Arrêter et supprimer les volumes (⚠️ données perdues!)
docker-compose down -v

# Arrêter un service spécifique
docker-compose stop backend
```

### Logs
```bash
# Tous les logs
docker-compose logs -f

# Logs d'un service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres

# Logs de la 100 dernières lignes
docker-compose logs --tail=100 backend
```

### Exécution
```bash
# Bash dans un container
docker-compose exec backend bash
docker-compose exec frontend sh
docker-compose exec postgres psql -U searchbook searchbook

# Commande unique
docker-compose exec backend python -m pip list
```

### Status
```bash
# État des containers
docker-compose ps

# Détails réseau
docker-compose exec backend curl http://nginx/health

# Vérifier la base de données
docker-compose exec postgres psql -U searchbook -d searchbook -c "SELECT COUNT(*) FROM inverted_index;"
```

### Rebuild
```bash
# Rebuild une image
docker-compose build backend
docker-compose build frontend

# Rebuild et redémarrer
docker-compose up -d --build backend

# Supprimer les images locales et rebuilder
docker image rm searchbook_backend searchbook_frontend
docker-compose up -d --build
```

---

## 🧪 Testing

### Healthchecks
```bash
# Attendre que tous les services soient healthy
docker-compose ps

# Checker manually
curl http://localhost/health              # Nginx
curl http://localhost:8000/health         # Backend (dev port)
docker-compose exec postgres pg_isready   # PostgreSQL
```

### Test API
```bash
# Simple search
curl -X POST http://localhost/api/search/simple \
  -H "Content-Type: application/json" \
  -d '{"query": "example", "ranking_by": "occurrences", "limit": 10}'

# Advanced search (regex)
curl -X POST http://localhost/api/search/advanced \
  -H "Content-Type: application/json" \
  -d '{"regex_pattern": "^the.*", "ranking_by": "pagerank", "limit": 10}'

# Swagger docs
curl http://localhost/docs
```

### Test Database
```bash
# Connexion directe
docker-compose exec postgres psql -U searchbook -d searchbook

# Commandes SQL
SELECT COUNT(*) FROM documents;
SELECT COUNT(*) FROM inverted_index;
SELECT COUNT(*) FROM centrality_scores;
```

---

## ⚙️ Configuration Avancée

### Variables d'environnement

Créez `.env` à la racine de `/test/`:

```bash
# PostgreSQL
POSTGRES_USER=searchbook
POSTGRES_PASSWORD=searchbookpass
POSTGRES_DB=searchbook

# Backend
LOG_LEVEL=debug  # debug, info, warning
CORS_ORIGINS=["http://localhost"]

# Frontend
API_URL=http://localhost/api

# Docker
RESTART_POLICY=unless-stopped
```

### Ports différents

Modifier `docker-compose.yml`:
```yaml
services:
  nginx:
    ports:
      - "8080:80"  # ← Nginx sur port 8080 au lieu de 80

  postgres:
    ports:
      - "54321:5432"  # ← PostgreSQL sur port 54321
```

### Limitation des ressources

Ajouter des limites dans `docker-compose.yml`:
```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 512M
        reservations:
          cpus: '0.5'
          memory: 256M
```

---

## 🚨 Troubleshooting

### "Connection refused"
```bash
# Backend ne communique pas avec PostgreSQL?
docker-compose logs postgres

# PostgreSQL n'est pas healthy?
docker-compose exec postgres pg_isready -U searchbook

# Attendre que PostgreSQL soit prêt
docker-compose up postgres -d
sleep 10  # Attendre la migration
docker-compose up backend -d
```

### Frontend affiche "Cannot GET /"
```bash
# Nginx ne forward pas vers frontend?
docker-compose logs nginx

# Frontend ne démarre pas?
docker-compose logs frontend

# Reconstruire frontend
docker-compose build --no-cache frontend
docker-compose up frontend -d
```

### API répond en 502 Bad Gateway
```bash
# Backend n'est pas accessible?
docker-compose logs backend

# Backend healthcheck échoue?
docker-compose exec nginx curl http://backend:8000/health

# Redémarrer backend
docker-compose restart backend
```

### Permissions denied dans volumes
```bash
# Si vous avez des erreurs de permissions:
sudo chown -R 1000:1000 pgdata  # PostgreSQL UID
docker-compose restart postgres
```

---

## 📊 Performance et Optimisation

### Image sizes
```
postgres:15-alpine         ~80 MB
nginx:1.25-alpine          ~40 MB
backend (runtime)          ~150 MB (avec deps)
frontend (Nginx + dist)    ~40 MB
─────────────────────
Total:                     ~310 MB
```

### Memory usage (typical)
```
PostgreSQL    : 100-200 MB
Backend       : 50-100 MB
Frontend/Nginx: 10-20 MB
Nginx (proxy) : 10-20 MB
─────────────────────
Total:        ~200-350 MB
```

### Optimisations
✅ Multi-stage builds (backend, frontend)
✅ Alpine Linux images (minimal)
✅ Gzip compression (nginx)
✅ Asset caching (expires 1y)
✅ Rate limiting (10 req/s API, 30 req/s general)
✅ Connection pooling (FastAPI)

---

## 📚 Références

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [React + Docker Best Practices](https://react.dev/learn/deployment)

---

**Status**: ✅ **Production-Ready**

*Docker setup complété le 28 novembre 2025*
