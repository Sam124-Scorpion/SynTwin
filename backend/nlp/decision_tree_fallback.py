"""Rule-based fallback formatter for NLP advice responses."""


def _generate_context(state: dict) -> str:
    emotion = state.get("dominant_emotion", "Neutral")
    energy = state.get("energy_level", "Normal")
    posture = state.get("posture_status", "Straight")

    context_parts = []

    if emotion == "Drowsy" or energy == "Low":
        context_parts.append("You seem tired")
    elif emotion == "Happy":
        context_parts.append("You're in a great mood")
    elif emotion == "Focused":
        context_parts.append("You're focused")

    if posture == "Slouching":
        context_parts.append("your posture needs attention")

    if state.get("needs_break"):
        context_parts.append("you might benefit from a break")

    if not context_parts:
        return "Based on your current state, here are some suggestions."

    return f"Based on analysis: {', '.join(context_parts)}."


def build_decision_tree_fallback(state: dict) -> dict:
    """Format a rule-based fallback response using the existing task logic."""
    if not state:
        state = {}

    emotion = state.get("dominant_emotion") or state.get("emotion") or "Neutral"
    posture = state.get("posture_status") or state.get("posture") or "Straight"
    energy = state.get("energy_level") or "Normal"
    sentiment = state.get("avg_sentiment")
    drowsy_score = state.get("drowsy_score")

    if state.get("data_points", 1) == 0:
        return {
            "advice": "No detection data is available yet. Start detection to receive personalized task suggestions.",
            "suggestions": [],
            "priority": "none",
            "state_summary": state,
            "recommendation_context": "No detection data available yet. Start detection to receive personalized task suggestions.",
            "source": "decision_tree",
        }

    suggestions = []
    priority = "medium"

    if isinstance(drowsy_score, (int, float)) and drowsy_score >= 0.45:
        suggestions.extend([
            "💤 Take a 10-20 min power nap or rest your eyes",
            "☕ Have some water or a light caffeine drink",
            "🚶 Stand up and walk for 5 minutes",
        ])
        priority = "high"
    elif emotion == "Happy":
        suggestions.extend([
            "🎯 Channel this energy into your most important task",
            "💬 Reach out to a colleague or friend",
            "📚 Learn something new while you are in a great headspace",
        ])
        priority = "low"
    else:
        suggestions.extend([
            "✅ Pick one small task and complete it",
            "🧘 Do a 2-minute mindfulness check-in",
            "🚶 Take a short walk to reset focus",
        ])

    if "Slouch" in posture or "Forward" in posture:
        suggestions.append("🪑 Sit back, roll your shoulders, and straighten your spine")

    if isinstance(sentiment, (int, float)) and sentiment < -0.5:
        suggestions.extend([
            "🎵 Listen to uplifting music",
            "👥 Reach out to a friend or colleague",
            "📝 Write down 3 things you're grateful for",
        ])
        priority = "high"

    if energy == "Low":
        priority = "high"

    unique_suggestions = list(dict.fromkeys(suggestions))[:5]
    task_lines = "\n".join(f"{index + 1}. {task}" for index, task in enumerate(unique_suggestions))
    advice = (
        f"**Current State:** {emotion} detected"
        + (" | drowsy" if isinstance(drowsy_score, (int, float)) and drowsy_score >= 0.45 else "")
        + f"\n\n**Suggested Tasks:**\n{task_lines}"
        + "\n\n*You've got this — small steps lead to big changes!*"
    )

    return {
        "advice": advice,
        "suggestions": unique_suggestions,
        "priority": priority,
        "state_summary": state,
        "recommendation_context": _generate_context(state),
        "source": "decision_tree",
    }