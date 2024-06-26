---
title: Approve Dag files (add Schedule interval)
author: bami jeong
categories: Startups
layout: post
comments: true
tags: 
  - Airflow
---

- [b] REF
> [Producer,Consumer 구동 원리 이해하기](https://magpienote.tistory.com/251)

| airka1 | Ubuntu Server 22.04 LTS | 172.16.11.62, 133.186.250.238 |
| ---- | ---- | ---- |
| airka2 | Ubuntu Server 22.04 LTS | 172.16.11.30, 133.186.218.83 |

- Dag 파일 수정
1. 토픽을 생성하고 그 토픽을 재활용 하기 
2. 배치 처리로 바꾸기 ( 실시간  말고 )

```python
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from kafka import KafkaProducer, KafkaConsumer
from kafka.admin import KafkaAdminClient, NewTopic
from datetime import datetime
from airflow.models import TaskInstance
from kafka.errors import TopicAlreadyExistsError

# Define Kafka broker
bootstrap_servers = '133.186.240.216:19092'
topic_name = 'airflow-topic'

# Function to check if Kafka is connected
def check_connected():
    try:
        producer = KafkaProducer(bootstrap_servers=bootstrap_servers)
        consumer = KafkaConsumer(topic_name, bootstrap_servers=bootstrap_servers)
        return True
    except Exception as e:
        print(f"Error connecting to Kafka: {str(e)}")
        return False
        
# Function to create Kafka topic
def create_topic():
    admin_client = KafkaAdminClient(bootstrap_servers=bootstrap_servers)
    existing_topics = admin_client.list_topics()
    
    if topic_name in existing_topics:
        print(f"Topic '{topic_name}' already exists.")
    else:
        topic = NewTopic(name=topic_name, num_partitions=1, replication_factor=1)
        try:
            admin_client.create_topics([topic])
            print(f"Topic '{topic_name}' created successfully.")
        except TopicAlreadyExistsError:
            print(f"Topic '{topic_name}' already exists.")


# Function to produce a message to Kafka
def produce_message():
    producer = KafkaProducer(bootstrap_servers=bootstrap_servers,linger_ms=20)
    message = f"Hello from Airflow. Message produced at {datetime.now()}"
    producer.send(topic_name, message.encode())
    producer.flush()

# Function to consume a message from Kafka
def consume_message(**context):
    consumer = KafkaConsumer(topic_name, bootstrap_servers=bootstrap_servers, auto_offset_reset='earliest')
    try:
        message = next(consumer)
        print(f"Message consumed: {message.value.decode()}")
        # Mark the task as success
        context['task_instance'].log.info("Message consumed successfully")
        context['task_instance'].state = "success"
    except StopIteration:
        # No message available, mark the task as failed
        context['task_instance'].log.info("No message available to consume")
        context['task_instance'].state = "failed"
    finally:
        # Close the consumer to release resources
        consumer.close()

# Function to finish
def finish():
    print("All tasks completed.")

# Define the DAG
default_args = {
    'owner': 'admin',
    'depends_on_past': False,
    'start_date': datetime(2024, 2, 7),
    'retries': 1,
}

dag = DAG(
    'airflow_kafka_interworking',
    default_args=default_args,
    description='DAG for testing interworking of Airflow and Kafka',
    schedule_interval=None,
)

# Define tasks
create_topic_task = PythonOperator(
    task_id='create_topic',
    python_callable=create_topic,
    dag=dag,
)

check_connected_task = PythonOperator(
    task_id='check_connected',
    python_callable=check_connected,
    dag=dag,
)

produce_message_task = PythonOperator(
    task_id='produce_message',
    python_callable=produce_message,
    dag=dag,
)

consume_message_task = PythonOperator(
    task_id='consume_message',
    python_callable=consume_message,
    dag=dag,
)

finish_task = PythonOperator(
    task_id='finish',
    python_callable=finish,
    dag=dag,
)

# Define task dependencies
check_connected_task >> create_topic_task  >> produce_message_task >> consume_message_task >> finish_task
```