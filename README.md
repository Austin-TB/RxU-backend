# RxU Backend API

A FastAPI-powered backend service providing drug information, sentiment analysis, and recommendation capabilities for the RxU platform.

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- pip (Python package manager)
- Optional: Docker for containerized deployment

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd RxU/backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env  # Create .env file and configure
   ```

5. **Run the application**
   ```bash
   python run.py
   ```

The API will be available at `http://localhost:8080`

### Environment Variables

Create a `.env` file in the backend directory with the following variables:

```env
# AWS S3 Configuration (for sentiment data storage)
AWS_ACCESS_KEY=your_aws_access_key
AWS_SECRET_KEY=your_aws_secret_key
AWS_REGION=ap-south-1
AWS_S3_BUCKET_NAME=rxu-bucket

# API Configuration
DEBUG=true
API_VERSION=v1

# Social Media API Configuration (optional)
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
TWITTER_BEARER_TOKEN=your_twitter_bearer_token
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret

# External APIs
OPENFDA_API_KEY=your_openfda_api_key
```

## 🏗️ Architecture

### Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application and routes
│   ├── config.py            # Configuration management
│   ├── api/                 # API route modules
│   ├── services/            # Business logic services
│   │   ├── drug_search.py   # Drug search functionality
│   │   ├── fetch_sentiment.py # Sentiment analysis service
│   │   └── cache/           # Caching utilities
│   └── utils/               # Utility functions
├── data/
│   ├── drugs.csv           # Drug database (DrugBank format)
│   └── agg/daily/          # Sentiment data files
├── requirements.txt        # Python dependencies
├── Dockerfile             # Container configuration
├── run.py                 # Application entry point
└── README.md              # This file
```

### Core Components

#### 1. **FastAPI Application** (`app/main.py`)
- RESTful API with automatic OpenAPI documentation
- CORS middleware for frontend integration
- Error handling and response standardization
- Health check endpoints

#### 2. **Drug Search Service** (`app/services/drug_search.py`)
- Pandas-powered drug database search
- Fuzzy matching capabilities
- Search by name, generic name, and synonyms
- Drug metadata retrieval

#### 3. **Sentiment Analysis Service** (`app/services/fetch_sentiment.py`)
- AWS S3 integration for sentiment data
- Local file fallback system
- Caching mechanism for performance
- Social media sentiment aggregation

#### 4. **Configuration Management** (`app/config.py`)
- Pydantic settings with environment variable support
- AWS credentials management
- API configuration and CORS settings

## 📡 API Endpoints

### Base URL
- **Development**: `http://localhost:8080`
- **Production**: `https://rxuu-backend-306624049631.europe-west1.run.app`

### Core Endpoints

#### 🔍 **Drug Search**
```http
GET /api/drugs/search?q={query}
```
**Description**: Search for drugs by name, generic name, or synonyms

**Parameters**:
- `q` (string, required): Search query

**Response**:
```json
{
  "query": "aspirin",
  "results": [
    {
      "drugbank_id": "DB00945",
      "name": "Aspirin",
      "generic_name": "acetylsalicylic acid",
      "brand_names": ["Bayer", "Excedrin"],
      "drug_class": "Analgesics",
      "description": "Pain reliever and anti-inflammatory",
      "match_score": 100,
      "match_type": "exact"
    }
  ],
  "total_found": 1
}
```

#### 📊 **Sentiment Analysis**
```http
GET /api/drugs/sentiment?drug_name={name}
```
**Description**: Get sentiment analysis data for a specific drug

**Parameters**:
- `drug_name` (string, required): Name of the drug

**Response**:
```json
{
  "drug_name": "aspirin",
  "sentiment_data": [
    {
      "date": "2024-01-15",
      "positive": 0.65,
      "neutral": 0.25,
      "negative": 0.10,
      "post_count": 150
    }
  ],
  "overall_sentiment": "positive",
  "sentiment_score": 0.72,
  "total_posts_analyzed": 1500,
  "analysis_date": "2024-01-20T10:00:00Z"
}
```

#### 💊 **Drug Recommendations**
```http
GET /api/drugs/recommend?drug_name={name}
```
**Description**: Get alternative drug recommendations

**Parameters**:
- `drug_name` (string, required): Name of the original drug

**Response**:
```json
{
  "original_drug": "aspirin",
  "recommendations": [
    {
      "name": "ibuprofen",
      "similarity_score": 0.85,
      "reason": "Alternative therapy from the same or similar drug class"
    }
  ]
}
```

