const API_BASE_URL = 'http://localhost:8000/api';

let currentBudgetTier = 'Power4_Elite';
let players = [];
let budgetTiers = {};

const navButtons = document.querySelectorAll('.nav-btn');
const tabContents = document.querySelectorAll('.tab-content');
const budgetTierElements = document.querySelectorAll('.budget-tier');
const addPlayerForm = document.getElementById('add-player-form');
const positionSelect = document.getElementById('player-position');
const playersListElement = document.getElementById('players-list');
const optimizationTierSelect = document.getElementById('optimization-tier');
const runOptimizationButton = document.getElementById('run-optimization');
const optimizationResults = document.getElementById('optimization-results');

document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
});

async function initializeApp() {
    try {
        await loadBudgetTiers();
        await loadPlayers();
        await loadMarketAnalysis();
        
        if (players.length === 0) {
            await addSampleData();
            await loadPlayers();
            await loadMarketAnalysis();
        }
    } catch (error) {
        console.error('Failed to initialize app:', error);
        showNotification('Failed to load application data', 'error');
    }
}

function setupEventListeners() {
    navButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabName = button.dataset.tab;
            switchTab(tabName);
        });
    });

    budgetTierElements.forEach(element => {
        element.addEventListener('click', () => {
            selectBudgetTier(element.dataset.tier);
        });
    });

    positionSelect.addEventListener('change', function() {
        showPositionStats(this.value);
    });

    addPlayerForm.addEventListener('submit', handleAddPlayer);

    runOptimizationButton.addEventListener('click', runOptimization);
}

function switchTab(tabName) {
    navButtons.forEach(btn => btn.classList.remove('active'));
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

    tabContents.forEach(content => content.classList.remove('active'));
    document.getElementById(tabName).classList.add('active');

    if (tabName === 'market') {
        loadMarketAnalysis();
    }
}

function selectBudgetTier(tier) {
    currentBudgetTier = tier;
    
    budgetTierElements.forEach(element => {
        element.classList.remove('selected');
    });
    document.querySelector(`[data-tier="${tier}"]`).classList.add('selected');
    
    optimizationTierSelect.value = tier;
}

function showPositionStats(position) {
    document.querySelectorAll('.position-stats').forEach(stats => {
        stats.style.display = 'none';
    });

    if (position === 'LB') {
        document.getElementById('lb-stats').style.display = 'block';
    } else if (position === 'QB') {
        document.getElementById('qb-stats').style.display = 'block';
    }
}

async function apiRequest(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const config = {
        headers: {
            'Content-Type': 'application/json',
        },
        ...options
    };

    try {
        const response = await fetch(url, config);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API request failed:', error);
        throw error;
    }
}

async function loadBudgetTiers() {
    try {
        budgetTiers = await apiRequest('/budget-tiers');
    } catch (error) {
        console.error('Failed to load budget tiers:', error);
    }
}

async function loadPlayers() {
    try {
        const athletesData = await apiRequest('/athletes');
        players = athletesData;
        renderPlayersList();
    } catch (error) {
        console.error('Failed to load players:', error);
        playersListElement.innerHTML = '<div class="loading">Failed to load players</div>';
    }
}

async function handleAddPlayer(event) {
    event.preventDefault();
    
    const formData = new FormData(addPlayerForm);
    const playerData = Object.fromEntries(formData.entries());
    
    ['games_played', 'market_value', 'total_tackles', 'solo_tackles', 
     'passing_yards', 'passing_tds', 'interceptions', 'completions', 'attempts'].forEach(field => {
        if (playerData[field]) {
            playerData[field] = parseInt(playerData[field]) || 0;
        }
    });

    try {
        const result = await apiRequest('/athletes', {
            method: 'POST',
            body: JSON.stringify(playerData)
        });
        
        showNotification('Player added successfully!', 'success');
        addPlayerForm.reset();
        showPositionStats(''); // Hide position stats
        
        await evaluatePlayer(result.id);
        
        await loadPlayers();
        await loadMarketAnalysis();
        
    } catch (error) {
        console.error('Failed to add player:', error);
        showNotification('Failed to add player', 'error');
    }
}

