/**
 * Data loading and management for College Football Swiss visualization
 */

class DataManager {
    constructor() {
        this.teams = null;
        this.matchups = null;
        this.currentRound = 1;
    }

    /**
     * Load teams and matchups data for a specific round
     */
    async loadRound(round) {
        try {
            const teamsPath = `data/teams_round${round - 1}.geojson`;
            const matchupsPath = `data/matchups_round${round}.geojson`;

            console.log(`Loading data for round ${round}...`);

            // Load both files in parallel
            const [teamsResponse, matchupsResponse] = await Promise.all([
                fetch(teamsPath),
                fetch(matchupsPath)
            ]);

            if (!teamsResponse.ok || !matchupsResponse.ok) {
                throw new Error('Failed to load data files');
            }

            this.teams = await teamsResponse.json();
            this.matchups = await matchupsResponse.json();
            this.currentRound = round;

            console.log(`Loaded ${this.teams.features.length} teams and ${this.matchups.features.length} matchups`);

            return {
                teams: this.teams,
                matchups: this.matchups
            };
        } catch (error) {
            console.error('Error loading round data:', error);
            throw error;
        }
    }

    /**
     * Get statistics about current matchups
     */
    getStats() {
        if (!this.matchups || !this.teams) {
            return {
                totalMatchups: 0,
                totalTeams: 0,
                avgDistance: 0,
                totalDistance: 0
            };
        }

        const totalMatchups = this.matchups.features.length;
        const totalTeams = this.teams.features.length;

        // Calculate total and average distance
        const totalDistance = this.matchups.features.reduce((sum, feature) => {
            return sum + (feature.properties.distance_miles || 0);
        }, 0);

        const avgDistance = totalMatchups > 0 ? Math.round(totalDistance / totalMatchups) : 0;

        return {
            totalMatchups,
            totalTeams,
            avgDistance,
            totalDistance: Math.round(totalDistance)
        };
    }

    /**
     * Filter matchups by zoom level
     * Returns matchups that should be visible at the current zoom level
     */
    filterMatchupsByZoom(zoomLevel) {
        if (!this.matchups) return [];

        const { NATIONAL, REGIONAL } = CONFIG.ZOOM_LEVELS;

        return this.matchups.features.filter(feature => {
            const props = feature.properties;

            // At national level (zoomed out), only show top matchups
            if (zoomLevel < NATIONAL) {
                return props.is_top_matchup;
            }

            // At regional level, show more matchups
            if (zoomLevel < REGIONAL) {
                return props.avg_rating >= 60; // Show good teams
            }

            // At local level (zoomed in), show all matchups
            return true;
        });
    }

    /**
     * Get color for a matchup based on its properties
     */
    getMatchupColor(properties) {
        if (properties.is_top_matchup) {
            return [255, 0, 128, 200]; // Pink for top matchups
        } else if (properties.avg_rating >= 60) {
            return [0, 255, 255, 180]; // Cyan for good matchups
        } else {
            return [100, 200, 100, 150]; // Green for other matchups
        }
    }

    /**
     * Get width for a matchup arc based on its importance
     */
    getMatchupWidth(properties) {
        if (properties.is_top_matchup) {
            return 3;
        } else if (properties.avg_rating >= 60) {
            return 2;
        } else {
            return 1.5;
        }
    }

    /**
     * Format matchup data for tooltip
     */
    formatMatchupTooltip(properties) {
        const {
            team_a_name,
            team_a_rating,
            team_a_record,
            team_b_name,
            team_b_rating,
            team_b_record,
            distance_miles,
            rating_diff
        } = properties;

        return `
            <div class="matchup-title">${team_a_name} vs ${team_b_name}</div>
            <div class="team-info">
                <strong>${team_a_name}</strong><br>
                Rating: ${team_a_rating.toFixed(1)} | Record: ${team_a_record}
            </div>
            <div class="team-info">
                <strong>${team_b_name}</strong><br>
                Rating: ${team_b_rating.toFixed(1)} | Record: ${team_b_record}
            </div>
            <div class="matchup-stats">
                Distance: ${distance_miles.toFixed(0)} miles<br>
                Rating difference: ${rating_diff.toFixed(1)}
            </div>
        `;
    }

    /**
     * Format team data for tooltip
     */
    formatTeamTooltip(properties) {
        const { team, rating, score, conference } = properties;

        return `
            <div class="matchup-title">${team}</div>
            <div class="team-info">
                Conference: ${conference}<br>
                Rating: ${rating.toFixed(1)}<br>
                Wins: ${score || 0}
            </div>
        `;
    }
}

// Create global data manager instance
window.dataManager = new DataManager();
