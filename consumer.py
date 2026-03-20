import json
from kafka import KafkaConsumer

BOOTSTRAP_SERVERS = "localhost:9092"
TOPIC = "orders"
GROUP_ID = "orders-consumer-group"

def create_consumer() -> KafkaConsumer:
    return KafkaConsumer(
        TOPIC,
        bootstrap_servers=BOOTSTRAP_SERVERS,
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        key_deserializer=lambda k: k.decode("utf-8") if k else None,
        group_id=GROUP_ID,
        auto_offset_reset="earliest",
        enable_auto_commit=True
    )

def main():
    consumer = create_consumer()

    try:
        for message in consumer:
            order = message.value
            print(order)
    except KeyboardInterrupt:
        print("Stopped")
    finally:
        consumer.close()
        print("Consumer closed")


if __name__ == "__main__":
    main()
