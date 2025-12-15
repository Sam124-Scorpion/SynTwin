# SynTwin Backend API Documentation

## Quick Start

### 1. Install Dependencies
```bash
pip install fastapi uvicorn pydantic
```

### 2. Start the Server
```bash
# From project root
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Access the API
- **API Root**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints Overview

### 🧠 NLP Service (`/api/nlp`)
Task recommendations and sentiment analysis

#### GET `/api/nlp/suggestions`
Get personalized task suggestions based on recent data.

**Query Parameters:**
- `minutes` (int, default: 10): Minutes of data to analyze

**Response:**
```json
{
  "success": true,
  "data": {
    "suggestions": ["☕ Take a coffee break", "🚶 Walk around"],
    "priority": "high",
    "state_summary": {...},
    "recommendation_context": "You seem tired..."
  }
}
```

#### GET `/api/nlp/state`
Get current user state analysis.

**Response:**
```json
{
  "success": true,
  "data": {
    "dominant_emotion": "Happy",
    "energy_level": "Normal",
    "needs_break": false,
    "avg_sentiment": 0.75
  }
}
```

#### GET `/api/nlp/daily-summary`
Get daily summary and insights.

**Query Parameters:**
- `hours` (int, default: 24): Hours of data to include

#### POST `/api/nlp/sentiment/analyze`
Analyze sentiment from text or behavioral data.

**Request Body:**
```json
{
  "text": "I had a great day!",
  "emotion": "Happy",
  "smile": "Smiling",
  "posture": "Upright"
}
```

---

### 📹 Detection Service (`/api/detection`)
Face/posture detection logging and retrieval

#### POST `/api/detection/log`
Log a detection entry to database and CSV.

**Request Body:**
```json
{
  "emotion": "Happy",
  "smile": "Smiling",
  "eyes": "Open",
  "posture": "Upright",
  "sentiment": 0.8,
  "cognitive_state": "Focused",
  "mood": "Happy"
}
```

#### GET `/api/detection/recent`
Get recent detection entries.

**Query Parameters:**
- `limit` (int, default: 10): Number of entries

**Response:**
```json
{
  "success": true,
  "count": 10,
  "data": [
    {
      "timestamp": "2025-12-06 10:30:00",
      "emotion": "Happy",
      "posture": "Upright",
      "sentiment": 0.8
    }
  ]
}
```

#### GET `/api/detection/stats`
Get detection statistics.

**Response:**
```json
{
  "success": true,
  "data": {
    "total_detections": 500,
    "emotion_distribution": {"Happy": 200, "Neutral": 150},
    "posture_distribution": {"Upright": 300, "Slouching": 100},
    "average_sentiment": 0.45
  }
}
```

#### GET `/api/detection/timeline`
Get detection timeline.

**Query Parameters:**
- `hours` (int, default: 24): Time period

#### DELETE `/api/detection/clear`
Clear all detection data (use with caution!)

---

### 📊 Analytics Service (`/api/analytics`)
Data analysis and visualization

#### GET `/api/analytics/summary`
Get overall analytics summary from CSV logs.

**Response:**
```json
{
  "success": true,
  "data": {
    "total_entries": 500,
    "emotion_distribution": {...},
    "average_sentiment": 0.55,
    "sentiment_trend": "Positive"
  }
}
```

#### GET `/api/analytics/timeline`
Get timeline of analytics data.

**Query Parameters:**
- `limit` (int, default: 50): Number of entries

#### POST `/api/analytics/log`
Log an analytics entry to CSV.

**Request Body:**
```json
{
  "emotion": "Happy",
  "smile": "Smiling",
  "eyes": "Open",
  "posture": "Upright",
  "sentiment": 0.8
}
```

#### GET `/api/analytics/emotion-trends`
Get emotion trends over time.

**Query Parameters:**
- `hours` (int, default: 24): Time period

#### DELETE `/api/analytics/clear-logs`
Clear CSV log file.

---

### 🎭 State Service (`/api/state`)
Digital twin state management

#### GET `/api/state/`
Get current twin state (all data).

**Response:**
```json
{
  "success": true,
  "data": {
    "cognitive_state": {...},
    "mood_state": {...},
    "physical_state": {...},
    "social_state": {...}
  }
}
```

#### POST `/api/state/update`
Update twin state with new inputs.

**Request Body:**
```json
{
  "cognitive": {"state": "Focused"},
  "mood": {"mood": "Happy"},
  "sentiment": 0.8,
  "environment": "Office"
}
```

#### GET `/api/state/cognitive`
Get only cognitive state.

#### GET `/api/state/mood`
Get only mood state.

#### GET `/api/state/physical`
Get only physical state.

#### GET `/api/state/social`
Get only social state.

#### POST `/api/state/reset`
Reset twin state to defaults.

---

## Frontend Integration Examples

### JavaScript/React Example

```javascript
// Get task suggestions
async function getTaskSuggestions() {
  const response = await fetch('http://localhost:8000/api/nlp/suggestions?minutes=10');
  const data = await response.json();
  
  if (data.success) {
    console.log('Suggestions:', data.data.suggestions);
    console.log('Priority:', data.data.priority);
  }
}

