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
    allow_origins=["http://localhost:5173", "https://rxu.austintbabu.com"],
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
    try:
        # First, search for the drug to get its details
        search_results = drug_search_service.search_drugs(drug_name, limit=1)
        
        if not search_results:
            return {
                "original_drug": drug_name,
                "recommendations": [],
                "message": f"No drug found matching '{drug_name}'"
            }
        
        original_drug = search_results[0]
        alternatives_str = original_drug.get("alternatives", "")
        
        if not alternatives_str or alternatives_str.strip() == "":
            return {
                "original_drug": drug_name,
                "recommendations": [],
                "message": f"No alternatives available for '{drug_name}'"
            }
        
        # Parse alternatives string (semicolon separated)
        alternatives_list = [alt.strip() for alt in alternatives_str.split(";") if alt.strip()]
        
        recommendations = []
        for i, alt in enumerate(alternatives_list):
            # Calculate a mock similarity score based on position (first alternative is most similar)
            similarity_score = max(0.95 - (i * 0.1), 0.5)
            
            recommendations.append({
                "name": alt,
                "similarity_score": similarity_score,
                "reason": f"Alternative therapy from the same or similar drug class"
            })
        
        return {
            "original_drug": drug_name,
            "recommendations": recommendations
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching recommendations: {str(e)}")

@app.get("/api/drugs/side-effects")
async def get_side_effects(drug_name: str = Query(..., description="Drug name to get side effects for")):
    """Get side effect information"""
    try:
        # First, search for the drug to get its details
        search_results = drug_search_service.search_drugs(drug_name, limit=1)
        
        if not search_results:
            return {
                "drug_name": drug_name,
                "common_side_effects": [],
                "serious_side_effects": [],
                "message": f"No drug found matching '{drug_name}'"
            }
        
        original_drug = search_results[0]
        side_effects_str = original_drug.get("side_effects", "")
        
        if not side_effects_str or side_effects_str.strip() == "":
            return {
                "drug_name": drug_name,
                "common_side_effects": [],
                "serious_side_effects": [],
                "message": f"No side effects data available for '{drug_name}'"
            }
        
        # Parse side effects string (semicolon separated)
        side_effects_list = [effect.strip() for effect in side_effects_str.split(";") if effect.strip()]
        
        common_side_effects = []
        serious_side_effects = []
        
        for effect in side_effects_list:
            effect_lower = effect.lower()
            
            # Categorize effects based on keywords
            if any(keyword in effect_lower for keyword in ["severe", "major", "serious", "life-threatening", "rare", "hemorrhage", "anaphylaxis", "apoplexy"]):
                # Determine frequency based on keywords
                if "rare" in effect_lower:
                    frequency = "rare"
                elif any(word in effect_lower for word in ["major", "severe"]):
                    frequency = "uncommon"
                else:
                    frequency = "rare"
                
                serious_side_effects.append({
                    "effect": effect,
                    "frequency": frequency,
                    "severity": "severe"
                })
            else:
                # Common side effects
                # Determine frequency for common effects
                if any(word in effect_lower for word in ["common", "frequent"]):
                    frequency = "common"
                elif any(word in effect_lower for word in ["uncommon", "occasional"]):
                    frequency = "uncommon"
                else:
                    frequency = "common"  # Default for non-categorized effects
                
                # Determine severity
                if any(word in effect_lower for word in ["mild", "minor"]):
                    severity = "mild"
                elif any(word in effect_lower for word in ["moderate"]):
                    severity = "moderate"
                else:
                    severity = "mild"  # Default
                
                common_side_effects.append({
                    "effect": effect,
                    "frequency": frequency,
                    "severity": severity
                })
        
        return {
            "drug_name": drug_name,
            "common_side_effects": common_side_effects,
            "serious_side_effects": serious_side_effects
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching side effects: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)