import json
import os
from typing import Dict, Optional
from fastapi import HTTPException

class SentimentService:
    """Service to fetch sentiment analysis data from aggregated JSON files"""
    
    def __init__(self):
        # Path to the ingestservice data directory relative to backend
        self.data_dir = os.path.join(os.path.dirname(__file__), "../../../ingestservice/data/agg/daily")
        
    def get_sentiment_file_path(self, drug_name: str) -> str:
        """Get the file path for a drug's sentiment data"""
        # Normalize drug name to lowercase for file matching
        normalized_name = drug_name.lower().strip()
        return os.path.join(self.data_dir, f"{normalized_name}.json")
    
    def read_sentiment_data(self, file_path: str) -> Optional[Dict]:
        """Read sentiment data from JSON file"""
        try:
            if not os.path.exists(file_path):
                return None
                
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error reading sentiment file {file_path}: {e}")
            return None
    
    def fetch_drug_sentiment(self, drug_name: str) -> Dict:
        """
        Fetch sentiment analysis data for a specific drug
        
        Args:
            drug_name (str): Name of the drug to get sentiment data for
            
        Returns:
            Dict: Sentiment analysis data or empty structure if no data available
        """
        if not drug_name or not drug_name.strip():
            return self._get_empty_sentiment_response(drug_name)
        
        file_path = self.get_sentiment_file_path(drug_name)
        sentiment_data = self.read_sentiment_data(file_path)
        
        if sentiment_data is None:
            return self._get_empty_sentiment_response(drug_name)
        
        # Validate that we have the expected structure
        required_fields = ["drug_name", "sentiment_data", "overall_sentiment", "sentiment_score", "total_posts_analyzed", "analysis_date"]
        missing_fields = [field for field in required_fields if field not in sentiment_data]
        
        if missing_fields:
            # Return empty response instead of error for malformed data
            print(f"Warning: Invalid sentiment data structure for {drug_name}. Missing fields: {missing_fields}")
            return self._get_empty_sentiment_response(drug_name)
        
        return sentiment_data
    
    def _get_empty_sentiment_response(self, drug_name: str) -> Dict:
        """Return empty sentiment response structure"""
        return {
            "drug_name": drug_name,
            "sentiment_data": [],
            "overall_sentiment": "neutral",
            "sentiment_score": 0.0,
            "total_posts_analyzed": 0,
            "analysis_date": None,
            "data_available": False,
            "message": f"No sentiment data available for '{drug_name}'"
        }
    
    def list_available_drugs(self) -> list:
        """Get list of drugs that have sentiment data available"""
        try:
            if not os.path.exists(self.data_dir):
                return []
            
            drugs = []
            for filename in os.listdir(self.data_dir):
                if filename.endswith('.json'):
                    drug_name = filename[:-5]  # Remove .json extension
                    drugs.append(drug_name)
            
            return sorted(drugs)
        except Exception as e:
            print(f"Error listing available drugs: {e}")
            return []

# Global instance for easy access
sentiment_service = SentimentService()

def fetch_sentiment(drug_name: str) -> Dict:
    """
    Main function to fetch sentiment data for a drug
    This is the function called by the FastAPI endpoint
    """
    return sentiment_service.fetch_drug_sentiment(drug_name)

# Additional helper function for the API
def get_available_drugs() -> Dict:
    """Get list of drugs with available sentiment data"""
    drugs = sentiment_service.list_available_drugs()
    return {
        "available_drugs": drugs,
        "total_count": len(drugs)
    }
