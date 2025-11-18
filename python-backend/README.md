# ClearanceAI Python Backend

AI-powered risk assessment backend using OpenAI GPT-4o.

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   ```bash
   cp .env.example .env
   ```
   Then edit `.env` and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   PYTHON_SERVICE_URL=http://localhost:8000
   ```

3. **Run the service:**
   ```bash
   uvicorn main:app --reload --port 8000
   ```

The service will be available at `http://localhost:8000`

## API Endpoints

### Health Check
- `GET /health` - Service health status

### Assessments
- `POST /api/assess` - Perform risk assessment on a shipment
  - Request body: `ShipmentData` (shipper, importer, commodity, origin, etc.)
  - Returns: `RiskAssessment` (risk level, score, flags, recommendations)

### Entity Research
- `POST /api/entities/research` - Research a specific entity
  - Request body: `EntityResearchRequest` (name, type, country)
  - Returns: `EntityResearch` (blacklist status, news items, trading patterns)

## Architecture

- **FastAPI** - Web framework
- **OpenAI GPT-4o** - AI-powered entity research and risk analysis
- **Pydantic** - Data validation and serialization
- **Mock JSON data** - Blacklists and commodity patterns (in `app/data/`)

## Development

The service integrates with the Cloudflare Workers backend, which proxies AI requests to this Python service. Make sure both services are running:

1. Python backend: `uvicorn main:app --reload --port 8000`
2. Workers backend: `npm run dev` (or `wrangler dev`)

