#!/bin/bash

# College Football Swiss - Update Script
# Run this to update the deployment after code changes

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

APP_NAME="college-football-swiss"
APP_DIR="/var/www/${APP_NAME}"
REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "=================================="
echo "College Football Swiss - Update"
echo "=================================="
echo ""

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}This script must be run as root or with sudo${NC}"
   echo "Please run: sudo bash deploy/update.sh"
   exit 1
fi

# Check if app directory exists
if [ ! -d "$APP_DIR" ]; then
    echo -e "${RED}Error: Application directory not found at ${APP_DIR}${NC}"
    echo "Have you run the initial deployment? Run: sudo bash deploy/deploy.sh"
    exit 1
fi

echo -e "${YELLOW}Step 1: Pulling latest changes from Git...${NC}"
cd ${REPO_DIR}
git pull
echo -e "${GREEN}✓ Code updated${NC}"

echo ""
echo -e "${YELLOW}Step 2: Updating Python dependencies...${NC}"
source venv/bin/activate
pip install --upgrade pip
pip install --upgrade -r requirements.txt
echo -e "${GREEN}✓ Dependencies updated${NC}"

echo ""
echo -e "${YELLOW}Step 3: Regenerating GeoJSON data...${NC}"
python src/export_geojson.py
echo -e "${GREEN}✓ Data regenerated${NC}"

echo ""
echo -e "${YELLOW}Step 4: Copying updated files to web directory...${NC}"

# Backup current config if it has a Mapbox token
if [ -f "${APP_DIR}/js/config.js" ]; then
    if grep -q "pk\." "${APP_DIR}/js/config.js"; then
        echo "  Backing up existing config.js (contains Mapbox token)..."
        cp ${APP_DIR}/js/config.js /tmp/config.js.backup
        RESTORE_CONFIG=true
    fi
fi

# Copy all web files
cp -r ${REPO_DIR}/web/* ${APP_DIR}/

# Restore config if we backed it up
if [ "$RESTORE_CONFIG" = true ]; then
    echo "  Restoring config.js with your Mapbox token..."
    cp /tmp/config.js.backup ${APP_DIR}/js/config.js
    rm /tmp/config.js.backup
fi

echo -e "${GREEN}✓ Files copied${NC}"

echo ""
echo -e "${YELLOW}Step 5: Setting permissions...${NC}"
chown -R www-data:www-data ${APP_DIR}
chmod -R 755 ${APP_DIR}
echo -e "${GREEN}✓ Permissions set${NC}"

echo ""
echo -e "${YELLOW}Step 6: Reloading Nginx...${NC}"
nginx -t  # Test configuration
systemctl reload nginx
echo -e "${GREEN}✓ Nginx reloaded${NC}"

echo ""
echo "=================================="
echo -e "${GREEN}Update Complete!${NC}"
echo "=================================="
echo ""
echo "Your site has been updated with the latest code and data."
echo ""
echo "To verify:"
echo "  1. Visit your site and check that everything works"
echo "  2. Check logs: sudo tail -f /var/log/nginx/${APP_NAME}_access.log"
echo ""
