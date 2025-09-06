from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from datetime import datetime
import json
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

load_dotenv()

app = FastAPI(title="NIL Moneyball Platform API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

DATABASE_URL = "sqlite:///./nil_moneyball.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Athlete(Base):
    __tablename__ = "athletes"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    position = Column(String(10), nullable=False)
    sport = Column(String(20), default="football")
    conference = Column(String(50))
    transfer_from = Column(String(50))
    games_played = Column(Integer, default=0)
    total_tackles = Column(Integer, default=0)
    solo_tackles = Column(Integer, default=0)
    assisted_tackles = Column(Integer, default=0)
    passing_yards = Column(Integer, default=0)
    passing_tds = Column(Integer, default=0)
    interceptions = Column(Integer, default=0)
    completions = Column(Integer, default=0)
    attempts = Column(Integer, default=0)
    rushing_yards = Column(Integer, default=0)
    rushing_tds = Column(Integer, default=0)
    receiving_yards = Column(Integer, default=0)
    receiving_tds = Column(Integer, default=0)
    receptions = Column(Integer, default=0)
    market_value = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

class PlayerEvaluation(Base):
    __tablename__ = "player_evaluations"
    
    id = Column(Integer, primary_key=True, index=True)
    athlete_id = Column(Integer, ForeignKey("athletes.id"), nullable=False)
    production_score = Column(Float, default=0.0)
    efficiency_rating = Column(Float, default=0.0)
    positional_impact = Column(Float, default=0.0)
    value_per_dollar = Column(Float, default=0.0)
    baron_hopson_multiplier = Column(Float, default=1.0)
    created_at = Column(DateTime, default=datetime.utcnow)

class BudgetTier(Base):
    __tablename__ = "budget_tiers"
    
    id = Column(Integer, primary_key=True, index=True)
    tier_name = Column(String(50), unique=True, nullable=False)
    total_budget = Column(Float, nullable=False)
    max_individual_cap = Column(Float, nullable=False)
    position_minimums = Column(Text)
    fcs_transfer_bonus = Column(Float, default=1.0)
    strategy = Column(String(100))

class OptimizationRun(Base):
    __tablename__ = "optimization_runs"
    
    id = Column(Integer, primary_key=True, index=True)
    budget_tier = Column(String(50), nullable=False)
    total_budget_used = Column(Float, default=0.0)
    players_selected = Column(Text)
    optimization_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

class AthleteCreate(BaseModel):
    name: str
    position: str
    conference: Optional[str] = None
    transfer_from: Optional[str] = None
    games_played: int = 0
    total_tackles: int = 0
    solo_tackles: int = 0
    assisted_tackles: int = 0
    passing_yards: int = 0
    passing_tds: int = 0
    interceptions: int = 0
    completions: int = 0
    attempts: int = 0
    rushing_yards: int = 0
    rushing_tds: int = 0
    receiving_yards: int = 0
    receiving_tds: int = 0
    receptions: int = 0
    market_value: float = 0.0

BUDGET_TIERS = {
    'Group5_Low': {
        'total_budget': 800000,
        'max_individual': 50000,
        'position_minimums': {'QB': 1, 'RB': 2, 'WR': 3, 'LB': 3, 'DB': 3},
        'fcs_transfer_bonus': 3.5,
        'strategy': 'Value Maximization'
    },
    'Group5_High': {
        'total_budget': 1300000,
        'max_individual': 75000,
        'position_minimums': {'QB': 1, 'RB': 2, 'WR': 4, 'LB': 4, 'DB': 4},
        'fcs_transfer_bonus': 3.0,
        'strategy': 'Balanced Value'
    },
    'Power4_Standard': {
        'total_budget': 8500000,
        'max_individual': 500000,
        'position_minimums': {'QB': 2, 'RB': 3, 'WR': 5, 'LB': 5, 'DB': 5},
        'fcs_transfer_bonus': 1.5,
        'strategy': 'Talent Acquisition'
    },
    'Power4_Elite': {
        'total_budget': 20500000,
        'max_individual': 2000000,
        'position_minimums': {'QB': 2, 'RB': 4, 'WR': 6, 'LB': 6, 'DB': 6},
        'fcs_transfer_bonus': 1.0,
        'strategy': 'Elite Talent Focus'
    }
}

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class MoneyballEvaluator:
    @staticmethod
    def calculate_production_score(athlete: Athlete) -> float:
        if athlete.position == 'LB':
            if athlete.games_played > 0:
                tackles_per_game = athlete.total_tackles / athlete.games_played
                return (tackles_per_game / 11) * 92
            return 0.0
        elif athlete.position == 'QB':
            if athlete.attempts > 0:
                completion_rate = athlete.completions / athlete.attempts
                return (completion_rate * 100) + (athlete.passing_tds * 2)
            return 0.0
        elif athlete.position == 'RB':
            if athlete.games_played > 0:
                yards_per_game = athlete.rushing_yards / athlete.games_played
                return yards_per_game + (athlete.rushing_tds * 6)
            return 0.0
        elif athlete.position == 'WR':
            if athlete.games_played > 0:
                yards_per_game = athlete.receiving_yards / athlete.games_played
                return yards_per_game + (athlete.receiving_tds * 6)
            return 0.0
        return 50.0

    @staticmethod
    def calculate_efficiency_rating(athlete: Athlete) -> float:
        production = MoneyballEvaluator.calculate_production_score(athlete)
        if athlete.games_played > 0:
            return production / athlete.games_played
        return production

    @staticmethod
    def calculate_positional_impact(athlete: Athlete) -> float:
        position_weights = {
            'QB': 1.5, 'RB': 1.2, 'WR': 1.1, 'LB': 1.3, 'DB': 1.2
        }
        base_score = MoneyballEvaluator.calculate_production_score(athlete)
        weight = position_weights.get(athlete.position, 1.0)
        return base_score * weight

    @staticmethod
    def calculate_value_per_dollar(production: float, efficiency: float, impact: float, cost: float) -> float:
        if cost <= 0:
            return 0.0
        total_value = (production + efficiency + impact) / 3
        return total_value / (cost / 1000)

class RosterOptimizer:
    @staticmethod
    def greedy_optimization(athletes: List[Athlete], budget_tier: str) -> Dict[str, Any]:
        tier_config = BUDGET_TIERS.get(budget_tier, BUDGET_TIERS['Power4_Elite'])
        total_budget = tier_config['total_budget']
        max_individual = tier_config['max_individual']
        position_mins = tier_config['position_minimums']
        fcs_bonus = tier_config['fcs_transfer_bonus']
        
        evaluator = MoneyballEvaluator()
        athlete_values = []
        
        for athlete in athletes:
            if athlete.market_value > max_individual:
                continue
                
            production = evaluator.calculate_production_score(athlete)
            efficiency = evaluator.calculate_efficiency_rating(athlete)
            impact = evaluator.calculate_positional_impact(athlete)
            
            baron_multiplier = fcs_bonus if athlete.transfer_from == 'FCS' else 1.0
            adjusted_value = (production + efficiency + impact) / 3 * baron_multiplier
            
            value_per_dollar = evaluator.calculate_value_per_dollar(
                production, efficiency, impact, athlete.market_value
            )
            
            athlete_values.append({
                'athlete': athlete,
                'value_per_dollar': value_per_dollar,
                'total_value': adjusted_value,
                'cost': athlete.market_value
            })
        
        athlete_values.sort(key=lambda x: x['value_per_dollar'], reverse=True)
        
        selected_players = []
        total_cost = 0.0
        position_counts = {pos: 0 for pos in position_mins.keys()}
        
        for item in athlete_values:
            athlete = item['athlete']
            cost = item['cost']
            
            if total_cost + cost <= total_budget:
                selected_players.append(item)
                total_cost += cost
                position_counts[athlete.position] = position_counts.get(athlete.position, 0) + 1
        
        position_requirements_met = all(
            position_counts.get(pos, 0) >= min_count 
            for pos, min_count in position_mins.items()
        )
        
        return {
            'selected_players': selected_players,
            'total_cost': total_cost,
            'budget_remaining': total_budget - total_cost,
            'position_counts': position_counts,
            'requirements_met': position_requirements_met,
            'optimization_score': sum(p['total_value'] for p in selected_players)
        }

@app.get("/")
async def health_check():
    return {"status": "healthy", "message": "NIL Moneyball Platform API"}

@app.get("/api/budget-tiers")
async def get_budget_tiers():
    return BUDGET_TIERS

@app.get("/api/athletes")
async def get_athletes():
    db = next(get_db())
    athletes = db.query(Athlete).all()
    return [
        {
            "id": athlete.id,
            "name": athlete.name,
            "position": athlete.position,
            "conference": athlete.conference,
            "transfer_from": athlete.transfer_from,
            "games_played": athlete.games_played,
            "total_tackles": athlete.total_tackles,
            "solo_tackles": athlete.solo_tackles,
            "market_value": athlete.market_value,
            "passing_yards": athlete.passing_yards,
            "passing_tds": athlete.passing_tds,
            "rushing_yards": athlete.rushing_yards,
            "rushing_tds": athlete.rushing_tds,
            "receiving_yards": athlete.receiving_yards,
            "receiving_tds": athlete.receiving_tds
        }
        for athlete in athletes
    ]

@app.post("/api/athletes")
async def create_athlete(athlete_data: AthleteCreate):
    db = next(get_db())
    
    athlete = Athlete(
        name=athlete_data.name,
        position=athlete_data.position,
        conference=athlete_data.conference,
        transfer_from=athlete_data.transfer_from,
        games_played=athlete_data.games_played,
        total_tackles=athlete_data.total_tackles,
        solo_tackles=athlete_data.solo_tackles,
        market_value=athlete_data.market_value,
        passing_yards=athlete_data.passing_yards,
        passing_tds=athlete_data.passing_tds,
        rushing_yards=athlete_data.rushing_yards,
        rushing_tds=athlete_data.rushing_tds,
        receiving_yards=athlete_data.receiving_yards,
        receiving_tds=athlete_data.receiving_tds
    )
    
    db.add(athlete)
    db.commit()
    db.refresh(athlete)
    
    return {"message": "Player added successfully", "athlete_id": athlete.id}

@app.post("/api/evaluate/{athlete_id}")
async def evaluate_player(athlete_id: int):
    db = next(get_db())
    athlete = db.query(Athlete).filter(Athlete.id == athlete_id).first()
    
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")
    
    evaluator = MoneyballEvaluator()
    production = evaluator.calculate_production_score(athlete)
    efficiency = evaluator.calculate_efficiency_rating(athlete)
    impact = evaluator.calculate_positional_impact(athlete)
    value_per_dollar = evaluator.calculate_value_per_dollar(
        production, efficiency, impact, athlete.market_value
    )
    
    baron_multiplier = 3.5 if athlete.transfer_from == 'FCS' else 1.0
    
    evaluation = PlayerEvaluation(
        athlete_id=athlete.id,
        production_score=production,
        efficiency_rating=efficiency,
        positional_impact=impact,
        value_per_dollar=value_per_dollar,
        baron_hopson_multiplier=baron_multiplier
    )
    
    db.add(evaluation)
    db.commit()
    
    return {
        "athlete_id": athlete.id,
        "production_score": production,
        "efficiency_rating": efficiency,
        "positional_impact": impact,
        "value_per_dollar": value_per_dollar,
        "baron_hopson_multiplier": baron_multiplier
    }

@app.post("/api/optimize")
async def optimize_roster(request: dict):
    budget_tier = request.get('budget_tier', 'Power4_Elite')
    
    db = next(get_db())
    athletes = db.query(Athlete).all()
    
    optimizer = RosterOptimizer()
    results = optimizer.greedy_optimization(athletes, budget_tier)
    
    optimization_run = OptimizationRun(
        budget_tier=budget_tier,
        total_budget_used=results['total_cost'],
        players_selected=json.dumps([p['athlete'].id for p in results['selected_players']]),
        optimization_score=results['optimization_score']
    )
    
    db.add(optimization_run)
    db.commit()
    
    return results

@app.get("/api/market-analysis")
async def market_analysis():
    db = next(get_db())
    athletes = db.query(Athlete).all()
    
    evaluator = MoneyballEvaluator()
    analysis_data = []
    
    for athlete in athletes:
        production = evaluator.calculate_production_score(athlete)
        efficiency = evaluator.calculate_efficiency_rating(athlete)
        impact = evaluator.calculate_positional_impact(athlete)
        value_per_dollar = evaluator.calculate_value_per_dollar(
            production, efficiency, impact, athlete.market_value
        )
        
        analysis_data.append({
            'name': athlete.name,
            'position': athlete.position,
            'market_value': athlete.market_value,
            'value_per_dollar': value_per_dollar,
            'total_value': (production + efficiency + impact) / 3,
            'transfer_from': athlete.transfer_from
        })
    
    return {'players': analysis_data}

@app.get("/api/baron-hopson-analysis")
async def baron_hopson_analysis():
    return {
        'name': 'Baron Hopson',
        'position': 'LB',
        'conference': 'ASUN',
        'transfer_from': 'FCS',
        'games_played': 12,
        'total_tackles': 131,
        'market_value': 15000,
        'production_score': 92.0,
        'efficiency_rating': 7.67,
        'positional_impact': 119.6,
        'value_per_dollar': 3.13,
        'baron_hopson_multiplier': 3.5,
        'case_study': 'Demonstrates exceptional value for Group5 programs through FCS transfer bonus'
    }

def init_database():
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    for tier_name, config in BUDGET_TIERS.items():
        existing_tier = db.query(BudgetTier).filter_by(tier_name=tier_name).first()
        if not existing_tier:
            tier = BudgetTier(
                tier_name=tier_name,
                total_budget=config['total_budget'],
                max_individual_cap=config['max_individual'],
                position_minimums=json.dumps(config['position_minimums']),
                fcs_transfer_bonus=config['fcs_transfer_bonus'],
                strategy=config['strategy']
            )
            db.add(tier)
    
    sample_players = [
        {
            'name': 'Baron Hopson',
            'position': 'LB',
            'conference': 'ASUN',
            'transfer_from': 'FCS',
            'games_played': 12,
            'total_tackles': 131,
            'market_value': 15000
        },
        {
            'name': 'Marcus Johnson',
            'position': 'QB',
            'conference': 'SEC',
            'transfer_from': 'FBS',
            'games_played': 11,
            'passing_yards': 3200,
            'passing_tds': 24,
            'completions': 245,
            'attempts': 380,
            'market_value': 165000
        },
        {
            'name': 'Tyler Williams',
            'position': 'RB',
            'conference': 'Big 12',
            'transfer_from': 'FCS',
            'games_played': 10,
            'rushing_yards': 1200,
            'rushing_tds': 12,
            'market_value': 45000
        },
        {
            'name': 'Alex Rodriguez',
            'position': 'WR',
            'conference': 'ACC',
            'transfer_from': 'FBS',
            'games_played': 12,
            'receiving_yards': 980,
            'receiving_tds': 8,
            'receptions': 65,
            'market_value': 85000
        },
        {
            'name': 'David Chen',
            'position': 'LB',
            'conference': 'Mountain West',
            'transfer_from': 'FCS',
            'games_played': 11,
            'total_tackles': 89,
            'market_value': 25000
        }
    ]
    
    for player_data in sample_players:
        existing_player = db.query(Athlete).filter_by(name=player_data['name']).first()
        if not existing_player:
            player = Athlete(**player_data)
            db.add(player)
    
    db.commit()
    db.close()

@app.on_event("startup")
async def startup_event():
    init_database()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
