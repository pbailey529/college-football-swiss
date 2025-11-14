# iPhone Deployment Guide (Digital Ocean Console)

This guide is specifically for deploying from your iPhone using the Digital Ocean web console.

## Before You Start

Have these ready:
- [ ] Your Mapbox API token (get free at https://account.mapbox.com/)
- [ ] (Optional) Your domain name

## Step 1: Access Your VPS Console

1. Open Digital Ocean in your mobile browser
2. Go to your Droplets
3. Click on your droplet
4. Click "Access" → "Launch Droplet Console"
5. Log in as root (or your sudo user)

## Step 2: Clone the Repository

In the Digital Ocean console, run:

```bash
cd /root
git clone https://github.com/pbailey529/college-football-swiss.git
cd college-football-swiss
```

## Step 3: Run the Deployment Script

```bash
sudo bash deploy/deploy.sh
```

## Step 4: Answer the Prompts

The script will ask you questions. Here's what to enter:

### Prompt 1: Mapbox Token
```
Enter your Mapbox API token (or press Enter to configure later):
```
**What to do**: Paste your Mapbox token
- If you have it ready, paste it now
- If not, press Enter and configure it later (see Step 6)

### Prompt 2: Domain Name
```
Enter your domain name (or press Enter for IP-only access):
```
**What to do**:
- If you have a domain pointing to your VPS: enter it (e.g., `cfb.example.com`)
- If you just want to access via IP: press Enter

### Prompt 3: SSL Setup (only if you entered a domain)
```
Do you want to set up SSL now? (y/n):
```
**What to do**:
- Type `y` if your domain DNS is already pointing to this VPS IP
- Type `n` if you need to set up DNS first (you can add SSL later)

### Prompt 4: SSL Email (only if setting up SSL)
Certbot will ask for your email address for certificate notifications.

## Step 5: Wait for Completion

The script will:
- ✓ Install system packages (Nginx, Python, etc.)
- ✓ Create Python virtual environment
- ✓ Generate GeoJSON data files
- ✓ Configure Nginx
- ✓ Set up SSL (if you chose to)

This takes about 3-5 minutes.

## Step 6: Configure Mapbox Token (If Skipped Earlier)

If you didn't enter your Mapbox token during setup:

```bash
nano /var/www/college-football-swiss/js/config.js
```

Find this line:
```javascript
MAPBOX_TOKEN: 'YOUR_MAPBOX_TOKEN_HERE',
```

**On iPhone**: Editing with nano can be tricky. Here's an easier way:

```bash
# Replace YOUR_MAPBOX_TOKEN_HERE with your actual token
sed -i 's/YOUR_MAPBOX_TOKEN_HERE/pk.your_actual_token_here/' /var/www/college-football-swiss/js/config.js
```

Just replace `pk.your_actual_token_here` with your real token!

## Step 7: Access Your Site

The deployment script will tell you the URL. Typically:

- **Without domain**: `http://YOUR_VPS_IP`
- **With domain (no SSL)**: `http://your-domain.com`
- **With domain (SSL)**: `https://your-domain.com`

## Troubleshooting from iPhone

### Can't See the Map?

**Option 1**: Use the sed command above to set your Mapbox token

**Option 2**: Use the Digital Ocean console file editor:
1. In DO console: `cat /var/www/college-football-swiss/js/config.js`
2. Look for `YOUR_MAPBOX_TOKEN_HERE`
3. Copy the entire file content
4. Edit it in Notes app on iPhone (find/replace the token)
5. Use echo to write it back (see below)

### Pasting Multi-line Text on iPhone

The DO console can be finicky with pasting. If you need to paste a config file:

```bash
cat > /var/www/college-football-swiss/js/config.js << 'EOF'
[paste your entire config here]
EOF
```

### Site Not Loading?

Check the logs:
```bash
tail -20 /var/log/nginx/college-football-swiss_error.log
```

Restart Nginx:
```bash
systemctl restart nginx
```

### Check What's Running

```bash
systemctl status nginx
curl http://localhost
```

## Updating Later

When you make changes to the code and want to redeploy:

```bash
cd /root/college-football-swiss
sudo bash deploy/update.sh
```

## Alternative: Deploy from Your Laptop Later

If you find the iPhone console too difficult:

1. Stop here - your VPS is ready
2. When you get to your laptop, SSH in:
   ```bash
   ssh root@your-vps-ip
   ```
3. Continue from there with a better terminal experience

The deployment scripts work the same way!

## Setting Up SSH Key for Later

From your laptop later, generate an SSH key:

```bash
# On your Mac/PC
ssh-keygen -t ed25519 -C "your_email@example.com"
ssh-copy-id root@your-vps-ip
```

Then you can SSH without passwords.

## Adding SSL Later

If you skipped SSL setup and want to add it:

```bash
sudo certbot --nginx -d your-domain.com
```

Make sure your domain is pointing to your VPS IP first! Check with:
```bash
nslookup your-domain.com
```

## Quick Commands

```bash
# Check site is working
curl http://localhost

# Restart web server
systemctl restart nginx

# View logs
tail -f /var/log/nginx/college-football-swiss_access.log

# Regenerate data
cd /root/college-football-swiss
source venv/bin/activate
python src/export_geojson.py
cp -r web/data/* /var/www/college-football-swiss/data/
```

## Getting Help

- Full guide: [DEPLOY.md](./DEPLOY.md)
- Project README: [../README.md](../README.md)
- GitHub Issues: https://github.com/pbailey529/college-football-swiss/issues

## Tips for Using DO Console on iPhone

1. **Rotate to landscape** - Easier to see commands
2. **Use Safari** - Better than other mobile browsers for DO console
3. **Copy commands from Notes** - Prepare commands in Notes app first
4. **Take screenshots** - Document any errors for troubleshooting
5. **Request Desktop Site** - In Safari, helps with console rendering

## Success! Now What?

Once deployed:
- Visit your site and test the map
- Share the URL with friends
- Customize the map style in `config.js`
- Set up automated daily updates (optional):
  ```bash
  sudo bash deploy/install-auto-update.sh
  ```

---

Happy deploying from your iPhone! 📱🚀
