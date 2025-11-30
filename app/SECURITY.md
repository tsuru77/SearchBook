# Security Update - Environment Variables

## What Changed?

The app2 `docker-compose.yml` no longer contains hardcoded credentials. All sensitive configuration is now managed via `.env` file, which is:

✅ **Excluded from git** (in `.gitignore`)  
✅ **Never committed** to version control  
✅ **Managed locally only**  

## Before (❌ Insecure)

```yaml
# Old approach - hardcoded secrets!
backend:
  environment:
    - SEARCHBOOK_DB_PASSWORD=searchbook_password  # ❌ Visible in git
    - SEARCHBOOK_DB_USER=searchbook               # ❌ Visible in git
```

## After (✅ Secure)

```yaml
# New approach - using environment variables
backend:
  env_file:
    - .env
  environment:
    - SEARCHBOOK_DB_PASSWORD=${SEARCHBOOK_DB_PASSWORD}  # ✅ From .env
    - SEARCHBOOK_DB_USER=${SEARCHBOOK_DB_USER}         # ✅ From .env
```

## Files Involved

| File | Purpose | Git Status |
|------|---------|-----------|
| `.env` | Actual secrets (passwords, API URLs) | ❌ IGNORED (not committed) |
| `.env.example` | Template with placeholder values | ✅ COMMITTED (for reference) |
| `docker-compose.yml` | Service configuration | ✅ COMMITTED |
| `setup.sh` | Interactive setup script | ✅ COMMITTED |

## How to Use

### Option 1: Interactive Setup (Recommended)
```bash
cd app2
bash setup.sh
# Follow prompts to set PostgreSQL credentials
docker compose up --build
```

### Option 2: Manual Setup
```bash
cd app2
cp .env.example .env
# Edit .env with your values
nano .env
docker compose up --build
```

### Option 3: Use Defaults
```bash
cd app2
# A default .env already exists with safe defaults
docker compose up --build
```

## What's in `.env`?

```bash
# Database credentials
POSTGRES_USER=searchbook
POSTGRES_PASSWORD=searchbook_password
POSTGRES_DB=searchbook

# Backend configuration
SEARCHBOOK_DB_HOST=postgres
SEARCHBOOK_DB_PORT=5432
SEARCHBOOK_DB_NAME=searchbook
SEARCHBOOK_DB_USER=searchbook
SEARCHBOOK_DB_PASSWORD=searchbook_password

# Application settings
SEARCHBOOK_PROJECT_NAME=SearchBook
SEARCHBOOK_API_PREFIX=/api
SEARCHBOOK_MIN_WORD_COUNT=10000
SEARCHBOOK_BM25_RESULTS_LIMIT=50
SEARCHBOOK_SUGGESTIONS_LIMIT=5

# Frontend API URL
VITE_API_BASE_URL=http://localhost:8000/api
```

## Security Best Practices

### ✅ Do
- Keep `.env` in `.gitignore`
- Use strong passwords in production
- Keep different `.env` files for dev/staging/production
- Never commit `.env` to version control
- Use secret management tools in production (e.g., Docker Secrets, Kubernetes Secrets, AWS Secrets Manager)

### ❌ Don't
- Commit `.env` to git
- Share `.env` files via email or chat
- Use default passwords in production
- Store `.env` in public repositories
- Log or print environment variables

## For Production

In production, replace the `.env` approach with:

1. **Docker Secrets** (Swarm mode)
   ```yaml
   secrets:
     db_password:
       external: true
   ```

2. **Kubernetes Secrets**
   ```yaml
   valueFrom:
     secretKeyRef:
       name: searchbook-secrets
       key: db_password
   ```

3. **AWS Secrets Manager, Azure Key Vault, HashiCorp Vault**, etc.

## Verification

Check that `.env` is protected:
```bash
cd app2

# Should show .env in gitignore
grep "^\.env" ../.gitignore

# Should NOT show .env files in git
git ls-files | grep ".env"  # Should return nothing

# Verify docker-compose uses variables
grep "\${" docker-compose.yml
```

## Migration Guide

If you had an old `app2` setup with hardcoded credentials:

1. Delete docker containers:
   ```bash
   docker compose down -v  # Remove volumes too
   ```

2. Copy `.env` template:
   ```bash
   cp .env.example .env
   ```

3. Customize `.env` with your desired values

4. Restart:
   ```bash
   docker compose up --build
   ```

---

**Date**: November 29, 2025  
**Status**: ✅ Implemented & Tested
