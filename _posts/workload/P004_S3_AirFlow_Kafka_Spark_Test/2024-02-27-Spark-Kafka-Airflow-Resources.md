---
title: Spark, Kafka, Airflow Resources
author: bami jeong
categories: build
layout: post
comments: true
tags:
  - DataPipeline
  - Spark
  - Airflow
  - Docker
  - Kafka
---
# Kafka Resource

```yaml
version: '2'

networks:
  common-network:
    external: true

services:
  zookeeper:
    image: confluentinc/cp-zookeeper:6.1.15
    hostname: zookeeper
    container_name: zookeeper
    ports:
      - "2181:2181"
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
    networks:
      - common-network

  broker:
    image: confluentinc/cp-kafka:6.1.15
    hostname: broker
    container_name: broker
    depends_on:
      - zookeeper
    ports:
      - "19092:19092"
      - "9092:9092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: 'zookeeper:2181'
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: 'INTERNAL:PLAINTEXT,EXTERNAL:PLAINTEXT'
      KAFKA_ADVERTISED_LISTENERS: 'INTERNAL://broker:9092,EXTERNAL://125.6.40.186:19092'
      KAFKA_INTER_BROKER_LISTENER_NAME: INTERNAL
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_TRANSACTION_STATE_LOG_MIN_ISR: 1
      KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 1
      KAFKA_GROUP_INITIAL_REBALANCE_DELAY_MS: 0
    networks:
      - common-network
```

# Spark Resource

## Dockerfile

```dockerfile
FROM bitnami/spark:3.3.0

USER root

# Install necessary packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        vim \
        curl \
        netcat-openbsd && \
    rm -rf /var/lib/apt/lists/*

# Download Kafka client JAR
RUN curl -o /opt/bitnami/spark/jars/kafka-clients-3.3.0.jar https://repo1.maven.org/maven2/org/apache/kafka/kafka-clients/3.3.0/kafka-clients-3.3.0.jar

# Download Spark Kafka connector JAR
RUN curl -o /opt/bitnami/spark/jars/spark-token-provider-kafka-0-10_2.12-3.3.0.jar https://repo1.maven.org/maven2/org/apache/spark/spark-token-provider-kafka-0-10_2.12/3.3.0/spark-token-provider-kafka-0-10_2.12-3.3.0.jar

# Download Spark SQL Kafka connector JAR
RUN curl -o /opt/bitnami/spark/jars/spark-sql-kafka-0-10_2.12-3.3.0.jar https://repo1.maven.org/maven2/org/apache/spark/spark-sql-kafka-0-10_2.12/3.3.0/spark-sql-kafka-0-10_2.12-3.3.0.jar

RUN curl -o /opt/bitnami/spark/jars/commons-pool2-2.11.0.jar https://repo1.maven.org/maven2/org/apache/commons/commons-pool2/2.11.0/commons-pool2-2.11.0.jar

RUN pip install py4j==0.10.9.5

USER 1001
```

## docker-compose.yaml

```yaml
# Copyright VMware, Inc.
# SPDX-License-Identifier: APACHE-2.0

version: '2'

networks:
  common-network:
    external: true

services:
  spark:
    image: seunghyejeong/spark:1.0
    environment:
      - SPARK_MODE=master
      - SPARK_RPC_AUTHENTICATION_ENABLED=no
      - SPARK_RPC_ENCRYPTION_ENABLED=no
      - SPARK_LOCAL_STORAGE_ENCRYPTION_ENABLED=no
      - SPARK_SSL_ENABLED=no
      - SPARK_USER=spark
      - SPARK_MASTER_OPTS="-Dspark.rpc.message.maxSize=512"
    ports:
      - '8080:8080'
      - '7077:7077'
    networks:
      - common-network

  spark-worker:
    image: seunghyejeong/spark:1.0
    environment:
      - SPARK_MODE=worker
      - SPARK_MASTER_URL=spark://bami-cluster2:7077
      - SPARK_WORKER_MEMORY=1G
      - SPARK_WORKER_CORES=1
      - SPARK_RPC_AUTHENTICATION_ENABLED=no
      - SPARK_RPC_ENCRYPTION_ENABLED=no
      - SPARK_LOCAL_STORAGE_ENCRYPTION_ENABLED=no
      - SPARK_SSL_ENABLED=no
      - SPARK_USER=spark
      - SPARK_PUBLIC_DNS=bami-cluster2
      - SPARK_WORKER_OPTS="-Dspark.rpc.message.maxSize=512"
    networks:
      - common-network
```

> /etc/hosts![[Pasted image 20240227101354.png]]

# Docker Network

```
$docker network create common-network
c6e200e1d23e453357553975f326462c98dd93bc11d7b958b2a9f7c9ab837a6d
```

# INTO Spark-worker Container , Python code

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json
from pyspark.sql.types import StringType, StructField, StructType, ArrayType, LongType

spark = SparkSession \
    .builder \
    .appName("Streaming from Kafka") \
    .config("spark.streaming.stopGracefullyOnShutdown", True) \
    .config('spark.jars.packages', 'org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0') \
    .config("spark.sql.shuffle.partitions", 4) \
    .master("local[*]") \
    .getOrCreate()
