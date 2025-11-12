/**
 * Main application initialization and event handling
 */

class App {
    constructor() {
        this.currentRound = 1;
        this.isInitialized = false;
    }

    /**
     * Initialize the application
     */
    async init() {
        console.log('Initializing College Football Swiss Map...');

        try {
            // Show loading indicator
            this.showLoading(true);

            // Initialize map
            const mapInitialized = mapVisualization.initializeMap();
            if (!mapInitialized) {
                return;
            }

            // Wait for map to load
            mapVisualization.map.on('load', async () => {
                try {
                    // Load initial data
                    await dataManager.loadRound(this.currentRound);

                    // Initialize Deck.gl overlay
                    mapVisualization.initializeDeckOverlay();

                    // Update statistics
                    mapVisualization.updateStats();

                    // Setup event listeners
                    this.setupEventListeners();

                    // Hide loading indicator
                    this.showLoading(false);

                    this.isInitialized = true;
                    console.log('✅ Application initialized successfully');
                } catch (error) {
                    console.error('Error during initialization:', error);
                    mapVisualization.showError('Failed to load data. Please refresh the page.');
                }
            });

        } catch (error) {
            console.error('Error initializing application:', error);
            mapVisualization.showError('Failed to initialize map. Please check your Mapbox token.');
        }
    }

    /**
     * Setup event listeners for UI controls
     */
    setupEventListeners() {
        // Round selector
        const roundSelect = document.getElementById('round-select');
        roundSelect.addEventListener('change', async (e) => {
            const round = parseInt(e.target.value);
            await this.changeRound(round);
        });

        // Update subtitle when round changes
        this.updateSubtitle();
    }

    /**
     * Change to a different round
     */
    async changeRound(round) {
        if (round === this.currentRound) return;

        console.log(`Changing to round ${round}...`);
        this.showLoading(true);

        try {
            this.currentRound = round;
            await mapVisualization.updateData(round);
            this.updateSubtitle();
            this.showLoading(false);
        } catch (error) {
            console.error('Error changing round:', error);
            this.showLoading(false);
            alert('Failed to load round data');
        }
    }

    /**
     * Update subtitle text
     */
    updateSubtitle() {
        const subtitle = document.querySelector('.subtitle');
        subtitle.textContent = `Week ${this.currentRound} Matchups`;
    }

    /**
     * Show/hide loading indicator
     */
    showLoading(show) {
        const loading = document.getElementById('loading');
        if (show) {
            loading.classList.remove('hidden');
        } else {
            loading.classList.add('hidden');
        }
    }

    /**
     * Export current view as image (future feature)
     */
    exportImage() {
        // TODO: Implement screenshot functionality
        console.log('Export feature coming soon!');
    }

    /**
     * Show detailed matchup information (future feature)
     */
    showMatchupDetails(matchup) {
        // TODO: Implement detailed view panel
        console.log('Matchup details:', matchup);
    }
}

// Initialize application when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    const app = new App();
    app.init();

    // Make app available globally for debugging
    window.app = app;
});

// Log version info
console.log('College Football Swiss - Interactive Map v1.0.0');
console.log('Using Mapbox GL JS v3.0.1 + Deck.gl v9.0.23');
