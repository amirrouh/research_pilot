#!/bin/bash
# Project runner script - ADHD-friendly: clean, minimal, organized

set -e  # Exit on error

# Colors for clean output
BLUE='\033[0;34m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

case "$1" in
    documentation)
        case "$2" in
            build)
                echo -e "${BLUE}Building documentation...${NC}"
                uv run mkdocs build
                echo -e "${GREEN}✓ Built to site/${NC}"
                ;;

            serve)
                echo -e "${BLUE}Starting documentation server...${NC}"
                echo -e "${GREEN}✓ Open http://127.0.0.1:8000${NC}"
                uv run mkdocs serve
                ;;
            *)
                echo "Usage: ./run.sh documentation [build|serve]"
                exit 1
                ;;
        esac
        ;;

    help|--help|-h|"")
        echo ""
        echo "run.sh - Project Runner"
        echo ""
        echo "Usage:"
        echo "  ./run.sh documentation build    Build docs to site/"
        echo "  ./run.sh documentation serve    Start docs dev server (http://127.0.0.1:8000)"
        echo "  ./run.sh help                   Show this help"
        echo ""
        ;;

    *)
        echo "Unknown command: $1"
        echo "Run './run.sh help' for usage"
        exit 1
        ;;
esac
