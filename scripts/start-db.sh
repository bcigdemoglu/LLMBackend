#!/bin/bash

# Database LLM Wizard - Local PostgreSQL Setup
# This script starts a lightweight PostgreSQL instance for testing our wizard

set -e

DB_NAME="wizard_test"
DB_USER="wizard"
DB_PASSWORD="magic123"
DB_PORT="5432"
CONTAINER_NAME="wizard-postgres"

echo "🧙‍♂️ Starting Database LLM Wizard PostgreSQL..."

# Check if container already exists
if docker ps -a --format 'table {{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "📦 Container ${CONTAINER_NAME} already exists"
    
    # Check if it's running
    if docker ps --format 'table {{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        echo "✅ PostgreSQL is already running"
    else
        echo "🔄 Starting existing container..."
        docker start ${CONTAINER_NAME}
    fi
else
    echo "🆕 Creating new PostgreSQL container..."
    docker run --name ${CONTAINER_NAME} \
        -e POSTGRES_DB=${DB_NAME} \
        -e POSTGRES_USER=${DB_USER} \
        -e POSTGRES_PASSWORD=${DB_PASSWORD} \
        -p ${DB_PORT}:5432 \
        -d postgres:15-alpine
fi

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
sleep 3

# Test connection
echo "🔍 Testing database connection..."
docker exec ${CONTAINER_NAME} pg_isready -U ${DB_USER} -d ${DB_NAME}

if [ $? -eq 0 ]; then
    echo "✨ PostgreSQL is ready!"
    echo ""
    echo "🔗 Connection Details:"
    echo "   Host: localhost"
    echo "   Port: ${DB_PORT}"
    echo "   Database: ${DB_NAME}"
    echo "   Username: ${DB_USER}"
    echo "   Password: ${DB_PASSWORD}"
    echo ""
    echo "📝 DATABASE_URL: postgresql://${DB_USER}:${DB_PASSWORD}@localhost:${DB_PORT}/${DB_NAME}"
    echo ""
    echo "🛑 To stop: docker stop ${CONTAINER_NAME}"
    echo "🗑️  To remove: docker stop ${CONTAINER_NAME} && docker rm ${CONTAINER_NAME}"
else
    echo "❌ Failed to connect to PostgreSQL"
    exit 1
fi