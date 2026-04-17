#!/bin/bash
# FlowBridge - Linux Setup Script
# Run: bash setup-linux.sh

set -e

CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
GRAY='\033[0;37m'
NC='\033[0m'

echo ""
echo -e "${CYAN}==========================================${NC}"
echo -e "${CYAN}  FlowBridge - Linux Auto Setup${NC}"
echo -e "${CYAN}==========================================${NC}"
echo ""

# Step 1: Docker
echo -e "${YELLOW}[1/7] Checking Docker...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}  ERROR: Docker not installed${NC}"
    echo -e "${YELLOW}  Install: curl -fsSL https://get.docker.com | sudo sh${NC}"
    exit 1
fi
echo -e "${GREEN}  OK: $(docker --version)${NC}"

# Step 2: Docker daemon
echo -e "${YELLOW}[2/7] Checking Docker daemon...${NC}"
if ! docker ps &> /dev/null; then
    echo -e "${RED}  ERROR: Docker daemon not running. sudo systemctl start docker${NC}"
    exit 1
fi
echo -e "${GREEN}  OK: Docker daemon running${NC}"

# Step 3: Project root
PROJECT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." &> /dev/null && pwd )"
cd "$PROJECT_ROOT"
echo -e "${GREEN}[3/7] Project dir: $PROJECT_ROOT${NC}"

# Step 4: Folders
echo -e "${YELLOW}[4/7] Creating folders...${NC}"
mkdir -p "$PROJECT_ROOT/setup"
mkdir -p "$PROJECT_ROOT/chrome-profile"
echo -e "${GREEN}  OK: setup/ and chrome-profile/ ready${NC}"

# Step 5: .env
echo -e "${YELLOW}[5/7] Configuring .env...${NC}"
if [ ! -f "$PROJECT_ROOT/.env" ]; then
    read -p "  Enter your Google Sheet ID: " SHEET_ID
    cat > "$PROJECT_ROOT/.env" <<EOF
GOOGLE_SHEET_ID=$SHEET_ID
CHROME_PROFILE_PATH=/app/chrome-profile
EOF
    echo -e "${GREEN}  OK: .env created${NC}"
else
    echo -e "${GRAY}  SKIP: .env already exists${NC}"
fi

# Step 6: credentials.json
echo -e "${YELLOW}[6/7] Checking credentials.json...${NC}"
CRED_PATH="$PROJECT_ROOT/setup/credentials.json"
if [ ! -f "$CRED_PATH" ]; then
    echo -e "${RED}  MISSING: setup/credentials.json${NC}"
    echo ""
    echo -e "${YELLOW}  Download from Google Cloud Console:${NC}"
    echo "  1. Go to https://console.cloud.google.com"
    echo "  2. APIs and Services -> Credentials"
    echo "  3. Create OAuth 2.0 Client ID (Desktop app)"
    echo "  4. Download JSON"
    echo "  5. Save to: $CRED_PATH"
    echo ""
    read -p "  Press Enter once credentials.json is in place: "
    if [ ! -f "$CRED_PATH" ]; then
        echo -e "${RED}  ERROR: credentials.json still missing. Exit.${NC}"
        exit 1
    fi
fi
echo -e "${GREEN}  OK: credentials.json found${NC}"

# Step 7: Build + run
echo -e "${YELLOW}[7/7] Building and starting container...${NC}"
docker compose build
docker compose up -d

echo ""
echo -e "${GREEN}==========================================${NC}"
echo -e "${GREEN}  SUCCESS: FlowBridge running!${NC}"
echo -e "${GREEN}==========================================${NC}"
echo ""
echo -e "${CYAN}Next steps:${NC}"
echo "  1. First-time WhatsApp login:"
echo "     - Install VNC viewer: sudo apt install tigervnc-viewer"
echo "     - Connect: vncviewer localhost:5900"
echo "     - Scan QR code with your phone"
echo ""
echo "  2. View logs:    docker compose logs -f"
echo "  3. Stop:         docker compose down"
echo "  4. Restart:      docker compose restart"
echo ""
