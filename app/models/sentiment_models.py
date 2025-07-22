from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class SentimentDataPoint(BaseModel):
    """Individual sentiment data point for a specific time period"""
    date: str
    positive: float
    neutral: float  
    negative: float
    post_count: int

class SentimentAnalysisResult(BaseModel):
    """Complete sentiment analysis result for a drug"""
    drug_name: str
    sentiment_data: List[SentimentDataPoint]
    overall_sentiment: str  # "positive", "neutral", "negative"
    sentiment_score: float  # -1 to 1 scale
    total_posts_analyzed: int
    analysis_date: str
    top_keywords: Optional[List[str]] = None
    confidence_score: Optional[float] = None

class MockSocialPost(BaseModel):
    """Structure for mock social media posts"""
    id: str
    text: str
    date: str
    platform: str
    author: str
    sentiment_label: Optional[str] = None 