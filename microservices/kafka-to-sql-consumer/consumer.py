import os
from kafka import KafkaConsumer
import psycopg2

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")

consumer = KafkaConsumer(
    KAFKA_TOPIC,
    bootstrap_servers=[KAFKA_BOOTSTRAP_SERVERS]
)

def write_to_db(msg):
    conn = psycopg2.connect(host=POSTGRES_HOST, database=POSTGRES_DB,
                            user=POSTGRES_USER, password=POSTGRES_PASSWORD)
    cur = conn.cursor()
    cur.execute("INSERT INTO events (value) VALUES (%s)", (msg.value.decode(),))
    conn.commit()
    conn.close()

for msg in consumer:
    print(f"Received: {msg.value}")
    write_to_db(msg)
