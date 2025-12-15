# tests/test_simulator.py

"""
Integration test for SynTwin's simulator module.
It checks how the twin's internal state, life events, and environment interact.
"""

from backend.simulator.twin_state import TwinState
from backend.simulator.life_events import LifeEventGenerator
from backend.simulator.environment import Environment


def run_simulator_test():
    print("🧠 Starting SynTwin Simulator Test...\n")

    # Initialize components
    twin = TwinState()
    event_gen = LifeEventGenerator()
    env = Environment()

    # Simulated classifier + NLP data
    sample_inputs = [
        {"cognitive": {"state": "Focused"}, "mood": {"mood": "Calm"}, "sentiment": 0.8},
        {"cognitive": {"state": "Drowsy"}, "mood": {"mood": "Low"}, "sentiment": -0.4},
        {"cognitive": {"state": "Distracted"}, "mood": {"mood": "Tense"}, "sentiment": 0.1},
        {"cognitive": {"state": "Focused"}, "mood": {"mood": "Positive"}, "sentiment": 0.9},
    ]

    # Run multiple simulation cycles
    for i, data in enumerate(sample_inputs):
        print(f"🔹 Cycle {i + 1} — Updating Twin State")
        twin.update_from_inputs(
            data["cognitive"], data["mood"], sentiment=data["sentiment"]
        )

        snapshot = twin.get_snapshot()
        print(f"   Twin State: {snapshot}")

        # Generate event and adapt environment
        event = event_gen.generate_event(snapshot)
        env_feedback = env.adapt_environment(snapshot)

        # Display simulation results
        print(f"   Generated Life Event: {event['event']}")
        print(f"   Environment Feedback: {env_feedback['message']}")
        print("-------------------------------------------------\n")

    print("✅ Simulator test completed successfully!")


if __name__ == "__main__":
    run_simulator_test()
