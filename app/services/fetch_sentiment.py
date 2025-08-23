import json
import os
import boto3
from typing import Optional, Dict
from fastapi import HTTPException

AWS_ACCESS_KEY = "AKIATLIHLWTMONL4MO4Q"
AWS_SECRET_KEY = "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"
AWS_S3_BUCKET_NAME = "rxu-bucket"
AWS_REGION = "ap-south-1"
S3_PREFIX = "agg/"  # S3 folder prefix


class SentimentService:
    """Service to fetch sentiment analysis data from aggregated JSON files"""

    def __init__(self):
        app_dir = os.path.dirname(os.path.abspath(__file__))
        self.folder_path = os.path.join(app_dir, "cache")
        os.makedirs(self.folder_path, exist_ok=True)  # make sure cache exists

    def get_sentiment_file_path(self, drug_name: str) -> Optional[str]:
        """Get the file path for a drug's sentiment data and fetch if needed"""
        normalized_name = drug_name.lower().strip()
        json_path = os.path.join(self.folder_path, f"{normalized_name}.json")

        if os.path.exists(json_path):
            print(f"✅ Using cached file: {json_path}")
            return json_path    
        else:
            return self.fetch_file(json_path, drug_name)

    def fetch_file(self, json_path: str, drug_name: str) -> Optional[str]:
        """Fetch file from S3 and save locally"""
        try:
            # Create dynamic S3 key based on drug name
            normalized_name = drug_name.lower().strip()
            s3_key = f"{S3_PREFIX}{normalized_name}.json"
            
            s3_client = boto3.client(
                service_name="s3",
                region_name=AWS_REGION,
                aws_access_key_id=AWS_ACCESS_KEY,
                aws_secret_access_key=AWS_SECRET_KEY,
            )

            response = s3_client.get_object(Bucket=AWS_S3_BUCKET_NAME, Key=s3_key)
            content = response["Body"].read().decode("utf-8")
            data = json.loads(content)

            # Save JSON locally
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)

            print(f"✅ Fetched JSON from s3://{AWS_S3_BUCKET_NAME}/{s3_key}")
            return json_path

        except Exception as e:
            print(f"❌ Error fetching file s3://{AWS_S3_BUCKET_NAME}/{s3_key}: {e}")
            return None
    
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
        
        if not file_path:
            return self._get_empty_sentiment_response(drug_name)
            
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
            if not os.path.exists(self.folder_path):
                return []
            
            drugs = []
            for filename in os.listdir(self.folder_path):
                if filename.endswith('.json'):
                    drug_name = filename[:-5]  # Remove .json extension
                    drugs.append(drug_name)
            
            return sorted(drugs)
        except Exception as e:
            print(f"Error listing available drugs: {e}")
            return []

    def clear_cache(self, drug_name: str = None):
        """Clear cache for specific drug or all drugs"""
        try:
            if drug_name:
                # Clear specific drug cache
                normalized_name = drug_name.lower().strip()
                file_path = os.path.join(self.folder_path, f"{normalized_name}.json")
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"✅ Cleared cache for {drug_name}")
                else:
                    print(f"❌ No cache found for {drug_name}")
            else:
                # Clear all cache
                if os.path.exists(self.folder_path):
                    for filename in os.listdir(self.folder_path):
                        if filename.endswith('.json'):
                            os.remove(os.path.join(self.folder_path, filename))
                    print("✅ Cleared all cache")
        except Exception as e:
            print(f"❌ Error clearing cache: {e}")

    def force_fetch_drug_sentiment(self, drug_name: str) -> Dict:
        """Force fetch from S3 (ignores cache)"""
        # Clear cache first
        self.clear_cache(drug_name)
        # Then fetch normally (will go to S3)
        return self.fetch_drug_sentiment(drug_name)

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


if __name__ == "__main__":
    # Create service instance
    service = SentimentService()
    
    # Test with ALL the drugs you have in S3
    test_drugs = ["aspirin", "adalimumab", "biotin"]
    
    print("="*60)
    print("TESTING ALL DRUGS FROM S3")
    print("="*60)
    
    for drug_name in test_drugs:
        print(f"\n--- Fetching sentiment data for '{drug_name}' ---")
        sentiment_data = service.fetch_drug_sentiment(drug_name)
        
        if sentiment_data.get('data_available', False):
            print(f"✅ SUCCESS for {drug_name}")
            print(f"   - Overall sentiment: {sentiment_data.get('overall_sentiment', 'N/A')}")
            print(f"   - Sentiment score: {sentiment_data.get('sentiment_score', 'N/A')}")
            print(f"   - Total posts: {sentiment_data.get('total_posts_analyzed', 'N/A')}")
        else:
            print(f"❌ FAILED for {drug_name}")
            print(f"   - Message: {sentiment_data.get('message', 'N/A')}")
    
    # Test listing all available drugs in cache
    print(f"\n--- Available drugs in cache ---")
    available_drugs = service.list_available_drugs()
    print(f"Cached drugs: {available_drugs}")
    print(f"Total cached: {len(available_drugs)}")
    
    # Test individual drug (change this to test specific ones)
    single_test_drug = "adalimumab"  # Change this to test different drugs
    print(f"\n--- Single test for '{single_test_drug}' ---")
    file_path = service.get_sentiment_file_path(single_test_drug)
    print(f"File path: {file_path}")