"""
Test suite for the emotion detection system
"""
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def test_imports():
    """Test if all modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        import cv2
        print("✅ OpenCV imported")
    except Exception as e:
        print(f"❌ OpenCV import failed: {e}")
        return False
    
    try:
        import mediapipe as mp
        print("✅ MediaPipe imported")
    except Exception as e:
        print(f"⚠️  MediaPipe import warning: {e}")
        print("   Fallback to OpenCV Haar Cascade will be used")
    
    try:
        from backend.src.config import Config
        print("✅ Config imported")
    except Exception as e:
        print(f"❌ Config import failed: {e}")
        return False
    
    try:
        from backend.src.core.camera import VideoStream
        print("✅ VideoStream imported")
    except Exception as e:
        print(f"❌ VideoStream import failed: {e}")
        return False
    
    try:
        from backend.src.ui.visualizer import Visualizer
        print("✅ Visualizer imported")
    except Exception as e:
        print(f"❌ Visualizer import failed: {e}")
        return False
    
    try:
        from backend.src.utils.fps_counter import FPSCounter
        print("✅ FPSCounter imported")
    except Exception as e:
        print(f"❌ FPSCounter import failed: {e}")
        return False
    
    # Test DeepFace separately as it may have issues
    try:
        from deepface import DeepFace
        print("✅ DeepFace imported (may show TensorFlow warnings - ignore them)")
    except Exception as e:
        print(f"⚠️  DeepFace import warning: {e}")
        print("   This is OK if you're using the custom model instead")
    
    return True

def test_config():
    """Test configuration"""
    print("\n🧪 Testing configuration...")
    
    try:
        from backend.src.config import Config
        
        assert hasattr(Config, 'EMOTIONS'), "Config missing EMOTIONS"
        assert hasattr(Config, 'CAMERA_WIDTH'), "Config missing CAMERA_WIDTH"
        assert hasattr(Config, 'ANALYSIS_THROTTLE'), "Config missing ANALYSIS_THROTTLE"
        
        print("✅ Configuration valid")
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_camera_detection():
    """Test if camera can be detected"""
    print("\n🧪 Testing camera detection...")
    
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            print("✅ Camera detected and accessible")
            cap.release()
            return True
        else:
            print("⚠️  Camera not detected or in use by another application")
            return False
    except Exception as e:
        print(f"❌ Camera test failed: {e}")
        return False

def main():
    print("=" * 60)
    print("🧪 Running Test Suite")
    print("=" * 60)
    print()
    
    results = []
    
    # Run tests
    results.append(("Imports", test_imports()))
    results.append(("Configuration", test_config()))
    results.append(("Camera", test_camera_detection()))
    
    # Summary
    print()
    print("=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print()
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System ready to run.")
        return 0
    else:
        print("⚠️  Some tests failed. Please fix issues before running.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