#### ⚠️ **Side Effects**
```http
GET /api/drugs/side-effects?drug_name={name}
```
**Description**: Get side effect information for a drug

**Response**:
```json
{
  "drug_name": "aspirin",
  "common_side_effects": [
    {
      "effect": "Stomach upset",
      "frequency": "common",
      "severity": "mild"
    }
  ],
  "serious_side_effects": [
    {
      "effect": "Gastrointestinal bleeding",
      "frequency": "rare",
      "severity": "severe"
    }
  ]
}
```

#### 📋 **Available Drugs**
```http
GET /api/drugs/sentiment/available
```
**Description**: Get list of drugs with available sentiment data

### Health & Status

#### 🏥 **Health Check**
```http
GET /health
```
**Response**:
```json
{
  "status": "healthy"
}
```

#### 🏠 **Root Endpoint**
```http
GET /
```
**Response**:
```json
{
  "message": "RxU-backend API",
  "status": "running"
}
```

## 🛠️ Development

### Running in Development Mode

```bash
# With auto-reload
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload

# Or using the run script
python run.py
```

### API Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI**: `http://localhost:8080/docs`
- **ReDoc**: `http://localhost:8080/redoc`
- **OpenAPI Schema**: `http://localhost:8080/openapi.json`

### Testing

```bash
# Run the drug search service tests
python -m app.services.drug_search

# Run the sentiment service tests
python -m app.services.fetch_sentiment
```

### Code Quality

```bash
# Format code
black app/

# Type checking
mypy app/

# Linting
flake8 app/
```

## 🐳 Docker Deployment

### Build Image

```bash
docker build -t rxu-backend .
```

### Run Container

```bash
docker run -p 8080:8080 \
  -e AWS_ACCESS_KEY=your_key \
  -e AWS_SECRET_KEY=your_secret \
  rxu-backend
```

### Environment Variables for Docker

```bash
# Using environment file
docker run -p 8080:8080 --env-file .env rxu-backend
```

## ☁️ Cloud Deployment

The application is configured for deployment on Google Cloud Run with the following features:

- **Container Runtime**: Python 3.11 slim
- **Port Configuration**: Uses `$PORT` environment variable (default: 8080)
- **Health Checks**: Built-in health endpoint
- **Security**: Non-root user execution
- **Performance**: Optimized caching and dependency management

### Google Cloud Run Deployment

```bash
# Build and deploy
gcloud run deploy rxu-backend \
  --source . \
  --region europe-west1 \
  --allow-unauthenticated \
  --set-env-vars AWS_ACCESS_KEY=your_key,AWS_SECRET_KEY=your_secret
```

## 📊 Data Sources

### Drug Database
- **Source**: DrugBank database
- **Format**: CSV with drug metadata
- **Location**: `data/drugs.csv`
- **Fields**: DrugBank ID, names, synonyms, drug class, description, alternatives, side effects

### Sentiment Data
- **Source**: Social media platforms (Reddit, Twitter)
- **Storage**: AWS S3 with local fallback
- **Format**: Daily aggregated JSON files
- **Processing**: VADER sentiment analysis + transformer models

## 🔧 Configuration

### Settings Management

The application uses Pydantic Settings for configuration:

```python
from app.config import settings

# Access configuration
print(settings.aws_region)
print(settings.debug)
```

### CORS Configuration

Default allowed origins:
- `http://localhost:5173` (Vite dev server)
- `https://rxu.austintbabu.com` (Production frontend)

## 🚨 Error Handling

The API implements comprehensive error handling:

- **400 Bad Request**: Invalid parameters
- **404 Not Found**: Drug not found
- **500 Internal Server Error**: Server errors with detailed messages
- **CORS Errors**: Proper headers for cross-origin requests

## 📈 Performance

### Caching Strategy
- **Local Cache**: Sentiment data cached locally
- **S3 Integration**: Efficient data retrieval
- **DataFrame Operations**: Optimized pandas operations

### Monitoring
- **Health Checks**: Built-in health endpoint
- **Logging**: Structured logging with uvicorn
- **Error Tracking**: Comprehensive error reporting

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

### Development Guidelines
- Follow PEP 8 style guidelines
- Add type hints for all functions
- Include docstrings for public functions
- Write tests for new features
- Update documentation as needed

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the API documentation at `/docs`
- Review the error messages for debugging hints

## 🔄 Changelog

### v1.0.0
- Initial release with drug search functionality
- Sentiment analysis integration
- AWS S3 data storage
- Docker containerization
- Google Cloud Run deployment support