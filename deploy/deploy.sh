#!/bin/bash

# College Football Swiss - VPS Deployment Script
# Run this script on your Digital Ocean VPS after cloning the repository

set -e  # Exit on any error

echo "=================================="
echo "College Football Swiss Deployment"
echo "=================================="
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="college-football-swiss"
APP_DIR="/var/www/${APP_NAME}"
REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
NGINX_AVAILABLE="/etc/nginx/sites-available"
NGINX_ENABLED="/etc/nginx/sites-enabled"
PYTHON_VERSION="python3"

echo -e "${YELLOW}Step 1: Checking system requirements...${NC}"

# Check if running as root or with sudo
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}This script must be run as root or with sudo${NC}"
   echo "Please run: sudo bash deploy/deploy.sh"
   exit 1
fi

echo -e "${GREEN}✓ Running as root${NC}"

echo ""
echo -e "${YELLOW}Step 2: Installing system dependencies...${NC}"

# Update package lists
apt-get update

# Install required packages
apt-get install -y \
    nginx \
    python3 \
    python3-pip \
    python3-venv \
    git \
    certbot \
    python3-certbot-nginx

echo -e "${GREEN}✓ System dependencies installed${NC}"

echo ""
echo -e "${YELLOW}Step 3: Creating application directory...${NC}"

# Create app directory if it doesn't exist
mkdir -p ${APP_DIR}

