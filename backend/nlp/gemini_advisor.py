"""
Gemini AI Mental Wellness Advisor
──────────────────────────────────────────────────────────────
Reads the user's real-time emotion detection data, builds a
structured prompt, and asks Google Gemini to suggest
personalised mental-wellness tasks and micro-interventions.

Usage:
    advisor = GeminiAdvisor(api_key="YOUR_GEMINI_API_KEY")
    response = advisor.get_advice(detection_snapshot)
"""

import os
from datetime import datetime
from typing import Optional

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _describe_drowsy_score(score: float) -> str:
    if score >= 0.75:
        return "severely drowsy (eyes heavily closed, low blink rate)"
    elif score >= 0.45:
        return "moderately drowsy (frequent eye closure)"
    elif score >= 0.20:
        return "mildly fatigued"
    return "alert and awake"


def _describe_posture(posture: str) -> str:
    mapping = {
        "Straight":          "upright and well-aligned",
        "Slouching":         "slouching forward (spine curved)",
        "Leaning Sideways":  "leaning sideways (asymmetric load on spine)",
        "Leaning Back":      "leaning back / reclining",
        "Slouching Forward": "slouching forward with neck strain",
        "Looking Down":      "looking down (neck flexed forward)",
    }
    return mapping.get(posture, posture)


def _time_of_day() -> str:
    h = datetime.now().hour
    if 5  <= h < 12: return "morning"
    if 12 <= h < 17: return "afternoon"
    if 17 <= h < 21: return "evening"
    return "late night"


# ─────────────────────────────────────────────────────────────────────────────
# Prompt builder
# ─────────────────────────────────────────────────────────────────────────────

def build_prompt(data: dict) -> str:
    """
    Convert a detection snapshot dict into a human-readable Gemini prompt.

    Expected keys in `data` (all optional with fallbacks):
        emotion, confidence, smile, eyes, posture,
        drowsy_score, blink_rate, faces_detected,
        dominant_emotion_last_n (optional, list of recent emotions),
        session_minutes (optional)
    """
    emotion       = data.get("emotion",      "Neutral")
    confidence    = data.get("confidence",   0.0)
    smile         = data.get("smile",        "Not Smiling")
    eyes          = data.get("eyes",         "Eyes Open")
    posture       = data.get("posture",      "Straight")
    drowsy_score  = float(data.get("drowsy_score", 0.0))
    blink_rate    = float(data.get("blink_rate",   0.0))
    session_mins  = data.get("session_minutes", None)
    recent_emots  = data.get("recent_emotions", [])   # list of recent emotion strings
    tod           = _time_of_day()

    # ── build observation block ───────────────────────────────────────────
    lines = [
        f"It is currently {tod}.",
        f"The user's detected emotion is **{emotion}** (CNN confidence: {confidence:.0%}).",
        f"Their eyes are currently **{eyes}**.",
        f"Smile status: **{smile}**.",
        f"Posture: **{_describe_posture(posture)}**.",
        f"Drowsiness level: **{_describe_drowsy_score(drowsy_score)}** "
        f"(score {drowsy_score:.2f}/1.0).",
    ]

    if blink_rate > 0:
        lines.append(
            f"Blink rate: **{blink_rate:.0f} blinks/min** "
            f"({'low – possible fatigue' if blink_rate < 10 else 'normal'})."
        )

    if session_mins:
        lines.append(f"The user has been at their desk for approximately **{session_mins} minutes**.")

    if recent_emots:
        summary = ", ".join(recent_emots[-8:])
        lines.append(f"Recent emotion history (last few detections): {summary}.")

    observation = "\n".join(lines)

    prompt = f"""You are SynTwin's AI wellness advisor. You analyse real-time biometric 
data captured by a webcam-based emotion & drowsiness detection system and suggest 
concise, actionable tasks to improve the user's mental state and productivity.

────────────────────────────────────────────────
CURRENT USER STATE
────────────────────────────────────────────────
{observation}

────────────────────────────────────────────────
YOUR TASK
────────────────────────────────────────────────
Based strictly on the data above, provide:

1. **Mental State Assessment** (2-3 sentences summarising what you observe)
2. **Immediate Action** (1 single thing to do RIGHT NOW – max 1 sentence)
3. **Top 5 Personalised Tasks** – numbered list, each on its own line.
   - Tailor tasks to the emotion, fatigue level, posture, and time of day.
   - Include a mix of: physical breaks, mental resets, productivity tasks,
     social connection, or creative activities as appropriate.
   - Be specific and actionable (e.g. "Do 3 slow neck rolls to relieve tension"
     not just "stretch").
4. **Motivational Nudge** (1 encouraging sentence, warm tone)

Keep the entire response under 250 words. Use plain readable language.
Do NOT repeat the raw numbers back to the user.
"""
    return prompt


# ─────────────────────────────────────────────────────────────────────────────
# Main class
# ─────────────────────────────────────────────────────────────────────────────

