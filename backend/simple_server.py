#!/usr/bin/env python3
import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading

athletes = []
budget_tiers = {
    "Group5_Low": {"total_budget": 800000, "max_individual": 75000, "position_minimums": {"QB": 1, "RB": 2, "WR": 4, "LB": 3, "DB": 4}, "fcs_transfer_bonus": 3.5, "strategy": "Value Maximization"},
    "Group5_High": {"total_budget": 1300000, "max_individual": 140000, "position_minimums": {"QB": 1, "RB": 2, "WR": 4, "LB": 3, "DB": 4}, "fcs_transfer_bonus": 2.8, "strategy": "Balanced Value"},
    "Power4_Standard": {"total_budget": 8500000, "max_individual": 1500000, "position_minimums": {"QB": 2, "RB": 3, "WR": 5, "LB": 3, "DB": 5}, "fcs_transfer_bonus": 1.5, "strategy": "Talent Acquisition"},
    "Power4_Elite": {"total_budget": 20500000, "max_individual": 2500000, "position_minimums": {"QB": 2, "RB": 4, "WR": 6, "LB": 4, "DB": 6}, "fcs_transfer_bonus": 1.0, "strategy": "Elite Talent Focus"}
}

class APIHandler(BaseHTTPRequestHandler):
    def _send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        
    def _send_json_response(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self._send_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()
    
    def do_GET(self):
        path = urlparse(self.path).path
        
        if path == '/':
            self._send_json_response({"status": "healthy", "message": "NIL Moneyball Platform API"})
        elif path == '/api/budget-tiers':
            self._send_json_response(budget_tiers)
        elif path == '/api/athletes':
            self._send_json_response(athletes)
        elif path == '/api/market-analysis':
            analysis = {
                "high_value_low_cost": athletes[:2] if len(athletes) >= 2 else [],
                "high_value_high_cost": athletes[2:4] if len(athletes) >= 4 else [],
                "low_value_low_cost": athletes[4:6] if len(athletes) >= 6 else [],
                "low_value_high_cost": athletes[6:8] if len(athletes) >= 8 else []
            }
            self._send_json_response(analysis)
        else:
            self._send_json_response({"error": "Not found"}, 404)
    
    def do_POST(self):
        path = urlparse(self.path).path
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode())
        except:
            self._send_json_response({"error": "Invalid JSON"}, 400)
            return
        
        if path == '/api/athletes':
            new_athlete = {
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
            athletes.append(new_athlete)
            self._send_json_response(new_athlete, 201)
            
        elif path == '/api/evaluate':
            production_score = (data.get("total_tackles", 0) / 11) * 92 if data.get("total_tackles") else 0
            efficiency_rating = 85.0
            positional_impact = 78.0
            overall_score = (production_score + efficiency_rating + positional_impact) / 3
            
            evaluation = {
                "production_score": round(production_score, 2),
                "efficiency_rating": efficiency_rating,
                "positional_impact": positional_impact,
                "overall_score": round(overall_score, 2)
            }
            self._send_json_response(evaluation)
            
        elif path == '/api/optimize':
            budget_tier = data.get("budget_tier", "Power4_Elite")
            selected_players = athletes[:5] if len(athletes) >= 5 else athletes
            total_cost = sum(p.get("market_value", 0) for p in selected_players if p.get("market_value"))
            
            result = {
                "selected_players": selected_players,
                "total_cost": total_cost,
                "budget_tier": budget_tier,
                "optimization_score": 85.5
            }
            self._send_json_response(result)
        else:
            self._send_json_response({"error": "Not found"}, 404)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    server = HTTPServer(('0.0.0.0', port), APIHandler)
    print(f'Server running on port {port}')
    server.serve_forever()
