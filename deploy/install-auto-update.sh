#!/bin/bash

# Install automated data update service
# This is OPTIONAL - only run if you want automatic daily data regeneration

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}Installing automated data update service...${NC}"

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}This script must be run as root or with sudo${NC}"
   exit 1
fi

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"

# Copy service files to systemd directory
cp ${REPO_DIR}/deploy/systemd/cfb-swiss-update.service /etc/systemd/system/
cp ${REPO_DIR}/deploy/systemd/cfb-swiss-update.timer /etc/systemd/system/

# Update the WorkingDirectory in the service file to match actual repo location
sed -i "s|/var/www/college-football-swiss-repo|${REPO_DIR}|g" /etc/systemd/system/cfb-swiss-update.service

# Reload systemd
systemctl daemon-reload

# Enable and start the timer
systemctl enable cfb-swiss-update.timer
systemctl start cfb-swiss-update.timer

echo -e "${GREEN}✓ Automated update service installed${NC}"
echo ""
echo "Service will run daily at 3:00 AM"
echo ""
echo "Useful commands:"
echo "  - Check timer status: sudo systemctl status cfb-swiss-update.timer"
echo "  - Check service status: sudo systemctl status cfb-swiss-update.service"
echo "  - View logs: sudo journalctl -u cfb-swiss-update.service"
echo "  - Run manually now: sudo systemctl start cfb-swiss-update.service"
echo "  - Disable auto-update: sudo systemctl disable cfb-swiss-update.timer"
echo ""
