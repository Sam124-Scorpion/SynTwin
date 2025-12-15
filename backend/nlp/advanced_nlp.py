# backend/nlp/advanced_nlp.py
"""
Advanced NLP Module with Custom AI Models
Provides more accurate sentiment analysis and task recommendations using:
- Transformer-based models (BERT, DistilBERT)
- Pattern recognition from user history
- Personalized machine learning
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from collections import Counter, defaultdict
import sqlite3
from pathlib import Path

# Try to import transformers, fallback gracefully if not available
try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print("WARNING: transformers not available, using basic NLP")

# Try to import sklearn for ML models
try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.preprocessing import LabelEncoder
    import pickle
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("WARNING: sklearn not available, using rule-based system")


class AdvancedNLP:
    """
    Advanced NLP system with transformer models and custom ML.
    """
    
    def __init__(self, db_path=None):
        if db_path is None:
            db_path = Path(__file__).parent.parent / "database" / "syntwin.db"
        self.db_path = db_path
        
        # Initialize transformer-based sentiment analyzer
        self.sentiment_pipeline = None
        if TRANSFORMERS_AVAILABLE:
            try:
                print("[INFO] Loading transformer model for sentiment analysis...")
                self.sentiment_pipeline = pipeline(
                    "sentiment-analysis",
                    model="distilbert-base-uncased-finetuned-sst-2-english"
                )
                print("[SUCCESS] Transformer model loaded successfully!")
            except Exception as e:
                print(f"[WARNING] Could not load transformer model: {e}")
                self.sentiment_pipeline = None
        
        # Initialize custom ML model for task recommendations
        self.task_classifier = None
        self.label_encoder = LabelEncoder()
        self.model_path = Path(__file__).parent / "models" / "task_recommender.pkl"
        self._load_or_train_model()
    
    def _load_or_train_model(self):
        """Load existing ML model or train a new one."""
        if not SKLEARN_AVAILABLE:
            return
        
        if self.model_path.exists():
            try:
                with open(self.model_path, 'rb') as f:
                    model_data = pickle.load(f)
                    self.task_classifier = model_data['classifier']
                    self.label_encoder = model_data['encoder']
                print("[SUCCESS] Loaded pre-trained task recommendation model")
            except Exception as e:
                print(f"[WARNING] Could not load model: {e}, will train new one")
                self._train_initial_model()
        else:
            self._train_initial_model()
    
    def _train_initial_model(self):
        """Train initial ML model with synthetic data."""
        if not SKLEARN_AVAILABLE:
            return
        
        try:
            # Create training data based on common patterns
            # Features: [emotion_score, posture_score, energy_score, time_of_day, sentiment]
            training_data = [
                # Low energy patterns -> Break recommendations
                ([0.2, 0.3, 0.1, 14, -0.4], "take_break"),
                ([0.1, 0.2, 0.0, 15, -0.3], "take_break"),
                ([0.3, 0.4, 0.2, 16, -0.2], "take_break"),
                
                # Good posture, high energy -> Productive work
                ([0.8, 0.9, 0.8, 10, 0.6], "focus_work"),
                ([0.7, 0.8, 0.7, 11, 0.5], "focus_work"),
                ([0.9, 0.9, 0.9, 9, 0.7], "focus_work"),
                
                # Negative emotions -> Mental health
                ([-0.6, 0.5, 0.4, 12, -0.7], "mental_health"),
                ([-0.7, 0.4, 0.3, 13, -0.8], "mental_health"),
                ([-0.5, 0.6, 0.5, 14, -0.6], "mental_health"),
                
                # Poor posture -> Physical adjustment
                ([0.5, 0.1, 0.5, 11, 0.2], "posture_fix"),
                ([0.6, 0.2, 0.6, 12, 0.1], "posture_fix"),
                ([0.4, 0.1, 0.4, 15, 0.0], "posture_fix"),
                
                # High energy, good mood -> Challenge
                ([0.9, 0.8, 0.9, 10, 0.8], "challenging_task"),
                ([0.8, 0.9, 0.8, 11, 0.9], "challenging_task"),
                
                # End of day, tired -> Wind down
                ([0.3, 0.4, 0.2, 17, -0.2], "wind_down"),
                ([0.2, 0.3, 0.1, 18, -0.3], "wind_down"),
            ]
            
            X = [item[0] for item in training_data]
            y = [item[1] for item in training_data]
            
            # Encode labels
            y_encoded = self.label_encoder.fit_transform(y)
            
            # Train classifier
            self.task_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
            self.task_classifier.fit(X, y_encoded)
            
            # Save model
            self.model_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.model_path, 'wb') as f:
                pickle.dump({
                    'classifier': self.task_classifier,
                    'encoder': self.label_encoder
                }, f)
            
            print("[SUCCESS] Trained and saved initial task recommendation model")
        except Exception as e:
            print(f"[WARNING] Could not train model: {e}")
            self.task_classifier = None
    
    def analyze_sentiment_advanced(self, text: str) -> Dict:
        """
        Advanced sentiment analysis using transformer models.
        Falls back to basic analysis if transformers unavailable.
        """
        if self.sentiment_pipeline and text:
            try:
                result = self.sentiment_pipeline(text[:512])[0]  # Limit to 512 tokens
                
                # Convert to -1 to 1 scale
                score = result['score']
                if result['label'] == 'NEGATIVE':
                    score = -score
                
                return {
                    "sentiment": result['label'].lower(),
                    "confidence": result['score'],
                    "score": score,
                    "method": "transformer"
                }
            except Exception as e:
                print(f"[WARNING] Transformer analysis failed: {e}")
        
        # Fallback to basic sentiment
        return self._basic_sentiment_analysis(text)
    
    def _basic_sentiment_analysis(self, text: str) -> Dict:
        """Fallback basic sentiment analysis."""
        positive_words = ["good", "great", "happy", "excellent", "love", "amazing", "wonderful"]
        negative_words = ["bad", "terrible", "hate", "sad", "angry", "awful", "frustrated"]
        
        text_lower = text.lower()
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        total = pos_count + neg_count
        if total == 0:
            return {"sentiment": "neutral", "confidence": 0.5, "score": 0.0, "method": "basic"}
        
        score = (pos_count - neg_count) / total
        sentiment = "positive" if score > 0 else "negative" if score < 0 else "neutral"
        
        return {
            "sentiment": sentiment,
            "confidence": abs(score),
            "score": score,
            "method": "basic"
        }
    
    def get_user_patterns(self, days=7) -> Dict:
        """
        Analyze user behavioral patterns over time.
        Learn when they're most productive, common emotional states, etc.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        time_threshold = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute("""
            SELECT emotion, posture, sentiment, timestamp
            FROM detector_logs
            WHERE timestamp >= ?
        """, (time_threshold,))
        
        results = cursor.fetchall()
        conn.close()
        
        if not results:
            return {"patterns_found": False}
        
        # Analyze patterns
        hourly_data = defaultdict(list)
        daily_emotions = defaultdict(list)
        
        for emotion, posture, sentiment, timestamp in results:
            dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
            hour = dt.hour
            day = dt.strftime("%A")
            
            hourly_data[hour].append({
                'emotion': emotion,
                'posture': posture,
                'sentiment': sentiment
            })
            daily_emotions[day].append(emotion)
        
        # Find peak productivity hours (high positive sentiment + good posture)
        productivity_scores = {}
        for hour, data_points in hourly_data.items():
            avg_sentiment = np.mean([d['sentiment'] for d in data_points if d['sentiment']])
            good_posture_pct = sum(1 for d in data_points if d['posture'] == 'Good') / len(data_points)
            productivity_scores[hour] = avg_sentiment * 0.6 + good_posture_pct * 0.4
        
        peak_hours = sorted(productivity_scores.items(), key=lambda x: x[1], reverse=True)[:3]
        
        return {
            "patterns_found": True,
            "peak_productivity_hours": [h[0] for h in peak_hours],
            "total_data_points": len(results),
            "hourly_patterns": dict(hourly_data),
            "most_common_emotions": dict(Counter([r[0] for r in results if r[0]]).most_common(5))
        }
    
    def predict_task_category(self, current_state: Dict) -> str:
        """
        Use ML model to predict best task category based on current state.
        """
        if not self.task_classifier:
            return "general"  # Fallback
        
        try:
            # Extract features
            emotion_score = self._emotion_to_score(current_state.get('dominant_emotion', 'Neutral'))
            posture_score = self._posture_to_score(current_state.get('posture_status', 'Good'))
            energy_score = self._energy_to_score(current_state.get('energy_level', 'Medium'))
            time_of_day = datetime.now().hour
            sentiment = current_state.get('avg_sentiment', 0.0)
            
            features = [[emotion_score, posture_score, energy_score, time_of_day, sentiment]]
            
            # Predict
            prediction = self.task_classifier.predict(features)[0]
            category = self.label_encoder.inverse_transform([prediction])[0]
            
            return category
        except Exception as e:
            print(f"[WARNING] Prediction failed: {e}")
            return "general"
    
    def get_smart_recommendations(self, current_state: Dict, user_patterns: Dict = None) -> List[str]:
        """
        Generate smart, personalized task recommendations using ML and patterns.
        """
        category = self.predict_task_category(current_state)
        
        # Get base recommendations for category
        recommendations = self._get_category_tasks(category, current_state)
        
        # Personalize based on user patterns
        if user_patterns and user_patterns.get('patterns_found'):
            current_hour = datetime.now().hour
            peak_hours = user_patterns.get('peak_productivity_hours', [])
            
            if current_hour in peak_hours:
                recommendations.insert(0, "💪 You're in your peak productivity zone! Tackle your most important task now.")
            elif current_hour < min(peak_hours) if peak_hours else 12:
                recommendations.append(f"📊 Your peak hours are around {peak_hours[0]}:00. Plan accordingly!")
        
        return recommendations
    
    def _emotion_to_score(self, emotion: str) -> float:
        """Convert emotion to numerical score."""
        scores = {
            "Happy": 0.9, "Excited": 0.8, "Focused": 0.7, "Neutral": 0.5,
            "Sad": -0.7, "Angry": -0.8, "Frustrated": -0.6, "Drowsy": 0.1, "Tired": 0.2
        }
        return scores.get(emotion, 0.5)
    
    def _posture_to_score(self, posture: str) -> float:
        """Convert posture to numerical score."""
        scores = {"Good": 0.9, "Leaning": 0.5, "Slouching": 0.1}
        return scores.get(posture, 0.5)
    
    def _energy_to_score(self, energy: str) -> float:
        """Convert energy level to numerical score."""
        scores = {"High": 0.9, "Medium": 0.5, "Low": 0.1}
        return scores.get(energy, 0.5)
    
    def _get_category_tasks(self, category: str, state: Dict) -> List[str]:
        """Get task recommendations for a specific category."""
        tasks = {
            "take_break": [
                "☕ Take a 10-minute break",
                "🚶 Walk around and stretch",
                "💧 Drink water and refresh",
                "🪟 Get fresh air",
                "🎵 Listen to relaxing music"
            ],
            "focus_work": [
                "🎯 Work on your most important task",
                "📝 Complete that pending project",
                "⏰ Use Pomodoro technique (25min focus)",
                "📊 Review and prioritize your to-do list",
                "💻 Deep work session - eliminate distractions"
            ],
            "mental_health": [
                "🧘 Practice 5-minute meditation",
                "📝 Journal your thoughts",
                "👥 Connect with a friend",
                "🌞 Step outside for fresh perspective",
                "🎨 Do a creative activity"
            ],
            "posture_fix": [
                "🪑 Adjust your chair and desk height",
                "🏋️ Do shoulder and neck stretches",
                "⏰ Set posture reminders every 30 minutes",
                "👀 Check your screen is at eye level",
                "🧘 Practice sitting posture exercises"
            ],
            "challenging_task": [
                "🚀 Tackle that difficult project you've been avoiding",
                "📚 Learn something new or challenging",
                "💡 Brainstorm creative solutions",
                "🎯 Set ambitious goals for today",
                "🏆 Push yourself out of your comfort zone"
            ],
            "wind_down": [
                "📝 Review your day's accomplishments",
                "📅 Plan tomorrow's priorities",
                "🧹 Organize your workspace",
                "📖 Light reading or learning",
                "🌙 Prepare for a good night's rest"
            ],
            "general": [
                "✅ Review and update your task list",
                "📊 Check your progress on ongoing projects",
                "💬 Respond to messages and emails",
                "🎯 Set 3 clear goals for today"
            ]
        }
        
        return tasks.get(category, tasks["general"])[:5]  # Return top 5


# Singleton instance
_advanced_nlp_instance = None

def get_advanced_nlp(db_path=None):
    """Get or create singleton instance of AdvancedNLP."""
    global _advanced_nlp_instance
    if _advanced_nlp_instance is None:
        _advanced_nlp_instance = AdvancedNLP(db_path)
    return _advanced_nlp_instance
