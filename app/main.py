from fastapi import FastAPI, HTTPException
from typing import List, Dict
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="FGO API",
    description="A simple API for Fate/Grand Order servant data",
    version="0.1.0"
)

def load_servant_data() -> List[Dict]:
    """Load servant data from JSON file"""
    try:
        with open('data/servants.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error("Servants data file not found")
        return []
    except json.JSONDecodeError:
        logger.error("Error decoding servants data file")
        return []

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Welcome to the FGO API!"}

@app.get("/servants")
async def get_servants():
    """Get all servants"""
    servants = load_servant_data()
    if not servants:
        raise HTTPException(status_code=404, detail="No servant data available")
    return servants

@app.get("/servants/{servant_id}")
async def get_servant(servant_id: int):
    """Get a specific servant by ID"""
    servants = load_servant_data()
    for servant in servants:
        if servant['id'] == servant_id:
            return servant
    raise HTTPException(status_code=404, detail="Servant not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)