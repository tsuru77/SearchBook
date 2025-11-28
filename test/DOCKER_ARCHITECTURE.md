# 🏗️ Architecture Diagram - SearchBook Complete Stack

## Vue d'ensemble (High Level)

```
                          ┌─────────────────┐
                          │  Internet User  │
                          └────────┬────────┘
                                   │
                         HTTP Request (Port 80)
                                   │
        ┌──────────────────────────▼──────────────────────────┐
        │                                                      │
        │              NGINX Reverse Proxy                    │
        │                                                      │
        │  ✓ Single entry point (Port 80)                    │
        │  ✓ Route /api → Backend:8000                       │
        │  ✓ Route / → Frontend:80                           │
        │  ✓ Gzip compression                                │
        │  ✓ Rate limiting                                   │
        │  ✓ Error handling                                  │
        │                                                      │
        └──────────────────────────┬──────────────────────────┘
                                   │
                    ┌──────────────┴──────────────┐
                    │                             │
        ┌───────────▼──────────┐     ┌──────────▼────────────┐
        │                      │     │                       │
        │  Backend FastAPI     │     │  Frontend React       │
        │  (Python 3.11)       │     │  (Node.js + Nginx)    │
        │                      │     │                       │
        │  /api/search/simple  │     │  index.html           │
        │  /api/search/adv     │     │  app.js, styles.css   │
        │  /docs (Swagger)     │     │  (static assets)      │
        │                      │     │                       │
        └───────────┬──────────┘     └───────────────────────┘
                    │
                    │ PostgreSQL Driver (psycopg2)
                    │
        ┌───────────▼──────────────┐
        │                          │
        │  PostgreSQL 15           │
        │  (Alpine Linux)          │
        │                          │
        │  • documents table       │
        │  • inverted_index table  │
        │  • jaccard_edges table   │
        │  • centrality_scores     │
        │  • popularity_doc        │
        │                          │
        └──────────────────────────┘
```

---

## Flux de Requête - Frontend Recherche

```
1. Utilisateur tape "example" dans la barre de recherche
                           │
                           ▼
2. JavaScript (React) détecte le changement
   → Construits le JSON: {query: "example", ranking_by: "occurrences", limit: 20}
                           │
                           ▼
3. Fetch POST vers /api/search/simple
   fetch('http://localhost/api/search/simple', {
     method: 'POST',
     headers: {'Content-Type': 'application/json'},
     body: JSON.stringify({...})
   })
                           │
                           ▼
4. HTTP Request arrive à NGINX (:80)
   POST http://localhost/api/search/simple
                           │
5. Nginx matching: location /api/ {
      proxy_pass http://backend_api;  ← Forward vers backend:8000
   }
                           │
                           ▼
6. Backend FastAPI reçoit la requête
   POST /api/search/simple
                           │
7. FastAPI router envoie à SearchService.simple_search()
                           │
8. SearchService.simple_search() execute SQL:
   SELECT ... FROM inverted_index ii
     JOIN documents d ON d.id = ii.doc_id
     WHERE LOWER(ii.term) = LOWER('example')
     ORDER BY ii.occurrences DESC
     LIMIT 20
                           │
                           ▼
9. PostgreSQL répond avec les résultats
                           │
                           ▼
10. FastAPI formate JSON SearchResponse
   {
     "query": "example",
     "total_results": 42,
     "results": [...],
     "suggestions": [...],
     "execution_time_ms": 23
   }
                           │
                           ▼
11. Backend répond à Nginx (HTTP 200)
                           │
12. Nginx forward la réponse au client
                           │
                           ▼
13. JavaScript (React) reçoit JSON
   → setState({results: [...], loading: false})
                           │
                           ▼
14. React re-render avec résultats
                           │
                           ▼
15. Utilisateur voit les résultats 🎉
```

---

## Flux de Requête - Static Assets (Frontend Load)

