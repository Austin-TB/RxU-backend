from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import uvicorn

from app.services.drug_search import drug_search_service
from app.services.fetch_sentiment import fetch_sentiment, get_available_drugs

app = FastAPI(
    title="RxU-backend",
    description="API for RxU",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "RxU-backend API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# API endpoints
@app.get("/api/drugs/search")
async def search_drugs(q: str = Query(..., description="Drug name to search for")):
    """Search drugs and fetch metadata"""
    try:
        search_results = drug_search_service.search_drugs(q, limit=10)
        
        if not search_results:
            return {
                "query": q,
                "results": [],
                "message": "No drugs found matching your search query"
            }
        
        formatted_results = []
        for drug in search_results:
            # Convert synonyms string to array for brand_names
            synonyms_str = drug.get("synonyms", "")
            if synonyms_str and isinstance(synonyms_str, str):
                # Split on semicolon and clean up each item
                brand_names = [name.strip() for name in synonyms_str.split(";") if name.strip()]
            else:
                brand_names = []
            
            formatted_drug = {
                "drugbank_id": drug["drugbank_id"],
                "name": drug["name"],
                "generic_name": drug["generic_name"],
                "brand_names": brand_names,
                "drug_class": drug["drug_class"],
                "description": drug["description"],
                "match_score": drug.get("match_score", 100),
                "match_type": drug.get("match_type", "exact")
            }
            formatted_results.append(formatted_drug)
        
        return {
            "query": q,
            "results": formatted_results,
            "total_found": len(formatted_results)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")

@app.get("/api/drugs/sentiment")
async def get_drug_sentiment(drug_name: str = Query(..., description="Drug name for sentiment analysis")):
    """Retrieve sentiment trend data"""
    try:
        sentiment_result = fetch_sentiment(drug_name)
        return sentiment_result
    except Exception as e:
        # Only catch unexpected errors, return empty response for expected cases
        print(f"Unexpected error in sentiment analysis: {str(e)}")
        return {
            "drug_name": drug_name,
            "sentiment_data": [],
            "overall_sentiment": "neutral",
            "sentiment_score": 0.0,
            "total_posts_analyzed": 0,
            "analysis_date": None,
            "data_available": False,
            "message": f"Error processing sentiment data for '{drug_name}': {str(e)}"
        }

@app.get("/api/drugs/sentiment/available")
async def get_available_sentiment_drugs():
    """Get list of drugs with available sentiment data"""
    try:
        return get_available_drugs()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching available drugs: {str(e)}")

@app.get("/api/drugs/recommend")
async def recommend_drugs(drug_name: str = Query(..., description="Drug name to find alternatives for")):
    """Get recommended similar drugs"""
    
    

    return {
        "original_drug": drug_name,
        "recommendations": [
            {
                "name": f"Alternative 1 to {drug_name}",
                "similarity_score": 0.85,
                "reason": "Similar therapeutic effect with fewer side effects"
            },
            {
                "name": f"Alternative 2 to {drug_name}",
                "similarity_score": 0.78,
                "reason": "Same drug class with different mechanism"
            }
        ]
    }

@app.get("/api/drugs/side-effects")
async def get_side_effects(drug_name: str = Query(..., description="Drug name to get side effects for")):
    """Get side effect information"""
    # TODO: Implement side effects retrieval logic
    return {
        "drug_name": drug_name,
        "common_side_effects": [
            {"effect": "Nausea", "frequency": "common", "severity": "mild"},
            {"effect": "Headache", "frequency": "common", "severity": "mild"},
            {"effect": "Dizziness", "frequency": "uncommon", "severity": "moderate"}
        ],
        "serious_side_effects": [
            {"effect": "Liver damage", "frequency": "rare", "severity": "severe"}
        ]
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)