# College Football Swiss - Interactive Map

An interactive web visualization of College Football Swiss tournament matchups using Mapbox GL JS and Deck.gl.

## Features

- 🗺️ **Interactive Map**: Explore matchups across the United States
- ✈️ **Arc Visualizations**: Beautiful curved lines showing team travel paths
- 🔍 **Zoom-based Filtering**: See top matchups when zoomed out, more details when zoomed in
- 📊 **Live Statistics**: View matchup counts, team totals, and average travel distances
- 🎯 **Hover Tooltips**: Get instant matchup details by hovering over arcs
- 🎨 **Color-coded**: Top-ranked matchups highlighted in pink, regional in cyan

## Quick Start

### 1. Get a Mapbox API Token

1. Go to [https://account.mapbox.com/](https://account.mapbox.com/)
2. Sign up for a free account (no credit card required)
3. Copy your default public token from the dashboard
4. Free tier includes: **50,000 map loads per month**

### 2. Configure Your Token

Open `web/js/config.js` and replace `YOUR_MAPBOX_TOKEN_HERE` with your actual token:

```javascript
const CONFIG = {
  MAPBOX_TOKEN: 'pk.eyJ1IjoieW91ci11c2VybmFtZSIsImEiOi...',
  // ... rest of config
};
```

### 3. Generate Data

From the project root, run:

```bash
python src/export_geojson.py
```

This will generate GeoJSON files in `web/data/`:
- `teams_round0.geojson` - All team locations
- `matchups_round1.geojson` - Week 1 matchups
- `teams_round1.geojson` - Teams after Week 1
- `matchups_round2.geojson` - Week 2 matchups

### 4. Serve the Web App

You need to serve the files via HTTP (not `file://`). Choose one:

**Python 3:**
```bash
cd web
python -m http.server 8000
```

**Node.js (if installed):**
```bash
cd web
npx serve .
```

**VS Code:**
- Install "Live Server" extension
- Right-click `index.html` → "Open with Live Server"

### 5. Open in Browser

Navigate to: [http://localhost:8000](http://localhost:8000)

## How to Use

### Navigation
- **Scroll/Pinch**: Zoom in/out
- **Click + Drag**: Pan around the map
- **Right-click + Drag**: Rotate and tilt (3D view)

### Zoom Behavior
- **Zoomed Out (National)**: Shows only top-ranked team matchups
- **Medium Zoom (Regional)**: Shows good teams (rating ≥ 60)
- **Zoomed In (Local)**: Shows all matchups in the area

### Color Legend
- **Pink arcs**: Top-ranked matchups (both teams highly rated)
- **Cyan arcs**: Good matchups (average rating ≥ 60)
- **Green arcs**: Other matchups
- **Dots**: Team locations (pink = elite, orange = good, gray = others)

### Controls
- **Round Selector**: Switch between Week 1 and Week 2 matchups
- **Statistics Panel**: View live counts and averages
- **Hover**: See detailed matchup information

## Project Structure

```
web/
├── index.html          # Main HTML page
├── css/
│   └── style.css       # Styling and layout
├── js/
│   ├── config.js       # Configuration (API token, settings)
│   ├── data.js         # Data loading and management
│   ├── map.js          # Mapbox + Deck.gl visualization
│   └── app.js          # Application initialization
└── data/               # Generated GeoJSON files
    ├── teams_round0.geojson
    ├── matchups_round1.geojson
    ├── teams_round1.geojson
    └── matchups_round2.geojson
```

## Customization

### Adjust Zoom Thresholds

Edit `web/js/config.js`:

```javascript
ZOOM_LEVELS: {
  NATIONAL: 4,   // Show only top matchups
  REGIONAL: 6,   // Show regional matchups
  LOCAL: 8       // Show all matchups
}
```

### Change Map Style

Choose from Mapbox styles in `web/js/config.js`:

```javascript
MAP_STYLE: 'mapbox://styles/mapbox/dark-v11'  // Current (dark theme)
// Other options:
// 'mapbox://styles/mapbox/streets-v12'       // Streets
// 'mapbox://styles/mapbox/satellite-v9'      // Satellite
// 'mapbox://styles/mapbox/light-v11'         // Light theme
```

### Adjust Team Rating Threshold

To change what qualifies as a "top matchup", edit `web/js/config.js`:

```javascript
TOP_TEAMS_THRESHOLD: 25  // Only top 25 teams
```

Or modify the logic in `web/js/data.js`:

```javascript
is_top_matchup = avg_rating >= 75  // Change threshold here
```

## Troubleshooting

### Map Not Loading

1. **Check Console**: Open browser dev tools (F12) → Console tab
2. **Verify Token**: Make sure your Mapbox token is set in `config.js`
3. **Check Network**: Look for failed requests in Network tab
4. **CORS Issues**: Make sure you're serving via HTTP, not opening `file://`

### No Matchups Showing

1. **Verify Data**: Check that `web/data/*.geojson` files exist
2. **Run Export**: `python src/export_geojson.py`
3. **Check Zoom**: Try zooming in/out to trigger different visibility levels

### Arcs Not Appearing

1. **Check Deck.gl**: Look for errors in console
2. **Verify GeoJSON**: Open a data file and check format is correct
3. **Try Reloading**: Sometimes Deck.gl needs a refresh

## Performance Notes

- **Optimized for 250+ teams**: Uses WebGL for smooth rendering
- **Zoom-based filtering**: Reduces arcs shown when zoomed out
- **Efficient updates**: Only redraws when data or zoom changes
- **Mobile friendly**: Responsive design works on phones/tablets

## Next Steps

### Phase 2 Features (Future)
- Click on arc → detailed matchup panel
- Team schedule view
- Animated arcs (showing travel direction)
- Comparison mode (current system vs Swiss format)
- Statistics dashboard (total travel, competitive balance)

### Phase 3 Features (Future)
- Historical data (simulate past seasons)
- Real-time updates as results come in
- Share/export specific views
- Custom tournament parameters

## Technology Stack

- **Mapbox GL JS v3.0.1**: Base map and geographic rendering
- **Deck.gl v9.0.23**: WebGL-powered arc visualizations
- **Vanilla JavaScript**: No framework dependencies
- **GeoJSON**: Standard geographic data format

## License

See parent repository LICENSE file.

## Questions?

See main project [README.md](../README.md) for more information about the College Football Swiss tournament format.
