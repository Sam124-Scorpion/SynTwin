# backend/nlp/real_life_tasks.py
"""
Real-Life Task Suggestion Engine
Suggests actual daily tasks based on emotional state and energy levels.
Categories: Work, Personal, Learning, Social, Health, Creative
"""

from typing import Dict, List
from datetime import datetime


class RealLifeTaskEngine:
    """
    Suggests real-world tasks based on user's current state.
    """
    
    # Task database organized by context and requirements
    TASK_DATABASE = {
        # High energy + Good posture + Positive mood = Challenging work
        "high_energy_focused": {
            "work": [
                "💼 Complete that important project deadline",
                "📊 Prepare presentation for upcoming meeting",
                "💻 Code the complex feature you've been planning",
                "📝 Write detailed documentation or report",
                "🎯 Tackle the most difficult task on your list",
                "📧 Respond to complex client emails requiring thought",
                "🔍 Do deep analysis or research work",
                "📞 Make important business calls or negotiations"
            ],
            "learning": [
                "📚 Study new programming language or framework",
                "🎓 Take that challenging online course",
                "📖 Read technical documentation deeply",
                "💡 Work on personal skill development project",
                "🧪 Experiment with new tools or technologies"
            ],
            "creative": [
                "🎨 Work on your creative side project",
                "✍️ Write blog post or article",
                "🎬 Edit videos or create content",
                "🎵 Compose music or work on creative hobby",
                "📸 Plan and execute photo/design project"
            ]
        },
        
        # Medium energy + Neutral mood = Regular work
        "medium_energy_neutral": {
            "work": [
                "📧 Reply to pending emails in inbox",
                "📞 Return phone calls from earlier",
                "📅 Schedule meetings for next week",
                "📋 Review and organize task list",
                "💬 Chat with team members about updates",
                "📁 Organize files and documents",
                "✅ Complete routine tasks and checklists",
                "🔄 Update project status and progress"
            ],
            "personal": [
                "🛒 Plan grocery shopping list",
                "💰 Check bills and finances",
                "🏠 Organize home workspace",
                "📱 Backup important files and photos",
                "📝 Update personal calendar and reminders"
            ],
            "social": [
                "💬 Message friends you haven't talked to",
                "👥 Plan social activity for weekend",
                "📱 Check in with family members",
                "🎉 RSVP to pending invitations"
            ]
        },
        
        # Low energy + Tired = Light tasks
        "low_energy_tired": {
            "work": [
                "📧 Quick scan of urgent emails only",
                "📋 Make simple to-do list for tomorrow",
                "🗂️ Sort and file documents",
                "📊 Review simple reports or dashboards",
                "✅ Check off small completed tasks",
                "📝 Draft simple messages (save for later)",
                "🔖 Bookmark resources to read later"
            ],
            "personal": [
                "🎧 Listen to podcast or audiobook",
                "📱 Browse social media mindfully",
                "🖼️ Organize photo gallery",
                "🎮 Take gaming/entertainment break",
                "☕ Get coffee and recharge"
            ],
            "health": [
                "🚶 Take 10-minute walk outside",
                "☕ Make tea/coffee and hydrate",
                "🧘 Do light stretching exercises",
                "💤 Consider short power nap (15-20 min)",
                "🪟 Get fresh air by window"
            ]
        },
        
        # Negative emotions (sad/frustrated) = Mental wellness
        "negative_emotion": {
            "health": [
                "🧘 Meditation or breathing exercises",
                "🚶 Walk outside to clear head",
                "🎵 Listen to favorite uplifting music",
                "📝 Journal thoughts and feelings",
                "☎️ Call friend or family for chat"
            ],
            "personal": [
                "🎮 Play favorite game to unwind",
                "📺 Watch comfort show or movie",
                "🎨 Do relaxing creative activity",
                "🍽️ Prepare favorite meal or snack",
                "🛁 Take relaxing break"
            ],
            "work": [
                "✅ Do simple, satisfying tasks to feel accomplished",
                "📋 Organize workspace for fresh start",
                "🗑️ Delete old emails and clean inbox",
                "📁 Sort files and folders",
                "✨ Tidy desk and surroundings"
            ]
        },
        
        # Poor posture = Physical adjustment needed
        "poor_posture": {
            "health": [
                "🪑 Adjust chair height and back support",
                "🖥️ Check monitor is at eye level",
                "⌨️ Position keyboard and mouse ergonomically",
                "🧘 Do 5-minute posture exercises",
                "🏋️ Shoulder rolls and neck stretches",
                "🚶 Stand up and walk around",
                "⏰ Set hourly posture reminders"
            ],
            "work": [
                "📞 Make phone calls (standing up)",
                "🚶 Walk to colleague's desk instead of email",
                "☕ Get up to make coffee/water",
                "🗣️ Attend standing meeting if possible",
                "📋 Review tasks while standing"
            ]
        },
        
        # Happy + Good mood = Productive/social tasks
        "positive_mood": {
            "work": [
                "🤝 Collaborate with team on group project",
                "💡 Brainstorm new ideas with colleagues",
                "📞 Make networking calls or reach out to contacts",
                "✍️ Write positive feedback or recommendations",
                "🎯 Mentor or help junior team member",
                "🎉 Celebrate team wins and share good news",
                "💬 Have productive 1-on-1 conversations"
            ],
            "social": [
                "👥 Plan fun activity with friends",
                "📱 Send encouraging messages to people",
                "🎁 Think of gifts or surprises for loved ones",
                "🎊 Organize social gathering or event",
                "💌 Write thank you notes or appreciation"
            ],
            "personal": [
                "🎯 Set exciting personal goals",
                "🗺️ Plan future trip or adventure",
                "💪 Start new hobby or project",
                "📚 Begin that book you wanted to read",
                "🎨 Try new creative activity"
            ]
        },
        
        # Time-based tasks
        "morning_tasks": {
            "work": [
                "📊 Review today's priorities and schedule",
                "📧 Check urgent emails and messages",
                "🎯 Tackle most important task first (eat the frog)",
                "☕ Plan work blocks for the day",
                "📞 Schedule calls for later"
            ],
            "personal": [
                "🏃 Morning exercise or stretch",
                "📰 Read news or industry updates",
                "✅ Set daily intentions and goals",
                "🧘 Morning meditation or reflection"
            ]
        },
        
        "afternoon_tasks": {
            "work": [
                "📧 Reply to accumulated emails",
                "📞 Make phone calls and follow-ups",
                "👥 Attend scheduled meetings",
                "💬 Collaborate with team members",
                "📝 Update project documentation"
            ]
        },
        
        "evening_tasks": {
            "work": [
                "✅ Review what was completed today",
                "📋 Make tomorrow's priority list",
                "📧 Send any pending emails",
                "🗂️ Organize files and close tabs",
                "💾 Backup important work"
            ],
            "personal": [
                "🍽️ Plan or prepare dinner",
                "📚 Read for leisure",
                "👥 Connect with family/friends",
                "🎮 Relax with entertainment",
                "📅 Plan weekend activities",
                "💤 Prepare for good night's rest"
            ]
        }
    }
    
    def get_real_life_suggestions(self, state: Dict, max_suggestions: int = 5) -> Dict:
        """
        Get real-life task suggestions based on current state.
        
        Args:
            state: Dict with dominant_emotion, energy_level, posture_status, avg_sentiment
            max_suggestions: Maximum number of suggestions to return
            
        Returns:
            Dict with suggestions, categories, and context
        """
        emotion = state.get('dominant_emotion', 'Neutral')
        energy = state.get('energy_level', 'Medium')
        posture = state.get('posture_status', 'Good')
        sentiment = state.get('avg_sentiment', 0.0)
        
        # Determine current context
        current_hour = datetime.now().hour
        time_context = self._get_time_context(current_hour)
        
        suggestions = []
        categories_used = []
        
        # Priority 1: Handle poor posture (if present)
        if posture in ['Slouching', 'Leaning']:
            suggestions.extend(self._sample_tasks('poor_posture', 2))
            categories_used.append('posture_fix')
        
        # Priority 2: Handle negative emotions
        if emotion in ['Sad', 'Angry', 'Frustrated', 'Anxious'] or sentiment < -0.3:
            suggestions.extend(self._sample_tasks('negative_emotion', 2))
            categories_used.append('mental_wellness')
        
        # Priority 3: Energy-based task selection
        if energy == 'Low' or emotion == 'Drowsy':
            suggestions.extend(self._sample_tasks('low_energy_tired', 2))
            categories_used.append('light_work')
        elif energy == 'High' and sentiment > 0.5:
            suggestions.extend(self._sample_tasks('high_energy_focused', 3))
            categories_used.append('challenging_work')
        elif sentiment > 0.5:
            suggestions.extend(self._sample_tasks('positive_mood', 2))
            categories_used.append('collaborative_work')
        else:
            suggestions.extend(self._sample_tasks('medium_energy_neutral', 3))
            categories_used.append('routine_work')
        
        # Add time-specific tasks
        time_tasks = self._get_time_based_tasks(time_context)
        suggestions.extend(time_tasks)
        
        # Remove duplicates while preserving order
        unique_suggestions = []
        for sug in suggestions:
            if sug not in unique_suggestions:
                unique_suggestions.append(sug)
        
        # Limit to max suggestions
        final_suggestions = unique_suggestions[:max_suggestions]
        
        # Generate context
        context = self._generate_context(state, categories_used, time_context)
        
        return {
            'suggestions': final_suggestions,
            'categories': categories_used,
            'time_context': time_context,
            'context_message': context,
            'total_available': len(unique_suggestions)
        }
    
    def _sample_tasks(self, category: str, count: int) -> List[str]:
        """Sample tasks from a category."""
        import random
        
        if category not in self.TASK_DATABASE:
            return []
        
        category_data = self.TASK_DATABASE[category]
        all_tasks = []
        
        # Collect all tasks from all subcategories
        for subcategory, tasks in category_data.items():
            all_tasks.extend(tasks)
        
        # Sample without replacement if possible
        sample_count = min(count, len(all_tasks))
        return random.sample(all_tasks, sample_count)
    
    def _get_time_context(self, hour: int) -> str:
        """Determine time of day context."""
        if 5 <= hour < 12:
            return 'morning'
        elif 12 <= hour < 17:
            return 'afternoon'
        elif 17 <= hour < 21:
            return 'evening'
        else:
            return 'night'
    
    def _get_time_based_tasks(self, time_context: str, count: int = 1) -> List[str]:
        """Get time-specific tasks."""
        import random
        
        task_key = f'{time_context}_tasks'
        if task_key not in self.TASK_DATABASE:
            return []
        
        category_data = self.TASK_DATABASE[task_key]
        all_tasks = []
        
        for subcategory, tasks in category_data.items():
            all_tasks.extend(tasks)
        
        sample_count = min(count, len(all_tasks))
        return random.sample(all_tasks, sample_count) if all_tasks else []
    
    def _generate_context(self, state: Dict, categories: List[str], time_context: str) -> str:
        """Generate contextual message."""
        parts = []
        
        # Time context
        time_messages = {
            'morning': "Good morning! Start strong",
            'afternoon': "Afternoon momentum",
            'evening': "Evening wind-down",
            'night': "Late night"
        }
        parts.append(time_messages.get(time_context, ""))
        
        # Energy/emotion context
        emotion = state.get('dominant_emotion', 'Neutral')
        energy = state.get('energy_level', 'Medium')
        
        if energy == 'High':
            parts.append("you're energized for challenging tasks")
        elif energy == 'Low':
            parts.append("focus on lighter tasks")
        
        if emotion in ['Sad', 'Frustrated', 'Angry']:
            parts.append("take care of your wellbeing first")
        elif emotion == 'Happy':
            parts.append("great mood for collaboration")
        
        return " - " + ", ".join(parts) if parts else "Here are your task suggestions"


# Singleton instance
_real_life_task_engine = None

def get_real_life_task_engine():
    """Get or create singleton instance."""
    global _real_life_task_engine
    if _real_life_task_engine is None:
        _real_life_task_engine = RealLifeTaskEngine()
    return _real_life_task_engine
