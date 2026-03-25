from confluent_kafka import Consumer

BOOTSTRAP_SERVERS = "127.0.0.1:9092"
TOPIC = "orders"
GROUP_ID = "orders-consumer-group"

def create_consumer() -> Consumer:

    config = {
        "bootstrap.servers": BOOTSTRAP_SERVERS,
        "group.id": GROUP_ID,
        "auto.offset.reset": "earliest"
    }

    return Consumer(config)

def main():
    print("Consumer started")
    consumer = create_consumer()
    consumer.subscribe([TOPIC])

    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                pass
            elif msg.error():
                print(f"ERROR: {msg.error()}")
            else:
                key = msg.key().decode('utf-8') if msg.key() is not None else None
                print(f"Consumed event from topic {msg.topic()}: key = {key} value = {msg.value().decode('utf-8')}")
    except KeyboardInterrupt:
        print("Consumer stopped")
    finally:
        consumer.close()
        print("Consumer closed")


if __name__ == "__main__":
    main()
