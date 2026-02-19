# 📘 SynTwin - Complete User Guide

> **Your comprehensive guide to using the SynTwin AI-Powered Digital Twin System**

---

## 📑 Table of Contents

1. [Introduction](#1-introduction)
2. [System Requirements](#2-system-requirements)
3. [Installation Guide](#3-installation-guide)
4. [First-Time Setup](#4-first-time-setup)
5. [Starting the Application](#5-starting-the-application)
6. [Using the Dashboard](#6-using-the-dashboard)
7. [Understanding Detection Results](#7-understanding-detection-results)
8. [AI Task Recommendations](#8-ai-task-recommendations)
9. [Analytics & Insights](#9-analytics--insights)
10. [Advanced Features](#10-advanced-features)
11. [Troubleshooting](#11-troubleshooting)
12. [Best Practices](#12-best-practices)
13. [FAQ](#13-faq)

---

## 1. Introduction

### What is SynTwin?

SynTwin is an intelligent digital twin system that monitors your emotional state, posture, and behavior in real-time using computer vision and AI. It provides personalized task recommendations based on your current mental and physical state to optimize your productivity and well-being.

### Key Capabilities

- 🎭 **Real-time Emotion Detection**: 2 primary emotions (Happy, Angry) plus Neutral and Drowsy states
- 🧘 **Posture Monitoring**: Tracks if you're sitting properly, slouching, or leaning
- 👁️ **Eye Tracking**: Detects fatigue through eye open/closed patterns
- 😊 **Smile Detection**: Measures engagement and positivity
- 🤖 **AI Task Suggestions**: Context-aware recommendations using DistilBERT (99% accuracy)
- 📊 **Analytics Dashboard**: Visualize patterns and trends over time
- 💾 **Data Logging**: Automatic saving to database and CSV files

### Who Should Use SynTwin?

- Remote workers seeking productivity optimization
- Students managing study schedules
- Anyone interested in self-awareness and emotional intelligence
- Teams tracking mental health and well-being
- Researchers studying human-computer interaction

---

## 2. System Requirements

### Hardware Requirements

**Minimum:**
- Webcam (built-in or external)
- 4GB RAM
- 1GHz processor
- 500MB free disk space

**Recommended:**
- HD webcam (720p or higher)
- 8GB RAM
- Multi-core processor
- 2GB free disk space for logs

### Software Requirements

- **Operating System**: Windows 10/11, macOS 10.14+, or Linux (Ubuntu 18.04+)
- **Python**: Version 3.12 or higher
- **Web Browser**: Chrome 90+, Firefox 88+, or Edge 90+ (with WebSocket support)
- **Internet**: Required for first-time model downloads only

### Browser Permissions

You must allow:
- ✅ Camera access
- ✅ JavaScript enabled
- ✅ WebSocket connections

---

## 3. Installation Guide

### Step 1: Get the Project

**Option A: Clone Repository (Recommended)**
```bash
git clone <repository-url>
cd SynTwin_Project
```

**Option B: Download ZIP**
1. Download the project ZIP file
2. Extract to your desired location
3. Open terminal/command prompt in that folder

### Step 2: Create Virtual Environment

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

You should see `(.venv)` in your terminal prompt.

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- FastAPI (web framework)
- OpenCV (computer vision)
- Transformers (AI models)
- Scikit-learn (machine learning)
- And all other required packages

**Installation Time**: ~5-10 minutes depending on internet speed

### Step 4: Verify Installation

```bash
python start_api_server.py
```

If you see:
```
🚀 Starting SynTwin Backend API Server
============================================================
📡 Starting server...
   - Host: 0.0.0.0
   - Port: 8000
```

**✅ Installation successful!**

Press `Ctrl+C` to stop the server for now.

---

## 4. First-Time Setup

### Initial Model Download

When you first start the application, it will automatically download:
- DistilBERT sentiment model (~250MB)
- Haar Cascade classifiers (included in project)

This happens once and is cached for future use.

### Database Initialization

The first run automatically creates:
- `logs/syntwin_log.csv` - CSV log file
- SQLite database with tables for detections

No manual setup required!

### Camera Setup

**Test Your Camera:**
1. Open your system's camera app
2. Ensure the camera works and shows clear video
3. Position yourself so your face is visible
4. Ensure good lighting (front-facing light is best)

---

## 5. Starting the Application

### Method 1: One-Click Start (Windows - Easiest)

**Using Batch File:**
```bash
START_SYNTWIN.bat
```

This automatically:
- Activates virtual environment
- Starts backend server
- Opens browser with dashboard

### Method 2: Manual Start (All Platforms)

**Step 1: Start Backend Server**

Open Terminal 1:
```bash
# Activate virtual environment
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux

# Start server
python start_api_server.py
```

Wait for:
```
✅ Server started successfully!
🌐 API available at: http://localhost:8000
📚 API docs available at: http://localhost:8000/docs
```

**Step 2: Open Frontend**

**Option A: React Application (Modern)**
Open Terminal 2:
```bash
cd frontend
npm install  # First time only
npm run dev
```

Access at: http://localhost:5173

**Option B: Static HTML (Simple)**
Open `frontend_complete.html` in your browser.

---

## 6. Using the Dashboard

### Dashboard Layout

```
┌─────────────────────────────────────────────────┐
│              🧠 SynTwin Dashboard               │
├─────────────────────────────────────────────────┤
│  Server Status: 🟢 Online                      │
├─────────────────────────────────────────────────┤
│  [▶️ Start Detection]  [⏹️ Stop Detection]     │
├─────────────────────────────────────────────────┤
│  Live Video Feed          │  Current Detection  │
│  [Your webcam here]       │  Emotion: Happy     │
│                           │  Posture: Good      │
│                           │  Eyes: Open         │
│                           │  Sentiment: +0.75   │
├─────────────────────────────────────────────────┤
│  Task Suggestions                               │
│  🎯 Great time for challenging tasks!          │
│  📚 Tackle difficult projects                  │
├─────────────────────────────────────────────────┤
│  Analytics & Charts                             │
│  [Emotion Distribution] [Posture Trends]       │
│  [Sentiment Timeline]   [Activity Timeline]    │
└─────────────────────────────────────────────────┘
```

### Control Panel

#### Server Status Indicator

- **🟢 Server Online & Ready**: Backend is running, ready to detect
- **🔴 Server Offline**: Backend not responding, check if running
- **🟡 Connecting...**: Attempting to connect

#### Detection Controls

**Start Detection Button (▶️)**
- Click to begin real-time monitoring
- Camera permission prompt will appear (allow it)
- Video feed starts showing with overlays
- Data automatically logs every few seconds

**Stop Detection Button (⏹️)**
- Stops camera and logging
- Video feed freezes
- Data is saved
- Can restart anytime

#### Keyboard Shortcuts

- **S**: Start detection
- **Q** or **Esc**: Stop detection
- **R**: Refresh task suggestions

---

## 7. Understanding Detection Results

### Emotion Detection

**Available Emotions:**
- 😊 **Happy**: Smiling, positive expression
- � **Angry**: Furrowed brows, tense jaw
- 😐 **Neutral**: Relaxed, no strong emotion
- 😴 **Drowsy**: Eyes closed, tired state

**How It's Detected:**
- Uses CNN (Convolutional Neural Network) for emotion recognition
- Analyzes facial features in real-time
- Updates every frame (~30 FPS)

### Posture Detection

**Posture Types:**
- ✅ **Good**: Head centered, straight back
- ⚠️ **Slouching**: Head forward, shoulders dropped
- ↔️ **Leaning Left**: Body tilted to left
- ↔️ **Leaning Right**: Body tilted to right

**Health Tips:**
- Maintain good posture for 80%+ of the time
- Take breaks if slouching detected frequently
- Adjust chair/desk height if needed

### Eye Tracking

**States:**
- 👁️ **Open**: Alert, awake
- 😴 **Closed**: Eyes closed for 1+ seconds

**Fatigue Detection:**
- Frequent eye closing = drowsiness
- System suggests breaks when fatigue detected

### Smile Detection

**Smile Intensity:**
- 😊 High: Genuine smile
- 🙂 Medium: Slight smile
- 😐 Low: Not smiling

**Engagement Metric:**
- Higher smile frequency = better engagement
- Used for task recommendation optimization

### Sentiment Score

**Range:** -1.0 (very negative) to +1.0 (very positive)

**Interpretation:**
- **+0.7 to +1.0**: Very positive mood (excellent productivity)
- **+0.3 to +0.7**: Positive mood (good for work)
- **-0.3 to +0.3**: Neutral mood (stable, moderate tasks)
- **-0.7 to -0.3**: Negative mood (consider breaks)
- **-1.0 to -0.7**: Very negative mood (rest recommended)

**Calculated Using:**
- DistilBERT transformer model
- Analyzes combined emotional state
- Updated every detection cycle

---

## 8. AI Task Recommendations

### How Recommendations Work

```mermaid
User State → AI Analysis → Task Database → Personalized Suggestions
```

**Step 1: Data Collection**
- Last 10 minutes of detection data
- Emotion patterns
- Posture quality
- Energy levels
- Time of day

**Step 2: AI Processing**
- DistilBERT sentiment analysis
- Random Forest classification
- Pattern recognition
- Context evaluation

**Step 3: Task Matching**
- 100+ real-life tasks in database
- 6 categories: Work, Personal, Learning, Social, Health, Creative
- Priority assignment (High/Medium/Low)
- Time-appropriate filtering

### Task Categories

#### 💼 Work Tasks
*When you're focused and energized*

Examples:
- Complete project deadlines
- Reply to emails
- Attend meetings
- Review documents
- Make important decisions

#### 🏠 Personal Tasks
*For daily routines and maintenance*

Examples:
- Pay bills
- Organize workspace
- Clean environment
- Plan schedule
- Shopping errands

#### 📚 Learning Tasks
*When alert and curious*

Examples:
- Take online courses
- Read articles/books
- Practice new skills
- Watch tutorials
- Research topics

#### 👥 Social Tasks
*When feeling positive and energetic*

Examples:
- Call friends/family
- Reply to messages
- Plan social events
- Network professionally
- Collaborate on projects

#### 🏋️ Health Tasks
*For physical and mental wellness*

Examples:
- Exercise or stretch
- Take walks
- Practice meditation
- Prepare healthy meals
- Hydrate properly

#### 🎨 Creative Tasks
*When feeling inspired and positive*

Examples:
- Brainstorm ideas
- Design projects
- Write creatively
- Draw or paint
- Make music

### Priority Levels

#### 🔴 High Priority
**Triggers:**
- Low energy + urgent work tasks
- Negative mood + health needs
- Poor posture + corrective actions

**Actions:**
- Immediate attention required
- Shown at top of list
- Red indicator

#### 🟠 Medium Priority
**Triggers:**
- Neutral state + moderate tasks
- Mixed signals
- General recommendations

**Actions:**
- Should do soon
- Middle of list
- Orange indicator

#### 🟢 Low Priority
**Triggers:**
- Positive state + optional tasks
- Good energy + creative work
- Optimal conditions

**Actions:**
- Can do when convenient
- Bottom of list
- Green indicator

### Refresh Suggestions Button

**When to Use:**
- After completing tasks
- When mood changes
- Every 30-60 minutes
- If suggestions seem outdated

**How Often It Updates:**
- Manual: Click "Refresh Suggestions"
- Auto: Every 5 minutes (if enabled)

### Understanding Context Messages

Examples and what they mean:

**"Good energy, focused work recommended"**
- High sentiment score
- Alert eyes
- Good posture
- → Work on challenging tasks

**"You seem tired, take a break"**
- Frequent eye closing
- Slouching posture
- Low energy
- → Rest, hydrate, stretch

**"Great mood! Time for creativity"**
- Happy emotion detected
- High sentiment
- Engaged
- → Creative or social tasks

---

## 9. Analytics & Insights

### Summary Statistics

**Overall Stats Show:**
- Total detections logged
- Average sentiment score
- Most frequent emotion
- Posture quality percentage
- Smile frequency

**Time Period Options:**
- Last hour
- Today
- Last 7 days
- Last 30 days
- Custom range

### Recent Detections Table

**Displays Last 10 Entries:**

| Time | Emotion | Posture | Eyes | Sentiment |
|------|---------|---------|------|-----------|
| 10:45 | Happy | Good | Open | +0.82 |
| 10:44 | Happy | Good | Open | +0.79 |
| 10:43 | Neutral | Slouching | Open | +0.45 |

**Use Cases:**
- Track mood changes
- Identify patterns
- Verify detection accuracy

### Interactive Charts

#### 1. Emotion Distribution (Pie Chart)

**Shows:**
- Percentage of each emotion
- Color-coded segments
- Legend with counts

**Insights:**
- Are you mostly happy or stressed?
- Emotional balance check
- Mood trends

#### 2. Posture Distribution (Bar Chart)

**Shows:**
- Good posture percentage
- Slouching frequency
- Leaning patterns

**Insights:**
- Ergonomic improvement needed?
- Reminder to adjust setup
- Health awareness

#### 3. Sentiment Over Time (Line Chart)

**Shows:**
- Sentiment score timeline
- Positive/negative periods
- Trend direction

**Insights:**
- When are you most positive?
- Stress patterns
- Optimal work hours

#### 4. Combined Timeline (Mixed Chart)

**Shows:**
- Emotions as bars
- Posture as line
- Time progression

**Insights:**
- Correlation between emotion and posture
- Daily patterns
- Activity impact

### Exporting Data

**CSV File Location:**
`logs/syntwin_log.csv`

**Contains:**
- Timestamp
- Emotion detected
- Posture status
- Eye state
- Smile detected
- Sentiment score

**Can Be Used For:**
- Excel analysis
- External visualization
- Data science projects
- Research studies

### Clear History Feature

**⚠️ Use With Caution**

**What It Does:**
- Deletes all detection logs
- Clears database
- Removes CSV entries
- Resets analytics

**Double Confirmation:**
1. Click "Clear All History"
2. Confirm: "Are you sure?"
3. Final confirm: "This cannot be undone"

**When to Use:**
- Starting fresh
- Privacy concerns
- Testing purposes

---

## 10. Advanced Features

### WebSocket Streaming

**Real-time Communication:**
- Live detection updates
- No page refresh needed
- Instant feedback
- Low latency (<100ms)

**Auto-Reconnect:**
- Detects connection loss
- Attempts reconnection
- Shows status indicator
- Resumes automatically

### API Access

**For Developers:**

Base URL: `http://localhost:8000`

**Key Endpoints:**

```bash
# Get recent detections
GET /api/detection/recent?limit=10

# Get task suggestions
GET /api/nlp/suggestions?minutes=10

# Get analytics summary
GET /api/analytics/summary

# Clear history
DELETE /api/detection/clear
```

**Interactive Documentation:**
Visit: http://localhost:8000/docs

### Configuration Options

**Edit `backend/config.py`:**

```python
# Detection frequency
DETECTION_INTERVAL = 2  # seconds

# Camera settings
CAMERA_INDEX = 0  # 0 for default, 1 for external

# Model settings
SENTIMENT_MODEL = "distilbert-base-uncased-finetuned-sst-2-english"

# Analytics
ANALYTICS_WINDOW = 10  # minutes for suggestions
```

### Custom Task Database

**Add Your Own Tasks:**

Edit `backend/nlp/real_life_tasks.py`:

```python
TASK_DATABASE = {
    "work": [
        "Your custom work task here",
        # ... more tasks
    ],
    # ... other categories
}
```

---

## 11. Troubleshooting

### Camera Issues

#### Problem: "Cannot access webcam"

**Solutions:**
1. **Check browser permissions:**
   - Chrome: Settings → Privacy → Camera
   - Firefox: Settings → Permissions → Camera
   - Allow for localhost

2. **Close other apps using camera:**
   - Zoom, Skype, Teams
   - Other browser tabs
   - Camera app

3. **Test camera:**
   - Open system camera app
   - Verify it works independently

4. **Try different browser:**
   - Chrome (recommended)
   - Firefox
   - Edge

#### Problem: "Camera shows black screen"

**Solutions:**
- Check physical camera cover
- Update camera drivers
- Restart browser
- Restart computer

### Server Issues

#### Problem: "Server Offline" indicator

**Check if server is running:**

Windows:
```bash
netstat -ano | findstr :8000
```

macOS/Linux:
```bash
lsof -i :8000
```

**If nothing shows, start server:**
```bash
python start_api_server.py
```

#### Problem: "Port 8000 already in use"

**Windows:**
```bash
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

**macOS/Linux:**
```bash
lsof -ti:8000 | xargs kill -9
```

### Detection Issues

#### Problem: "No emotion detected"

**Solutions:**
- Face camera directly
- Improve lighting
- Move closer to camera
- Remove glasses (if glare)
- Ensure face is visible

#### Problem: "Wrong emotion detected"

**Known Limitations:**
- Low light affects accuracy
- Extreme angles confuse detector
- Partial face occlusion
- Fast movements

**Improvements:**
- Sit still for 2-3 seconds
- Face camera straight-on
- Neutral background
- Consistent lighting

### Task Suggestion Issues

#### Problem: "No suggestions available"

**Solutions:**
1. **Not enough data:**
   - Run detection for 30+ seconds
   - Click "Refresh Suggestions"

2. **Server not responding:**
   - Check backend is running
   - View console (F12) for errors

3. **Database empty:**
   - Restart detection
   - Wait for logging to begin

#### Problem: "Suggestions not relevant"

**Adjustments:**
- Run longer for better patterns
- Clear history and restart
- Check time of day settings
- Verify emotion detection accuracy

### Chart Issues

#### Problem: "Charts not loading"

**Solutions:**
1. **Check backend connection:**
   ```bash
   curl http://localhost:8000/api/analytics/summary
   ```

2. **Clear browser cache:**
   - Ctrl+Shift+Delete
   - Clear cached images and files

3. **Check console errors:**
   - F12 → Console tab
   - Look for red errors
   - Share with support if needed

#### Problem: "Charts show no data"

**Causes:**
- Detection not started yet
- History was cleared
- API endpoint error

**Solutions:**
- Start detection
- Wait 1-2 minutes
- Refresh page

### Performance Issues

#### Problem: "Slow detection / lag"

**Solutions:**
1. **Reduce detection frequency:**
   - Edit `config.py`
   - Increase `DETECTION_INTERVAL`

2. **Close background apps:**
   - Free up CPU
   - Free up RAM

3. **Lower camera resolution:**
   - System camera settings
   - 480p instead of 1080p

#### Problem: "High CPU usage"

**Normal:**
- 20-40% CPU during detection
- 10-20% CPU when idle

**If higher:**
- Check for memory leaks
- Restart server
- Update dependencies

---

## 12. Best Practices

### Optimal Setup

**Physical Environment:**
- ✅ Sit 1-2 feet from camera
- ✅ Face camera directly (eye level)
- ✅ Front-facing light (window or lamp)
- ✅ Neutral background
- ❌ Avoid backlighting (window behind you)
- ❌ Avoid extreme angles

**Session Duration:**
- **Short sessions**: 15-30 minutes (quick check-in)
- **Work sessions**: 1-2 hours (productivity tracking)
- **Full day**: 4-8 hours (comprehensive analysis)

### Privacy & Security

**Data Storage:**
- All data stored locally (no cloud)
- SQLite database on your computer
- CSV logs in `/logs` folder

**Webcam Usage:**
- Only active when you click "Start"
- Red indicator shows recording
- No images saved (only analysis results)

**Sharing Data:**
- Never auto-shared
- Full control over export
- Can delete anytime

### Usage Patterns

**Morning Routine:**
1. Start SynTwin at work desk
2. Check baseline mood
3. Get task suggestions
4. Plan day accordingly

**During Work:**
1. Let it run continuously
2. Check suggestions hourly
3. Take breaks when suggested
4. Monitor posture warnings

**End of Day:**
1. Review analytics
2. Check sentiment trends
3. Export data if needed
4. Stop detection

**Weekly Review:**
1. View 7-day trends
2. Identify patterns
3. Adjust habits
4. Optimize productivity

---

## 13. FAQ

### General Questions

**Q: Is my video stream recorded?**
A: No. Only analysis results (emotion, posture, etc.) are stored. No images or videos are saved.

**Q: Does SynTwin work offline?**
A: After first-time model download, yes. Internet only needed for initial setup.

**Q: Can multiple people use the same installation?**
A: Yes, but data is not separated by user. Clear history between users.

**Q: Is it resource-intensive?**
A: Moderate. Expect 20-40% CPU usage during active detection.

### Technical Questions

**Q: Which AI models are used?**
A: DistilBERT (sentiment), OpenCV Haar Cascades (face detection), Random Forest (classification).

**Q: How accurate is emotion detection?**
A: ~75-85% under good conditions. Improves with proper lighting and positioning.

**Q: Can I train custom models?**
A: Yes, for developers. Check `backend/classifiers/` for model training scripts.

**Q: What database does it use?**
A: SQLite (default). Can be configured for PostgreSQL.

### Data & Privacy

**Q: Where is my data stored?**
A: Locally in `logs/syntwin_log.csv` and SQLite database file.

**Q: Can I export my data?**
A: Yes, CSV file at `logs/syntwin_log.csv`. Can be opened in Excel.

**Q: How do I permanently delete data?**
A: Use "Clear All History" button or manually delete files in `/logs` folder.

**Q: Is data encrypted?**
A: Not by default. If needed, you can encrypt the SQLite database manually.

### Usage Questions

**Q: How long should I let it run?**
A: Minimum 30 seconds for basic suggestions. 10+ minutes for accurate patterns.

**Q: Why do suggestions repeat?**
A: Limited task database. You can add custom tasks in the code.

**Q: Can I use it without camera?**
A: No, camera is required for face/posture detection.

**Q: Does it work in dark rooms?**
A: Poorly. Good lighting is essential for accurate detection.

---

## 🎓 Conclusion

You're now ready to use SynTwin effectively! 

**Quick Start Checklist:**
- ✅ Install dependencies
- ✅ Start backend server
- ✅ Open frontend dashboard
- ✅ Allow camera permissions
- ✅ Start detection
- ✅ Get personalized suggestions
- ✅ Review analytics

**Need More Help?**
- 📚 Check [API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md)
- 🚀 See [QUICK_START.md](docs/QUICK_START.md)
- 📖 Read [PROJECT_SYNOPSIS.md](PROJECT_SYNOPSIS.md)

**Support:**
- Report issues on GitHub
- Check logs in `/logs` folder
- Review console (F12) for errors

---

<div align="center">

**Happy monitoring!**

Made with ❤️ by TEAM FUTURE5

</div>
