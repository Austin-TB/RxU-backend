import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # API Configuration
    app_name: str = "Drug Sentiment & Recommendation Dashboard"
    debug: bool = True
    api_version: str = "v1"
    
    # Database Configuration (for future use)
    database_url: Optional[str] = None
    
    # AWS S3 Configuration
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_region: str = "us-east-1"
    s3_bucket_name: str = "drug-dashboard"
    
    # Twitter API Configuration
    twitter_bearer_token: Optional[str] = None
    twitter_api_key: Optional[str] = None
    twitter_api_secret: Optional[str] = None
    
    # Reddit API Configuration
    reddit_client_id: Optional[str] = None
    reddit_client_secret: Optional[str] = None
    reddit_user_agent: str = "DrugDashboard/1.0"
    
    # OpenFDA Configuration
    openfda_api_key: Optional[str] = None
    
    # CORS Settings
    allowed_origins: list = ["http://localhost:5173"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings() 