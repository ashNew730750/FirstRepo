import time
import json
import random
from datetime import datetime, timezone
from google.cloud import pubsub_v1

# ───── CONFIG ────────────────────────────────────────────────────────────
PROJECT = "project-b0f4dac3-0a4b-47cd-880"
TOPIC   = "cab-telemetry"
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(PROJECT, TOPIC)

# Create 50 cab IDs and give each a random starting location
cab_ids = [f"CAB{i:03d}" for i in range(1, 51)]
cab_states = {
    cab: {"lat": 40.0 + random.random()*0.1, "lon": -74.0 + random.random()*0.1}
    for cab in cab_ids
}

# ───── MAIN LOOP ─────────────────────────────────────────────────────────
while True:
    for cab in cab_ids:
        state = cab_states[cab]

        # 80% chance the cab moves a tiny bit, otherwise stays put
        if random.random() < 0.8:
            state["lat"] += (random.random() - 0.5) * 0.0005
            state["lon"] += (random.random() - 0.5) * 0.0005

        # Random speed: either zero (idle) or somewhere between 5–60 km/h
        speed = random.choice([0.0, round(random.uniform(5, 60), 1)])

        msg = {
            "cab_id":    cab,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "lat":       state["lat"],
            "lon":       state["lon"],
            "speed":     speed
        }

        # Publish to Pub/Sub
        data = json.dumps(msg).encode("utf-8")
        publisher.publish(topic_path, data)
        print(f"Published: {msg}")

        # # Slight pause between each cab's message
        # time.sleep(2)

    # After looping all 10 cabs, wait before starting the next cycle
    print("Cycle complete — sleeping 10s before next cycle\n")
    time.sleep(10)