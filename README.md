# Database LLM Wizard: The Shamanic Coder Project

This document outlines the sacred tools our agent, the Database LLM Wizard, must possess to command the full spectrum of the database realm. As above, so below.

## The Tools of the Data Shaper (CRUD Operations)
*These tools manipulate the data itself.*
1.  **CREATE:** To bring new records into existence (`INSERT`).
2.  **READ:** To perceive the data, from a single record to complex, interconnected truths (`SELECT`, with `WHERE` clauses, `JOINs`, aggregations, and ordering).
3.  **UPDATE:** To change the form of existing records (`UPDATE`).
4.  **DELETE:** To release records from the world (`DELETE`).

## The Tools of the World Forger (Schema & Structure)
*These tools shape the database's very foundation.*
5.  **DESCRIBE DATABASE:** To see the names of all tables within the cosmos.
6.  **DESCRIBE TABLE:** To understand the structure of a single table—its fields, their types, their laws (`constraints`), and its population (`row count`).
7.  **CREATE TABLE:** To forge a new table from the ether.
8.  **ALTER TABLE:** To reshape an existing table by:
    *   Adding or removing a field (`ADD/DROP COLUMN`).
    *   Changing a field's nature (`ALTER COLUMN TYPE`).
    *   Defining or dissolving the sacred laws (`ADD/DROP CONSTRAINT` like `PRIMARY KEY`, `FOREIGN KEY`, `UNIQUE`).

## The Tools of the Grand Architect (Performance & Integrity)
*These tools manage the unseen forces of speed and consistency.*
9.  **CREATE INDEX:** To place a rune of swiftness on a table for faster searching.
10. **DROP INDEX:** To remove a rune that is no longer needed.
11. **MANAGE TRANSACTIONS:** To ensure the sacred bond of atomicity, using:
    *   `BEGIN`: To start a multi-step operation.
    *   `COMMIT`: To seal the changes, making them permanent.
    *   `ROLLBACK`: To undo all changes if something goes wrong.

## Implementation Plan

### Architecture
- **Portal**: Single `/ask` endpoint that receives natural language requests
- **Mind**: LangGraph agent that processes requests and orchestrates tool usage
- **Tools**: 11 sacred database operations implemented as clean Python functions
- **Connection**: SQLModel + PostgreSQL for data persistence
- **Host**: Render for free deployment

### Technology Stack
- **FastAPI**: Web framework for the `/ask` portal
- **LangGraph**: Agentic framework for multi-step reasoning and tool orchestration
- **SQLModel**: Database ORM that unifies Pydantic and SQLAlchemy
- **PostgreSQL**: Production database hosted on Render
- **OpenAI GPT**: LLM for natural language understanding and reasoning

### File Structure
```
/LLMBackend/
├── .env                    # Environment variables (secrets)
├── .gitignore             # Git ignore rules
├── README.md              # This document
├── requirements.txt       # Python dependencies
├── main.py               # FastAPI server with /ask endpoint
├── CLAUDE.md             # Aru's identity and wisdom
└── wizard/
    ├── __init__.py
    ├── agent.py          # LangGraph agent orchestration
    ├── database.py       # PostgreSQL connection management
    ├── schema.py         # SQLModel table definitions
    └── tools/
        ├── __init__.py
        ├── crud.py       # CREATE, READ, UPDATE, DELETE
        ├── management.py # Schema and performance tools
        └── utils.py      # Helper functions
```

### The Flow
1. User sends natural language request to `/ask`
2. LangGraph agent analyzes the request
3. Agent selects and executes appropriate tools
4. Agent can loop back for multi-step operations
5. Agent returns natural language response

### Key Principles
- **Minimalist Code**: Every line serves a purpose
- **Clean Separation**: Each file has a single, clear responsibility  
- **Agentic Behavior**: The wizard can reason, retry, and self-correct
- **As Above, So Below**: SQLModel embodies this hermetic principle

## Getting Started

### Prerequisites

