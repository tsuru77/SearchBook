#!/bin/bash
# Script to apply the click suggestions migration

echo "Applying migration 003_click_suggestions.sql..."
docker compose exec -T postgres psql -U searchbook -d searchbook < ../database/migrations/003_click_suggestions.sql

if [ $? -eq 0 ]; then
    echo "Migration applied successfully!"
else
    echo "Error applying migration. Make sure the postgres container is running."
fi