async function evaluatePlayer(athleteId) {
    try {
        await apiRequest(`/evaluate-player/${athleteId}`, {
            method: 'POST',
            body: JSON.stringify({ budget_tier: currentBudgetTier })
        });
    } catch (error) {
        console.error('Failed to evaluate player:', error);
    }
}

async function runOptimization() {
    const budgetTier = optimizationTierSelect.value;
    
    try {
        runOptimizationButton.disabled = true;
        runOptimizationButton.textContent = 'Running Optimization...';
        
        const result = await apiRequest('/optimize-roster', {
            method: 'POST',
            body: JSON.stringify({ budget_tier: budgetTier })
        });
        
        displayOptimizationResults(result, budgetTier);
        optimizationResults.style.display = 'block';
        
    } catch (error) {
        console.error('Optimization failed:', error);
        showNotification('Optimization failed', 'error');
    } finally {
        runOptimizationButton.disabled = false;
        runOptimizationButton.textContent = 'Run Optimization';
    }
}

async function loadMarketAnalysis() {
    try {
        const matrix = await apiRequest('/market-analysis');
        renderMarketMatrix(matrix);
    } catch (error) {
        console.error('Failed to load market analysis:', error);
    }
}

function renderPlayersList() {
    if (players.length === 0) {
        playersListElement.innerHTML = '<div class="loading">No players found. Add some players to get started.</div>';
        return;
    }

    playersListElement.innerHTML = players.map(player => `
        <div class="player-card">
            <h4>${player.name}</h4>
            <div class="player-info">
                <span class="position">${player.position}</span>
                <span class="market-value">$${player.market_value.toLocaleString()}</span>
            </div>
            <div class="stats">
                ${player.conference ? `Conference: ${player.conference}` : ''}
                ${player.transfer_from ? ` • Transfer from: ${player.transfer_from}` : ''}
                ${player.games_played ? ` • Games: ${player.games_played}` : ''}
                ${player.total_tackles ? ` • Tackles: ${player.total_tackles}` : ''}
            </div>
            <div class="player-actions">
                <button class="btn btn-small btn-secondary" onclick="evaluatePlayerUI(${player.id})">
                    Evaluate
                </button>
                <button class="btn btn-small btn-secondary" onclick="viewBaronHopsonAnalysis(${player.id})">
                    Baron Analysis
                </button>
            </div>
        </div>
    `).join('');
}

function displayOptimizationResults(result, budgetTier) {
    const tierConfig = budgetTiers[budgetTier];
    
    optimizationResults.innerHTML = `
        <h3>Optimization Results - ${budgetTier}</h3>
        
        <div class="optimization-summary">
            <div class="summary-metric">
                <div class="label">Total Budget</div>
                <div class="value primary">$${tierConfig.total_budget.toLocaleString()}</div>
            </div>
            <div class="summary-metric">
                <div class="label">Total Cost</div>
                <div class="value">$${result.total_cost.toLocaleString()}</div>
            </div>
            <div class="summary-metric">
                <div class="label">Remaining Budget</div>
                <div class="value success">$${result.remaining_budget.toLocaleString()}</div>
            </div>
            <div class="summary-metric">
                <div class="label">Total Value Score</div>
                <div class="value primary">${result.total_value.toFixed(1)}</div>
            </div>
            <div class="summary-metric">
                <div class="label">Players Selected</div>
                <div class="value">${result.selected_players.length}</div>
            </div>
            <div class="summary-metric">
                <div class="label">Optimization Method</div>
                <div class="value">${result.method}</div>
            </div>
        </div>

        <h4>Position Distribution</h4>
        <div class="position-distribution">
            ${Object.entries(result.position_counts).map(([position, count]) => `
                <div class="position-count">
                    <span class="position">${position}</span>: ${count}
                </div>
            `).join('')}
        </div>

        <h4>Selected Players</h4>
        <div class="selected-players">
            ${result.selected_players.map(player => `
                <div class="selected-player">
                    <div class="player-header">
                        <span class="player-name">${player.name}</span>
                        <span class="player-value">$${player.market_value.toLocaleString()}</span>
                    </div>
                    <div class="player-details">
                        ${player.position} • Value/$ Ratio: ${player.value_per_dollar.toFixed(2)}
                        ${player.transfer_from ? ` • Transfer from: ${player.transfer_from}` : ''}
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}

