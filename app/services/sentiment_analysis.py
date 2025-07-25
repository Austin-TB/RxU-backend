import re
import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from app.models.sentiment_models import SentimentAnalysisResult, SentimentDataPoint, MockSocialPost

class SentimentAnalysisService:
    """
    Service for analyzing sentiment of social media posts about drugs.
    """
    
    def __init__(self):
        self.mock_posts_cache = {}
        print("SentimentAnalysisService initialized")
    
    def preprocess_text(self, text: str) -> str:
        if not text:
            return ""
        
        # Convert to lowercase
        cleaned_text = text.lower()
        
        # Remove URLs
        cleaned_text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', cleaned_text)
        
        # Remove mentions and hashtags (keep the text, remove the symbols)
        cleaned_text = re.sub(r'[@#](\w+)', r'\1', cleaned_text)
        
        # Remove extra whitespace and special characters
        cleaned_text = re.sub(r'[^\w\s]', ' ', cleaned_text)
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
        
        # Strip leading/trailing whitespace
        cleaned_text = cleaned_text.strip()
        
        return cleaned_text
    
    def _generate_mock_posts(self, drug_name: str, num_posts: int = 50) -> List[MockSocialPost]:
        """
        Generate realistic mock social media posts for testing.
        
        Args:
            drug_name (str): Name of the drug to generate posts about
            num_posts (int): Number of posts to generate
            
        Returns:
            List[MockSocialPost]: List of mock social media posts
        """
        # Cache posts for consistent results
        cache_key = f"{drug_name}_{num_posts}"
        if cache_key in self.mock_posts_cache:
            return self.mock_posts_cache[cache_key]
        
        # Template posts with different sentiment patterns
        positive_templates = [
            f"{drug_name} really helped with my pain! Feeling much better now 😊",
            f"Been taking {drug_name} for a week and the difference is amazing",
            f"My doctor recommended {drug_name} and it's working great so far",
            f"Finally found relief with {drug_name}. Highly recommend!",
            f"{drug_name} has been a game changer for my condition",
            f"So grateful that {drug_name} exists. Life is so much better now",
            f"Love how effective {drug_name} is. No major side effects either"
        ]
        
        neutral_templates = [
            f"Taking {drug_name} as prescribed. Will see how it goes",
            f"Just started {drug_name}. Doctor says it should help",
            f"Day 3 of {drug_name} treatment. Monitoring progress",
            f"Anyone else tried {drug_name}? Looking for experiences",
            f"Switching to {drug_name} from my previous medication",
            f"Pharmacy had {drug_name} in stock today. Time to start treatment",
            f"Reading about {drug_name} side effects before starting"
        ]
        
        negative_templates = [
            f"{drug_name} giving me terrible side effects. Not sure if worth it",
            f"Been on {drug_name} for 2 weeks, still no improvement 😞",
            f"Had to stop taking {drug_name} due to nausea and headaches",
            f"{drug_name} isn't working for me at all. Very disappointed",
            f"The side effects of {drug_name} are worse than my original problem",
            f"Expensive and {drug_name} doesn't seem to be helping much",
            f"Really struggling with {drug_name}. Looking for alternatives"
        ]
        
        all_templates = positive_templates + neutral_templates + negative_templates
        platforms = ["twitter", "reddit", "facebook"]
        
        posts = []
        base_date = datetime.now() - timedelta(days=30)
        
        for i in range(num_posts):
            # Select template and determine sentiment
            template = random.choice(all_templates)
            if template in positive_templates:
                sentiment_label = "positive"
            elif template in neutral_templates:
                sentiment_label = "neutral"
            else:
                sentiment_label = "negative"
            
            # Generate post data
            post_date = base_date + timedelta(days=random.randint(0, 29))
            post = MockSocialPost(
                id=f"post_{drug_name}_{i+1}",
                text=template,
                date=post_date.strftime("%Y-%m-%d"),
                platform=random.choice(platforms),
                author=f"user_{random.randint(1000, 9999)}",
                sentiment_label=sentiment_label
            )
            posts.append(post)
        
        # Cache the generated posts
        self.mock_posts_cache[cache_key] = posts
        return posts
    
    def analyze_text(self, text: str) -> Dict[str, float]:
        """
        Perform basic sentiment analysis on a single text.
        Currently uses simple rule-based analysis for testing.
        
        Args:
            text (str): Text to analyze
            
        Returns:
            Dict[str, float]: Sentiment scores for positive, neutral, negative
        """
        if not text:
            return {"positive": 0.0, "neutral": 1.0, "negative": 0.0}
        
        # Preprocess the text
        cleaned_text = self.preprocess_text(text)
        
        # Simple keyword-based sentiment analysis for testing
        positive_words = ["great", "amazing", "love", "excellent", "helpful", "better", "relief", "recommend", "effective", "grateful", "good"]
        negative_words = ["terrible", "bad", "awful", "disappointed", "struggling", "worse", "expensive", "side effects", "nausea", "headache", "stop"]
        
        words = cleaned_text.split()
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)
        
        # Calculate scores
        total_sentiment_words = positive_count + negative_count
        if total_sentiment_words == 0:
            return {"positive": 0.1, "neutral": 0.8, "negative": 0.1}
        
        positive_score = positive_count / len(words)
        negative_score = negative_count / len(words)
        neutral_score = max(0, 1 - positive_score - negative_score)
        
        #Normalize
        total = positive_score + neutral_score + negative_score
        if total > 0:
            return {
                "positive": positive_score / total,
                "neutral": neutral_score / total,
                "negative": negative_score / total
            }
        else:
            return {"positive": 0.1, "neutral": 0.8, "negative": 0.1}
    
    def get_drug_sentiment(self, drug_name: str) -> SentimentAnalysisResult:
        """
        Get sentiment analysis results for a specific drug.
        
        Args:
            drug_name (str): Name of the drug to analyze
            
        Returns:
            SentimentAnalysisResult: Complete sentiment analysis results
        """
        # Generate mock posts
        mock_posts = self._generate_mock_posts(drug_name)
        
        # Analyze sentiment for each post
        daily_sentiments = {}
        total_positive = 0
        total_neutral = 0
        total_negative = 0
        
        for post in mock_posts:
            sentiment_scores = self.analyze_text(post.text)
            date = post.date
            
            if date not in daily_sentiments:
                daily_sentiments[date] = {
                    "positive": 0,
                    "neutral": 0,
                    "negative": 0,
                    "post_count": 0
                }
            
            daily_sentiments[date]["positive"] += sentiment_scores["positive"]
            daily_sentiments[date]["neutral"] += sentiment_scores["neutral"]
            daily_sentiments[date]["negative"] += sentiment_scores["negative"]
            daily_sentiments[date]["post_count"] += 1
            
            total_positive += sentiment_scores["positive"]
            total_neutral += sentiment_scores["neutral"]
            total_negative += sentiment_scores["negative"]
        
        # Calculate daily averages and create data points
        sentiment_data = []
        for date, values in sorted(daily_sentiments.items()):
            post_count = values["post_count"]
            sentiment_data.append(SentimentDataPoint(
                date=date,
                positive=round(values["positive"] / post_count, 3),
                neutral=round(values["neutral"] / post_count, 3),
                negative=round(values["negative"] / post_count, 3),
                post_count=post_count
            ))
        
        # Calculate overall sentiment
        total_posts = len(mock_posts)
        avg_positive = total_positive / total_posts
        avg_negative = total_negative / total_posts
        
        if avg_positive > avg_negative:
            overall_sentiment = "positive"
            sentiment_score = round(avg_positive - avg_negative, 3)
        elif avg_negative > avg_positive:
            overall_sentiment = "negative" 
            sentiment_score = round(avg_negative - avg_positive, 3) * -1
        else:
            overall_sentiment = "neutral"
            sentiment_score = 0.0
        
        return SentimentAnalysisResult(
            drug_name=drug_name,
            sentiment_data=sentiment_data,
            overall_sentiment=overall_sentiment,
            sentiment_score=sentiment_score,
            total_posts_analyzed=total_posts,
            analysis_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            top_keywords=["pain", "relief", "side effects", "doctor", "treatment"],  # Mock keywords for now
            confidence_score=0.75  # Mock confidence score
        )

# Global instance for easy access
sentiment_service = SentimentAnalysisService()

# Example usage for testing
if __name__ == "__main__":
    service = SentimentAnalysisService()
    
    # Test text preprocessing
    sample_text = "Check out this link: https://example.com @user #health Taking aspirin for my headache! 😊"
    cleaned = service.preprocess_text(sample_text)
    print(f"Original: {sample_text}")
    print(f"Cleaned: {cleaned}")
    
    # Test sentiment analysis
    result = service.get_drug_sentiment("aspirin")
    print(f"\nSentiment analysis for {result.drug_name}:")
    print(f"Overall sentiment: {result.overall_sentiment}")
    print(f"Sentiment score: {result.sentiment_score}")
    print(f"Total posts: {result.total_posts_analyzed}") 