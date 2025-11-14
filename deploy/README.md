# Deployment Scripts

This directory contains scripts and configuration files for deploying College Football Swiss to a VPS.

## Quick Start

**For first-time deployment on your Digital Ocean VPS:**

```bash
# 1. SSH into your VPS
ssh root@your-vps-ip

# 2. Clone the repository
git clone https://github.com/pbailey529/college-football-swiss.git
cd college-football-swiss

# 3. Run the deployment script
sudo bash deploy/deploy.sh
```

The script will guide you through the setup process interactively.

## Files in This Directory

### Scripts

- **`deploy.sh`** - Main deployment script (run this first!)
  - Installs system dependencies
  - Sets up Python environment
  - Configures Nginx web server
  - Generates initial data
  - Optionally sets up SSL/HTTPS

- **`update.sh`** - Update script for future deployments
  - Pulls latest code from Git
  - Updates Python dependencies
  - Regenerates data files
  - Safely updates web files (preserves config)

- **`install-auto-update.sh`** - Sets up automated daily data updates (optional)
  - Installs systemd service and timer
  - Runs data generation daily at 3 AM

### Configuration Files

- **`nginx/college-football-swiss.conf`** - Nginx web server configuration template
  - Static file serving
  - GeoJSON MIME types
  - Caching headers
  - Security headers
  - Gzip compression

- **`systemd/cfb-swiss-update.service`** - Systemd service for automated updates
- **`systemd/cfb-swiss-update.timer`** - Systemd timer for scheduling updates

### Documentation

- **`DEPLOY.md`** - Comprehensive deployment guide
  - Detailed step-by-step instructions
  - Troubleshooting tips
  - Security best practices
  - Cost estimates
  - Backup strategies

## Typical Workflow

### Initial Deployment

```bash
# On your VPS
cd /root
git clone https://github.com/pbailey529/college-football-swiss.git
cd college-football-swiss
sudo bash deploy/deploy.sh
```

Have ready:
- Your Mapbox API token
- (Optional) Your domain name

### Updating After Code Changes

```bash
# On your VPS
cd /root/college-football-swiss
sudo bash deploy/update.sh
```

### Manual Data Refresh

```bash
# On your VPS
cd /root/college-football-swiss
source venv/bin/activate
python src/export_geojson.py
cp -r web/data/* /var/www/college-football-swiss/data/
```

## Requirements

- **OS**: Ubuntu 20.04+ or Debian 10+
- **RAM**: 1GB minimum, 2GB recommended
- **Disk**: 10GB minimum
- **Access**: Root or sudo privileges

## What Gets Installed

- Python 3 + pip + venv
- Nginx web server
- Git
- Certbot (for SSL)
- Python packages (networkx, pandas, geopy, etc.)

## Ports Used

- **80** (HTTP) - Web traffic
- **443** (HTTPS) - Secure web traffic (if SSL enabled)

Make sure these ports are open in your firewall!

## Directory Structure After Deployment

```
/var/www/college-football-swiss/    # ← Web app (public)
├── index.html
├── css/
├── js/
│   └── config.js                    # ← Configure Mapbox token here
└── data/
    └── *.geojson                    # ← Generated data files

/root/college-football-swiss/        # ← Source code (private)
├── src/                              # Python source
├── web/                              # Web source
├── deploy/                           # Deployment scripts (you are here!)
└── venv/                             # Python virtual environment
```

## Need Help?

1. **Read the detailed guide**: [DEPLOY.md](./DEPLOY.md)
2. **Check the main README**: [../README.md](../README.md)
3. **Open an issue**: https://github.com/pbailey529/college-football-swiss/issues

## Security Notes

- `.env` files with credentials are automatically ignored by Git
- SSL certificates are free via Let's Encrypt
- Keep your system updated: `apt update && apt upgrade`
- Use SSH keys instead of passwords
- Consider setting up a firewall with `ufw`

## Quick Commands Reference

```bash
# Check if site is running
curl http://localhost

# View Nginx logs
sudo tail -f /var/log/nginx/college-football-swiss_access.log

# Restart Nginx
sudo systemctl restart nginx

# Check Nginx configuration
sudo nginx -t

# Regenerate data
cd /root/college-football-swiss
source venv/bin/activate
python src/export_geojson.py

# Update deployment
sudo bash deploy/update.sh
```

## Troubleshooting

**Site not loading?**
```bash
sudo systemctl status nginx
sudo tail -f /var/log/nginx/college-football-swiss_error.log
```

**Map not showing?**
- Check browser console (F12)
- Verify Mapbox token in `/var/www/college-football-swiss/js/config.js`

**Permission errors?**
```bash
sudo chown -R www-data:www-data /var/www/college-football-swiss
sudo chmod -R 755 /var/www/college-football-swiss
```

---

**Ready to deploy?** Run `sudo bash deploy/deploy.sh` on your VPS!