class GeminiAdvisor:
    """
    Wraps the Google Gemini API to generate mental wellness advice
    from emotion detection data.
    """

    DEFAULT_MODEL = "gemini-2.5-flash"   # fast + free-tier friendly

    def __init__(self, api_key: Optional[str] = None,
                 model: str = DEFAULT_MODEL) -> None:
        """
        Args:
            api_key: Gemini API key. Falls back to env var GEMINI_API_KEY.
            model:   Gemini model name (default: gemini-1.5-flash).
        """
        self._key   = api_key or os.environ.get("GEMINI_API_KEY", "AIzaSyAoEqgS7P7Ab7Lb3WN0aSNZWfyMfQDf9OQ")
        self._model = model
        self._client = None

        # ═══════════════════════════════════════════════════════════════
        # GEMINI API INITIALIZATION - Re-enabled
        # ═══════════════════════════════════════════════════════════════
        
        if not GEMINI_AVAILABLE:
            print("  ⚠ google-generativeai not installed. "
                  "Run: pip install google-generativeai")
            print("  ✓ Fallback advisor ready (Gemini unavailable)")
            return

        if not self._key:
            print("  ⚠ No Gemini API key supplied. "
                  "Set GEMINI_API_KEY env var or pass api_key=...")
            print("  ✓ Fallback advisor ready (No API key)")
            return

        try:
            genai.configure(api_key=self._key)
            self._client = genai.GenerativeModel(self._model)
            print(f"  ✓ Gemini AI: ENABLED (model: {self._model})")
            print(f"  ✓ API Key configured (ending: ...{self._key[-8:]})")
        except Exception as e:
            print(f"  ✗ Gemini init failed: {e}")
            print(f"  ✓ Fallback advisor ready")

    # ------------------------------------------------------------------
    @property
    def ready(self) -> bool:
        return self._client is not None

    # ------------------------------------------------------------------
    def get_advice(self, detection_data: dict) -> dict:
        """
        Generate AI wellness advice from detection data.

        Args:
            detection_data: dict from CombinedDetector.detect() result,
                            optionally augmented with recent_emotions /
                            session_minutes.

        Returns:
            {
                "success": bool,
                "advice":  str,          # full Gemini response
                "prompt":  str,          # prompt sent (for debugging)
                "emotion": str,
                "error":   str | None
            }
        """
        prompt = build_prompt(detection_data)

        if not self.ready:
            # Graceful offline fallback
            fallback = self._offline_fallback(detection_data)
            return {
                "success":  False,
                "advice":   fallback,
                "prompt":   prompt,
                "emotion":  detection_data.get("emotion", "Neutral"),
                "error":    "Gemini unavailable – using offline fallback",
            }

        try:
            response = self._client.generate_content(prompt)
            return {
                "success": True,
                "advice":  response.text.strip(),
                "prompt":  prompt,
                "emotion": detection_data.get("emotion", "Neutral"),
                "error":   None,
            }
        except Exception as e:
            fallback = self._offline_fallback(detection_data)
            return {
                "success": False,
                "advice":  fallback,
                "prompt":  prompt,
                "emotion": detection_data.get("emotion", "Neutral"),
                "error":   str(e),
            }

    # ------------------------------------------------------------------
    def _offline_fallback(self, data: dict) -> str:
        """Rule-based fallback when Gemini is unreachable."""
        emotion      = data.get("emotion",     "Neutral")
        drowsy_score = float(data.get("drowsy_score", 0.0))
        posture      = data.get("posture",     "Straight")

        tasks = []

        if drowsy_score >= 0.45:
            tasks += [
                "💤 Take a 10-20 min power nap or rest your eyes",
                "☕ Have some water or a light caffeine drink",
                "🚶 Stand up and walk for 5 minutes",
            ]
        elif emotion == "Angry":
            tasks += [
                "🧘 Do 4-7-8 breathing: inhale 4s, hold 7s, exhale 8s — repeat 3×",
                "🚶 Step away from the screen immediately for 3–5 minutes",
                "💧 Drink a full glass of cold water slowly and mindfully",
                "✍️ Write down exactly what triggered this feeling, then close the note",
                "🤲 Tense every muscle for 5 seconds, then fully release (progressive relaxation)",
            ]
        elif emotion == "Happy":
            tasks += [
                "🎯 Channel this energy into your most important task",
                "💬 Reach out to a colleague or friend",
                "📚 Learn something new while you are in a great headspace",
            ]
        else:
            tasks += [
                "✅ Pick one small task and complete it",
                "🧘 Do a 2-minute mindfulness check-in",
                "🚶 Take a short walk to reset focus",
            ]

        if "Slouch" in posture or "Forward" in posture:
            tasks.append("🪑 Sit back, roll your shoulders, and straighten your spine")

        task_list = "\n".join(f"{i+1}. {t}" for i, t in enumerate(tasks[:5]))
        return (
            f"**Current State:** {emotion} detected"
            + (" | drowsy" if drowsy_score >= 0.45 else "")
            + f"\n\n**Suggested Tasks:**\n{task_list}"
            + "\n\n*You've got this — small steps lead to big changes!*"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Singleton helper
# ─────────────────────────────────────────────────────────────────────────────

_advisor: Optional[GeminiAdvisor] = None


def get_gemini_advisor(api_key: Optional[str] = None) -> GeminiAdvisor:
    """Return (or create) the singleton GeminiAdvisor."""
    global _advisor
    if _advisor is None:
        _advisor = GeminiAdvisor(api_key=api_key)
    return _advisor
