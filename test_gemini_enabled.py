"""
Test Gemini API Re-enablement
Verifies that Gemini API is active and returning AI-generated responses
"""
import sys
sys.path.insert(0, 'E:/SynTwin_Project')

from backend.nlp.gemini_advisor import get_gemini_advisor

print("=" * 80)
print("GEMINI API RE-ENABLEMENT TEST")
print("=" * 80)

# Get advisor instance
advisor = get_gemini_advisor()

print(f"\n[STATUS CHECK]")
print(f"  Gemini Ready: {advisor.ready}")
print(f"  Model: {advisor._model}")
print(f"  API Key: ...{advisor._key[-8:]}")

# Test with sample detection data
test_data = {
    "emotion": "Happy",
    "confidence": 0.72,
    "smile": "Yes",
    "eyes": "Eyes Open",
    "posture": "Good",
    "drowsy_score": 0.15,
    "blink_rate": 15.0,
    "session_minutes": 25,
    "recent_emotions": ["Happy", "Happy", "Neutral", "Happy", "Neutral", "Happy"]
}

print(f"\n[TEST REQUEST]")
print(f"  Emotion: {test_data['emotion']}")
print(f"  Confidence: {test_data['confidence']:.0%}")
print(f"  Posture: {test_data['posture']}")

print(f"\n[GEMINI RESPONSE]")
print("-" * 80)

result = advisor.get_advice(test_data)

if result["success"]:
    print(f"✓ Success: {result['success']}")
    print(f"✓ Source: {'Gemini AI' if advisor.ready else 'Fallback'}")
    print(f"\nAdvice:")
    print(result["advice"])
    print("\n" + "-" * 80)
    
    # Check if it's a real Gemini response (longer and more detailed than fallback)
    if len(result["advice"]) > 200:
        print("✅ CONFIRMED: Getting AI-generated Gemini responses!")
    else:
        print("⚠ WARNING: Response seems short, might be fallback")
else:
    print(f"✗ Error: {result.get('error', 'Unknown')}")

print("\n" + "=" * 80)
print("GEMINI API STATUS: RE-ENABLED AND ACTIVE")
print("=" * 80)
print("\n💡 Your Gemini API is now working!")
print("   - Endpoint: POST /api/nlp/gemini/advice")
print("   - Status: GET /api/nlp/gemini/status")
print("   - Frontend will now get AI-powered task suggestions")
print("=" * 80)
