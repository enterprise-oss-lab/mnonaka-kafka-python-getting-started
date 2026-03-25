import time

from random import choice
from confluent_kafka import Producer

BOOTSTRAP_SERVERS="127.0.0.1:9092"
TOPIC = "orders"

def create_producer() -> Producer:

    config = {
        "bootstrap.servers": BOOTSTRAP_SERVERS,
        "acks": "all"
    }

    return Producer(config)

def delivery_callback(err, msg):
    if err:
        print(f"ERROR: Message failed delivery: {err}")
    else:
        print(f"Produced event to topic {msg.topic()}: key = {msg.key().decode('utf-8')} value = {msg.value().decode('utf-8')}")

def main():
    print("Producer started")
    producer = create_producer()

    user_ids = ['eabara', 'jsmith', 'sgarcia', 'jbernard', 'htanaka', 'awalther']
    products = ['book', 'alarm clock', 't-shirts', 'gift card', 'batteries']

    try:
        for _ in range(1, 11):
            product = choice(products)
            user_id = choice(user_ids)
            producer.produce(topic=TOPIC, value=product, key=user_id, callback=delivery_callback)
            time.sleep(0.5)

            producer.poll(0)
    except KeyboardInterrupt:
        print("Stopped")
    finally:
        producer.flush()
        print("Producer closed")

if __name__ == "__main__":
    main()
