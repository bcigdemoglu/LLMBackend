# Database LLM Wizard - Scripts

This directory contains scripts to help you set up and test the Database LLM Wizard locally.

## Quick Start

### 1. Start PostgreSQL Database
```bash
./scripts/start-db.sh
```
This will:
- Start a PostgreSQL container with Docker
- Create a database called `wizard_test`
- Set up user `wizard` with password `magic123`
- Configure the database to run on port 5432

### 2. Install Python Dependencies for Seeding
```bash
pip install psycopg2-binary
```

### 3. Seed Test Data
```bash
python scripts/seed-db.py
```
This creates sample data for:
- **E-commerce**: customers, products, orders
- **Blog**: users, posts, comments  
- **Library**: authors, books, borrowers

### 4. Start the Wizard Server
```bash
# Install dependencies first
pip install -r requirements.txt

# Set your OpenAI API key in .env
# DATABASE_URL is already configured for local testing

# Start the server
uvicorn main:app --reload
```

### 5. Test the Wizard
```bash
# Install test dependencies
pip install aiohttp

# Run comprehensive tests
python scripts/test-wizard.py
```

## Scripts Overview

### Database Management
- **`start-db.sh`** - Start PostgreSQL container
- **`stop-db.sh`** - Stop (and optionally remove) PostgreSQL container
- **`seed-db.py`** - Populate database with test data

### Testing
- **`test-wizard.py`** - Comprehensive test suite for the wizard

## Example Test Queries

Once everything is running, you can test these natural language queries:

### Basic Operations
- "What tables exist in the database?"
- "Show me all customers"
- "How many products do we have?"

### Data Creation
- "Add a new customer named John Doe with email john@example.com"
- "Create a new product called Magic Wand with price $99.99"

### Complex Queries
- "Show me all customers who have placed orders"
- "Find all books by British authors"
- "What are the top 3 best-selling product categories?"

### Schema Operations
- "Describe the structure of the customers table"
- "Create a new table called reviews"
- "Add a phone_verified column to customers"

## Troubleshooting

### Database Connection Issues
```bash
# Check if container is running
docker ps

# Check logs
docker logs wizard-postgres

# Restart container
./scripts/stop-db.sh
./scripts/start-db.sh
```

### Server Issues
- Make sure your OpenAI API key is set in `.env`
- Check that all dependencies are installed: `pip install -r requirements.txt`
- Verify the server is running: `curl http://localhost:8000/`

### Seeding Issues
- Make sure PostgreSQL is running
- Install psycopg2: `pip install psycopg2-binary`
- Check database connection settings in `seed-db.py`

## Clean Up

To completely remove the test database:
```bash
./scripts/stop-db.sh
# Choose 'y' when asked to remove container
```