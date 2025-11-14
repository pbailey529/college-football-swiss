// Configuration file for API keys and settings
// Copy this file to config.js and add your API keys

const CONFIG = {
  // Get your free Mapbox API token at: https://account.mapbox.com/
  // Free tier: 50,000 map loads/month
  MAPBOX_TOKEN: 'YOUR_MAPBOX_TOKEN_HERE',

  // Map settings
  MAP_STYLE: 'mapbox://styles/mapbox/dark-v11', // Dark theme for better arc visibility
  INITIAL_VIEW: {
    longitude: -98.5795, // Center of US
    latitude: 39.8283,
    zoom: 4,
    pitch: 0,
    bearing: 0
  },

  // Zoom thresholds for filtering
  ZOOM_LEVELS: {
    NATIONAL: 4,      // Show only top matchups
    REGIONAL: 6,      // Show regional matchups
    LOCAL: 8          // Show all matchups
  },

  // Team ranking threshold for national view
  TOP_TEAMS_THRESHOLD: 25  // Only show teams ranked in top 25 at national zoom
};
