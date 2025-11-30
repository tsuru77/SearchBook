#!/bin/bash

echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║         SearchBook PostgreSQL Edition - Verification Script          ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ERRORS=0

# Function to check file existence
check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} $1"
    else
        echo -e "${RED}✗${NC} $1 (MISSING)"
        ((ERRORS++))
    fi
}

# Function to check directory existence
check_dir() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✓${NC} $1/"
    else
        echo -e "${RED}✗${NC} $1/ (MISSING)"
        ((ERRORS++))
    fi
}

echo "📁 Directory Structure:"
check_dir "backend"
check_dir "frontend"
check_dir "ingestion"

echo ""
echo "📄 Backend Configuration Files:"
check_file "backend/requirements.txt"
check_file "backend/.env.example"
check_file "backend/app/core/config.py"
check_file "backend/app/core/database.py"
check_file "backend/init_db.sql"

echo ""
echo "🔧 Backend Services:"
check_file "backend/app/services/search_service.py"
check_file "backend/app/services/books_service.py"
check_file "backend/app/services/suggestions_service.py"

# Check that elasticsearch.py is NOT present
if [ ! -f "backend/app/services/elasticsearch.py" ]; then
    echo -e "${GREEN}✓${NC} elasticsearch.py (removed)"
else
    echo -e "${RED}✗${NC} elasticsearch.py (should be removed)"
    ((ERRORS++))
fi

echo ""
echo "🚀 Ingestion Pipeline:"
check_file "ingestion/load_books.py"

echo ""
echo "🐳 Docker Configuration:"
check_file "docker-compose.yml"
if [ -f "Dockerfile" ] || [ -f "DockerFile" ]; then
    echo -e "${GREEN}✓${NC} Dockerfile"
else
    echo -e "${RED}✗${NC} Dockerfile (MISSING)"
    ((ERRORS++))
fi
check_file "nginx.conf"

echo ""
echo "📚 Documentation:"
check_file "QUICKSTART.md"
check_file "POSTGRESQL_MIGRATION.md"
check_file "VERIFICATION.sh"

echo ""
echo "📦 Dependencies Check:"
if grep -q "psycopg2-binary" backend/requirements.txt; then
    echo -e "${GREEN}✓${NC} psycopg2-binary in requirements.txt"
else
    echo -e "${RED}✗${NC} psycopg2-binary missing from requirements.txt"
    ((ERRORS++))
fi

if grep -q "rank-bm25" backend/requirements.txt; then
    echo -e "${GREEN}✓${NC} rank-bm25 in requirements.txt"
else
    echo -e "${RED}✗${NC} rank-bm25 missing from requirements.txt"
    ((ERRORS++))
fi

if ! grep -q "elasticsearch" backend/requirements.txt; then
    echo -e "${GREEN}✓${NC} elasticsearch removed from requirements.txt"
else
    echo -e "${RED}✗${NC} elasticsearch still in requirements.txt"
    ((ERRORS++))
fi

echo ""
echo "🔍 Code Quality Checks:"

# Check for Elasticsearch imports in critical files
if ! grep -r "from elasticsearch" backend/app/services/ 2>/dev/null | grep -v ".pyc" > /dev/null; then
    echo -e "${GREEN}✓${NC} No elasticsearch imports in services"
else
    echo -e "${RED}✗${NC} elasticsearch imports still present"
    ((ERRORS++))
fi

if grep -q "from app.core.database import" backend/app/services/search_service.py; then
    echo -e "${GREEN}✓${NC} search_service.py uses PostgreSQL utilities"
else
    echo -e "${RED}✗${NC} search_service.py missing PostgreSQL utilities"
    ((ERRORS++))
fi

if grep -q "BM25Okapi" backend/app/services/search_service.py; then
    echo -e "${GREEN}✓${NC} search_service.py implements BM25"
else
    echo -e "${RED}✗${NC} BM25Okapi not found in search_service.py"
    ((ERRORS++))
fi

echo ""
echo "═════════════════════════════════════════════════════════════════════════"

if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✅ All checks passed! Ready to start.${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Review QUICKSTART.md for setup instructions"
    echo "  2. Run: docker compose up --build"
    echo "  3. Test API at: http://localhost:8000/docs"
    exit 0
else
    echo -e "${RED}❌ $ERRORS issue(s) found. Please review the above.${NC}"
    exit 1
fi
