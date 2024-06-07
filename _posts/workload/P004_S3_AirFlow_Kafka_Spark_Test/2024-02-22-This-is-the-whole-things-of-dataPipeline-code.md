---
title: This is whole steps rebuilding code of Data Proccessing
author: bami jeong
categories: Build
layout: post
comments: true
tags:
  - DataPipeline
  - Spark
  - Airflow
  - Docker
  - Kafka
---


- [b] REF
> https://taaewoo.tistory.com/32?category=887744
> https://github.com/subhamkharwal/ease-with-apache-spark/blob/master/33_spark_streaming_read_from_kafka.ipynb

- [i] version
> spark 3.4.2
> java 17
> scala 2.13

- [i] version(jar) 
> kafka-clients-3.4.1
> spark-token-provider-kafka-0-10_2.13-3.4.2
> spark-sql-kafka-0-10_2.13-3.4.2
> 
# Spark Dockerfile / docker-compose.yaml Source

##### custom images

```dockerfile
FROM bitnami/spark:3.4.2

USER root

# Install necessary packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        vim \
        curl && \
    rm -rf /var/lib/apt/lists/*


USER 1001

# Download Kafka client JAR
RUN curl -o /opt/bitnami/spark/jars/kafka-clients-3.4.1.jar https://repo1.maven.org/maven2/org/apache/kafka/kafka-clients/3.4.1/kafka-clients-3.4.1.jar

# Download Spark Kafka connector JAR
RUN curl -o /opt/bitnami/spark/jars/spark-token-provider-kafka-0-10_2.13-3.4.2.jar https://repo1.maven.org/maven2/org/apache/spark/spark-token-provider-kafka-0-10_2.13/3.4.2/spark-token-provider-kafka-0-10_2.13-3.4.2.jar

RUN curl -o /opt/bitnami/spark/jars/spark-sql-kafka-0-10_2.13-3.4.2.jar https://repo1.maven.org/maven2/org/apache/spark/spark-sql-kafka-0-10_2.13/3.4.2/spark-sql-kafka-0-10_2.13-3.4.2.jar

```

##### docker-compose.yaml

> 위에서 생성한 이미지를 사용

```yaml
# Copyright VMware, Inc.
# SPDX-License-Identifier: APACHE-2.0

version: '2'

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
    ports:
      - '8080:8080'
      - '7077:7077'
  spark-worker:
    image: seunghyejeong/spark:1.0
    environment:
      - SPARK_MODE=worker
      - SPARK_MASTER_URL=spark://spark:7077
      - SPARK_WORKER_MEMORY=1G
      - SPARK_WORKER_CORES=1
      - SPARK_RPC_AUTHENTICATION_ENABLED=no
      - SPARK_RPC_ENCRYPTION_ENABLED=no
      - SPARK_LOCAL_STORAGE_ENCRYPTION_ENABLED=no
      - SPARK_SSL_ENABLED=no
      - SPARK_USER=spark
```

# Spark streaming Soruce

