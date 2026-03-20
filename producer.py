import json
import time
from kafka import KafkaProducer
from kafka.partitioner.default import random
from datetime import datetime

BOOTSTRAP_SERVERS="localhost:9092"
TOPIC = "orders"

def create_producer() -> KafkaProducer:
    return KafkaProducer(
        bootstrap_servers=BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        key_serializer=lambda k: k.encode("utf-8"),
    )

def make_order(order_id: int) -> dict:
    items = ["Apple", "Banana", "Orange", "Grape"]
    return {
        "order_id": order_id,
        "item": random.choice(items),
        "quantity": random.randint(1, 10),
        "price": round(random.uniform(100, 1000), 2),
        "timestamp": datetime.now().isoformat(),
    }

def main():
    producer = create_producer()

    try:
        for i in range(1, 11):
            order = make_order(i)
            key=f"order-{i}"
            future = producer.send(TOPIC, key=key, value=order)
            record_metadata = future.get(timeout=10)
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("Stopped")
    finally:
        producer.flush()
        producer.close()
        print("Producer closed")

if __name__ == "__main__":
    main()
