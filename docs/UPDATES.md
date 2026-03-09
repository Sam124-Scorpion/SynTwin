# SynTwin — Project Updates

> Changelog of all significant additions and changes to the SynTwin system.

---

## v1.1 — March 9, 2026

### 1. Desktop Detection Mode (`backend/main.py`)

`main.py` is now dual-mode:

| Mode | How to run |
|------|-----------|
| API Server (default) | `python start_api_server.py` |
| Desktop window | `python -m backend.main --mode desktop` |

The new `run_desktop_detection()` function launches a standalone OpenCV window with real-time emotion detection — no browser or FastAPI required.

**Features:**
- MediaPipe face detection with automatic OpenCV Haar Cascade fallback
- Threaded `VideoStream` at up to 1920×1080 @ 60 FPS
- Non-blocking `EmotionAnalyzer` (analysis-lock prevents concurrent model calls)
- Live HUD: emotion label, probability bars, FPS counter, coloured face bounding box
- `r` key — toggle video recording to file
- `q` key — graceful exit
- `argparse` CLI for mode selection

**Emotion classes (desktop mode):** `angry`, `disgust`, `fear`, `happy`, `sad`, `surprise`, `neutral`

---

### 2. New `backend/src/` Package

A modular, self-contained package powering the desktop detection runner.

| Module | Class / Purpose |
|--------|----------------|
| `backend/src/config.py` | `Config` — all window, camera, model, emotion-color, and throttle settings |
| `backend/src/core/analyzer.py` | `EmotionAnalyzer` — threaded, dual-backend (custom FER model + DeepFace fallback) |
| `backend/src/core/camera.py` | `VideoStream` — thread-safe `cv2.CAP_DSHOW` capture |
| `backend/src/core/face_detector.py` | `SimpleFaceDetector` — Haar Cascade face detection |
| `backend/src/ui/visualizer.py` | `Visualizer` — `draw_face_box()` and `draw_hud()` overlay rendering |
| `backend/src/utils/fps_counter.py` | `FPSCounter` — rolling FPS (configurable window, default 30) |
| `backend/src/utils/logger.py` | Structured logging utility |

**Key `Config` values:**
```python
CAMERA_ID      = 0
CAMERA_WIDTH   = 1920
CAMERA_HEIGHT  = 1080
FPS            = 60
ANALYSIS_THROTTLE = 3   # analyse every N frames
SMOOTHING_WINDOW  = 10
MODEL_PATH     = 'fer2013_mini_XCEPTION.102-0.66.hdf5'
```

**`EmotionAnalyzer` internals:**
- Primary: custom FER model (Keras/tf_keras, 48×48 grayscale input)
- Fallback: DeepFace (used only when custom model is absent)
- Thread-safe with `threading.Lock` on results and `analysis_lock` to prevent duplicate inference threads
- `start()` / `stop()` lifecycle; `analyze(face_img)` submits; `get_results()` returns `(emotion, probs)`

---

### 3. New Utility Scripts (`backend/scripts/`)

| Script | Purpose |
|--------|---------|
| `check_environment.py` | Validates Python version (3.8+ required; warns on 3.13+) and checks all package dependencies |
| `download_dataset.py` | Downloads FER2013 from Kaggle into `data/fer2013/`; requires authenticated `kaggle.json` |
| `test_system.py` | Pre-flight integration tests — imports OpenCV, MediaPipe, `Config`, `VideoStream`, `EmotionAnalyzer` and reports pass/fail |

**Recommended pre-startup sequence:**
```bash
python -m backend.scripts.check_environment
python -m backend.scripts.test_system
```

---

### 4. Frontend: Lighting Quality & Confidence Panel (`DetectionInfo.jsx`)

Two new fields added to the Detection Results card:

| Field | Detail |
|-------|--------|
| **Lighting Quality** | Text label with CSS class (`lighting-excellent` / `lighting-good` / `lighting-fair` / `lighting-poor`) |
| **Lighting icon** | 🌙 dark · ☀ bright · ✔ normal |
| **Confidence** | Numeric confidence value from the CNN detector stream |

