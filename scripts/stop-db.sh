#!/bin/bash

# Database LLM Wizard - Stop Local PostgreSQL
# This script stops and optionally removes the test database

CONTAINER_NAME="wizard-postgres"

echo "🧙‍♂️ Stopping Database LLM Wizard PostgreSQL..."

if docker ps --format 'table {{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "🛑 Stopping PostgreSQL container..."
    docker stop ${CONTAINER_NAME}
    echo "✅ PostgreSQL stopped"
else
    echo "ℹ️  PostgreSQL container is not running"
fi

# Ask if user wants to remove the container
read -p "🗑️  Remove container completely? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if docker ps -a --format 'table {{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        docker rm ${CONTAINER_NAME}
        echo "🗑️  Container removed"
    else
        echo "ℹ️  Container doesn't exist"
    fi
else
    echo "📦 Container preserved (use 'docker start ${CONTAINER_NAME}' to restart)"
fi