- [b] REF
> [streaming](https://subhamkharwal.medium.com/pyspark-structured-streaming-read-from-kafka-64c40767155f)
> [Streaming kafka,spark github source](https://github.com/subhamkharwal/ease-with-apache-spark)

- [*] Cluster 정보  
> topic name:  device
> broker ip: broker:9092
> broker external ip: 133.186.217.113:19092

1. 토픽 생성
```bash
docker exec  -ti broker kafka-topics --create --topic devices --bootstrap-server broker:9092 --replication-factor 1 --partitions 1
```


- topic 생성
```bash
docker compose exec broker kafka-topics --create --topic kafka-topic --bootstrap-server broker:9092 --replication-factor 1 --partitions 1
```

- topic 확인 
```bash
[appuser@broker ~]$ docker compose exec broker kafka-topics --list --bootstrap-server  {EXTERNAL_IP}:19092
__consumer_offsets
my-topic
```

### KAFKA Container 

2. Sample JSON 파일
```json
{"eventId": "e3cb26d3-41b2-49a2-84f3-0156ed8d7502", "eventOffset": 10001, "eventPublisher": "device", "customerId": "CI00103", "data": {"devices": [{"deviceId": "D001", "temperature": 15, "measure": "C", "status": "ERROR"}, {"deviceId": "D002", "temperature": 16, "measure": "C", "status": "SUCCESS"}]}, "eventTime": "2023-01-05 11:13:53.643364"}
```

3. Sample JSON 'device' data
```json
{"eventId": "ba2ea9f4-a5d9-434e-8e4d-1c80c2d4b456", "eventOffset": 10000, "eventPublisher": "device", "customerId": "CI00119", "data": {"devices": []}, "eventTime": "2023-01-05 11:13:53.643364"}
{"eventId": "e3cb26d3-41b2-49a2-84f3-0156ed8d7502", "eventOffset": 10001, "eventPublisher": "device", "customerId": "CI00103", "data": {"devices": [{"deviceId": "D001", "temperature": 15, "measure": "C", "status": "ERROR"}, {"deviceId": "D002", "temperature": 16, "measure": "C", "status": "SUCCESS"}]}, "eventTime": "2023-01-05 11:13:53.643364"}
{"eventId": "8c202190-bc24-4485-89ec-de78e602dd68", "eventOffset": 10002, "eventPublisher": "device", "customerId": "CI00104", "data": {"devices": []}, "eventTime": "2023-01-05 11:13:53.643364"}
{"eventId": "aa90011f-3967-496c-b94b-a0c8de19a3d3", "eventOffset": 10003, "eventPublisher": "device", "customerId": "CI00108", "data": {"devices": [{"deviceId": "D004", "temperature": 16, "measure": "C", "status": "SUCCESS"}]}, "eventTime": "2023-01-05 11:13:53.643364"}
{"eventId": "e8859641-e9ad-44f8-94ce-353b840cff73", "eventOffset": 10004, "eventPublisher": "device", "customerId": "CI00116", "data": {"devices": []}, "eventTime": "2023-01-05 11:13:53.643364"}
{"eventId": "804e8fa3-307b-482e-b629-af880c52e884", "eventOffset": 10005, "eventPublisher": "device", "customerId": "CI00106", "data": {"devices": [{"deviceId": "D002", "temperature": 30, "measure": "C", "status": "ERROR"}, {"deviceId": "D001", "temperature": 10, "measure": "C", "status": "STANDBY"}, {"deviceId": "D001", "temperature": 6, "measure": "C", "status": "SUCCESS"}]}, "eventTime": "2023-01-05 11:13:53.643364"}
{"eventId": "b8675032-3fdf-4e1e-8816-3d4c1cd852cf", "eventOffset": 10006, "eventPublisher": "device", "customerId": "CI00120", "data": {"devices": []}, "eventTime": "2023-01-05 11:13:53.643364"}
{"eventId": "1c8d9682-56f0-4c3d-95c8-fce1bac45a74", "eventOffset": 10007, "eventPublisher": "device", "customerId": "CI00119", "data": {"devices": [{"deviceId": "D002", "temperature": 15, "measure": "C", "status": "ERROR"}, {"deviceId": "D002", "temperature": 12, "measure": "C", "status": "SUCCESS"}]}, "eventTime": "2023-01-05 11:13:53.643364"}
{"eventId": "fc625d0e-06c2-46b1-b9b5-b4a067e0a212", "eventOffset": 10008, "eventPublisher": "device", "customerId": "CI00117", "data": {"devices": [{"deviceId": "D003", "temperature": 6, "measure": "C", "status": "ERROR"}, {"deviceId": "D001", "temperature": 19, "measure": "C", "status": "ERROR"}, {"deviceId": "D005", "temperature": 0, "measure": "C", "status": "ERROR"}]}, "eventTime": "2023-01-05 11:13:53.643364"}
{"eventId": "7dba5625-33e9-4d9f-b767-b44bd03e098d", "eventOffset": 10009, "eventPublisher": "device", "customerId": "CI00100", "data": {"devices": [{"deviceId": "D003", "temperature": 27, "measure": "C", "status": "STANDBY"}, {"deviceId": "D001", "temperature": 24, "measure": "C", "status": "SUCCESS"}]}, "eventTime": "2023-01-05 11:13:53.643364"}
{"eventId": "209cab2d-7934-4ad2-ac36-dcae0b42d96b", "eventOffset": 10010, "eventPublisher": "device", "customerId": "CI00118", "data": {"devices": [{"deviceId": "D002", "temperature": 27, "measure": "C", "status": "SUCCESS"}, {"deviceId": "D005", "temperature": 23, "measure": "C", "status": "STANDBY"}]}, "eventTime": "2023-01-05 11:13:53.643364"}
{"eventId": "158c282f-3bbc-447a-9303-1e978a23274a", "eventOffset": 10011, "eventPublisher": "device", "customerId": "CI00119", "data": {"devices": []}, "eventTime": "2023-01-05 11:13:53.643364"}
{"eventId": "7146c4a8-54ed-4075-b013-c2d99e65d295", "eventOffset": 10012, "eventPublisher": "device", "customerId": "CI00117", "data": {"devices": [{"deviceId": "D002", "temperature": 5, "measure": "C", "status": "SUCCESS"}]}, "eventTime": "2023-01-05 11:13:53.643895"}
{"eventId": "1ff547fd-e335-457e-9a1f-686cfbe903e3", "eventOffset": 10013, "eventPublisher": "device", "customerId": "CI00103", "data": {"devices": [{"deviceId": "D004", "temperature": 23, "measure": "C", "status": "SUCCESS"}]}, "eventTime": "2023-01-05 11:13:53.643895"}
{"eventId": "692e9999-1110-4441-a20e-fd76692e2c17", "eventOffset": 10014, "eventPublisher": "device", "customerId": "CI00109", "data": {"devices": [{"deviceId": "D003", "temperature": 18, "measure": "C", "status": "ERROR"}]}, "eventTime": "2023-01-05 11:13:53.643895"}
{"eventId": "80101e8c-af6a-4ff5-81ae-3bf5db432811", "eventOffset": 10015, "eventPublisher": "device", "customerId": "CI00101", "data": {"devices": []}, "eventTime": "2023-01-05 11:13:53.649684"}
{"eventId": "7f0b1fba-3cd1-440d-9203-5dea57057ca8", "eventOffset": 10016, "eventPublisher": "device", "customerId": "CI00102", "data": {"devices": []}, "eventTime": "2023-01-05 11:13:53.649684"}
{"eventId": "cb8a6a8f-89c9-498a-9106-7d148ba998b7", "eventOffset": 10017, "eventPublisher": "device", "customerId": "CI00104", "data": {"devices": [{"deviceId": "D004", "temperature": 5, "measure": "C", "status": "STANDBY"}, {"deviceId": "D004", "temperature": 22, "measure": "C", "status": "SUCCESS"}, {"deviceId": "D004", "temperature": 9, "measure": "C", "status": "ERROR"}]}, "eventTime": "2023-01-05 11:13:53.649684"}
{"eventId": "a920562e-e8c0-4884-ad28-b74d82fc9ad8", "eventOffset": 10018, "eventPublisher": "device", "customerId": "CI00118", "data": {"devices": []}, "eventTime": "2023-01-05 11:13:53.649684"}
{"eventId": "87941320-3424-42dc-b853-371698b9e7dd", "eventOffset": 10019, "eventPublisher": "device", "customerId": "CI00104", "data": {"devices": [{"deviceId": "D005", "temperature": 20, "measure": "C", "status": "ERROR"}, {"deviceId": "D005", "temperature": 4, "measure": "C", "status": "STANDBY"}]}, "eventTime": "2023-01-05 11:13:53.649684"}
{"eventId": "37b1b74d-1538-4dd2-b689-cb8f2b214a0a", "eventOffset": 10020, "eventPublisher": "device", "customerId": "CI00101", "data": {"devices": [{"deviceId": "D003", "temperature": 22, "measure": "C", "status": "SUCCESS"}, {"deviceId": "D004", "temperature": 15, "measure": "C", "status": "STANDBY"}]}, "eventTime": "2023-01-05 11:13:53.649684"}
{"eventId": "db78b51f-2569-49de-8931-26f5c0bd424f", "eventOffset": 10021, "eventPublisher": "device", "customerId": "CI00102", "data": {"devices": [{"deviceId": "D002", "temperature": 22, "measure": "C", "status": "ERROR"}]}, "eventTime": "2023-01-05 11:13:53.649684"}
{"eventId": "1a8377a8-79e2-4138-8870-ce63b1bda703", "eventOffset": 10022, "eventPublisher": "device", "customerId": "CI00116", "data": {"devices": [{"deviceId": "D003", "temperature": 20, "measure": "C", "status": "STANDBY"}]}, "eventTime": "2023-01-05 11:13:53.649684"}
{"eventId": "e12d25f8-acc5-4331-92fb-ec25e998f243", "eventOffset": 10023, "eventPublisher": "device", "customerId": "CI00120", "data": {"devices": [{"deviceId": "D003", "temperature": 20, "measure": "C", "status": "ERROR"}, {"deviceId": "D004", "temperature": 24, "measure": "C", "status": "STANDBY"}]}, "eventTime": "2023-01-05 11:13:53.649684"}
{"eventId": "46a14162-f772-4acf-8a12-bb90790effaa", "eventOffset": 10024, "eventPublisher": "device", "customerId": "CI00109", "data": {"devices": []}, "eventTime": "2023-01-05 11:13:53.649684"}
{"eventId": "95ad03f2-46c9-4d9d-9c02-ea2d0fcf5578", "eventOffset": 10025, "eventPublisher": "device", "customerId": "CI00104", "data": {"devices": [{"deviceId": "D001", "temperature": 10, "measure": "C", "status": "ERROR"}, {"deviceId": "D001", "temperature": 4, "measure": "C", "status": "ERROR"}]}, "eventTime": "2023-01-05 11:13:53.649684"}
{"eventId": "0d7af0e0-9606-4130-adf2-c22c973ebf2c", "eventOffset": 10026, "eventPublisher": "device", "customerId": "CI00113", "data": {"devices": [{"deviceId": "D002", "temperature": 15, "measure": "C", "status": "SUCCESS"}]}, "eventTime": "2023-01-05 11:13:53.649684"}
{"eventId": "bee50d5e-3280-496e-a381-1eae3576d698", "eventOffset": 10027, "eventPublisher": "device", "customerId": "CI00118", "data": {"devices": [{"deviceId": "D003", "temperature": 17, "measure": "C", "status": "SUCCESS"}, {"deviceId": "D004", "temperature": 16, "measure": "C", "status": "STANDBY"}]}, "eventTime": "2023-01-05 11:13:53.649684"}
{"eventId": "78aad1aa-a427-4b5b-a33a-07f2effe9bab", "eventOffset": 10028, "eventPublisher": "device", "customerId": "CI00107", "data": {"devices": [{"deviceId": "D002", "temperature": 28, "measure": "C", "status": "ERROR"}, {"deviceId": "D003", "temperature": 12, "measure": "C", "status": "STANDBY"}]}, "eventTime": "2023-01-05 11:13:53.649684"}
{"eventId": "88bb528f-d8b8-4c6f-af79-937091390440", "eventOffset": 10029, "eventPublisher": "device", "customerId": "CI00114", "data": {"devices": [{"deviceId": "D003", "temperature": 22, "measure": "C", "status": "SUCCESS"}, {"deviceId": "D001", "temperature": 29, "measure": "C", "status": "ERROR"}, {"deviceId": "D003", "temperature": 16, "measure": "C", "status": "SUCCESS"}]}, "eventTime": "2023-01-05 11:13:53.649684"}
{"eventId": "655ea4c8-58ed-48e1-bcea-911c4b79f1bc", "eventOffset": 10030, "eventPublisher": "device", "customerId": "CI00120", "data": {"devices": [{"deviceId": "D005", "temperature": 14, "measure": "C", "status": "STANDBY"}]}, "eventTime": "2023-01-05 11:13:53.649684"}
```

> ./post_to_kafka.py

```python
# Method posts events to Kafka Server
# run command in kafka server to create topic : 
# ./usr/bin/kafka-topics --create --topic device_data --bootstrap-server kafka:9092 
from kafka import KafkaProducer, KafkaConsumer
import time
import random
from device_events import generate_events

__bootstrap_server = "133.186.217.113:19092"


def post_to_kafka(data):
    print('data: '+ str(data))
    producer = KafkaProducer(bootstrap_servers=__bootstrap_server)
    producer.send('devices', key=b'device', value=data)
    #producer.flush()
    producer.close()
    print("Posted to topic")


if __name__ == "__main__":
    _offset = 10000
    while True:
        post_to_kafka(bytes(str(generate_events(offset=_offset)), 'utf-8'))
        time.sleep(random.randint(0, 5))
        _offset += 1
```

```
kafka-console-producer --topic devices --bootstrap-server broker:9092
```

### SPARK Container 

5. Spakr 세션 만들기 
```python
from pyspark.sql import SparkSession
from pyspark.sql.types import StringType, StructField, StructType, ArrayType, LongType

spark = SparkSession \
    .builder \
    .appName("Streaming from Kafka") \
    .config("spark.streaming.stopGracefullyOnShutdown", True) \
    .config('spark.jars.packages', 'org.apache.spark:spark-sql-kafka-0-10_2.13:3.4.0') \
    .config("spark.sql.shuffle.partitions", 4) \
    .master("local[*]") \
    .getOrCreate()
```

3. Kafka에서 데이터 읽기를 위한 스트리밍 데이터 프레임 만들기 
```python
# Create the streaming_df to read from kafka
streaming_df = spark.readStream\
    .format("kafka") \
    .option("kafka.bootstrap.servers", "133.186.217.113:19092") \
    .option("subscribe", "devices") \
    .option("startingOffsets", "earliest") \
    .load()
```

```
# 데이터 스키마에 kafka 메시지를 게시하고 readStream을 read로 변경합니다  
# streaming_df.printSchema()  
# streaming_df.show(truncate=false)
```
4. JSON schema
```python
**# JSON Schema**  
from pyspark.sql.types import StringType, StructField, StructType, ArrayType, LongType  

json_schema = StructType([StructField('customerId', StringType(), True),
StructField('data', StructType([StructField('devices', ArrayType(StructType([ 
StructField('deviceId', StringType(), True),  
StructField('measure', StringType(), True), 
StructField('status', StringType(), True), \  
StructField('temperature', LongType(), True)]), True), True)]), True),
StructField('eventId', StringType(), True),
StructField('eventOffset', LongType(), True), 
StructField('eventPublisher', StringType(), True),
StructField('eventTime', StringType(), True)])
```

/opt/bitnami/spark/bin/spark-submit 

4. key-values 값에서 데이터를 읽고 JSON파일 형식으로 포맷
```python
**# Parse value from binay to string**  
json_df = streaming_df.selectExpr("cast(value as string) as value")  
  
**# Apply Schema to JSON value column and expand the value**  
from pyspark.sql.functions import from_json  
  
json_expanded_df = json_df.withColumn("value", from_json(json_df["value"], json_schema)).select("value.*")
```

5. 데이터를 Array
```python
**# Lets explode the data as devices contains list/array of device reading**  
from pyspark.sql.functions import explode, col  
  
exploded_df = json_expanded_df \  
.select("customerId", "eventId", "eventOffset", "eventPublisher", "eventTime", "data") \  
.withColumn("devices", explode("data.devices")) \  
.drop("data")
```

6. Array를 간소화시키기
```python
flattened_df = exploded_df \  
.selectExpr("customerId", "eventId", "eventOffset", "eventPublisher", "cast(eventTime as timestamp) as eventTime",  
"devices.deviceId as deviceId", "devices.measure as measure",  
"devices.status as status", "devices.temperature as temperature")
```

7. 평균값을 구하여 SUCCESS 시키기
```python
**# Aggregate the dataframes to find the average temparature  
# per Customer per device throughout the day for SUCCESS events**  
from pyspark.sql.functions import to_date, avg  
  
agg_df = flattened_df.where("STATUS = 'SUCCESS'") \  
.withColumn("eventDate", to_date("eventTime", "yyyy-MM-dd")) \  
.groupBy("customerId","deviceId","eventDate") \  
.agg(avg("temperature").alias("avg_temp"))
```

8. console에 출력하기
```python
**# Write the output to console sink to check the output**  
writing_df = agg_df.writeStream \  
.format("console") \  
.option("checkpointLocation","checkpoint_dir") \  
.outputMode("complete") \  
.start()  
  
**# Start the streaming application to run until the following happens  
# 1. Exception in the running program  
# 2. Manual Interruption**  
writing_df.awaitTermination()
```

# downgrade 3.3.0

### ERROR: java.lang.NoClassDefFoundError: scala/$less$colon$less

1.`spark-submit` CLI 로 python을 설치 할 때 .load() 부분에서 계속 에러가 남
```
24/02/22 05:29:03 INFO SharedState: Warehouse path is 'file:/spark-warehouse'.
Traceback (most recent call last):
  File "/spark_streaming.py", line 19, in <module>
    .load()
     ^^^^^^
  File "/opt/bitnami/spark/python/lib/pyspark.zip/pyspark/sql/streaming/readwriter.py", line 277, in load
  File "/opt/bitnami/spark/python/lib/py4j-0.10.9.7-src.zip/py4j/java_gateway.py", line 1322, in __call__
  File "/opt/bitnami/spark/python/lib/pyspark.zip/pyspark/errors/exceptions/captured.py", line 169, in deco
  File "/opt/bitnami/spark/python/lib/py4j-0.10.9.7-src.zip/py4j/protocol.py", line 326, in get_return_value
py4j.protocol.Py4JJavaError: An error occurred while calling o35.load.
: java.lang.NoClassDefFoundError: scala/$less$colon$less
```

: 이 때의 버전은 3.4.0에 스칼라 2.13 버전이었고, 예제는 3.3.0에 2.12 버전이었음.
아무래도 높은 버전의 이유인거 같아서 다운 그레이드 진행 

```Dockerfile
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

USER 1001

```

```
https://repo1.maven.org/maven2/org/apache/kafka/kafka-clients/3.3.0/kafka-clients-3.3.0.jar
```

```
https://repo1.maven.org/maven2/org/apache/spark/spark-token-provider-kafka-0-10_2.12/3.3.0/spark-token-provider-kafka-0-10_2.12-3.3.0.jar
```

```
https://repo1.maven.org/maven2/org/apache/spark/spark-sql-kafka-0-10_2.12/3.3.0/spark-sql-kafka-0-10_2.12-3.3.0.jar 
```

# `Python` CLI 사용하기

> 실행한 코드 

```python
from pyspark.sql import SparkSession
from pyspark.sql.types import StringType, StructField, StructType, ArrayType, LongType

spark = SparkSession \
    .builder \
    .appName("Streaming from Kafka") \
    .config("spark.streaming.stopGracefullyOnShutdown", True) \
    .config('spark.jars.packages', 'org.apache.spark:spark-sql-kafka-0-10_2.13:3.4.0') \
    .config("spark.sql.shuffle.partitions", 4) \
    .master("local[*]") \
    .getOrCreate()

streaming_df = spark.readStream\
    .format("kafka") \
    .option("kafka.bootstrap.servers", "133.186.217.113:19092") \
    .option("subscribe", "devices") \
    .option("startingOffsets", "earliest") \
    .load()

# JSON Schema
from pyspark.sql.types import StringType, StructField, StructType, ArrayType, LongType
json_schema = StructType([StructField('customerId', StringType(), True), \
StructField('data', StructType([StructField('devices', ArrayType(StructType([ \
StructField('deviceId', StringType(), True), \
StructField('measure', StringType(), True), \
StructField('status', StringType(), True), \
StructField('temperature', LongType(), True)]), True), True)]), True), \
StructField('eventId', StringType(), True), \
StructField('eventOffset', LongType(), True), \
StructField('eventPublisher', StringType(), True), \
StructField('eventTime', StringType(), True)])

# Parse value from binay to string
json_df = streaming_df.selectExpr("cast(value as string) as value")

# Apply Schema to JSON value column and expand the value
from pyspark.sql.functions import from_json

json_expanded_df = json_df.withColumn("value", from_json(json_df["value"], json_schema)).select("value.*")

```
### ERROR: ModuleNotFoundError: No module named 'py4j'

REF 에서 진행되는 프로세스를 보니 `python` 명령어를 사용 하길래 한번 시도해봄 

> CHAT GPT Said 💁‍♀️
```
what am i use CLI for run that codes?

# Launch Python interpreter python
python
```

> python spark_streaming.py ![[Pasted image 20240222153354.png]]

: 그러더니 모듈이 없다고 나오길래 설치 해줌

```bash
pip install py4j==0.10.9.5
```

그리고 python 실행 

> $ python spark_streaming.py

> 그리고 나의 OUTPUT
```bash
:: loading settings :: url = jar:file:/opt/bitnami/spark/jars/ivy-2.5.0.jar!/org/apache/ivy/core/settings/ivysettings.xml
Ivy Default Cache set to: /opt/bitnami/spark/.ivy2/cache
The jars for the packages stored in: /opt/bitnami/spark/.ivy2/jars
org.apache.spark#spark-sql-kafka-0-10_2.13 added as a dependency
:: resolving dependencies :: org.apache.spark#spark-submit-parent-49284453-8db1-4df1-8cc3-25cb272d9304;1.0
	confs: [default]
	found org.apache.spark#spark-sql-kafka-0-10_2.13;3.4.0 in central
	found org.apache.spark#spark-token-provider-kafka-0-10_2.13;3.4.0 in central
	found org.apache.kafka#kafka-clients;3.3.2 in central
	found org.lz4#lz4-java;1.8.0 in central
	found org.xerial.snappy#snappy-java;1.1.9.1 in central
	found org.slf4j#slf4j-api;2.0.6 in central
	found org.apache.hadoop#hadoop-client-runtime;3.3.4 in central
	found org.apache.hadoop#hadoop-client-api;3.3.4 in central
	found commons-logging#commons-logging;1.1.3 in central
	found com.google.code.findbugs#jsr305;3.0.0 in central
	found org.scala-lang.modules#scala-parallel-collections_2.13;1.0.4 in central
	found org.apache.commons#commons-pool2;2.11.1 in central
downloading https://repo1.maven.org/maven2/org/apache/spark/spark-sql-kafka-0-10_2.13/3.4.0/spark-sql-kafka-0-10_2.13-3.4.0.jar ...
	[SUCCESSFUL ] org.apache.spark#spark-sql-kafka-0-10_2.13;3.4.0!spark-sql-kafka-0-10_2.13.jar (508ms)
downloading https://repo1.maven.org/maven2/org/apache/spark/spark-token-provider-kafka-0-10_2.13/3.4.0/spark-token-provider-kafka-0-10_2.13-3.4.0.jar ...
	[SUCCESSFUL ] org.apache.spark#spark-token-provider-kafka-0-10_2.13;3.4.0!spark-token-provider-kafka-0-10_2.13.jar (266ms)
downloading https://repo1.maven.org/maven2/org/scala-lang/modules/scala-parallel-collections_2.13/1.0.4/scala-parallel-collections_2.13-1.0.4.jar ...
	[SUCCESSFUL ] org.scala-lang.modules#scala-parallel-collections_2.13;1.0.4!scala-parallel-collections_2.13.jar (420ms)
downloading https://repo1.maven.org/maven2/org/apache/kafka/kafka-clients/3.3.2/kafka-clients-3.3.2.jar ...
	[SUCCESSFUL ] org.apache.kafka#kafka-clients;3.3.2!kafka-clients.jar (513ms)
downloading https://repo1.maven.org/maven2/com/google/code/findbugs/jsr305/3.0.0/jsr305-3.0.0.jar ...
	[SUCCESSFUL ] com.google.code.findbugs#jsr305;3.0.0!jsr305.jar (256ms)
downloading https://repo1.maven.org/maven2/org/apache/commons/commons-pool2/2.11.1/commons-pool2-2.11.1.jar ...
	[SUCCESSFUL ] org.apache.commons#commons-pool2;2.11.1!commons-pool2.jar (259ms)
downloading https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-client-runtime/3.3.4/hadoop-client-runtime-3.3.4.jar ...
	[SUCCESSFUL ] org.apache.hadoop#hadoop-client-runtime;3.3.4!hadoop-client-runtime.jar (1537ms)
downloading https://repo1.maven.org/maven2/org/lz4/lz4-java/1.8.0/lz4-java-1.8.0.jar ...
	[SUCCESSFUL ] org.lz4#lz4-java;1.8.0!lz4-java.jar (283ms)
downloading https://repo1.maven.org/maven2/org/xerial/snappy/snappy-java/1.1.9.1/snappy-java-1.1.9.1.jar ...
	[SUCCESSFUL ] org.xerial.snappy#snappy-java;1.1.9.1!snappy-java.jar(bundle) (274ms)
downloading https://repo1.maven.org/maven2/org/slf4j/slf4j-api/2.0.6/slf4j-api-2.0.6.jar ...
	[SUCCESSFUL ] org.slf4j#slf4j-api;2.0.6!slf4j-api.jar (276ms)
downloading https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-client-api/3.3.4/hadoop-client-api-3.3.4.jar ...
	[SUCCESSFUL ] org.apache.hadoop#hadoop-client-api;3.3.4!hadoop-client-api.jar (1030ms)
downloading https://repo1.maven.org/maven2/commons-logging/commons-logging/1.1.3/commons-logging-1.1.3.jar ...
	[SUCCESSFUL ] commons-logging#commons-logging;1.1.3!commons-logging.jar (278ms)
:: resolution report :: resolve 16510ms :: artifacts dl 5920ms
	:: modules in use:
	com.google.code.findbugs#jsr305;3.0.0 from central in [default]
	commons-logging#commons-logging;1.1.3 from central in [default]
	org.apache.commons#commons-pool2;2.11.1 from central in [default]
	org.apache.hadoop#hadoop-client-api;3.3.4 from central in [default]
	org.apache.hadoop#hadoop-client-runtime;3.3.4 from central in [default]
	org.apache.kafka#kafka-clients;3.3.2 from central in [default]
	org.apache.spark#spark-sql-kafka-0-10_2.13;3.4.0 from central in [default]
	org.apache.spark#spark-token-provider-kafka-0-10_2.13;3.4.0 from central in [default]
	org.lz4#lz4-java;1.8.0 from central in [default]
	org.scala-lang.modules#scala-parallel-collections_2.13;1.0.4 from central in [default]
	org.slf4j#slf4j-api;2.0.6 from central in [default]
	org.xerial.snappy#snappy-java;1.1.9.1 from central in [default]
	---------------------------------------------------------------------
	|                  |            modules            ||   artifacts   |
	|       conf       | number| search|dwnlded|evicted|| number|dwnlded|
	---------------------------------------------------------------------
	|      default     |   12  |   12  |   12  |   0   ||   12  |   12  |
	---------------------------------------------------------------------
:: retrieving :: org.apache.spark#spark-submit-parent-49284453-8db1-4df1-8cc3-25cb272d9304
	confs: [default]
	12 artifacts copied, 0 already retrieved (57458kB/125ms)
24/02/22 06:24:51 WARN NativeCodeLoader: Unable to load native-hadoop library for your platform... using builtin-java classes where applicable
Setting default log level to "WARN".
To adjust logging level use sc.setLogLevel(newLevel). For SparkR, use setLogLevel(newLevel).
```

> 형아 아웃풋  ![[Pasted image 20240222153512.png]]

: 🧐 이거 완조니 형아가 말한 output이랑 똑같은거 ㅠ... 된거일까? 

# 그래서 Dockerfile을 수정한다

```Dockerfile
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

RUN pip install py4j==0.10.9.5

USER 1001
```

```
docker build --no-cache -t seunghyejeong/spark:1.0 .
docker push seunghyejeong/spark:1.0
```
# Streaming Code를 계속 추가해봄(*worker*)

- [!] 형아가 Kafka에서 메세지를 받아오려면 readstream을 read로 바꾸랬다.![[Pasted image 20240222154250.png]]


```python
from pyspark.sql import SparkSession
from pyspark.sql.types import StringType, StructField, StructType, ArrayType, LongType
from pyspark.sql.functions import from_json

spark = SparkSession \
    .builder \
    .appName("Streaming from Kafka") \
    .config("spark.streaming.stopGracefullyOnShutdown", True) \
    .config('spark.jars.packages', 'org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0') \
    .config("spark.sql.shuffle.partitions", 4) \
    .master("local[*]") `\`
    .getOrCreate()

streaming_df = spark.read\
    .format("kafka") \
    .option("kafka.bootstrap.servers", "133.186.217.113:19092") \
    .option("subscribe", "devices") \
    .option("startingOffsets", "earliest") \
    .load()
streaming_df.printSchema()
streaming_df.show(truncate=False)

# JSON Schema
json_schema = StructType([StructField('customerId', StringType(), True), \
StructField('data', StructType([StructField('devices', ArrayType(StructType([ \
StructField('deviceId', StringType(), True), \
StructField('measure', StringType(), True), \
StructField('status', StringType(), True), \
StructField('temperature', LongType(), True)]), True), True)]), True), \
StructField('eventId', StringType(), True), \
StructField('eventOffset', LongType(), True), \
StructField('eventPublisher', StringType(), True), \
StructField('eventTime', StringType(), True)])

# Parse value from binay to string
json_df = streaming_df.selectExpr("cast(value as string) as value")

# Apply Schema to JSON value column and expand the value
json_expanded_df = json_df.withColumn("value", from_json(json_df["value"], json_schema)).select("value.*")

# Validate Schema
json_expanded_df.show(10, False)
json_expanded_df.printSchema()

```

### ERROR : org.apache.spark.SparkException: Job aborted due to stage failure: Task 0 in stage 0.0 failed 1 times, most recent failure: Lost task 0.0 in stage 0.0 (TID 0) (83449ffc642fexecutor driver): java.lang.NoClassDefFoundError: org/apache/commons/pool2/impl/GenericKeyedObjectPoolConfig


아 자꾸 또 class 없다고 떠..서... 
보니까 spark.master라는 변수가.. local로 되어있었음. 바꿔봄..

```python
from pyspark.sql import SparkSession
from pyspark.sql.types import StringType, StructField, StructType, ArrayType, LongType
from pyspark.sql.functions import from_json

spark = SparkSession \
    .builder \
    .appName("Streaming from Kafka") \
    .config("spark.streaming.stopGracefullyOnShutdown", True) \
    .config('spark.jars.packages', 'org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0') \
    .config("spark.sql.shuffle.partitions", 4) \
    .master("spark://spark:7077") `\`
    .getOrCreate()
```

했떠니~

### ERROR: 24/02/22 07:46:26 WARN TaskSetManager: Lost task 0.0 in stage 0.0 (TID 0) (172.18.0.3 executor 0): java.lang.NoClassDefFoundError: org/apache/commons/pool2/impl/GenericKeyedObjectPoolConfig

다른게 떴고 뭔가 될거같음.. ip 가 나오는거 보니. . . . 

> Master ip를 삽입.

```python
from pyspark.sql import SparkSession
from pyspark.sql.types import StringType, StructField, StructType, ArrayType, LongType
from pyspark.sql.functions import from_json

spark = SparkSession \
    .builder \
    .appName("Streaming from Kafka") \
    .config("spark.streaming.stopGracefullyOnShutdown", True) \
    .config('spark.jars.packages', 'org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0') \
    .config("spark.sql.shuffle.partitions", 4) \
    .master("spark://133.186.217.113:7077") \
    .getOrCreate()
```

### ERROR AsyncEventQueue: Listener AppStatusListener threw an exception java.lang.NullPointerException

> docker compose file에 있는 master ip를 public ip로 연결 후 컨테이너를 다시 만듦.

```yaml
 spark-worker:
    image: seunghyejeong/spark:1.0
    environment:
      - SPARK_MODE=worker
      - SPARK_MASTER_URL=spark://133.186.217.113:7077
      - SPARK_WORKER_MEMORY=1G
```

몰러.. 마스터아이피가 저게 아닌가봐 .. 7077이랑 통신이 안돼 ..

- [b] REF
> [스파크 배포 및 실행 방법에 대한 이해](https://velog.io/@jskim/Spark-%EB%B0%B0%ED%8F%AC-%EB%B0%8F-%EC%8B%A4%ED%96%89-%EB%B0%A9%EB%B2%95%EC%97%90-%EB%8C%80%ED%95%9C-%EC%9D%B4%ED%95%B4)
> [Spark 서비스 포트 설정 이해하고 넘어가기](https://1mini2.tistory.com/102)