// Log detection
async function logDetection(detectionData) {
  const response = await fetch('http://localhost:8000/api/detection/log', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      emotion: detectionData.emotion,
      smile: detectionData.smile,
      eyes: detectionData.eyes,
      posture: detectionData.posture,
      sentiment: detectionData.sentiment
    })
  });
  
  const result = await response.json();
  return result;
}

// Get analytics summary
async function getAnalytics() {
  const response = await fetch('http://localhost:8000/api/analytics/summary');
  const data = await response.json();
  
  if (data.success) {
    console.log('Total entries:', data.data.total_entries);
    console.log('Emotions:', data.data.emotion_distribution);
  }
}

// Update twin state
async function updateState(stateData) {
  const response = await fetch('http://localhost:8000/api/state/update', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(stateData)
  });
  
  const result = await response.json();
  return result;
}
```

### Python Example

```python
import requests

BASE_URL = "http://localhost:8000"

# Get task suggestions
response = requests.get(f"{BASE_URL}/api/nlp/suggestions", params={"minutes": 10})
suggestions = response.json()
print(suggestions['data']['suggestions'])

# Log detection
detection = {
    "emotion": "Happy",
    "smile": "Smiling",
    "eyes": "Open",
    "posture": "Upright",
    "sentiment": 0.8
}
response = requests.post(f"{BASE_URL}/api/detection/log", json=detection)
print(response.json())

# Get analytics
response = requests.get(f"{BASE_URL}/api/analytics/summary")
analytics = response.json()
print(analytics['data'])
```

## Error Handling

All endpoints return consistent error responses:

```json
{
  "detail": "Error message description"
}
```

HTTP Status Codes:
- `200`: Success
- `400`: Bad Request
- `404`: Not Found
- `500`: Internal Server Error

## CORS Configuration

The API is configured to accept requests from any origin (`*`). For production, update the `allow_origins` in `backend/main.py` to specific domains:

```python
allow_origins=[
    "http://localhost:3000",
    "https://yourdomain.com"
]
```

## Testing the API

### Using curl

```bash
# Get suggestions
curl http://localhost:8000/api/nlp/suggestions?minutes=10

# Log detection
curl -X POST http://localhost:8000/api/detection/log \
  -H "Content-Type: application/json" \
  -d '{"emotion":"Happy","smile":"Smiling","eyes":"Open","posture":"Upright"}'

# Get analytics
curl http://localhost:8000/api/analytics/summary

# Get state
curl http://localhost:8000/api/state/
```

### Using Interactive Docs

Visit http://localhost:8000/docs for built-in Swagger UI where you can test all endpoints interactively.

---

**SynTwin API v1.0.0** 🧠
*Digital Twin with AI-Powered Insights*
