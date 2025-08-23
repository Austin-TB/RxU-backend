import json
import os
import shutil
import boto3
from botocore.exceptions import ClientError, NoCredentialsError, PartialCredentialsError
from typing import Optional, Dict

from dotenv import load_dotenv

load_dotenv(override=True)

AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
AWS_S3_BUCKET_NAME = "rxu-bucket"
AWS_REGION = "ap-south-1"
S3_PREFIX = "agg/"


class SentimentService:
    """Service to fetch sentiment analysis data from aggregated JSON files"""

    def __init__(self):
        app_dir = os.path.dirname(os.path.abspath(__file__))
        self.folder_path = os.path.join(app_dir, "cache")
        os.makedirs(self.folder_path, exist_ok=True)  # make sure cache exists
        
        # Set up local fallback directory
        project_root = os.path.abspath(os.path.join(app_dir, "../../../"))
        self.local_data_path = os.path.join(project_root, "backend", "data", "agg", "daily")
        
        # Initialize S3 client once and reuse
        self._s3_client = None
        self._validate_aws_config()

    def get_sentiment_file_path(self, drug_name: str) -> Optional[str]:
        """Get the file path for a drug's sentiment data and fetch if needed"""
        normalized_name = drug_name.lower().strip()
        json_path = os.path.join(self.folder_path, f"{normalized_name}.json")

        if os.path.exists(json_path):
            print(f"✅ Using cached file: {json_path}")
            return json_path    
        else:
            return self.fetch_file(json_path, drug_name)
    
    def _validate_aws_config(self) -> None:
        """Validate AWS configuration"""
        if not AWS_ACCESS_KEY or not AWS_SECRET_KEY:
            print("⚠️  Warning: AWS credentials not found in environment variables")
            print("   S3 functionality will be disabled. Will use local fallback if available.")
    
    def _get_local_file_path(self, drug_name: str) -> Optional[str]:
        """Get local file path for drug data"""
        normalized_name = drug_name.lower().strip()
        local_file_path = os.path.join(self.local_data_path, f"{normalized_name}.json")
        
        if os.path.exists(local_file_path):
            return local_file_path
        return None
    
    def _copy_from_local_to_cache(self, local_path: str, cache_path: str) -> bool:
        """Copy file from local storage to cache"""
        try:
            shutil.copy2(local_path, cache_path)
            print(f"✅ Copied from local storage: {local_path} -> {cache_path}")
            return True
        except Exception as e:
            print(f"❌ Failed to copy from local storage: {e}")
            return False
    
    @property
    def s3_client(self):
        """Lazy initialization of S3 client"""
        if self._s3_client is None:
            if not AWS_ACCESS_KEY or not AWS_SECRET_KEY:
                return None
            
            try:
                self._s3_client = boto3.client(
                    service_name="s3",
                    region_name=AWS_REGION,
                    aws_access_key_id=AWS_ACCESS_KEY,
                    aws_secret_access_key=AWS_SECRET_KEY,
                )
            except (NoCredentialsError, PartialCredentialsError) as e:
                print(f"❌ AWS credentials error: {e}")
                return None
        return self._s3_client

    def fetch_file(self, json_path: str, drug_name: str) -> Optional[str]:
        """Fetch file from S3 and save locally, with local fallback"""
        # Try S3 first if available
        if self.s3_client is not None:
            s3_result = self._fetch_from_s3(json_path, drug_name)
            if s3_result:
                return s3_result
        else:
            print(f"🔄 S3 not available, trying local fallback for {drug_name}")
        
        # Fallback to local storage
        return self._fetch_from_local(json_path, drug_name)
    
    def _fetch_from_s3(self, json_path: str, drug_name: str) -> Optional[str]:
        """Fetch file from S3 and save locally"""
        try:
            # Create dynamic S3 key based on drug name
            normalized_name = drug_name.lower().strip()
            s3_key = f"{S3_PREFIX}{normalized_name}.json"
            
            print(f"🔄 Fetching from S3: s3://{AWS_S3_BUCKET_NAME}/{s3_key}")
            
            response = self.s3_client.get_object(Bucket=AWS_S3_BUCKET_NAME, Key=s3_key)
            content = response["Body"].read().decode("utf-8")
            
            # Validate JSON before saving
            try:
                data = json.loads(content)
            except json.JSONDecodeError as e:
                print(f"❌ Invalid JSON format in S3 file {s3_key}: {e}")
                return None

            # Save JSON locally
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)

            print(f"✅ Fetched JSON from s3://{AWS_S3_BUCKET_NAME}/{s3_key}")
            return json_path

        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'NoSuchKey':
                print(f"⚠️  File not found in S3: s3://{AWS_S3_BUCKET_NAME}/{s3_key}")
            elif error_code == 'NoSuchBucket':
                print(f"❌ S3 bucket not found: {AWS_S3_BUCKET_NAME}")
            elif error_code == 'AccessDenied':
                print(f"❌ Access denied to S3: s3://{AWS_S3_BUCKET_NAME}/{s3_key}")
            else:
                print(f"❌ S3 error ({error_code}): {e}")
            return None
        except Exception as e:
            print(f"❌ Unexpected error fetching file s3://{AWS_S3_BUCKET_NAME}/{s3_key}: {e}")
            return None
    
    def _fetch_from_local(self, json_path: str, drug_name: str) -> Optional[str]:
        """Fetch file from local storage and copy to cache"""
        local_file_path = self._get_local_file_path(drug_name)
        
        if local_file_path is None:
            print(f"❌ File not found in local storage: {drug_name}")
            return None
        
        print(f"🔄 Using local fallback: {local_file_path}")
        
        # Copy from local storage to cache
        if self._copy_from_local_to_cache(local_file_path, json_path):
            return json_path
        else:
            # If copy fails, return the local path directly
            print(f"⚠️  Copy failed, using local file directly: {local_file_path}")
            return local_file_path
    
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
            "top_keywords": None,
            "confidence_score": None,
            "data_available": False,
            "message": f"No sentiment data available for '{drug_name}'"
        }
    
    def list_available_drugs(self) -> list:
        """Get list of drugs that have sentiment data available (cache + local storage)"""
        drugs = set()
        
        try:
            # Add drugs from cache
            if os.path.exists(self.folder_path):
                for filename in os.listdir(self.folder_path):
                    if filename.endswith('.json'):
                        drug_name = filename[:-5]  # Remove .json extension
                        drugs.add(drug_name)
            
            # Add drugs from local storage
            if os.path.exists(self.local_data_path):
                for filename in os.listdir(self.local_data_path):
                    if filename.endswith('.json'):
                        drug_name = filename[:-5]  # Remove .json extension
                        drugs.add(drug_name)
            
            return sorted(list(drugs))
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
    """Test script for sentiment service"""
    service = SentimentService()
    test_drugs = ["aspirin", "adalimumab", "biotin"]
    
    print("="*60)
    print("TESTING SENTIMENT SERVICE")
    print("="*60)
    
    for drug_name in test_drugs:
        print(f"\n--- Testing '{drug_name}' ---")
        sentiment_data = service.fetch_drug_sentiment(drug_name)
        
        if sentiment_data.get('data_available', True):  # Default to True since successful data won't have this field
            print(f"✅ SUCCESS for {sentiment_data.get('drug_name', drug_name)}")
            print(f"   📊 Overall sentiment: {sentiment_data.get('overall_sentiment', 'N/A')}")
            print(f"   📈 Sentiment score: {sentiment_data.get('sentiment_score', 'N/A')}")
            print(f"   📝 Total posts analyzed: {sentiment_data.get('total_posts_analyzed', 'N/A')}")
            print(f"   📅 Analysis date: {sentiment_data.get('analysis_date', 'N/A')}")
            
            # Show sentiment data summary
            sentiment_points = sentiment_data.get('sentiment_data', [])
            if sentiment_points:
                print(f"   📋 Sentiment data points: {len(sentiment_points)} days")
                total_posts = sum(point.get('post_count', 0) for point in sentiment_points)
                print(f"   📊 Total posts in timeline: {total_posts}")
        else:
            print(f"❌ FAILED: {sentiment_data.get('message', 'N/A')}")
    
    print(f"\n--- Cached drugs: {service.list_available_drugs()} ---")