New CSS classes in `DetectionInfo.css`:
- `.lighting-excellent` — green
- `.lighting-good` — light green
- `.lighting-fair` — amber
- `.lighting-poor` — red

---

### 5. SQLite Database Committed

`backend/database/syntwin.db` (~1.9 MB) is now tracked in the repository.  
No migration step required on first run — the database is pre-seeded and ready to use.

---

### 6. Detector Refactoring

All three detector modules were significantly slimmed down for maintainability:

| Module | Before | After | Change |
|--------|--------|-------|--------|
| `detectors/emotion_cnn.py` | ~495 lines | streamlined | Removed dead branches, consolidated scoring |
| `detectors/combined_detector.py` | ~392 lines | streamlined | Cleaner integration between face + emotion modules |
| `detectors/cnn_face_detector.py` | ~239 lines | streamlined | Focused on DNN + Haar Cascade fallback only |

**Also updated for detector compatibility:**
`analytics/data_logger.py`, `classifiers/mood_classifier.py`, `nlp/gemini_advisor.py`,
`nlp/sentiment_analyzer.py`, `nlp/task_recommender.py`, `services/nlp_service.py`, `services/stream_service.py`

---

## v1.0 — February 2026

### 1. CNN Emotion Detection System

Implemented a custom CNN-style feature extraction pipeline for real-time emotion detection, with optimised happy emotion recognition.

**New files:**

| File | Purpose |
|------|---------|
| `detectors/emotion_cnn.py` | Core emotion detector with 3-tier happy classification |
| `detectors/combined_detector.py` | Unified face + emotion pipeline with temporal smoothing |
| `detectors/cnn_face_detector.py` | OpenCV DNN face detector with Haar Cascade fallback |

**3-Tier Happy Detection:**

| Tier | Brightness | Mouth brightness | Condition |
|------|-----------|-----------------|-----------|
| Subtle | ≥ 95 | ≥ 105 | smile_ratio ≥ 1.03 |
| Moderate | ≥ 110 | ≥ 120 | variance ≥ 220 |
| Strong | ≥ 125 | ≥ 135 | variance ≥ 380 |

**Feature weights:**
```python
weights = {
    'brightness':       2.5,
    'mouth_brightness': 3.2,   # highest — key smile indicator
    'variance':         2.0,
    'eye_brightness':   2.8,   # Duchenne smile detection
    'smile_ratio':      2.3
}
```

**Stability mechanisms:**
- 7-frame history buffer with exponential weighting (0.7–1.0)
- Hysteresis: 20% probability lead required to override current stable emotion
- 30% confidence boost applied when smile indicators are active
- 15% minimum lead required for Happy over Neutral when scores are close

**Performance:**
- Overall accuracy: 80%
- Happy detection confidence: 63–71%
- Stability (no fluctuation): 85%+
- Real-time capable: 30 FPS

---

### 2. Gemini AI Task Recommendations

Integrated Google Gemini 2.5 Flash as the primary task recommendation engine.

**New file:** `nlp/gemini_advisor.py`

**API endpoints:**

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/nlp/gemini/advice` | POST | Get AI task suggestions with full state context |
| `/api/nlp/gemini/status` | GET | Check Gemini API availability |
| `/api/nlp/suggestions` | GET | Auto-routes to Gemini or local ML fallback |

**Prompt context sent to Gemini:**
- Current emotion + CNN confidence %
- Eye state and drowsiness score
- Posture quality
- Time of day
- Session duration
- Recent 10-state emotional trend

**Fallback chain (when Gemini is unavailable):**
1. Local Random Forest classifier (100 trees)
2. Rule-based sentiment-aware task matching
3. Offline task database (100+ curated tasks, 6 categories)

---

### 3. Stream Service Update (`services/stream_service.py`)

- Replaced `detector.detect()` → `detector.process_frame()`
- Replaced `draw_detections()` → `draw_results()`
- Added `intensity` field to WebSocket detection payloads
- Integrated 3-tier happy intensity into the live video stream output
