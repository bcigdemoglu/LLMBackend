#!/bin/bash

# Database LLM Wizard - Master Run Script
# This script orchestrates the entire wizard setup and testing process

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
WIZARD_DIR=$(dirname $(dirname $(realpath $0)))
SCRIPTS_DIR="$WIZARD_DIR/scripts"
LOG_FILE="$WIZARD_DIR/wizard_debug.log"

# Functions
log() {
    echo -e "${GREEN}[$(date +'%H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
    exit 1
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

check_dependencies() {
    log "🔍 Checking dependencies..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed. Please install Docker first."
    fi
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        error "Python 3 is not installed."
    fi
    
    # Check if .env has OpenAI key
    if ! grep -q "OPENAI_API_KEY=sk-" "$WIZARD_DIR/.env" 2>/dev/null; then
        warning "OpenAI API key not found in .env file!"
        echo "Please add your OpenAI API key to .env file:"
        echo "OPENAI_API_KEY=sk-your-key-here"
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    log "✅ Dependencies check passed"
}

install_python_deps() {
    log "📦 Installing Python dependencies with uv..."
    cd "$WIZARD_DIR"
    
    # Check if uv is installed
    if ! command -v uv &> /dev/null; then
        log "Installing uv..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
        source $HOME/.cargo/env
    fi
    
    # Create virtual environment if it doesn't exist
    if [ ! -d ".venv" ]; then
        log "Creating virtual environment..."
        uv venv
    fi
    
    # Install requirements
    uv pip install -r requirements.txt
    
    # Install additional testing dependencies
    uv pip install psycopg2-binary aiohttp
    
    log "✅ Python dependencies installed"
}

start_database() {
    log "🐳 Starting PostgreSQL database..."
    "$SCRIPTS_DIR/start-db.sh" >> "$LOG_FILE" 2>&1
    
    # Give PostgreSQL a moment to fully start
    sleep 5
    
    log "✅ Database started"
}

seed_database() {
    log "🌱 Seeding database with test data..."
    uv run python "$SCRIPTS_DIR/seed-db.py" >> "$LOG_FILE" 2>&1
    log "✅ Database seeded"
}

start_wizard_server() {
    log "🧙‍♂️ Starting wizard server..."
    
    # Kill any existing uvicorn process
    pkill -f "uvicorn main:app" || true
    
    # Start server in background
    cd "$WIZARD_DIR"
    uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000 >> "$LOG_FILE" 2>&1 &
    SERVER_PID=$!
    
    # Wait for server to start
    log "Waiting for server to be ready..."
    for i in {1..30}; do
        if curl -s http://localhost:8000/ > /dev/null 2>&1; then
            log "✅ Wizard server is ready (PID: $SERVER_PID)"
            return 0
        fi
        sleep 1
    done
    
    error "Server failed to start. Check $LOG_FILE for details"
}

run_tests() {
    log "🧪 Running wizard tests..."
    
    cd "$WIZARD_DIR"
    
    # Run specific test if provided
    if [ -n "$1" ]; then
        log "Running specific test: $1"
        uv run python -c "
import asyncio
from scripts.test_wizard import WizardTester

async def run_single_test(question):
    async with WizardTester() as tester:
        result = await tester.ask_wizard(question)
        tester.print_result(result)

asyncio.run(run_single_test('$1'))
"
    else
        # Run full test suite
        uv run python "$SCRIPTS_DIR/test-wizard.py"
    fi
}

stop_server() {
    log "🛑 Stopping wizard server..."
    pkill -f "uvicorn main:app" || true
    log "✅ Server stopped"
}

show_logs() {
    echo ""
    log "📋 Recent server logs:"
    echo "========================"
    tail -n 50 "$LOG_FILE" | grep -E "(ERROR|WARNING|wizard|agent)" || true
    echo "========================"
    echo "Full logs available at: $LOG_FILE"
}

debug_mode() {
    log "🐛 Starting in debug mode..."
    
    cd "$WIZARD_DIR"
    
    # Start server with more verbose logging
    PYTHONUNBUFFERED=1 uv run uvicorn main:app --reload --log-level debug
}

interactive_mode() {
    log "💬 Starting interactive mode..."
    
    cd "$WIZARD_DIR"
    
    uv run python -c "
import asyncio
import aiohttp
import json

async def interactive():
    print('🧙‍♂️ Database LLM Wizard - Interactive Mode')
    print('Type your questions (or \"exit\" to quit)')
    print('='*50)
    
    async with aiohttp.ClientSession() as session:
        while True:
            question = input('\\n🔮 Ask: ').strip()
            if question.lower() in ['exit', 'quit', 'q']:
                break
                
            try:
                async with session.post(
                    'http://localhost:8000/ask',
                    json={'question': question}
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        print(f\"✨ Answer: {result['answer']}\")
                    else:
                        print(f\"❌ Error: {await response.text()}\")
            except Exception as e:
                print(f'❌ Error: {e}')
                
    print('\\n👋 Goodbye!')

asyncio.run(interactive())
"
}

# Main menu
show_menu() {
    echo ""
    echo "🧙‍♂️ Database LLM Wizard - Control Panel"
    echo "========================================"
    echo "1) Full Setup & Test (recommended for first run)"
    echo "2) Start Wizard Server only"
    echo "3) Run Tests only"
    echo "4) Interactive Mode (chat with wizard)"
    echo "5) Debug Mode (verbose logging)"
    echo "6) Seed Database only"
    echo "7) Show Recent Logs"
    echo "8) Stop Everything"
    echo "9) Run Single Test Query"
    echo "0) Exit"
    echo "========================================"
}

# Parse command line arguments
case "$1" in
    "setup")
        log "🚀 Running full setup..."
        check_dependencies
        install_python_deps
        start_database
        seed_database
        start_wizard_server
        run_tests
        ;;
    "start")
        check_dependencies
        start_wizard_server
        ;;
    "test")
        run_tests "$2"
        ;;
    "debug")
        check_dependencies
        debug_mode
        ;;
    "interactive"|"chat")
        interactive_mode
        ;;
    "logs")
        show_logs
        ;;
    "stop")
        stop_server
        ;;
    *)
        # Interactive menu
        while true; do
            show_menu
            read -p "Select option: " choice
            
            case $choice in
                1)
                    log "🚀 Running full setup..."
                    check_dependencies
                    install_python_deps
                    start_database
                    seed_database
                    start_wizard_server
                    run_tests
                    ;;
                2)
                    check_dependencies
                    start_wizard_server
                    ;;
                3)
                    run_tests
                    ;;
                4)
                    interactive_mode
                    ;;
                5)
                    check_dependencies
                    debug_mode
                    ;;
                6)
                    seed_database
                    ;;
                7)
                    show_logs
                    ;;
                8)
                    stop_server
                    "$SCRIPTS_DIR/stop-db.sh"
                    ;;
                9)
                    read -p "Enter your question: " question
                    run_tests "$question"
                    ;;
                0)
                    log "👋 Exiting..."
                    exit 0
                    ;;
                *)
                    warning "Invalid option"
                    ;;
            esac
            
            read -p "Press Enter to continue..."
        done
        ;;
esac