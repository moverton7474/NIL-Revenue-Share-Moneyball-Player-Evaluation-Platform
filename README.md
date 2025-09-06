# NIL Moneyball Platform

A comprehensive college football roster optimization platform using Moneyball analytics and NIL budget constraints.

## Features

- **Player Evaluation System**: Position-specific production scores and efficiency ratings
- **Budget Management**: Four distinct budget tiers from $800K to $20.5M
- **Baron Hopson Methodology**: 3.5x value multiplier for FCS transfers at Group5 schools
- **Optimization Algorithm**: Greedy algorithm selecting players by value-per-dollar ratio
- **Market Analysis**: Transfer portal market opportunity matrix
- **Responsive UI**: Purple gradient header design with intuitive dashboard

## Budget Tiers

1. **Group5_Low**: $800,000 total budget
2. **Group5_High**: $1,300,000 total budget  
3. **Power4_Standard**: $8,500,000 total budget
4. **Power4_Elite**: $20,500,000 total budget

## Mathematical Formulas

### Production Score (Linebackers)
```
Production Score = (tackles_per_game / 11) * 92
```

### Value per Dollar Calculation
```
Value per Dollar = (production + efficiency + impact) / 3 / (cost / 1000)
```

### Baron Hopson Multipliers
- Group5_Low: 3.5x for FCS transfers
- Group5_High: 3.0x for FCS transfers
- Power4_Standard: 1.5x for FCS transfers
- Power4_Elite: 1.0x for FCS transfers

## Quick Start

### Using Docker (Recommended)

1. Clone the repository
2. Build and run with Docker Compose:
```bash
docker-compose up --build
```
3. Access the application at http://localhost

### Manual Setup

#### Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

#### Frontend Setup
```bash
cd frontend
# Serve with any static file server
python3 -m http.server 8080
```

## API Endpoints

### Core Endpoints
- `GET /api/health` - Health check
- `GET /api/budget-tiers` - Get budget tier configurations
- `GET /api/athletes` - Get all athletes
- `POST /api/athletes` - Create new athlete
- `POST /api/evaluate-player/<id>` - Evaluate player with Moneyball metrics
- `POST /api/optimize-roster` - Run roster optimization
- `GET /api/market-analysis` - Get market opportunity matrix
- `GET /api/baron-hopson-analysis/<id>` - Get Baron Hopson analysis

### Request Examples

#### Add Player
```json
POST /api/athletes
{
  "name": "Baron Hopson",
  "position": "LB",
  "conference": "ASUN",
  "transfer_from": "FCS",
  "games_played": 12,
  "market_value": 15000,
  "total_tackles": 11,
  "solo_tackles": 6
}
```

#### Run Optimization
```json
POST /api/optimize-roster
{
  "budget_tier": "Group5_Low"
}
```

## Database Schema

### Athletes Table
- Personal information and performance statistics
- Position-specific metrics (tackles, passing yards, etc.)
- Market value and transfer information

### Player Evaluations Table
- Production scores and efficiency ratings
- Value per dollar calculations
- Transfer multipliers

### Budget Tiers Table
- Tier configurations and constraints
- Position minimums and strategy settings

### Optimization Runs Table
- Historical optimization results
- Budget allocation and player selections

## Architecture

### Backend (Flask)
- RESTful API with SQLAlchemy ORM
- SQLite database for data persistence
- Moneyball evaluation engine
- Greedy optimization algorithm

### Frontend (Vanilla JavaScript)
- Responsive dashboard with purple gradient header
- Interactive budget tier selection
- Real-time market analysis visualization
- Player management interface

### Deployment (Docker)
- Multi-container setup with Docker Compose
- Nginx reverse proxy for frontend
- Persistent data volumes
- Production-ready configuration

## Baron Hopson Case Study

The platform implements the Baron Hopson methodology based on his performance:
- 11 total tackles vs Wake Forest = 92/100 production score
- $15,000 NIL value vs $165,000 SEC comparable
- 6.57 value/dollar ratio vs 0.58 for SEC equivalent
- 3.5x multiplier for FCS transfers at Group5 schools

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

MIT License - see LICENSE file for details
