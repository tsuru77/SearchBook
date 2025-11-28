# SearchBook

Full-text library search engine for the DAAR Project 3 assignment. The platform combines a Vite + React SPA, a FastAPI backend, and Elasticsearch for indexing, along with a graph-based ranking layer (Jaccard similarities + centrality metrics). Everything runs locally via Docker Compose.

## Repository layout

```
.
├── backend/          # FastAPI app, routers, services, requirements
├── frontend/         # React (Vite) SPA
├── ingestion/        # Data preparation + ES ingestion scripts
├── docker/           # Helper configs (e.g. Kibana)
├── docker-compose.yml
├── datasets/         # Local book corpus (ignored in git)
└── README.md
```

## Development prerequisites

- Python 3.11+
- Node.js 20+
- Docker Desktop (or compatible engine) with Compose v2
- Elasticsearch 8.x Docker image credentials (elastic / password)

## Quick start

1. Clone the repo & install dependencies for each service (`backend` and `frontend`).
2. Copy `backend/env.example` to `backend/.env` (or export the same variables another way).
3. Place your sample corpus (e.g. 5 books) under `datasets/sample_books/`.
4. Create a Python virtualenv for `backend`, install requirements, and run the ingestion script targeting the sample data:

```bash
cd backend && python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python ../ingestion/load_books.py --corpus-path ../datasets/sample_books --limit 5
```

5. Start the stack:

```bash
docker compose up --build
```

Frontend served at http://localhost:8080, backend at http://localhost:8000, Elasticsearch at http://localhost:9200.

More detailed instructions will be documented as the implementation evolves.