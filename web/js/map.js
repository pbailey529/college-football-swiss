/**
 * Map visualization using Mapbox GL + Deck.gl
 */

class MapVisualization {
    constructor() {
        this.map = null;
        this.deckOverlay = null;
        this.currentZoom = CONFIG.INITIAL_VIEW.zoom;
        this.hoveredFeature = null;
    }

    /**
     * Initialize Mapbox map
     */
    initializeMap() {
        // Check if API token is set
        if (!CONFIG.MAPBOX_TOKEN || CONFIG.MAPBOX_TOKEN === 'YOUR_MAPBOX_TOKEN_HERE') {
            console.error('Mapbox token not set! Please add your token to js/config.js');
            this.showError('Mapbox API token not configured. Please see README for setup instructions.');
            return false;
        }

        mapboxgl.accessToken = CONFIG.MAPBOX_TOKEN;

        this.map = new mapboxgl.Map({
            container: 'map',
            style: CONFIG.MAP_STYLE,
            center: [CONFIG.INITIAL_VIEW.longitude, CONFIG.INITIAL_VIEW.latitude],
            zoom: CONFIG.INITIAL_VIEW.zoom,
            pitch: CONFIG.INITIAL_VIEW.pitch,
            bearing: CONFIG.INITIAL_VIEW.bearing
        });

        // Add navigation controls
        this.map.addControl(new mapboxgl.NavigationControl(), 'top-right');

        // Listen to zoom changes
        this.map.on('zoom', () => {
            this.currentZoom = this.map.getZoom();
            this.updateLayers();
        });

        // Listen to move events for updating visible matchups
        this.map.on('moveend', () => {
            this.updateLayers();
        });

        return true;
    }

    /**
     * Create Deck.gl layers
     */
    createLayers() {
        const { ArcLayer, ScatterplotLayer } = deck;

        // Get filtered matchups based on zoom level
        const visibleMatchups = dataManager.filterMatchupsByZoom(this.currentZoom);

        // Arc layer for matchup connections
        const arcLayer = new ArcLayer({
            id: 'matchup-arcs',
            data: visibleMatchups,
            getSourcePosition: d => d.geometry.coordinates[0],
            getTargetPosition: d => d.geometry.coordinates[1],
            getSourceColor: d => dataManager.getMatchupColor(d.properties),
            getTargetColor: d => dataManager.getMatchupColor(d.properties),
            getWidth: d => dataManager.getMatchupWidth(d.properties),
            getHeight: 0.3,
            getTilt: 0,
            pickable: true,
            autoHighlight: true,
            highlightColor: [255, 255, 255, 200],
            onHover: info => this.handleHover(info, 'matchup')
        });

        // Scatterplot layer for team locations
        const teamsLayer = new ScatterplotLayer({
            id: 'team-locations',
            data: dataManager.teams ? dataManager.teams.features : [],
            getPosition: d => d.geometry.coordinates,
            getFillColor: d => {
                // Color based on team rating
                const rating = d.properties.rating;
                if (rating >= 80) return [255, 0, 128]; // Pink for top teams
                if (rating >= 70) return [255, 140, 0];  // Orange for good teams
                return [200, 200, 200];                  // Gray for others
            },
            getRadius: d => {
                // Size based on zoom and team rating
                const baseRadius = this.currentZoom < 5 ? 20000 : 10000;
                const ratingMultiplier = d.properties.rating >= 75 ? 1.5 : 1;
                return baseRadius * ratingMultiplier;
            },
            radiusMinPixels: 3,
            radiusMaxPixels: 15,
            pickable: true,
            autoHighlight: true,
            highlightColor: [255, 255, 255, 200],
            onHover: info => this.handleHover(info, 'team')
        });

        return [arcLayer, teamsLayer];
    }

    /**
     * Initialize Deck.gl overlay
     */
    initializeDeckOverlay() {
        const { MapboxOverlay } = deck;

        this.deckOverlay = new MapboxOverlay({
            interleaved: true,
            layers: this.createLayers()
        });

        this.map.addControl(this.deckOverlay);
    }

    /**
     * Update Deck.gl layers
     */
    updateLayers() {
        if (!this.deckOverlay) return;

        this.deckOverlay.setProps({
            layers: this.createLayers()
        });
    }

    /**
     * Handle hover events
     */
    handleHover(info, type) {
        const tooltip = document.getElementById('tooltip');

        if (info.object) {
            this.hoveredFeature = info.object;

            // Update tooltip content
            if (type === 'matchup') {
                tooltip.innerHTML = dataManager.formatMatchupTooltip(info.object.properties);
            } else if (type === 'team') {
                tooltip.innerHTML = dataManager.formatTeamTooltip(info.object.properties);
            }

            // Position tooltip
            tooltip.style.left = `${info.x}px`;
            tooltip.style.top = `${info.y}px`;
            tooltip.classList.add('visible');
        } else {
            this.hoveredFeature = null;
            tooltip.classList.remove('visible');
        }
    }

    /**
     * Update visualization with new data
     */
    async updateData(round) {
        try {
            await dataManager.loadRound(round);
            this.updateLayers();
            this.updateStats();
        } catch (error) {
            console.error('Error updating data:', error);
            this.showError('Failed to load round data');
        }
    }

    /**
     * Update statistics display
     */
    updateStats() {
        const stats = dataManager.getStats();

        document.getElementById('total-matchups').textContent = stats.totalMatchups;
        document.getElementById('total-teams').textContent = stats.totalTeams;
        document.getElementById('avg-distance').textContent = `${stats.avgDistance}mi`;
    }

    /**
     * Show error message
     */
    showError(message) {
        const loading = document.getElementById('loading');
        loading.innerHTML = `
            <div style="color: #ff4444;">
                <p style="font-size: 18px; margin-bottom: 8px;">⚠️ Error</p>
                <p>${message}</p>
            </div>
        `;
    }
}

// Create global map instance
window.mapVisualization = new MapVisualization();