function renderMarketMatrix(matrix) {
    const quadrants = [
        { key: 'high_value_low_cost', element: 'high-value-low-cost' },
        { key: 'high_value_high_cost', element: 'high-value-high-cost' },
        { key: 'low_value_low_cost', element: 'low-value-low-cost' },
        { key: 'low_value_high_cost', element: 'low-value-high-cost' }
    ];

    quadrants.forEach(({ key, element }) => {
        const container = document.getElementById(element);
        const players = matrix[key] || [];
        
        if (players.length === 0) {
            container.innerHTML = '<div class="text-muted">No players in this quadrant</div>';
            return;
        }

        container.innerHTML = players.slice(0, 10).map(player => `
            <div class="matrix-player">
                <div class="player-header">
                    <span class="player-name">${player.name}</span>
                    <span class="player-value">$${player.market_value.toLocaleString()}</span>
                </div>
                <div class="player-details">
                    ${player.position} • ${player.conference || 'Unknown Conference'}
                    ${player.transfer_from ? ` • From: ${player.transfer_from}` : ''}
                    <br>Ratio: ${player.value_per_dollar.toFixed(2)} • Score: ${player.production_score}
                </div>
            </div>
        `).join('');
    });
}

async function evaluatePlayerUI(athleteId) {
    try {
        const result = await apiRequest(`/evaluate-player/${athleteId}`, {
            method: 'POST',
            body: JSON.stringify({ budget_tier: currentBudgetTier })
        });
        
        showNotification(`Player evaluated! Value/$ Ratio: ${result.value_per_dollar.toFixed(2)}`, 'success');
        await loadPlayers();
        await loadMarketAnalysis();
        
    } catch (error) {
        console.error('Failed to evaluate player:', error);
        showNotification('Failed to evaluate player', 'error');
    }
}

