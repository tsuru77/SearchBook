#!/bin/bash

# 🚀 DOCKER DEPLOYMENT QUICKSTART
# SearchBook - Full Stack Application
# 28 novembre 2025

cat << 'EOF'

╔════════════════════════════════════════════════════════════════════════╗
║                 🐳 SEARCHBOOK DOCKER DEPLOYMENT                       ║
║                                                                        ║
║          Complete Stack: PostgreSQL + FastAPI + React + Nginx        ║
╚════════════════════════════════════════════════════════════════════════╝

📋 QUICKSTART (5 minutes)
─────────────────────────────────────────────────────────────────────────

Step 1: Préparation
─────────────────────────────────────────────────────────────────────────
cd SearchBook/test

# Créer le fichier .env (optionnel, default OK)
cp .env.example .env

Step 2: Démarrer les services
─────────────────────────────────────────────────────────────────────────
# Terminal 1: Démarrer tous les services avec logs
docker-compose up

# OU en arrière-plan (Terminal 2: docker-compose logs -f)
docker-compose up -d

Step 3: Attendre la readiness (1-2 min)
─────────────────────────────────────────────────────────────────────────
# Vérifier le statut
docker-compose ps

# Attendre:
#   postgres    : "healthy" 
#   backend     : "healthy"
#   frontend    : "Up"
#   nginx       : "healthy"

Step 4: Tester l'application
─────────────────────────────────────────────────────────────────────────
# Frontend
open http://localhost/

# API Swagger UI
open http://localhost/docs

# Direct API call
curl -X POST http://localhost/api/search/simple \
  -H "Content-Type: application/json" \
  -d '{"query": "example", "ranking_by": "occurrences", "limit": 10}'

✅ SUCCESS! Application accessible

─────────────────────────────────────────────────────────────────────────

🏗️  ARCHITECTURE
─────────────────────────────────────────────────────────────────────────

                  NGINX (Port 80)
                    ↙         ↖
              /api/ (40MB)    / (40MB)
              ↙               ↖
         Backend           Frontend
         (150MB)           (Nginx)
            ↓
        PostgreSQL
        (Alpine)

Network: All services connected via searchbook-network (internal)
Ports exposed to host: 80 (HTTP), 5432 (PostgreSQL, dev only)

─────────────────────────────────────────────────────────────────────────

📝 COMMANDES COURANTES
─────────────────────────────────────────────────────────────────────────

# Démarrer/arrêter
docker-compose up -d              # Démarrer en arrière-plan
docker-compose down               # Arrêter
docker-compose restart            # Redémarrer

# Logs
docker-compose logs -f            # Tous les logs
docker-compose logs -f backend    # Logs spécifique
docker-compose logs --tail=50     # 50 dernières lignes

# Exécution
docker-compose exec backend bash                    # Bash dans backend
docker-compose exec postgres psql -U searchbook     # Connecter à PostgreSQL

# Rebuild
docker-compose build --no-cache backend   # Rebuild backend sans cache
docker-compose up -d --build              # Rebuild et redémarrer tout

─────────────────────────────────────────────────────────────────────────

🧪 TESTS
─────────────────────────────────────────────────────────────────────────

# Health checks
curl http://localhost/health                  # Nginx
curl http://localhost:8000/health             # Backend (dev port)

# Database check
docker-compose exec postgres psql -U searchbook searchbook
  \c searchbook
  SELECT COUNT(*) FROM documents;
  \q

# Simple search
curl -X POST http://localhost/api/search/simple \
  -H "Content-Type: application/json" \
  -d '{
    "query": "the",
    "ranking_by": "occurrences",
    "limit": 5
  }' | jq .

# Advanced search (regex)
curl -X POST http://localhost/api/search/advanced \
  -H "Content-Type: application/json" \
  -d '{
    "regex_pattern": "^the.*",
    "ranking_by": "pagerank",
    "limit": 5
  }' | jq .

─────────────────────────────────────────────────────────────────────────

⚙️  CONFIGURATION
─────────────────────────────────────────────────────────────────────────

Modifier .env pour customiser:
  POSTGRES_USER          → searchbook
  POSTGRES_PASSWORD      → searchbookpass
  LOG_LEVEL              → info (ou debug)
  API_URL                → http://localhost/api

Modifier docker-compose.yml pour changer les ports:
  nginx ports: "80:80"           → "8080:80" (nginx sur 8080)
  postgres ports: "5432:5432"    → "54321:5432" (postgres sur 54321)

Modifier nginx.conf pour custom routes/cache/rate-limiting

─────────────────────────────────────────────────────────────────────────

🐛 TROUBLESHOOTING
─────────────────────────────────────────────────────────────────────────

❌ "Connection refused" (backend)
✓ docker-compose logs postgres
✓ docker-compose exec postgres pg_isready -U searchbook
✓ Attendre 10-15 secondes après docker-compose up

❌ "Cannot GET /" (frontend)
✓ docker-compose logs frontend nginx
✓ docker-compose ps (vérifier frontend healthy)
✓ docker-compose up frontend --build

❌ "502 Bad Gateway"
✓ docker-compose logs backend
✓ docker-compose logs nginx
✓ Vérifier que backend healthcheck passe

❌ "port already in use"
✓ Changer le port dans docker-compose.yml
✓ Ou: sudo fuser -k 80/tcp (libérer port 80)

─────────────────────────────────────────────────────────────────────────

📊 RESOURCE USAGE
─────────────────────────────────────────────────────────────────────────

Image sizes:
  postgres:15-alpine         ~80 MB
  nginx:1.25-alpine          ~40 MB
  backend (built)            ~150 MB
  frontend (built)           ~40 MB
  Total:                     ~310 MB disk

Memory (running):
  PostgreSQL                 100-200 MB
  Backend                    50-100 MB
  Frontend/Nginx             10-20 MB
  Nginx proxy                10-20 MB
  Total:                     ~200-350 MB RAM

─────────────────────────────────────────────────────────────────────────

📚 FICHIERS DOCUMENTÉS
─────────────────────────────────────────────────────────────────────────

Lire pour plus de détails:
  ✓ DOCKER_SETUP.md       → Documentation complète
  ✓ docker-compose.yml    → Voir services définition
  ✓ nginx.conf            → Voir reverse proxy config
  ✓ backend/Dockerfile    → Voir build multi-stage
  ✓ frontend/Dockerfile   → Voir build + Nginx config
  ✓ .env.example          → Voir variables disponibles

─────────────────────────────────────────────────────────────────────────

✅ READY TO GO!

Your application is now:
  • Frontend: http://localhost/
  • API Docs: http://localhost/docs
  • Database: postgres://localhost:5432/searchbook

Happy coding! 🚀

EOF