```
1. Utilisateur ouvre http://localhost/
                           │
                           ▼
2. HTTP GET /
                           │
                           ▼
3. Nginx matche: location / {
     proxy_pass http://frontend_app;
   }
                           │
                           ▼
4. Frontend Nginx (internal:80) reçoit GET /
                           │
5. Frontend Nginx match: location / {
     try_files $uri $uri/ /index.html;  ← SPA routing
   }
   → serve /usr/share/nginx/html/index.html
                           │
                           ▼
6. Frontend Nginx répond avec index.html (HTTP 200)
   + Headers: Cache-Control: no-cache
                           │
                           ▼
7. Browser parse HTML, voit scripts:
   <script src="/assets/main-abc123.js"></script>
   <link rel="stylesheet" href="/assets/style-def456.css">
                           │
                           ▼
8. Browser requête les assets: GET /assets/main-abc123.js
                           │
                           ▼
9. Nginx matche: location ~* \.(js|css|...)$ {
     expires 1y;  ← Long cache
     add_header Cache-Control "public, immutable";
   }
                           │
10. Frontend Nginx serve assets depuis /dist/ (gzipped)
                           │
                           ▼
11. Browser exécute JavaScript
    → React app mounts
    → Utilisateur peut interagir
```

---

## Architecture Réseau Interne (Docker Network)