async function viewBaronHopsonAnalysis(athleteId) {
    try {
        const analysis = await apiRequest(`/baron-hopson-analysis/${athleteId}`);
        
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.innerHTML = `
            <div class="modal">
                <div class="modal-header">
                    <h3>Baron Hopson Analysis - ${analysis.player_name}</h3>
                    <button class="modal-close">&times;</button>
                </div>
                <div class="modal-content">
                    <div class="analysis-grid">
                        <div class="analysis-section">
                            <h4>Player Stats</h4>
                            <div class="metric">
                                <span>Position:</span>
                                <span>${analysis.player_position}</span>
                            </div>
                            <div class="metric">
                                <span>Total Tackles:</span>
                                <span>${analysis.player_stats.total_tackles}</span>
                            </div>
                            <div class="metric">
                                <span>Tackles/Game:</span>
                                <span>${analysis.player_stats.tackles_per_game.toFixed(1)}</span>
                            </div>
                            <div class="metric">
                                <span>Production Score:</span>
                                <span class="highlight">${analysis.player_evaluation.production_score}/100</span>
                            </div>
                        </div>
                        
                        <div class="analysis-section">
                            <h4>Market Analysis</h4>
                            <div class="metric">
                                <span>Market Value:</span>
                                <span>$${analysis.player_evaluation.market_value.toLocaleString()}</span>
                            </div>
                            <div class="metric">
                                <span>Value/$ Ratio:</span>
                                <span class="highlight">${analysis.player_evaluation.value_per_dollar.toFixed(2)}</span>
                            </div>
                            <div class="metric">
                                <span>Transfer Multiplier:</span>
                                <span>${analysis.player_evaluation.transfer_multiplier}x</span>
                            </div>
                        </div>
                        
                        <div class="analysis-section">
                            <h4>Baron Comparison</h4>
                            <div class="metric">
                                <span>Production Ratio:</span>
                                <span>${analysis.baron_comparison.production_ratio.toFixed(2)}</span>
                            </div>
                            <div class="metric">
                                <span>Value Ratio:</span>
                                <span>${analysis.baron_comparison.value_ratio.toFixed(2)}</span>
                            </div>
                            <div class="metric">
                                <span>Cost Efficiency:</span>
                                <span class="highlight">${analysis.baron_comparison.cost_efficiency}</span>
                            </div>
                            <div class="metric">
                                <span>Recommendation:</span>
                                <span class="highlight">${analysis.recommendation}</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        modal.querySelector('.modal-close').addEventListener('click', () => {
            document.body.removeChild(modal);
        });
        
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                document.body.removeChild(modal);
            }
        });
        
    } catch (error) {
        console.error('Failed to load Baron Hopson analysis:', error);
        showNotification('Failed to load analysis', 'error');
    }
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.classList.add('show');
    }, 100);
    
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            if (document.body.contains(notification)) {
                document.body.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

async function addSampleData() {
    const samplePlayers = [
        {
            name: "Baron Hopson",
            position: "LB",
            conference: "ASUN",
            transfer_from: "FCS",
            games_played: 12,
            market_value: 15000,
            total_tackles: 11,
            solo_tackles: 6
        },
        {
            name: "Marcus Johnson",
            position: "QB",
            conference: "SEC",
            transfer_from: "FBS",
            games_played: 11,
            market_value: 165000,
            passing_yards: 3200,
            passing_tds: 24,
            interceptions: 8,
            completions: 245,
            attempts: 380
        },
        {
            name: "Tyler Williams",
            position: "RB",
            conference: "Big 12",
            transfer_from: "FCS",
            games_played: 10,
            market_value: 45000,
            rushing_yards: 1200,
            rushing_tds: 12
        },
        {
            name: "Alex Rodriguez",
            position: "WR",
            conference: "ACC",
            transfer_from: "FBS",
            games_played: 12,
            market_value: 85000,
            receiving_yards: 950,
            receiving_tds: 8,
            receptions: 65
        },
        {
            name: "David Chen",
            position: "LB",
            conference: "Mountain West",
            transfer_from: "FCS",
            games_played: 11,
            market_value: 25000,
            total_tackles: 89,
            solo_tackles: 52
        }
    ];

    for (const player of samplePlayers) {
        try {
            const result = await apiRequest('/athletes', {
                method: 'POST',
                body: JSON.stringify(player)
            });
            
            await evaluatePlayer(result.id);
        } catch (error) {
            console.error('Failed to add sample player:', error);
        }
    }
}

const modalStyles = `
<style>
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
}

.modal {
    background: white;
    border-radius: 12px;
    max-width: 800px;
    width: 90%;
    max-height: 80%;
    overflow-y: auto;
    box-shadow: 0 20px 25px rgba(0, 0, 0, 0.1);
}

.modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1.5rem;
    border-bottom: 1px solid #e2e8f0;
}

.modal-header h3 {
    margin: 0;
    color: #2d3748;
}

.modal-close {
    background: none;
    border: none;
    font-size: 1.5rem;
    cursor: pointer;
    color: #718096;
    padding: 0;
    width: 30px;
    height: 30px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.modal-close:hover {
    color: #2d3748;
}

.modal-content {
    padding: 1.5rem;
}

.analysis-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 2rem;
}

.analysis-section h4 {
    font-size: 1.1rem;
    font-weight: 600;
    margin-bottom: 1rem;
    color: #2d3748;
}

.notification {
    position: fixed;
    top: 20px;
    right: 20px;
    padding: 1rem 1.5rem;
    border-radius: 6px;
    color: white;
    font-weight: 500;
    z-index: 1001;
    transform: translateX(100%);
    transition: transform 0.3s ease;
}

.notification.show {
    transform: translateX(0);
}

.notification-success {
    background: #38a169;
}

.notification-error {
    background: #e53e3e;
}

.notification-info {
    background: #3182ce;
}

.position-distribution {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
    gap: 0.5rem;
    margin-bottom: 1.5rem;
}

.position-count {
    background: #f8fafc;
    padding: 0.5rem;
    border-radius: 4px;
    text-align: center;
    font-size: 0.9rem;
}

.selected-players {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    max-height: 300px;
    overflow-y: auto;
}

.selected-player {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    padding: 0.75rem;
}

.selected-player .player-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.25rem;
}

.selected-player .player-name {
    font-weight: 600;
    color: #2d3748;
}

.selected-player .player-value {
    font-weight: 600;
    color: #38a169;
}

.selected-player .player-details {
    font-size: 0.9rem;
    color: #718096;
}
</style>
`;

document.head.insertAdjacentHTML('beforeend', modalStyles);
