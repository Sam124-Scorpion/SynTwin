# tests/test_fusion.py

import cv2
from backend.detectors.fusion import DetectorFusion


def run_fusion_test():
    print("🧠 Starting SynTwin Detector Fusion Test...")
    cap = cv2.VideoCapture(0)
    fusion = DetectorFusion()

    print("📸 Press 'q' to stop live fusion test.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        fused_output = fusion.analyze_frame(frame)
        fused = fused_output["fused"]

        print(f"\n[State Snapshot] Emotion={fused['emotion']}, "
              f"Attention={fused['attention']}, Blink={fused['blink_rate']}, "
              f"Smile={fused['smile_score']}, Posture={fused['posture']}")

        cv2.imshow("SynTwin Fusion", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("✅ Fusion test completed successfully!")


if __name__ == "__main__":
    run_fusion_test()