# Define Kafka connection properties
kafka_params = {
    "kafka.bootstrap.servers": "125.6.40.186:19092",
    "subscribe": "devices",
    "startingOffsets": "earliest"
}

# Define JSON Schema
json_schema = StructType([
    StructField('eventId', StringType(), True),
    StructField('eventOffset', LongType(), True),
    StructField('eventPublisher', StringType(), True),
    StructField('customerId', StringType(), True),
    StructField('data', StructType([
        StructField('devices', ArrayType(StructType([
            StructField('deviceId', StringType(), True),
            StructField('temperature', LongType(), True),
            StructField('measure', StringType(), True),
            StructField('status', StringType(), True)
        ]), True), True)
    ]), True),
    StructField('eventTime', StringType(), True)
])

# Read Kafka messages
streaming_df = spark \
    .readStream \
    .format("kafka") \
    .options(**kafka_params) \
    .load()

# Parse JSON messages
json_df = streaming_df.selectExpr("CAST(value AS STRING) AS json") \
    .select(from_json("json", json_schema).alias("data")) \
    .select("data.*")

# Start streaming query
query = json_df \
    .writeStream \
    .outputMode("append") \
    .format("console") \
    .start()

# Wait for the termination of the query
query.awaitTermination()
```

---

# *airflow dag 작성*

## workflow 

1. kafka 연결
2. kafka 연결 체크, spark 연결 체크
3. 생성된 토픽 가져오기 

⬇️ 소스 변경 ⬇️

1. ✅produce 하기: smaple JSON 파일 examplemsg.sh 실행 
2. ✅spark 서버에서 consume 실행 
3. ✅실행 값 받아오기 
4. ✅data 저장하기 ( postgres )


```python
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from kafka import KafkaProducer, KafkaConsumer
from kafka.admin import KafkaAdminClient, NewTopic
from datetime import datetime
from airflow.models import TaskInstance
from kafka.errors import TopicAlreadyExistsError

# Define Kafka broker
ansible.cfgbootstrap_servers = '133.186.240.216:19092'
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
    # 토픽이 이미 생성 되어 있다면 생성 되어 있는 토픽을 가져온다.
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
    producer = KafkaProducer(bootstrap_servers=bootstrap_servers,linger_ms=20)#실시간 스트리밍이 아닌 20초 간격으로 메세지를 전송한다.
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


```

## spark를 위한 PyPI 파일 

### Apache Spark Connections[](https://airflow.apache.org/docs/apache-airflow-providers-apache-spark/stable/connections/index.html#apache-spark-connections "Permalink to this heading")

- [Apache Spark Connect Connection](https://airflow.apache.org/docs/apache-airflow-providers-apache-spark/stable/connections/spark-connect.html)
- [Apache Spark SQL Connection](https://airflow.apache.org/docs/apache-airflow-providers-apache-spark/stable/connections/spark-sql.html)
- [Apache Spark Submit Connection](https://airflow.apache.org/docs/apache-airflow-providers-apache-spark/stable/connections/spark-submit.html)
- apache-airflow-providers-apache-spark

### Airflow Connection 만들기 

- connection type: Spark
- Host: spark://master
- port: 7077

> pip 설치하면 생길 것 같고. . 
### 단계 별 필요한 코드 작성하기 

- [b] REF
> [예제 코드](https://medium.com/swlh/using-airflow-to-schedule-spark-jobs-811becf3a960)

2. produce 하기: smaple JSON 파일 examplemsg.sh 실행

```python
import os, sys

def produce_message():
  producer = KafkaProducer(bootstrap_servers=bootstrap_servers,linger_ms=20)
  meesage = os.system('source examplemsg.sh')
  producer.send('devices', message.encode())
  producer.flush

def consume_message():
SparkSubmitOperator
from airflow.contrib.operators.spark_submit_operator import SparkSubmitOperator
```

```yaml
#airflowHome: /home/ubuntu/airflow
# Custom Images (include PyPI Packages)
images:
  airflow:
    repository: seunghyejeong/airflow
    tag: "1.0"
    digest: ~
    pullPolicy: IfNotPresent

# Load Examples
extraEnv: |
  - name: AIRFLOW__CORE__LOAD_EXAMPLES
    value: 'True'

# Webserver configure
webserver:
  defaultUser:
    enabled: true
    role: Admin
    username: admin
    email: admin@example.com
    firstName: admin
    lastName: user
    password: admin
  service:
    type: NodePort
    ports:
      - name: airflow-ui
        port: 8080
        targetPort: 8080
        nodePort: 31151
  # Mount additional volumes into webserver. 
  extraVolumeMounts: # container
     - name: airflow-dags
       mountPath: /opt/airflow/dags
  extraVolumes: # local
     - name: airflow-dags
       persistentVolumeClaim:
         claimName: airflow-dags
# bind w strogaeClass
dags:
  persistence:
    enabled: true
    storageClassName: cp-storageclass
    accessMode: ReadWriteMany
    size: 5Gi
workers:
  persistence:
    enabled: true
    storageClassName: cp-storageclass
    size: 5Gi
logs:
  persistence:
    enabled: true
    storageClassName: cp-storageclass    
```