# Copy web files to app directory
cp -r ${REPO_DIR}/web/* ${APP_DIR}/

echo -e "${GREEN}✓ Application files copied to ${APP_DIR}${NC}"

echo ""
echo -e "${YELLOW}Step 4: Setting up Python environment...${NC}"

# Create Python virtual environment
cd ${REPO_DIR}
${PYTHON_VERSION} -m venv venv

# Activate virtual environment and install dependencies
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo -e "${GREEN}✓ Python environment set up${NC}"

echo ""
echo -e "${YELLOW}Step 5: Configuring Mapbox token...${NC}"

# Prompt for Mapbox token
read -p "Enter your Mapbox API token (or press Enter to configure later): " MAPBOX_TOKEN

if [ ! -z "$MAPBOX_TOKEN" ]; then
    # Update config.js with the token
    CONFIG_FILE="${APP_DIR}/js/config.js"

    if [ -f "$CONFIG_FILE" ]; then
        sed -i "s/YOUR_MAPBOX_TOKEN_HERE/${MAPBOX_TOKEN}/g" "$CONFIG_FILE"
        echo -e "${GREEN}✓ Mapbox token configured${NC}"
    else
        echo -e "${YELLOW}⚠ Config file not found. You'll need to configure it manually.${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Skipping Mapbox configuration. Remember to update web/js/config.js manually!${NC}"
fi

echo ""
echo -e "${YELLOW}Step 6: Generating GeoJSON data...${NC}"

# Generate initial data
cd ${REPO_DIR}
source venv/bin/activate
python src/export_geojson.py

# Copy generated data to web directory
cp -r web/data/* ${APP_DIR}/data/

echo -e "${GREEN}✓ GeoJSON data generated and copied${NC}"

echo ""
echo -e "${YELLOW}Step 7: Configuring Nginx...${NC}"

# Prompt for domain name
read -p "Enter your domain name (or press Enter for IP-only access): " DOMAIN_NAME

if [ -z "$DOMAIN_NAME" ]; then
    DOMAIN_NAME="_"  # Default Nginx server
    USE_SSL=false
else
    USE_SSL=true
fi

# Create Nginx configuration
cat > ${NGINX_AVAILABLE}/${APP_NAME} <<EOF
server {
    listen 80;
    listen [::]:80;

    server_name ${DOMAIN_NAME};

    root ${APP_DIR};
    index index.html;

    # Logging
    access_log /var/log/nginx/${APP_NAME}_access.log;
    error_log /var/log/nginx/${APP_NAME}_error.log;

    # Main location
    location / {
        try_files \$uri \$uri/ =404;
    }

    # GeoJSON files - set proper MIME type
    location ~* \.geojson$ {
        add_header Content-Type application/json;
        add_header Access-Control-Allow-Origin *;
    }

    # Static assets caching
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/json application/javascript application/xml+rss application/rss+xml font/truetype font/opentype application/vnd.ms-fontobject image/svg+xml;
}
EOF

# Enable the site
ln -sf ${NGINX_AVAILABLE}/${APP_NAME} ${NGINX_ENABLED}/${APP_NAME}

# Remove default site if it exists
if [ -f "${NGINX_ENABLED}/default" ]; then
    rm ${NGINX_ENABLED}/default
fi

# Test Nginx configuration
nginx -t

# Reload Nginx
systemctl reload nginx

echo -e "${GREEN}✓ Nginx configured and reloaded${NC}"

echo ""
echo -e "${YELLOW}Step 8: Setting permissions...${NC}"

# Set proper ownership
chown -R www-data:www-data ${APP_DIR}
chmod -R 755 ${APP_DIR}

echo -e "${GREEN}✓ Permissions set${NC}"

# SSL Setup (if domain provided)
if [ "$USE_SSL" = true ]; then
    echo ""
    echo -e "${YELLOW}Step 9: Setting up SSL with Let's Encrypt...${NC}"
    echo "This will obtain a free SSL certificate from Let's Encrypt"

    read -p "Do you want to set up SSL now? (y/n): " SETUP_SSL

    if [ "$SETUP_SSL" = "y" ] || [ "$SETUP_SSL" = "Y" ]; then
        # Make sure domain is pointing to this server
        echo ""
        echo -e "${YELLOW}⚠ IMPORTANT: Make sure your domain ${DOMAIN_NAME} is pointing to this server's IP!${NC}"
        read -p "Press Enter when ready to continue, or Ctrl+C to cancel..."

        # Run certbot
        certbot --nginx -d ${DOMAIN_NAME}

        echo -e "${GREEN}✓ SSL certificate installed${NC}"
    else
        echo -e "${YELLOW}⚠ Skipping SSL setup. You can run this later:${NC}"
        echo "   sudo certbot --nginx -d ${DOMAIN_NAME}"
    fi
fi

# Create update script
echo ""
echo -e "${YELLOW}Step 10: Creating update script...${NC}"

cat > ${REPO_DIR}/deploy/update.sh <<'UPDATEEOF'
#!/bin/bash

# College Football Swiss - Update Script
# Run this to update the deployment after code changes

set -e

APP_NAME="college-football-swiss"
APP_DIR="/var/www/${APP_NAME}"
REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "Updating College Football Swiss deployment..."

# Pull latest changes
cd ${REPO_DIR}
git pull

# Update Python dependencies
source venv/bin/activate
pip install --upgrade -r requirements.txt

# Regenerate data
python src/export_geojson.py

# Copy updated files
cp -r web/* ${APP_DIR}/

# Set permissions
chown -R www-data:www-data ${APP_DIR}

# Reload Nginx
systemctl reload nginx

echo "✓ Deployment updated successfully!"
UPDATEEOF

chmod +x ${REPO_DIR}/deploy/update.sh

echo -e "${GREEN}✓ Update script created${NC}"

echo ""
echo "=================================="
echo -e "${GREEN}Deployment Complete!${NC}"
echo "=================================="
echo ""
echo "Your application is now running at:"
if [ "$DOMAIN_NAME" = "_" ]; then
    SERVER_IP=$(hostname -I | awk '{print $1}')
    echo -e "  ${GREEN}http://${SERVER_IP}${NC}"
else
    if [ "$USE_SSL" = true ] && [ "$SETUP_SSL" = "y" ]; then
        echo -e "  ${GREEN}https://${DOMAIN_NAME}${NC}"
    else
        echo -e "  ${GREEN}http://${DOMAIN_NAME}${NC}"
    fi
fi
echo ""
echo "Next steps:"
echo "  1. Visit your site in a web browser"
if [ -z "$MAPBOX_TOKEN" ]; then
    echo "  2. Configure Mapbox token in: ${APP_DIR}/js/config.js"
fi
echo "  3. To update in the future, run: sudo bash deploy/update.sh"
echo ""
echo "Useful commands:"
echo "  - View Nginx logs: sudo tail -f /var/log/nginx/${APP_NAME}_access.log"
echo "  - Restart Nginx: sudo systemctl restart nginx"
echo "  - Regenerate data: cd ${REPO_DIR} && source venv/bin/activate && python src/export_geojson.py"
echo ""