```
Docker Network: searchbook-network (bridge)

┌─────────────────────────────────────────────────────────┐
│                 searchbook-network                      │
│                                                         │
│  Service Names Resolution (DNS):                       │
│  • postgres → 172.20.0.2:5432                         │
│  • backend → 172.20.0.3:8000                          │
│  • frontend → 172.20.0.4:80                           │
│  • nginx → 172.20.0.5:80                              │
│                                                         │
│  Internal Communication (NO exposure):                 │
│  • nginx:80 → backend:8000 (proxy_pass)              │
│  • nginx:80 → frontend:80 (proxy_pass)                │
│  • backend:8000 → postgres:5432 (database driver)    │
│                                                         │
│  Exposed to Host:                                      │
│  • nginx:80 (public HTTP)                             │
│  • nginx:443 (public HTTPS, future)                   │
│  • postgres:5432 (dev only)                           │
│  • backend:8000 (dev only, exposed for direct access) │
│  • frontend:3000 (dev only)                           │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Path Routing Rules (Nginx)

```
Incoming Request → Nginx (:80)
                       │
                       ├─ GET /health
                       │  └─ return 200 "OK" (health check)
                       │
                       ├─ POST /api/*
                       │  └─ proxy_pass http://backend:8000
                       │     (all /api/* routes → backend)
                       │
                       ├─ GET /docs
                       │  └─ proxy_pass http://backend:8000/docs
                       │     (Swagger UI)
                       │
                       ├─ GET /openapi.json
                       │  └─ proxy_pass http://backend:8000/openapi.json
                       │
                       ├─ GET /assets/* (js, css, images)
                       │  └─ proxy_pass http://frontend:80
                       │     headers: Cache-Control "1y"
                       │     (long cache for immutable assets)
                       │
                       └─ GET / (root + all other routes)
                          └─ proxy_pass http://frontend:80
                             (React SPA routing)
```

---

## Request Headers Flow

```
CLIENT BROWSER
     │
     └─► HTTP Headers:
         • Host: localhost
         • User-Agent: Mozilla/5.0...
         • Accept: application/json
         • Content-Type: application/json (POST)
                              │
                              ▼
                        NGINX (:80)
                              │
                        Add headers:
                              │
                              ├─ X-Real-IP: 172.30.0.1 (client IP)
                              ├─ X-Forwarded-For: 172.30.0.1
                              ├─ X-Forwarded-Proto: http
                              ├─ X-Forwarded-Host: localhost
                              ├─ Host: backend (rewrite)
                              │
                              ▼
                        BACKEND (:8000)
                              │
                        FastAPI sees:
                        • request.client.host = 172.30.0.1 (via X-Real-IP)
                        • request.url.path = /api/search/simple
                        • request.method = POST
                        │
                        └─► Process request → Response JSON
                              │
                              ▼
                        NGINX (relay)
                              │
                              ├─ Content-Type: application/json
                              ├─ Content-Encoding: gzip (if enabled)
                              ├─ Cache-Control: no-cache (API)
                              │
                              ▼
                        CLIENT BROWSER
                              │
                              └─► JavaScript parses JSON
                                   → React setState
                                   → Re-render UI
```

---

## Database Connection Pooling

```
FastAPI Backend (running in container)
        │
        └─ Connection Pool: SimpleConnectionPool(minconn=2, maxconn=20)
                 │
         ┌───────┼───────┐
         │       │       │
      Conn1   Conn2   Conn3 ... Conn20
         │       │       │
         └───────┼───────┘
                 │
                 ▼ (over TCP/IP)
        PostgreSQL Container
        (postgres:5432)
                 │
         SELECT/INSERT/UPDATE
                 │
         Response (rows/affected)
                 │
                 ▼
        Backend processes
                 │
                 ▼
        Return JSON to Nginx
```

---

## Volume Persistence

```
Host Machine
     │
     ├─ Docker Volume: pgdata
     │      │
     │      ▼
     │   {hash}/postgresql/data
     │   (persistent data, survives docker-compose down)
     │      │
     │      ▼
     │  PostgreSQL Container
     │  /var/lib/postgresql/data (mounted)
     │      │
     │      ├─ base/
     │      │  ├─ {oid}/
     │      │  │  ├─ 16384 (table data)
     │      │  │  ├─ 16384.1 (overflow)
     │      │  │  └─ ...
     │      │  └─ ...
     │      │
     │      ├─ pg_xlog/ (WAL logs)
     │      └─ global/ (system tables)
     │
     └─ Warning: docker-compose down -v
        (supprime le volume → données perdues!)
```

---

## Service Dependencies

```
docker-compose.yml:

nginx (depends on: backend, frontend)
     │
     ├─ backend (depends on: postgres, condition: service_healthy)
     │      │
     │      └─ postgres (healthcheck: pg_isready)
     │
     └─ frontend (depends on: backend)

Startup order:
1. postgres starts
2. postgres reaches "healthy" (pg_isready passes)
3. backend starts (only after postgres healthy)
4. frontend starts
5. nginx starts (only after backend + frontend up)
```

---

## Performance Optimizations Applied

```
✅ Reverse Proxy Caching
   nginx caches static assets (1 year expiry)
   
✅ Gzip Compression
   nginx compresses responses (min 256 bytes)
   
✅ Connection Pooling
   FastAPI: SimpleConnectionPool(min=2, max=20)
   → reuse database connections
   
✅ Database Indexing
   ✓ inverted_index_term_trgm (trigram search)
   ✓ centrality_pagerank (DESC for ranking)
   ✓ doc_id indexes (foreign keys)
   
✅ Multi-stage Builds
   ✓ backend: 150 MB (with deps)
   ✓ frontend: 40 MB (dist only)
   
✅ Alpine Linux
   ✓ postgres:15-alpine (~80 MB)
   ✓ nginx:1.25-alpine (~40 MB)
   ✓ python:3.11-slim (~150 MB built)
   
✅ Rate Limiting
   /api/* : 10 req/s (limit_req)
   /* : 30 req/s (general)
   
✅ SPA Routing
   location / { try_files $uri $uri/ /index.html; }
   → all routes served by React, no 404s
```

---

## Monitoring & Health Checks

```
All services have HEALTHCHECK:

postgres:
  CMD-SHELL: pg_isready -U searchbook -d searchbook
  → checks if database accepting connections

backend:
  CMD: curl -f http://localhost:8000/health
  → depends on GET /health returning 200

frontend:
  CMD: wget --quiet --tries=1 --spider http://localhost/
  → checks if HTTP 200 on root

nginx:
  CMD: wget --quiet --tries=1 --spider http://localhost/health
  → depends on Nginx health endpoint (proxied to backend)

docker-compose ps shows health status:
  postgres    : healthy / starting / unhealthy
  backend     : healthy / starting / unhealthy
  frontend    : Up (no built-in health endpoint)
  nginx       : healthy / starting / unhealthy
```

---

*Architecture documentation - 28 novembre 2025*
