# backend/nlp/task_recommender.py
"""
Task Recommendation Engine
Suggests daily tasks based on user's emotional state, posture, and behavioral patterns.
Enhanced with Advanced NLP and ML models for more accurate recommendations.
NOW WITH REAL-LIFE TASK SUGGESTIONS!
"""
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from collections import Counter

# Import advanced NLP module
try:
    from .advanced_nlp import get_advanced_nlp
    ADVANCED_NLP_AVAILABLE = True
except ImportError:
    ADVANCED_NLP_AVAILABLE = False
    print("WARNING: Advanced NLP not available, using basic recommendations")

# Import real-life task engine
try:
    from .real_life_tasks import get_real_life_task_engine
    REAL_LIFE_TASKS_AVAILABLE = True
except ImportError:
    REAL_LIFE_TASKS_AVAILABLE = False
    print("WARNING: Real-life task engine not available")


class TaskRecommender:
    """
    Analyzes user behavior and recommends personalized daily tasks.
    Now integrated with advanced NLP, ML models, and REAL-LIFE task suggestions!
    """

    def __init__(self, db_path=None, use_advanced_nlp=True, use_real_life_tasks=True):
        if db_path is None:
            db_path = Path(__file__).parent.parent / "database" / "syntwin.db"
        self.db_path = db_path
        
        # Initialize advanced NLP if available
        self.advanced_nlp = None
        self.use_advanced = use_advanced_nlp and ADVANCED_NLP_AVAILABLE
        
        if self.use_advanced:
            try:
                self.advanced_nlp = get_advanced_nlp(db_path)
                print("[SUCCESS] Advanced NLP engine initialized")
            except Exception as e:
                print(f"[WARNING] Could not initialize advanced NLP: {e}")
                self.use_advanced = False
        
        # Initialize real-life task engine
        self.real_life_engine = None
        self.use_real_life = use_real_life_tasks and REAL_LIFE_TASKS_AVAILABLE
        
        if self.use_real_life:
            try:
                self.real_life_engine = get_real_life_task_engine()
                print("[SUCCESS] Real-life task engine initialized")
            except Exception as e:
                print(f"[WARNING] Could not initialize real-life tasks: {e}")
                self.use_advanced = False

    def get_recent_data(self, minutes=30):
        """
        Fetch recent detection data from database.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        time_threshold = (datetime.now() - timedelta(minutes=minutes)).strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute("""
            SELECT emotion, smile, eyes, posture, sentiment, timestamp
            FROM detector_logs
            WHERE timestamp >= ?
            ORDER BY timestamp DESC
        """, (time_threshold,))
        
        results = cursor.fetchall()
        conn.close()
        
        return results

    def analyze_current_state(self, minutes=10):
        """
        Analyze user's current emotional and physical state.
        Returns a summary of dominant patterns.
        """
        data = self.get_recent_data(minutes)
        
        if not data:
            return {
                "dominant_emotion": "Unknown",
                "posture_status": "Unknown",
                "energy_level": "Unknown",
                "avg_sentiment": 0,
                "needs_break": False,
                "data_points": 0
            }
        
        emotions = [row[0] for row in data if row[0]]
        postures = [row[3] for row in data if row[3]]
        eyes = [row[2] for row in data if row[2]]
        sentiments = [row[4] for row in data if row[4] is not None]
        
        # Count occurrences
        emotion_counter = Counter(emotions)
        posture_counter = Counter(postures)
        
        # Determine dominant patterns
        dominant_emotion = emotion_counter.most_common(1)[0][0] if emotion_counter else "Neutral"
        dominant_posture = posture_counter.most_common(1)[0][0] if posture_counter else "Unknown"
        
        # Calculate average sentiment
        avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0
        
        # Determine energy level
        closed_eyes_count = eyes.count("Closed")
        drowsy_count = emotions.count("Drowsy")
        energy_level = "Low" if (closed_eyes_count > len(eyes) * 0.3 or drowsy_count > 3) else "Normal"
        
        # Check if user needs a break
        slouching_count = postures.count("Slouching")
        needs_break = slouching_count > len(postures) * 0.5 or energy_level == "Low"
        
        return {
            "dominant_emotion": dominant_emotion,
            "posture_status": dominant_posture,
            "energy_level": energy_level,
            "avg_sentiment": round(avg_sentiment, 2),
            "needs_break": needs_break,
            "data_points": len(data),
            "closed_eyes_ratio": round(closed_eyes_count / len(eyes), 2) if eyes else 0
        }

    def get_task_suggestions(self, minutes=10):
        """
        Generate personalized REAL-LIFE task suggestions based on current state.
        Enhanced with Advanced NLP, ML predictions, and actual daily tasks!
        """
        state = self.analyze_current_state(minutes)
        
        # Check if there's any data available
        if state['data_points'] == 0:
            return {
                "suggestions": [],
                "priority": "none",
                "current_state": state,
                "recommendation_context": "No detection data available yet. Start detection to receive personalized task suggestions.",
                "method": "no_data"
            }
        
        # PRIORITY: Use real-life task engine first (if available)
        if self.use_real_life and self.real_life_engine:
            try:
                result = self.real_life_engine.get_real_life_suggestions(state, max_suggestions=7)
                
                # Determine priority
                categories = result['categories']
                if 'mental_wellness' in categories or 'posture_fix' in categories:
                    priority = 'high'
                elif 'challenging_work' in categories or 'collaborative_work' in categories:
                    priority = 'medium'
                else:
                    priority = 'low'
                
                return {
                    "suggestions": result['suggestions'],
                    "priority": priority,
                    "current_state": state,
                    "recommendation_context": result['context_message'],
                    "task_categories": categories,
                    "time_context": result['time_context'],
                    "method": "real_life_tasks"
                }
            except Exception as e:
                print(f"[WARNING] Real-life task engine failed: {e}, falling back...")
        
        # Fallback 1: Use advanced NLP if available
        if self.use_advanced and self.advanced_nlp:
            try:
                # Get user behavioral patterns
                user_patterns = self.advanced_nlp.get_user_patterns(days=7)
                
                # Get smart ML-based recommendations
                suggestions = self.advanced_nlp.get_smart_recommendations(state, user_patterns)
                
                # Determine priority using ML prediction
                category = self.advanced_nlp.predict_task_category(state)
                priority = self._category_to_priority(category, state)
                
                context = self._generate_smart_context(state, category, user_patterns)
                
                return {
                    "suggestions": suggestions[:5],  # Top 5
                    "priority": priority,
                    "current_state": state,
                    "recommendation_context": context,
                    "ml_category": category,
                    "method": "advanced_nlp"
                }
            except Exception as e:
                print(f"[WARNING] Advanced NLP failed, falling back to basic: {e}")
                # Fall through to basic recommendations
        
        # Basic rule-based recommendations (fallback)
        suggestions = []
        priority = "medium"
        
        emotion = state["dominant_emotion"]
        posture = state["posture_status"]
        energy = state["energy_level"]
        sentiment = state["avg_sentiment"]
        
        # Energy-based suggestions
        if energy == "Low" or emotion == "Drowsy":
            suggestions.extend([
                "☕ Take a coffee/tea break",
                "🚶 Walk around for 5-10 minutes",
                "💧 Drink some water to refresh",
                "🪟 Get some fresh air or open a window",
                "🧘 Do light stretching exercises"
            ])
            priority = "high"
        
        # Posture-based suggestions
        if posture == "Slouching":
            suggestions.extend([
                "🪑 Adjust your sitting posture",
                "🏋️ Do shoulder rolls and neck stretches",
                "⏰ Set up posture reminder alerts"
            ])
            if priority != "high":
                priority = "medium"
        
        # Emotion-based suggestions
        if emotion == "Sad" or sentiment < -0.3:
            suggestions.extend([
                "🎵 Listen to uplifting music",
                "👥 Reach out to a friend or colleague",
                "📝 Write down 3 things you're grateful for",
                "🌞 Take a break and go outside",
                "🎨 Do a creative activity you enjoy"
            ])
            priority = "high"
        
        elif emotion == "Angry" or emotion == "Frustrated":
            suggestions.extend([
                "🧘 Practice deep breathing (4-7-8 technique)",
                "🚶 Take a short walk to cool down",
                "✍️ Journal your thoughts",
                "🎧 Listen to calming music",
                "💬 Talk to someone about what's bothering you"
            ])
            priority = "high"
        
        elif emotion == "Happy" and sentiment > 0.5:
            suggestions.extend([
                "🎯 Great time for challenging tasks!",
                "📚 Tackle that difficult project you've been postponing",
                "💡 Brainstorm new ideas while you're energized",
                "🤝 Help a colleague with their work",
                "🎉 Celebrate your good mood - you earned it!"
            ])
            priority = "low"
        
        elif emotion == "Focused" or emotion == "Neutral":
            suggestions.extend([
                "🎯 Perfect time for deep work",
                "📊 Work on analytical or complex tasks",
                "📖 Learn something new",
                "🔍 Review and refine existing work",
                "⏱️ Use Pomodoro technique for productivity"
            ])
            priority = "low"
        
        # General wellness suggestions
        if state["data_points"] > 100:  # Long session
            suggestions.extend([
                "⏰ You've been working for a while - consider a break",
                "👁️ Give your eyes a rest (20-20-20 rule)",
                "🧘 Do a quick mindfulness exercise"
            ])
            if priority == "low":
                priority = "medium"
        
        # Remove duplicates while preserving order
        unique_suggestions = list(dict.fromkeys(suggestions))
        
        return {
            "suggestions": unique_suggestions[:8],  # Return top 8 suggestions
            "priority": priority,
            "state_summary": state,
            "recommendation_context": self._generate_context(state)
        }

    def _generate_context(self, state):
        """
        Generate a natural language summary of why suggestions were made.
        """
        emotion = state["dominant_emotion"]
        energy = state["energy_level"]
        posture = state["posture_status"]
        
        context_parts = []
        
        if emotion == "Drowsy" or energy == "Low":
            context_parts.append("You seem tired")
        elif emotion == "Happy":
            context_parts.append("You're in a great mood")
        elif emotion == "Sad":
            context_parts.append("You seem down")
        elif emotion == "Focused":
            context_parts.append("You're focused")
        
        if posture == "Slouching":
            context_parts.append("your posture needs attention")
        
        if state["needs_break"]:
            context_parts.append("you might benefit from a break")
        
        if not context_parts:
            return "Based on your current state, here are some suggestions."
        
        return f"Based on analysis: {', '.join(context_parts)}."

    def get_daily_summary(self, hours=24):
        """
        Get a summary of the user's day for end-of-day insights.
        """
        data = self.get_recent_data(minutes=hours * 60)
        
        if not data:
            return {"message": "No data available for today"}
        
        emotions = [row[0] for row in data if row[0]]
        postures = [row[3] for row in data if row[3]]
        sentiments = [row[4] for row in data if row[4] is not None]
        
        emotion_summary = Counter(emotions).most_common(3)
        posture_summary = Counter(postures).most_common(3)
        avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0
        
        return {
            "total_detections": len(data),
            "top_emotions": emotion_summary,
            "top_postures": posture_summary,
            "average_sentiment": round(avg_sentiment, 2),
            "sentiment_trend": "Positive" if avg_sentiment > 0.3 else "Negative" if avg_sentiment < -0.3 else "Neutral",
            "productive_hours": self._estimate_productive_time(emotions, postures)
        }
    
    def _category_to_priority(self, category: str, state: dict) -> str:
        """Convert ML category to priority level."""
        high_priority = ["take_break", "mental_health", "posture_fix"]
        medium_priority = ["focus_work", "wind_down"]
        
        if category in high_priority:
            return "high"
        elif category in medium_priority:
            return "medium"
        else:
            return "low"
    
    def _generate_smart_context(self, state: dict, category: str, patterns: dict) -> str:
        """Generate intelligent context message using ML insights."""
        context_parts = []
        
        # Category-based context
        category_contexts = {
            "take_break": "You need a break to recharge",
            "focus_work": "You're in great shape for focused work",
            "mental_health": "Your emotional wellbeing needs attention",
            "posture_fix": "Your posture needs adjustment",
            "challenging_task": "You have high energy for difficult tasks",
            "wind_down": "Time to wind down and prepare for rest"
        }
        
        if category in category_contexts:
            context_parts.append(category_contexts[category])
        
        # Add pattern-based insights
        if patterns and patterns.get('patterns_found'):
            current_hour = datetime.now().hour
            peak_hours = patterns.get('peak_productivity_hours', [])
            
            if current_hour in peak_hours:
                context_parts.append("you're in your peak productivity zone")
            elif peak_hours and current_hour < min(peak_hours):
                context_parts.append(f"your peak time is usually around {min(peak_hours)}:00")
        
        # Add state-based context
        if state.get('needs_break'):
            context_parts.append("break recommended")
        
        if not context_parts:
            return f"Based on ML analysis (category: {category}), here are personalized suggestions."
        
        return f"🤖 AI Analysis: {', '.join(context_parts)}."

    def _estimate_productive_time(self, emotions, postures):
        """
        Estimate productive time based on focused/happy emotions and good posture.
        """
        productive_states = ["Happy", "Focused", "Neutral"]
        good_postures = ["Upright", "Slightly Forward"]
        
        productive_count = sum(1 for e in emotions if e in productive_states)
        good_posture_count = sum(1 for p in postures if p in good_postures)
        
        # Rough estimate (each detection ~1-2 seconds)
        productive_minutes = (productive_count * 2) / 60
        
        return round(productive_minutes, 1)


# Convenience function
def get_suggestions(minutes=10):
    """Quick access to get task suggestions."""
    recommender = TaskRecommender()
    return recommender.get_task_suggestions(minutes)


if __name__ == "__main__":
    # Test the recommender
    recommender = TaskRecommender(use_advanced_nlp=True)
    
    print("🧠 SynTwin Task Recommender - Enhanced with Advanced NLP\n")
    print("="*60)
    
    print("\n📊 Analyzing your current state...\n")
    state = recommender.analyze_current_state(minutes=30)
    print("Current State:")
    for key, value in state.items():
        print(f"  {key}: {value}")
    
    print("\n" + "="*60)
    print("📋 Task Suggestions (AI-Powered):\n")
    
    result = recommender.get_task_suggestions(minutes=30)
    print(f"Priority: {result['priority'].upper()}")
    print(f"Method: {result.get('method', 'basic').upper()}")
    if 'ml_category' in result:
        print(f"ML Category: {result['ml_category']}")
    print(f"Context: {result['recommendation_context']}\n")
    
    print("Suggested Tasks:")
    for i, suggestion in enumerate(result['suggestions'], 1):
        print(f"  {i}. {suggestion}")
    
    print("\n" + "="*60)
    print("📊 Daily Summary:\n")
    
    daily = recommender.get_daily_summary(hours=24)
    for key, value in daily.items():
        print(f"  {key}: {value}")
    
    # Test advanced NLP features if available
    if recommender.use_advanced and recommender.advanced_nlp:
        print("\n" + "="*60)
        print("🤖 Advanced NLP Features:\n")
        
        patterns = recommender.advanced_nlp.get_user_patterns(days=7)
        if patterns.get('patterns_found'):
            print("User Behavioral Patterns:")
            print(f"  Peak Productivity Hours: {patterns['peak_productivity_hours']}")
            print(f"  Total Data Points: {patterns['total_data_points']}")
            print(f"  Most Common Emotions: {list(patterns['most_common_emotions'].keys())[:3]}")
        
        # Test sentiment analysis
        test_text = "I'm feeling great today and very productive!"
        sentiment = recommender.advanced_nlp.analyze_sentiment_advanced(test_text)
        print(f"\n  Text Sentiment Analysis: '{test_text}'")
        print(f"    Sentiment: {sentiment['sentiment']}")
        print(f"    Score: {sentiment['score']:.2f}")
        print(f"    Confidence: {sentiment['confidence']:.2f}")
        print(f"    Method: {sentiment['method']}")

