---
title: The long adventure to success Pipeline...3) Do I need 'hostaliases' for connected Public? 
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



> [!tip] 
> 
> The Answer is "NONONONONONO" 

## Project Name: Hostaliases 설정 및 spark 코드 작성 

#KAFKA_SPARK_DOCKER_COMPOSE
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
      KAFKA_ADVERTISED_LISTENERS: 'INTERNAL://broker:9092,EXTERNAL://133.186.244.202:19092'
      KAFKA_INTER_BROKER_LISTENER_NAME: INTERNAL
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_TRANSACTION_STATE_LOG_MIN_ISR: 1
      KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 1
      KAFKA_GROUP_INITIAL_REBALANCE_DELAY_MS: 0
    networks:
      - common-network

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

```
helm upgrade airflow apache-airflow/airflow --namespace airflow -f custom_values.yaml
```

```bash
sudo docker compose exec broker kafka-topics --create --topic devices --bootstrap-server broker:9092 --replication-factor 1 --partitions 1
```

- 확인하기

```bash
sudo docker compose exec broker kafka-topics --describe --topic devices --bootstrap-server broker:9092 
```

```bash
kafka-console-producer --topic devices --bootstrap-server broker:9092
```

- 예제 토픽

```bash
{"eventId": "e3cb26d3-41b2-49a2-84f3-0156ed8d7502", "eventOffset": 10001, "eventPublisher": "device", "customerId": "CI00103", "data": {"devices": [{"deviceId": "D001", "temperature": 15, "measure": "C", "status": "ERROR"}, {"deviceId": "D002", "temperature": 16, "measure": "C", "status": "SUCCESS"}]}, "eventTime": "2023-01-05 11:13:53.643364"}
```

```
./bin/spark-submit \
--class <main-class> \
--master <master-url> \
--deploy-mode cluster \
--conf <key>=<value> \
... # 다른 옵션
<application-jar> \
[application-arguments]
```

## BUG: FileNotFoundError: [Errno 2] No such file or directory: '/home/airflow/.local/python/pyspark/shell.py' && /home/airflow/.local/bin/load-spark-env.sh: line 68: ps: command not found

1. SPARK_HOME을 다른 경로로 수정하기 

    ```
       ENV SPARK_HOME=/home/airflow/.local/assembly/target/scala-2.12
    ```


# airflow webserver-ui pod


```python
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.models import Connection
from datetime import datetime
from airflow.operators.python_operator import PythonOperator
from kafka import KafkaProducer
from pyspark.sql import SparkSession
from airflow.hooks.base_hook import BaseHook

bootstrap_servers = '125.6.40.186:19092'

def check_connected_kafka():
    try:
        producer = KafkaProducer(bootstrap_servers=bootstrap_servers)
        print("####SUCCESS CONNECTING KAFKA#######")
        return True
    except Exception as e:
        print(f"Error connecting to Kafka: {str(e)}")
        return False

def check_spark_connection():
    try:
        spark_conn = BaseHook.get_connection("spark_sql_default")
        spark_master_url = spark_conn.host+spark_conn.port
        spark = SparkSession.builder \
            .appName("Spark Connection Test") \
            .master(spark_master_url) \
            .getOrCreate()
        if spark:
            print("Spark connection successful!")
        else:
            print("Failed to establish Spark connection!")
    except Exception as e:
        print(f"Error occurred while checking Spark connection: {str(e)}")

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 1, 1),
    'retries': 1,
}

with DAG('spark_connection_check', default_args=default_args, schedule_interval=None) as dag:

    check_connected_kafka_task = PythonOperator(
        task_id='check_connected_kafka',
        python_callable=check_connected_kafka,
        dag=dag,
    )
    
    # Define the task to check Spark connection
    check_spark_conn_task = PythonOperator(
        task_id='check_spark_connection',
        python_callable=check_spark_connection,
        dag=dag,
    )

# Set the task dependencies
check_connected_kafka_task >> check_spark_conn_task

```

# 결론

나는 외부와 통신하기 위해서는 Hostaliases를 꼭 써야하는줄 알았다.. 