---
title: Kafka Message Check
author: bami jeong
categories: Startups
layout: post
comments: true
tags:
  - Airflow
---


- [b] REF
> [kafka official docs getting start](https://kafka.apache.org/documentation/#quickstart)
> 시작하기: [[Quick Start]]

- airflow url
```
{MASTER_IP}:8080
```

- Topic 만들기 

```bash
bin/kafka-topics.sh --create --topic quickstart-events --bootstrap-server localhost:9092
```

```bash
bin/kafka-topics.sh --describe --topic quickstart-events --bootstrap-server localhost:9092
```

- producer
```bash
bin/kafka-console-producer.sh --topic quickstart-events --bootstrap-server localhost:9092
This is my first event
This is my second event
```

- consumer
```bash
bin/kafka-console-consumer.sh --topic quickstart-events --from-beginning --bootstrap-server localhost:9092
This is my first event
This is my second event
```

##### Connection
>REF: [데이터 이벤트 스트림 가져오기/내보내기](https://kafka.apache.org/documentation/#connect)


~~## Airflow Kafka 통합~~ 

- [b] REF
> [Airflow/Kafka통합](https://www.restack.io/docs/airflow-knowledge-apache-kafka-operator-consumer-provider-example)
> [spark와 통합](https://www.restack.io/docs/airflow-knowledge-apache-spark-example-jobs#clp31wvme017hzi0u51pvxlof)




### Kafka 연산자 
- Consume: 메세지를 사용하다 
- tasks
```python
consume_task = ConsumeFromTopicOperator(
    task_id='consume_from_topic',
    topic='your_topic',
    apply_function=process_messages_function
)
```

- Produce: 메세지를 생성 
- tasks
```python
produce_task = ProduceToTopicOperator(
    task_id='produce_to_topic',
    topic='your_topic',
    producer_function=create_messages_function
)
```

### Airflow Dag와 연결 

- [?] 연결 확인 용도로 쓰이는건가 ? 
- tasks
```python
# Example of using KafkaConsumerOperator
consume_task = KafkaConsumerOperator(
    task_id='consume_kafka_topic',
    topic='your_topic',
    consumer_config={'bootstrap.servers': 'localhost:9092'}
)
```

### Airflow의 Kafka *producer* 사용해 메세지 생성

- tasks
```python
from airflow.providers.apache.kafka.operators.produce import ProduceToTopicOperator

def producer_function(**context):
    return 'key', 'message to send'

produce_task = ProduceToTopicOperator(
    task_id='produce_to_kafka_topic',
    producer_function=producer_function,
    kafka_conn_id='kafka_default',
    topic='your_topic'
)
```

### Airflow의 Kafka *consumer* 사용해 메세지 사용 
```bash
pip install apache-airflow-providers-apache-kafka
```

- tasks
```python
from airflow.providers.apache.kafka.operators.consume import ConsumeFromTopicOperator

consume_task = ConsumeFromTopicOperator(
    task_id='consume_from_topic',
    topic='your_topic',
    apply_function=your_processing_function,
    max_messages=10,
    kafka_conn_id='kafka_default'
)
```

- Dags
```python
# Example DAG to consume messages from a Kafka topic
from airflow import DAG
from airflow.utils.dates import days_ago

with DAG('kafka_consumer_example',
         start_date=days_ago(1),
         schedule_interval=None) as dag:

    consume_task
```

# Airflow 연동에 필요한 패키지 

![[Pasted image 20240201153446.png]]

- [b] REF
> https://airflow.apache.org/docs/apache-airflow/stable/installation/installing-from-pypi.html

```bash
pip install apache-airflow==2.8.1
pip install confluent-kafka
pip install asgiref
```

# 버전 업그레이드에 따른 Parameter key값 변경

- [b] REF
> https://airflow.apache.org/docs/apache-airflow-providers-apache-kafka/stable/_api/airflow/providers/apache/kafka/operators/consume/index.html

```python
pip install apache-airflow-providers-google
```