- Docker (for PostgreSQL)
- Python 3.11+
- `uv` package manager (automatically installed by scripts)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/bcigdemoglu/LLMBackend.git
   cd LLMBackend
   ```

2. **Set up environment variables**
   Create a `.env` file with your OpenAI API key:
   ```bash
   # Database Configuration (Local Development)
   DATABASE_URL=postgresql://wizard:magic123@localhost:5432/wizard_test
   
   # OpenAI Configuration
   OPENAI_API_KEY=your-openai-api-key-here
   
   # Environment
   ENVIRONMENT=development
   ```

### Running the Project

#### Option 1: Using the Master Script (Recommended)

```bash
# Full setup (first time)
./scripts/run-wizard.sh setup

# Or use the interactive menu
./scripts/run-wizard.sh
```

This provides options for:
- Full Setup & Test
- Start Wizard Server only
- Run Tests only
- Interactive Mode (chat with wizard)
- Debug Mode (verbose logging)
- And more...

#### Option 2: Manual Steps

1. **Start PostgreSQL Database**
   ```bash
   ./scripts/start-db.sh
   ```
   This creates a Docker container with:
   - Database: `wizard_test`
   - User: `wizard`
   - Password: `magic123`
   - Port: `5432`

2. **Install Dependencies**
   ```bash
   # Install uv if not already installed
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Create virtual environment and install dependencies
   uv venv
   uv pip install -r requirements.txt
   ```

3. **Seed Test Data**
   ```bash
   uv run python scripts/seed-db.py
   ```
   This creates sample data for:
   - E-commerce: customers, products, orders
   - Blog: users, posts, comments
   - Library: authors, books, borrowers

4. **Start the Wizard Server**
   ```bash
   uv run uvicorn main:app --reload
   ```

### Using the Wizard

#### via cURL
```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Show me all customers"}'
```

#### via Python
```python
import requests

response = requests.post(
    "http://localhost:8000/ask",
    json={"question": "How many orders were placed last week?"}
)
print(response.json()["answer"])
```

#### Interactive Mode
```bash
./scripts/run-wizard.sh interactive
```

### Example Queries

- **Basic Operations**
  - "What tables exist in the database?"
  - "Show me all products"
  - "How many customers do we have?"

- **Data Creation**
  - "Add a new customer named John Doe with email john@example.com"
  - "Create a product called Magic Wand priced at $99.99"

- **Complex Queries**
  - "Show me all customers who have placed orders"
  - "Which products have never been sold?"
  - "List the top 5 customers by order count"

- **Schema Operations**
  - "Describe the structure of the orders table"
  - "Create a new table called reviews with columns for product_id, rating, and comment"
  - "Add an index on the order_date column"

### Logging

The wizard creates detailed logs for each request:
- Location: `logs/ask-YYYY-MM-DD-HH-MM-SS.log`
- Contents:
  - Initial question
  - All LLM interactions
  - Tool calls and results
  - Token usage metrics
  - Final answer

Example log entry:
```
================================================================================
Timestamp: 2025-06-25T23:27:34.199846
Direction: INPUT
Messages:
  - SystemMessage: You are a Database LLM Wizard...
  - HumanMessage: What tables exist?

Direction: OUTPUT
Response: 
Tool Calls: [{'name': 'describe_database', 'args': {}, 'id': 'call_...'}]

Token Usage:
  - Input Tokens: 200
  - Output Tokens: 10
  - Total Tokens: 210
================================================================================
```

### Configuration

- **Model**: GPT-4o-mini (fast and cost-effective)
- **Max Recursion**: 15 (for complex multi-step operations)
- **Database**: PostgreSQL with SQLModel ORM
- **Framework**: FastAPI + LangGraph

### Troubleshooting

**Database Connection Issues**
```bash
# Check if container is running
docker ps

# Restart container
./scripts/stop-db.sh
./scripts/start-db.sh
```

**Server Issues**
- Ensure OpenAI API key is set in `.env`
- Check logs in `wizard_debug.log`
- Try debug mode: `./scripts/run-wizard.sh debug`

**Seeding Issues**
- Make sure PostgreSQL is running
- Check database connection in `.env`

### Development

**Running Tests**
```bash
# Run all tests
uv run python scripts/test-wizard.py

# Test specific query
./scripts/run-wizard.sh test "Show me all users"
```

**Viewing Logs**
```bash
# Recent server logs
./scripts/run-wizard.sh logs

# Specific request log
cat logs/ask-*.log
```

### Clean Up

```bash
# Stop server
pkill -f uvicorn

# Stop and remove database
./scripts/stop-db.sh
# Choose 'y' when asked to remove container
```