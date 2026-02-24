#!/bin/bash
# scripts/security-check.sh
# 安全扫描脚本

set -e

echo "🔒 Starting security checks..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Backend directory
cd "$(dirname "$0")/../backend" || exit 1

echo -e "\n${YELLOW}📦 Checking Python dependencies...${NC}"
if command -v safety &> /dev/null; then
    safety check || true
else
    echo -e "${YELLOW}⚠️  safety not installed, skipping dependency check${NC}"
    echo "   Install with: pip install safety"
fi

echo -e "\n${YELLOW}🔍 Running Bandit security linter...${NC}"
if command -v bandit &> /dev/null; then
    bandit -r app -f json -o bandit-report.json || true
    bandit -r app -ll || true
else
    echo -e "${YELLOW}⚠️  bandit not installed, skipping security lint${NC}"
    echo "   Install with: pip install bandit"
fi

echo -e "\n${YELLOW}🔐 Checking for secrets in code...${NC}"
if command -v detect-secrets &> /dev/null; then
    detect-secrets scan --all-files --force-use-all-plugins || true
else
    echo -e "${YELLOW}⚠️  detect-secrets not installed, skipping secret scan${NC}"
    echo "   Install with: pip install detect-secrets"
fi

# Frontend directory
cd "../frontend" || exit 1

echo -e "\n${YELLOW}📦 Checking Node.js dependencies...${NC}"
if command -v npm &> /dev/null; then
    npm audit --audit-level=high || true
else
    echo -e "${YELLOW}⚠️  npm not found${NC}"
fi

echo -e "\n${GREEN}✅ Security checks completed${NC}"
echo "   Check bandit-report.json for detailed findings"
