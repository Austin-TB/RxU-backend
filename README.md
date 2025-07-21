# Drug Sentiment & Recommendation Dashboard - Backend

FastAPI backend for the Drug Sentiment & Recommendation Dashboard.

## Features

- Drug search and metadata retrieval
- Sentiment analysis of drug mentions
- Drug recommendation engine
- Side effects information
- AWS S3 integration for caching

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment configuration:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

3. **Run the development server:**
   ```bash
   # From the backend directory
   python -m app.main
   
   # Or using uvicorn directly
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## API Endpoints

The API will be available at `http://localhost:8000`

### Available Endpoints:

- `GET /` - Health check and API info
- `GET /health` - Health status
- `GET /api/drugs/search?q={drug_name}` - Search for drugs
- `GET /api/drugs/sentiment?drug_name={drug_name}` - Get sentiment analysis
- `GET /api/drugs/recommend?drug_name={drug_name}` - Get drug recommendations
- `GET /api/drugs/side-effects?drug_name={drug_name}` - Get side effects

### API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── config.py           # Configuration and settings
│   ├── api/                # API route definitions
│   ├── services/           # Business logic (sentiment, recommendations)
│   ├── models/             # Pydantic data models
│   └── utils/              # Utility functions
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
└── README.md              # This file
```

## Development

- All endpoints currently return mock data
- Implement the actual logic in the respective service modules
- Add proper error handling and validation
- Set up logging and monitoring

## Next Steps

1. Implement sentiment analysis service
2. Create drug recommendation logic
3. Integrate with OpenFDA for drug metadata
4. Add Twitter/Reddit data fetching
5. Implement S3 caching mechanism 