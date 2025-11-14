# College Football Swiss - VPS Deployment Guide

This guide will help you deploy the College Football Swiss web application to your Digital Ocean VPS.

## Prerequisites

Before you begin, make sure you have:

- [ ] A Digital Ocean VPS (Droplet) running Ubuntu 20.04 or later
- [ ] SSH access to your VPS (root or sudo user)
- [ ] A Mapbox API token (free tier: https://account.mapbox.com/)
- [ ] (Optional) A domain name pointing to your VPS IP address
- [ ] At least 1GB RAM and 10GB disk space

## Quick Start (Recommended)

If you want to get up and running quickly, follow these steps:

### 1. Connect to Your VPS

Using the Digital Ocean web console or SSH:

```bash
ssh root@your-vps-ip
```

### 2. Clone the Repository

```bash
cd /root
git clone https://github.com/pbailey529/college-football-swiss.git
cd college-football-swiss
```

### 3. Run the Deployment Script

```bash
sudo bash deploy/deploy.sh
```

The script will:
- Install all required system packages (Nginx, Python, etc.)
- Set up a Python virtual environment
- Prompt you for your Mapbox API token
- Generate the GeoJSON data files
- Configure Nginx web server
- Optionally set up SSL/HTTPS with Let's Encrypt

**Note**: The script is interactive and will ask you questions. Have your Mapbox token and domain name ready!

### 4. Access Your Site

Once deployment completes, visit:
- **Without domain**: `http://your-vps-ip`
- **With domain**: `http://your-domain.com` (or `https://` if you set up SSL)

## What Gets Installed

### System Packages
- **nginx** - Web server
- **python3** - Python runtime
- **python3-pip** - Python package manager
- **python3-venv** - Virtual environment support
- **git** - Version control
- **certbot** - SSL certificate management (optional)

### Python Packages
- geopy - Geographic calculations
- networkx - Graph algorithms
- pandas - Data processing
- cfbd - College Football Data API client
- python-dotenv - Environment variable management

### Directory Structure

After deployment:

```
/var/www/college-football-swiss/    # Web application (served by Nginx)
├── index.html
├── css/
├── js/
│   ├── config.js                    # ← Your Mapbox token goes here
│   ├── app.js
│   ├── data.js
│   └── map.js
└── data/
    ├── teams_round0.geojson
    ├── matchups_round1.geojson
    ├── teams_round1.geojson
    └── matchups_round2.geojson

/root/college-football-swiss/        # Source repository
├── src/                              # Python source code
├── web/                              # Web source files
└── deploy/                           # Deployment scripts
```

## Manual Configuration

If you skipped any steps during deployment or need to configure manually:

### Configure Mapbox Token

Edit the config file:

```bash
nano /var/www/college-football-swiss/js/config.js
```

Find the line:
```javascript
MAPBOX_TOKEN: 'YOUR_MAPBOX_TOKEN_HERE',
```

Replace `YOUR_MAPBOX_TOKEN_HERE` with your actual token.

### Regenerate Data

If you need to regenerate the GeoJSON data files:

```bash
cd /root/college-football-swiss
source venv/bin/activate
python src/export_geojson.py
cp -r web/data/* /var/www/college-football-swiss/data/
```

### Configure Domain Name

If you didn't set up a domain during deployment:

1. Edit the Nginx configuration:
   ```bash
   nano /etc/nginx/sites-available/college-football-swiss
   ```

2. Change `server_name` from `_` to your domain:
   ```nginx
   server_name your-domain.com;
   ```

3. Reload Nginx:
   ```bash
   systemctl reload nginx
   ```

### Set Up SSL/HTTPS

If you have a domain and want HTTPS:

```bash
sudo certbot --nginx -d your-domain.com
```

Certbot will:
- Obtain a free SSL certificate from Let's Encrypt
- Automatically configure Nginx for HTTPS
- Set up auto-renewal

## Updating Your Deployment

When you make changes to the code or want to update the data:

### Option 1: Use the Update Script

```bash
cd /root/college-football-swiss
sudo bash deploy/update.sh
```

This script will:
- Pull the latest code from GitHub
- Update Python dependencies
- Regenerate GeoJSON data
- Copy files to the web directory
- Reload Nginx

### Option 2: Manual Update

```bash
cd /root/college-football-swiss
git pull
source venv/bin/activate
pip install --upgrade -r requirements.txt
python src/export_geojson.py
cp -r web/* /var/www/college-football-swiss/
systemctl reload nginx
```

## Optional: Automated Daily Updates

If you want the data to regenerate automatically every day at 3 AM:

```bash
cd /root/college-football-swiss
sudo bash deploy/install-auto-update.sh
```

This installs a systemd timer that runs daily. Useful if you're fetching fresh data from APIs.

Check the status:
```bash
systemctl status cfb-swiss-update.timer
```

View logs:
```bash
journalctl -u cfb-swiss-update.service
```

## Troubleshooting

### Site Not Loading

1. **Check Nginx is running**:
   ```bash
   systemctl status nginx
   ```

2. **Check Nginx error logs**:
   ```bash
   tail -f /var/log/nginx/college-football-swiss_error.log
   ```

3. **Verify files exist**:
   ```bash
   ls -la /var/www/college-football-swiss/
   ```

### Blank Map or Loading Error

1. **Check browser console** (F12 in most browsers)
2. **Verify Mapbox token** is configured in `/var/www/college-football-swiss/js/config.js`
3. **Check data files exist**:
   ```bash
   ls -la /var/www/college-football-swiss/data/
   ```

### Permission Errors

Fix file permissions:
```bash
chown -R www-data:www-data /var/www/college-football-swiss
chmod -R 755 /var/www/college-football-swiss
```

### Firewall Issues

Make sure ports 80 (HTTP) and 443 (HTTPS) are open:

```bash
# Ubuntu/Debian with ufw
ufw allow 'Nginx Full'
ufw status

# Or check iptables
iptables -L -n | grep -E '80|443'
```

On Digital Ocean, also check your Droplet's firewall settings in the web console.

### SSL Certificate Issues

If certbot fails:
1. Make sure your domain DNS is pointing to the VPS IP
2. Check DNS propagation: `nslookup your-domain.com`
3. Try again after DNS propagates (can take up to 48 hours)

## Useful Commands

### Nginx
```bash
# Restart Nginx
systemctl restart nginx

# Reload configuration (no downtime)
systemctl reload nginx

# Test configuration syntax
nginx -t

# View access logs
tail -f /var/log/nginx/college-football-swiss_access.log

# View error logs
tail -f /var/log/nginx/college-football-swiss_error.log
```

### Python Environment
```bash
# Activate virtual environment
cd /root/college-football-swiss
source venv/bin/activate

# Install new package
pip install package-name

# Regenerate data
python src/export_geojson.py

# Deactivate virtual environment
deactivate
```

### System Monitoring
```bash
# Check disk space
df -h

# Check memory usage
free -h

# Check CPU and processes
top

# Check system logs
journalctl -xe
```

## Security Best Practices

### 1. Update Your System Regularly

```bash
apt update && apt upgrade -y
```

### 2. Set Up a Firewall

```bash
ufw enable
ufw allow ssh
ufw allow 'Nginx Full'
```

### 3. Create a Non-Root User

Instead of running everything as root:

```bash
adduser deployuser
usermod -aG sudo deployuser
```

### 4. Use SSH Keys (Not Passwords)

Generate on your local machine:
```bash
ssh-keygen -t ed25519
ssh-copy-id deployuser@your-vps-ip
```

### 5. Keep SSL Certificates Updated

Certbot auto-renews, but you can test renewal:
```bash
certbot renew --dry-run
```

## Advanced Configuration

### Custom Nginx Settings

Edit `/etc/nginx/sites-available/college-football-swiss` to customize:
- Cache headers
- Rate limiting
- IP restrictions
- Custom error pages

After changes:
```bash
nginx -t  # Test configuration
systemctl reload nginx  # Apply changes
```

### Environment Variables

Create a `.env` file for API keys and secrets:

```bash
cd /root/college-football-swiss
nano .env
```

Add:
```env
CFBD_API_KEY=your_college_football_data_api_key
MAPBOX_TOKEN=your_mapbox_token
```

The Python scripts will automatically load these.

### Performance Tuning

For high traffic, edit Nginx worker processes:

```bash
nano /etc/nginx/nginx.conf
```

Adjust based on CPU cores:
```nginx
worker_processes auto;
worker_connections 1024;
```

### Monitoring

Install monitoring tools:

```bash
# htop - better than top
apt install htop

# nginx stats
apt install nginx-extras

# System monitoring
apt install nethogs iotop
```

## Cost Estimation

### Digital Ocean Droplet
- **Basic Droplet**: $6/month (1GB RAM, 1 CPU, 25GB SSD)
- **Recommended**: $12/month (2GB RAM, 1 CPU, 50GB SSD)

### Bandwidth
- Included: 1TB - 2TB outbound transfer
- Typical usage: < 50GB/month for moderate traffic

### Total Monthly Cost
- **Minimum**: $6/month (droplet only)
- **Recommended**: $12/month
- **Domain** (optional): $10-15/year
- **SSL Certificate**: FREE (Let's Encrypt)

## Backup Strategy

### 1. Backup Data Files

```bash
# Create backup directory
mkdir -p /root/backups

# Backup script
cat > /root/backup.sh <<'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
tar -czf /root/backups/cfb-swiss-$DATE.tar.gz \
  /root/college-football-swiss \
  /var/www/college-football-swiss \
  /etc/nginx/sites-available/college-football-swiss
EOF

chmod +x /root/backup.sh
```

### 2. Automated Backups

Use Digital Ocean's built-in backup feature (adds 20% to droplet cost) or set up a cron job:

```bash
crontab -e
```

Add:
```cron
# Daily backup at 2 AM
0 2 * * * /root/backup.sh
```

### 3. Download Backups

From your local machine:
```bash
scp root@your-vps-ip:/root/backups/cfb-swiss-*.tar.gz ./
```

## Rollback Procedure

If an update breaks something:

```bash
cd /root/college-football-swiss
git log  # Find previous commit
git checkout <commit-hash>
bash deploy/update.sh
```

Or restore from backup:
```bash
tar -xzf /root/backups/cfb-swiss-YYYYMMDD_HHMMSS.tar.gz -C /
systemctl reload nginx
```

## Support and Resources

- **Project Repository**: https://github.com/pbailey529/college-football-swiss
- **Nginx Documentation**: https://nginx.org/en/docs/
- **Digital Ocean Tutorials**: https://www.digitalocean.com/community/tutorials
- **Let's Encrypt**: https://letsencrypt.org/getting-started/
- **Mapbox Documentation**: https://docs.mapbox.com/

## Uninstalling

To completely remove the deployment:

```bash
# Stop and disable services
systemctl stop nginx
systemctl disable cfb-swiss-update.timer

# Remove files
rm -rf /var/www/college-football-swiss
rm -rf /root/college-football-swiss
rm /etc/nginx/sites-available/college-football-swiss
rm /etc/nginx/sites-enabled/college-football-swiss
rm /etc/systemd/system/cfb-swiss-update.*

# Remove packages (optional)
apt remove nginx python3-pip

# Remove SSL certificate (if installed)
certbot delete --cert-name your-domain.com
```

## Next Steps

Once your site is deployed:

1. **Test thoroughly** - Click around, check the map, verify data loads
2. **Monitor logs** - Watch for errors in the first few days
3. **Share your site** - Get feedback from users
4. **Customize** - Adjust colors, zoom levels, map styles in `config.js`
5. **Add features** - Fork the repo and build new functionality!

---

**Need help?** Open an issue on GitHub or check the main README.md for more information.

Happy deploying! 🚀
