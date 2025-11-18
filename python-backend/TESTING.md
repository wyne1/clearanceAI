# Testing Guide

## Prerequisites

1. **Python 3.8+ installed**
2. **OpenAI API key** (get from https://platform.openai.com/api-keys)
3. **Node.js and npm** (for the frontend/Workers backend)

## Setup Steps

### 1. Set up Python Backend

```bash
cd python-backend
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:
```
OPENAI_API_KEY=sk-your-actual-api-key-here
PYTHON_SERVICE_URL=http://localhost:8000
```

### 2. Start Python Backend

```bash
# In python-backend directory
uvicorn main:app --reload --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 3. Start Workers Backend (in project root)

```bash
# In project root directory
npm run dev
```

## Testing Checklist

### Test 1: Python Backend Health Check

**Direct API test:**
```bash
curl http://localhost:8000/health
```

**Expected response:**
```json
{"status":"ok","service":"clearanceai-python-backend"}
```

### Test 2: Python Backend - Assessment Endpoint (Direct)

**Test with curl:**
```bash
curl -X POST http://localhost:8000/api/assess \
  -H "Content-Type: application/json" \
  -d '{
    "shipper": "Global Trade Corp",
    "importer": "Mexico Imports SA",
    "commodity": "Soccer Balls",
    "origin": "China"
  }'
```

**What to check:**
- ✅ Response includes `riskLevel` (high/medium/low)
- ✅ Response includes `riskScore` (0-100)
- ✅ Response includes `flags` array
- ✅ Response includes `entityChecks` for shipper/importer
- ✅ Response includes `recommendations` array
- ✅ Response includes `patternAnalysis` text
- ✅ Response includes `aiInsights` text
- ✅ For "Soccer Balls" from "China", should detect origin mismatch (high risk)

### Test 3: Python Backend - Entity Research (Direct)

**Test with curl:**
```bash
curl -X POST http://localhost:8000/api/entities/research \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Rapid Shift Logistics",
    "type": "shipper",
    "country": "Panama"
  }'
```

**What to check:**
- ✅ Response includes `riskLevel` and `riskScore`
- ✅ Response includes `blacklistStatus` with `list60B: true` (this entity is in mock blacklist)
- ✅ Response includes `newsItems` array (from OpenAI)
- ✅ Response includes `tradingPatterns` array
- ✅ News items have sentiment (negative/neutral/positive)

### Test 4: Workers Backend Proxy

**Test assessment through Workers:**
```bash
curl -X POST http://localhost:3002/api/assess \
  -H "Content-Type: application/json" \
  -d '{
    "shipper": "Global Trade Corp",
    "importer": "Mexico Imports SA",
    "commodity": "Soccer Balls",
    "origin": "China"
  }'
```

**What to check:**
- ✅ Same response structure as direct Python test
- ✅ No CORS errors
- ✅ Response time is reasonable (may take 10-30 seconds due to OpenAI calls)

### Test 5: Frontend - New Assessment Page

1. **Navigate to:** `http://localhost:3002/assess`

2. **Fill in the form:**
   - Shipper: `Global Trade Corp`
   - Importer: `Mexico Imports SA`
   - Commodity: `Soccer Balls`
   - Origin: `China`
   - (Optional: Add value, weight, etc.)

3. **Click "Run Risk Assessment"**

4. **What to check:**
   - ✅ Loading animation appears
   - ✅ After 10-30 seconds, results appear
   - ✅ Risk badge shows "High Risk" (for Soccer Balls from China)
   - ✅ Risk flags include "Commodity Origin Mismatch"
   - ✅ Entity verification shows status for shipper/importer
   - ✅ Pattern analysis explains the anomaly
   - ✅ AI insights provide comprehensive summary
   - ✅ Recommendations are actionable

### Test 6: Frontend - Entity Intelligence Page

1. **Navigate to:** `http://localhost:3002/entities`

2. **Select an entity** from the list (e.g., "Rapid Shift Logistics")

3. **Click "Research" button**

4. **What to check:**
   - ✅ Button shows "Researching..." with spinner
   - ✅ After 10-30 seconds, data updates
   - ✅ Shows "Data refreshed via AI research" message
   - ✅ Blacklist status updates (Rapid Shift should show 60B List: FLAGGED)
   - ✅ News items appear (from OpenAI)
   - ✅ Risk score updates based on research
   - ✅ Toast notification shows success

### Test 7: Different Risk Scenarios

**Test Low Risk:**
- Shipper: `Pacific Logistics Ltd`
- Importer: `Automotive Parts MX`
- Commodity: `Auto Parts`
- Origin: `Japan`

**Expected:** Low risk, no flags, clean entity checks

**Test Medium Risk:**
- Shipper: `Flores International`
- Importer: `Decoraciones Mexico`
- Commodity: `Hibiscus Flowers`
- Origin: `Colombia` (should flag - expected Nigeria)

**Expected:** Medium risk, origin anomaly flag

**Test High Risk:**
- Shipper: `Rapid Shift Logistics` (on 60B list)
- Importer: `Juguetes Mexico`
- Commodity: `Toys`
- Origin: `Vietnam`

**Expected:** High risk, multiple flags including 60B list

## Common Issues & Solutions

### Issue: "Failed to connect to AI service"
- **Solution:** Make sure Python backend is running on port 8000
- Check: `curl http://localhost:8000/health`

### Issue: "OpenAI API error"
- **Solution:** Check your `.env` file has correct `OPENAI_API_KEY`
- Verify key is valid at https://platform.openai.com/api-keys

### Issue: CORS errors in browser
- **Solution:** Workers backend should handle CORS, but check it's running
- Check: `curl http://localhost:3002/api/health`

### Issue: Slow responses
- **Normal:** OpenAI API calls take 10-30 seconds
- First call may be slower due to cold start
- Subsequent calls should be faster

### Issue: "Assessment failed" error
- **Check:** Python backend logs for error details
- **Check:** OpenAI API key has sufficient credits
- **Check:** Network connectivity

## Performance Expectations

- **Direct Python API:** 10-30 seconds (OpenAI processing time)
- **Through Workers proxy:** +100-500ms overhead
- **Frontend display:** Immediate after API response

## Success Criteria

✅ All API endpoints respond correctly  
✅ OpenAI integration works (real AI responses)  
✅ Risk scoring is accurate based on inputs  
✅ Blacklist checking works (Rapid Shift Logistics flagged)  
✅ Pattern analysis detects anomalies (Soccer Balls from China)  
✅ Frontend displays all data correctly  
✅ Error handling works (shows user-friendly messages)  

## Next Steps After Testing

Once all tests pass:
1. ✅ System is ready for real-world use
2. Consider adding more mock data to JSON files
3. Consider caching OpenAI responses for faster repeated queries
4. Consider adding rate limiting for production

