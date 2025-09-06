from flask import Flask, jsonify, request
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)

athletes = []
budget_tiers = {
    "Group5_Low": {"total_budget": 800000, "max_individual": 75000, "position_minimums": {"QB": 1, "RB": 2, "WR": 4, "LB": 3, "DB": 4}, "fcs_transfer_bonus": 3.5, "strategy": "Value Maximization"},
    "Group5_High": {"total_budget": 1300000, "max_individual": 140000, "position_minimums": {"QB": 1, "RB": 2, "WR": 4, "LB": 3, "DB": 4}, "fcs_transfer_bonus": 2.8, "strategy": "Balanced Value"},
    "Power4_Standard": {"total_budget": 8500000, "max_individual": 1500000, "position_minimums": {"QB": 2, "RB": 3, "WR": 5, "LB": 3, "DB": 5}, "fcs_transfer_bonus": 1.5, "strategy": "Talent Acquisition"},
    "Power4_Elite": {"total_budget": 20500000, "max_individual": 2500000, "position_minimums": {"QB": 2, "RB": 4, "WR": 6, "LB": 4, "DB": 6}, "fcs_transfer_bonus": 1.0, "strategy": "Elite Talent Focus"}
}

@app.route('/', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "message": "NIL Moneyball Platform API"})

@app.route('/api/budget-tiers', methods=['GET'])
def get_budget_tiers():
    return jsonify(budget_tiers)

@app.route('/api/athletes', methods=['GET'])
def get_athletes():
    return jsonify(athletes)

@app.route('/api/athletes', methods=['POST'])
def create_athlete():
    data = request.get_json()
    
    athlete = {
        "id": len(athletes) + 1,
        "name": data.get("name"),
        "position": data.get("position"),
        "conference": data.get("conference"),
        "transfer_from": data.get("transfer_from"),
        "games_played": data.get("games_played"),
        "market_value": data.get("market_value"),
        "total_tackles": data.get("total_tackles", 0),
        "solo_tackles": data.get("solo_tackles", 0)
    }
    
    athletes.append(athlete)
    return jsonify(athlete), 201

@app.route('/api/evaluate', methods=['POST'])
def evaluate_player():
    data = request.get_json()
    
    production_score = (data.get("total_tackles", 0) / 11) * 92
    efficiency_rating = 85.0  # Simplified
    positional_impact = 78.0  # Simplified
    
    evaluation = {
        "production_score": production_score,
        "efficiency_rating": efficiency_rating,
        "positional_impact": positional_impact,
        "overall_score": (production_score + efficiency_rating + positional_impact) / 3
    }
    
    return jsonify(evaluation)

@app.route('/api/optimize', methods=['POST'])
def optimize_roster():
    data = request.get_json()
    budget_tier = data.get("budget_tier", "Power4_Elite")
    
    selected_players = athletes[:5] if len(athletes) >= 5 else athletes
    
    result = {
        "selected_players": selected_players,
        "total_cost": sum(p.get("market_value", 0) for p in selected_players),
        "budget_tier": budget_tier,
        "optimization_score": 85.5
    }
    
    return jsonify(result)

@app.route('/api/market-analysis', methods=['GET'])
def market_analysis():
    analysis = {
        "high_value_low_cost": athletes[:2] if len(athletes) >= 2 else [],
        "high_value_high_cost": athletes[2:4] if len(athletes) >= 4 else [],
        "low_value_low_cost": athletes[4:6] if len(athletes) >= 6 else [],
        "low_value_high_cost": athletes[6:8] if len(athletes) >= 8 else []
    }
    
    return jsonify(analysis)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
