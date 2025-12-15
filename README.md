# 🧠 SynTwin - AI-Powered Digital Twin with Real-Time Emotion Detection

<div align="center">

**Neuroadaptive Life Simulation & Task Recommendation System**

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.116.1-green.svg)](https://fastapi.tiangolo.com/)
[![Transformers](https://img.shields.io/badge/Transformers-4.55.2-orange.svg)](https://huggingface.co/transformers/)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Quick Start](#-quick-start)
- [Project Structure](#-project-structure)
- [Technology Stack](#-technology-stack)
- [Usage Guide](#-usage-guide)
- [API Documentation](#-api-documentation)
- [Troubleshooting](#-troubleshooting)

---

## 🎯 Overview

**SynTwin** is an advanced AI-powered digital twin system that monitors your emotional state, posture, and behavior in real-time through webcam detection. It uses machine learning and NLP to provide personalized, actionable task recommendations based on your current mental and physical state.

### What Makes SynTwin Unique?

- 🎭 **Real-time emotion detection** using facial recognition
- 🧘 **Posture monitoring** with instant feedback
- 🤖 **AI-powered task suggestions** using transformer models (DistilBERT) and ML classifiers
- 📊 **Live analytics dashboard** with interactive charts
- 🎯 **Context-aware recommendations** based on time of day, energy levels, and mood
- 💼 **Real-life task suggestions** (work, personal, learning, social, health, creative)

---

## ✨ Key Features

### 1. Multi-Modal Detection System
- **Emotion Recognition**: Happy, Sad, Angry, Neutral, Surprised, Fearful, Disgusted
- **Eye Tracking**: Open/Closed detection for fatigue monitoring
- **Smile Detection**: Engagement and positivity tracking
- **Posture Analysis**: Good, Slouching, Leaning (Left/Right)
- **Sentiment Analysis**: Real-time mood scoring (-1 to +1)

### 2. Advanced AI Task Recommendations
- **Transformer-based NLP**: DistilBERT sentiment analysis (99% accuracy)
- **ML Classification**: Random Forest model for task category prediction
- **Behavioral Pattern Learning**: Adapts to your daily routines over 7 days
- **Real-life Task Database**: 100+ actual daily tasks across 6 categories
- **Context-aware Suggestions**: Time-sensitive and state-dependent recommendations

### 3. Comprehensive Analytics
- **Emotion Distribution**: Pie charts showing emotional patterns
- **Posture Trends**: Track slouching and posture quality over time
- **Sentiment Timeline**: Visualize mood changes throughout the day
- **Peak Productivity Hours**: Identify when you're most focused
- **Data Management**: Clear history feature with double-confirmation safety

### 4. Responsive Dashboard
- **Mobile-Friendly**: Responsive design for all device sizes
- **Real-time Updates**: WebSocket streaming for live detection
- **Interactive Charts**: Chart.js visualizations with dynamic resizing
- **Clean UI**: Modern gradient design with intuitive controls

---

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Webcam
- Windows/Linux/macOS

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd SynTwin_Project
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   ```

3. **Activate virtual environment**
   - Windows: `.venv\Scripts\activate`
   - Linux/macOS: `source .venv/bin/activate`

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

**Option 1: One-Click Start (Windows)**
```bash
START_SYNTWIN.bat
```

**Option 2: Manual Start**

1. Start the backend server:
   ```bash
   python start_api_server.py
   ```

2. Open `frontend_complete.html` in your browser

### First-Time Usage

1. **Allow camera permissions** when prompted
2. Click **"Start Detection"** to begin real-time monitoring
3. View live updates in the **Current State** section
4. Click **"Refresh Suggestions"** for AI-powered task recommendations
5. Explore **Analytics Dashboard** for insights and charts

---

## 📁 Project Structure

```
SynTwin_Project/
├── backend/                          # Backend application
│   ├── analytics/                    # Data analysis & visualization
│   ├── assets/haarcascades/         # OpenCV Haar Cascade models
│   ├── classifiers/                  # State classification
│   ├── database/                     # Database layer & SQLite
│   ├── detectors/                    # Detection modules
│   ├── nlp/                          # NLP & task recommendations
│   ├── services/                     # API services
│   ├── simulator/                    # Digital twin simulator
│   ├── utils/                        # Utility functions
│   ├── config.py                    # Configuration
│   └── main.py                      # FastAPI application
├── logs/                             # Log files
├── tests/                            # Unit tests
├── frontend_complete.html            # Main dashboard UI
├── start_api_server.py              # Server launcher
├── START_SYNTWIN.bat                # One-click startup
├── requirements.txt                 # Dependencies
└── README.md                        # This file
```

---

## 🛠️ Technology Stack

### Backend
- **FastAPI 0.116.1**: High-performance async web framework
- **Python 3.12**: Modern Python with type hints
- **OpenCV**: Computer vision for face/posture detection
- **SQLite**: Lightweight database for detection logs

### AI & Machine Learning
- **Transformers 4.55.2**: Hugging Face library for DistilBERT
- **DistilBERT**: 99% accurate sentiment analysis
- **Scikit-learn 1.7.1**: Random Forest classifier
- **NumPy <2.0**: Numerical computing

### Frontend
- **HTML5/CSS3**: Modern responsive design
- **JavaScript (ES6+)**: Async/await, fetch API
- **Chart.js 4.4.0**: Interactive visualizations
- **WebSocket**: Real-time communication

---

## 📖 Usage Guide

### Dashboard Features

#### 1. Video Stream & Detection
- **Start/Stop Detection**: Toggle real-time webcam monitoring
- **Live Indicators**: See detected emotion, posture, eyes, sentiment

#### 2. AI Task Suggestions
- **Refresh Suggestions**: Get updated recommendations
- **Priority Levels**: High (red), Medium (orange), Low (green)
- **Context Message**: Explains why tasks are suggested

#### 3. Current State Analysis
- **Dominant Emotion**: Most frequent emotion in last 10 minutes
- **Energy Level**: High, Normal, or Low
- **Posture Status**: Good, Slouching, Leaning
- **Average Sentiment**: Numerical mood score

#### 4. Analytics Dashboard
- **Summary**: View detailed statistics
- **Recent Detections**: Last 10 entries
- **Clear All History**: Wipe database (with confirmation)

#### 5. Interactive Charts
- **Emotion Distribution**: Pie chart of emotional states
- **Posture Distribution**: Bar chart of posture quality
- **Sentiment Over Time**: Line chart showing mood trends
- **Timeline**: Combined view of emotions and posture

---

## 📚 API Documentation

### Base URL
```
http://localhost:8000
```

### Key Endpoints

#### Detection Service (`/api/detection`)
- `POST /log` - Log detection entry
- `GET /recent?limit=10` - Get recent detections
- `GET /stats` - Get detection statistics
- `GET /timeline?hours=24` - Get timeline data
- `DELETE /clear` - Clear all detection history

#### NLP Service (`/api/nlp`)
- `GET /suggestions?minutes=10` - Get AI task suggestions
- `GET /state?minutes=10` - Get current state analysis
- `GET /daily-summary?hours=24` - Get daily summary

#### Analytics Service (`/api/analytics`)
- `GET /summary` - Get analytics summary
- `GET /patterns` - Get behavioral patterns
- `GET /productivity` - Get productivity metrics

### Example API Call

**Get Task Suggestions:**
```bash
curl http://localhost:8000/api/nlp/suggestions?minutes=10
```

**Response:**
```json
{
  "success": true,
  "data": {
    "suggestions": [
      "💼 Complete that important project deadline",
      "📧 Reply to pending emails in inbox"
    ],
    "priority": "medium",
    "recommendation_context": "Good energy, focused work recommended"
  }
}
```

Full API documentation: [API_DOCUMENTATION.md](API_DOCUMENTATION.md)

---

## 🐛 Troubleshooting

### Common Issues

#### Camera Not Working
**Problem**: "Cannot access webcam"

**Solution**:
- Check browser permissions (allow camera access)
- Ensure no other app is using the camera
- Try Chrome or Edge browser

#### No Task Suggestions
**Problem**: Shows "No data yet..."

**Solution**:
- Let detection run for at least 30 seconds
- Check if backend server is running
- Click "Refresh Suggestions" button

#### Charts Not Loading
**Problem**: Empty chart areas

**Solution**:
- Ensure backend API is accessible at `http://localhost:8000`
- Check browser console for errors (F12)
- Refresh the page

#### Port Already in Use
**Problem**: "Port 8000 already in use"

**Solution** (Windows):
```bash
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

---

## 📄 Additional Documentation

- **Complete System Guide**: [COMPLETE_SYSTEM_GUIDE.md](COMPLETE_SYSTEM_GUIDE.md)
- **API Reference**: [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
- **Clear History Fix**: [CLEAR_HISTORY_FIX.md](CLEAR_HISTORY_FIX.md)

---

## 🗺️ Roadmap

### Future Features
- [ ] Voice interaction and commands
- [ ] Multi-user support
- [ ] Mobile app (iOS/Android)
- [ ] Advanced pose estimation
- [ ] Calendar/email integration
- [ ] Sleep quality analysis
- [ ] Cloud deployment option

---

<div align="center">

**Made with ❤️ using FastAPI, Transformers, and OpenCV**

⭐ Star this repo if you find it useful!

</div>
