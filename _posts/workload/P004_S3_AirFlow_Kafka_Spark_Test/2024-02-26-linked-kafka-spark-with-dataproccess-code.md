---
title: Kafka,Spark Containers are linked. Test Origin code of 'data proccess'
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



- [b] REF
> [docker network로 컨테이너 연결하기](https://towardsdatascience.com/end-to-end-data-engineering-system-on-real-data-with-kafka-spark-airflow-postgres-and-docker-a70e18df4090)

# Docker Container Network

- 도커 컨테이너끼리 연결 하려면 같은 bridge network를 사용해야 한다. 
- kafka와 spark의 컨테이너 네트워크를 `common-network`로 통일 시켜 재배포 한다.

> kafka docker-compose.yaml
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
      KAFKA_ADVERTISED_LISTENERS: 'INTERNAL://broker:9092,EXTERNAL://133.186.134.165:19092'
      KAFKA_INTER_BROKER_LISTENER_NAME: INTERNAL
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_TRANSACTION_STATE_LOG_MIN_ISR: 1
      KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 1
      KAFKA_GROUP_INITIAL_REBALANCE_DELAY_MS: 0
    networks:
      - common-network
```

> spark docker-compose.yaml

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
    networks:
      - common-network
```

# Spark의 PUBLIC_DNS는 HOST_NAME이다.

```yaml
  spark-worker:
    environment:  
      - SPARK_PUBLIC_DNS=bami-cluster2
      - SPARK_MASTER_URL=spark://bami-cluster2:7077 
```

- `SPAKR_PUBLIC_DNS`는 `${HOSTNAME}`을 사용한다.
- DNS를 사용한다는 뜻인데, , VM에서는 해당 VM의 이름이 해당한다.
- 원래는 보안상 사용되지 않지만 테스트 환경이라 Public ip와 dns이름을 매핑 시켰다.
- 연관된 에러는 아래와 같음.

> spark workers docker logs

#### 1. 아예 매핑을 안했을 때: Failed to connect to master bami-cluster2:7077
```bash
24/02/26 05:12:37 WARN Worker: Failed to connect to master bami-cluster2:7077
org.apache.spark.SparkException: Exception thrown in awaitResult:
	at org.apache.spark.util.ThreadUtils$.awaitResult(ThreadUtils.scala:301)
	at org.apache.spark.rpc.RpcTimeout.awaitResult(RpcTimeout.scala:75)
	at org.apache.spark.rpc.RpcEnv.setupEndpointRefByURI(RpcEnv.scala:102)
	at org.apache.spark.rpc.RpcEnv.setupEndpointRef(RpcEnv.scala:110)
	at org.apache.spark.deploy.worker.Worker$$anon$1.run(Worker.scala:313)
	at java.util.concurrent.Executors$RunnableAdapter.call(Executors.java:511)
	at java.util.concurrent.FutureTask.run(FutureTask.java:266)
	at java.util.concurrent.ThreadPoolExecutor.runWorker(ThreadPoolExecutor.java:1149)
	at java.util.concurrent.ThreadPoolExecutor$Worker.run(ThreadPoolExecutor.java:624)
	at java.lang.Thread.run(Thread.java:750)
Caused by: java.io.IOException: Failed to connect to bami-cluster2/127.0.1.1:7077
	at org.apache.spark.network.client.TransportClientFactory.createClient(TransportClientFactory.java:288)
	at org.apache.spark.network.client.TransportClientFactory.createClient(TransportClientFactory.java:218)
	at org.apache.spark.network.client.TransportClientFactory.createClient(TransportClientFactory.java:230)
	at org.apache.spark.rpc.netty.NettyRpcEnv.createClient(NettyRpcEnv.scala:204)
	at org.apache.spark.rpc.netty.Outbox$$anon$1.call(Outbox.scala:202)
	at org.apache.spark.rpc.netty.Outbox$$anon$1.call(Outbox.scala:198)
	... 4 more

```

#### 2: 잘못 매핑 했을 때(내부아이피 입력) 

> /etc/hosts 
```
{내부_IP} bami-cluster2
```

```bash
24/02/26 05:12:37 WARN Worker: Failed to connect to master bami-cluster2:7077
org.apache.spark.SparkException: Exception thrown in awaitResult:
	at org.apache.spark.util.ThreadUtils$.awaitResult(ThreadUtils.scala:301)
	at org.apache.spark.rpc.RpcTimeout.awaitResult(RpcTimeout.scala:75)
	at org.apache.spark.rpc.RpcEnv.setupEndpointRefByURI(RpcEnv.scala:102)
	at org.apache.spark.rpc.RpcEnv.setupEndpointRef(RpcEnv.scala:110)
	at org.apache.spark.deploy.worker.Worker$$anon$1.run(Worker.scala:313)
	at java.util.concurrent.Executors$RunnableAdapter.call(Executors.java:511)
	at java.util.concurrent.FutureTask.run(FutureTask.java:266)
	at java.util.concurrent.ThreadPoolExecutor.runWorker(ThreadPoolExecutor.java:1149)
	at java.util.concurrent.ThreadPoolExecutor$Worker.run(ThreadPoolExecutor.java:624)
	at java.lang.Thread.run(Thread.java:750)
Caused by: java.io.IOException: Failed to connect to bami-cluster2/127.0.1.1:7077
	at org.apache.spark.network.client.TransportClientFactory.createClient(TransportClientFactory.java:288)
	at org.apache.spark.network.client.TransportClientFactory.createClient(TransportClientFactory.java:218)
	at org.apache.spark.network.client.TransportClientFactory.createClient(TransportClientFactory.java:230)
	at org.apache.spark.rpc.netty.NettyRpcEnv.createClient(NettyRpcEnv.scala:204)
	at org.apache.spark.rpc.netty.Outbox$$anon$1.call(Outbox.scala:202)
	at org.apache.spark.rpc.netty.Outbox$$anon$1.call(Outbox.scala:198)

```

#### 2-1 잘못 매핑 했을 때(public ip 입력 but?) bami-cluster2/133.186.134.165:7077 timed out 

> /etc/hosts
```
#     /etc/cloud/cloud.cfg or cloud-config from user-data
#
127.0.1.1 bami-cluster2.novalocal bami-cluster2
127.0.0.1 localhost localhost.localdomain
133.186.134.165 bami-cluster2
```

```bash
24/02/26 05:14:39 INFO WorkerWebUI: Bound WorkerWebUI to 0.0.0.0, and started at http://bami-cluster2:8081
24/02/26 05:14:39 INFO Worker: Connecting to master bami-cluster2:7077...
24/02/26 05:14:46 INFO Worker: Retrying connection to master (attempt # 1)
24/02/26 05:14:46 INFO Worker: Connecting to master bami-cluster2:7077...
24/02/26 05:14:53 INFO Worker: Retrying connection to master (attempt # 2)
24/02/26 05:14:53 INFO Worker: Connecting to master bami-cluster2:7077...
24/02/26 05:15:00 INFO Worker: Retrying connection to master (attempt # 3)
24/02/26 05:15:00 INFO Worker: Connecting to master bami-cluster2:7077...
24/02/26 05:15:07 INFO Worker: Retrying connection to master (attempt # 4)
24/02/26 05:15:07 INFO Worker: Connecting to master bami-cluster2:7077...
24/02/26 05:15:14 INFO Worker: Retrying connection to master (attempt # 5)
24/02/26 05:15:14 INFO Worker: Connecting to master bami-cluster2:7077...
24/02/26 05:15:21 INFO Worker: Retrying connection to master (attempt # 6)
24/02/26 05:15:21 INFO Worker: Connecting to master bami-cluster2:7077...
24/02/26 05:16:03 INFO Worker: Retrying connection to master (attempt # 7)
24/02/26 05:16:03 INFO Worker: Connecting to master bami-cluster2:7077...
24/02/26 05:16:39 ERROR RpcOutboxMessage: Ask terminated before connecting successfully
24/02/26 05:16:39 WARN NettyRpcEnv: Ignored failure: java.io.IOException: Connecting to bami-cluster2/133.186.134.165:7077 timed out (120000 ms)
```

#### 3. 👍성공: 이유는 127.0.0.1과 더블 맵핑 되어있어서 그랬음

> /etc/hosts 
```
#127.0.1.1 bami-cluster2.novalocal bami-cluster2
127.0.0.1 localhost localhost.localdomain
133.186.134.165 bami-cluster2
```

```bash
24/02/26 05:16:48 INFO Utils: Successfully started service 'sparkWorker' on port 45317.
24/02/26 05:16:48 INFO Worker: Worker decommissioning not enabled.
24/02/26 05:16:48 INFO Worker: Starting Spark worker 172.20.0.3:45317 with 1 cores, 1024.0 MiB RAM
24/02/26 05:16:48 INFO Worker: Running Spark version 3.3.0
24/02/26 05:16:48 INFO Worker: Spark home: /opt/bitnami/spark
24/02/26 05:16:48 INFO ResourceUtils: ==============================================================
24/02/26 05:16:48 INFO ResourceUtils: No custom resources configured for spark.worker.
24/02/26 05:16:48 INFO ResourceUtils: ==============================================================
24/02/26 05:16:48 INFO Utils: Successfully started service 'WorkerUI' on port 8081.
24/02/26 05:16:48 INFO WorkerWebUI: Bound WorkerWebUI to 0.0.0.0, and started at http://bami-cluster2:8081
24/02/26 05:16:48 INFO Worker: Connecting to master bami-cluster2:7077...
24/02/26 05:16:48 INFO TransportClientFactory: Successfully created connection to bami-cluster2/133.186.134.165:7077 after 27 ms (0 ms spent in bootstraps)
24/02/26 05:16:48 INFO Worker: Successfully registered with master spark://9f9c7873a6de:7077
```

성공적 바인딩.


# Kafka와 Spark 통신 체크 

### 통신 체크 
> Spark에서 Kafka

```bash
I have no name!@216f325d25a3:/opt/bitnami/spark$ nc -vz 133.186.134.165 19092
Connection to 133.186.134.165 19092 port [tcp/*] succeeded!
```

> Kafka 에서 Spark
```bash
[appuser@broker ~]$ nc -vz 133.186.134.165 7077
Ncat: Version 7.92 ( https://nmap.org/ncat )
Ncat: Connected to 133.186.134.165:7077.
Ncat: 0 bytes sent, 0 bytes received in 0.01 seconds.
```
: 이것이 된것인지 아닌것인지 아리송.. 통신이 가기는 가는데 받아 올 값이 없다는 뜻이랬음.
이제까지 worker만 로그를 체크했는데 master log를 체크하니 이런 로그가 떴다. 

### 애매한 통신에 대한 로그 확인  👎

> Spark - master logs

```bash
this is spark master's logs : is it problem? 24/02/26 05:30:19 
INFO Master: 218.51.176.155:62574 got disassociated, removing it. 24/02/26 05:30:19 
WARN TransportChannelHandler: Exception in connection from /218.51.176.155:62575 java.lang.IllegalArgumentException: 
Too large frame: 1586112601866174457 24/02/26 05:29:01 

INFO Master: 133.186.134.165:53490 got disassociated, removing it. 24/02/26 05:29:17 I
NFO Master: 133.186.134.165:53640 got disassociated, removing it. 24/02/26 05:30:19 
WARN TransportChannelHandler: Exception in connection from /218.51.176.155:62574 java.lang.IllegalArgumentException:
Too large frame: 1586112602302382074 , . .
```

크기가 너무 커서..
option을 주어 용량을 제한 할 수 있음.

### 옵션 값을 변경 해야 함

- [b] REF
> [spark frame option](https://uncle-bae.blogspot.com/2016/05/spark-spark-install-guide-and.html)

> docker-compose.yaml
```yaml
services:
  spark:
    environment:
     - SPARK_MASTER_OPTS="-Dspark.rpc.message.maxSize=512"  # add 

  spark-worker:
    environment:
      - SPARK_WORKER_OPTS="-Dspark.rpc.message.maxSize=512"    # add
```

> logs

- Master 
```bash
24/02/26 05:48:16 INFO Utils: Successfully started service 'sparkMaster' on port 7077.
24/02/26 05:48:16 INFO Master: Starting Spark master at spark://a37c1b207dd4:7077
24/02/26 05:48:16 INFO Master: Running Spark version 3.3.0
24/02/26 05:48:16 INFO Utils: Successfully started service 'MasterUI' on port 8080.
24/02/26 05:48:16 INFO MasterWebUI: Bound MasterWebUI to 0.0.0.0, and started at http://a37c1b207dd4:8080
24/02/26 05:48:17 INFO Master: I have been elected leader! New state: ALIVE
24/02/26 05:48:17 INFO Master: Registering worker 172.20.0.2:37495 with 1 cores, 1024.0 MiB RAM

```

- worker 
```bash
24/02/26 05:48:16 INFO ResourceUtils: ==============================================================
24/02/26 05:48:16 INFO ResourceUtils: No custom resources configured for spark.worker.
24/02/26 05:48:16 INFO ResourceUtils: ==============================================================
24/02/26 05:48:16 INFO Utils: Successfully started service 'WorkerUI' on port 8081.
24/02/26 05:48:16 INFO WorkerWebUI: Bound WorkerWebUI to 0.0.0.0, and started at http://bami-cluster2:8081
24/02/26 05:48:16 INFO Worker: Connecting to master bami-cluster2:7077...
24/02/26 05:48:16 INFO TransportClientFactory: Successfully created connection to bami-cluster2/133.186.134.165:7077 after 104 ms (0 ms spent in bootstraps)
24/02/26 05:48:17 INFO Worker: Successfully registered with master spark://a37c1b207dd4:7077
```

### 정상적인(❌틀림) 로그 확인 후 통신 체크 👍->👎

~~> spark -> kafka~~ 

> ❓말이 안되잖아... !!! spark에서 spark 로그를 던지고있음;

```bash
I have no name!@a37c1b207dd4:/opt/bitnami/spark$ nc -vz 133.186.134.165 7077
Connection to 133.186.134.165 7077 port [tcp/*] succeeded!
```

*결론은 Frame이 너무 커서 Spark Master가 제대로 동작 되지 않았고 그래서 Response 할 반응이 없었던 것.*


# 연동

*kafka*
1. topic
```bash
kafka-console-producer --topic spark-topic --bootstrap-server broker:9092
```

*spark*

```python
from pyspark.sql import SparkSession
from pyspark.sql.types import StringType, StructField, StructType, ArrayType, LongType

spark = SparkSession \
    .builder \
    .appName("Streaming from Kafka") \
    .config("spark.streaming.stopGracefullyOnShutdown", True) \
    .config('spark.jars.packages', 'org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0') \
    .config("spark.sql.shuffle.partitions", 4) \
    .master("bami-cluster2") \
    .getOrCreate()
```

> output
```bash
org.apache.spark#spark-sql-kafka-0-10_2.13 added as a dependency
:: resolving dependencies :: org.apache.spark#spark-submit-parent-17f994c4-d2fe-4f7e-b5f0-898c71f6a1aa;1.0
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
	[SUCCESSFUL ] org.apache.spark#spark-sql-kafka-0-10_2.13;3.4.0!spark-sql-kafka-0-10_2.13.jar (434ms)
downloading https://repo1.maven.org/maven2/org/apache/spark/spark-token-provider-kafka-0-10_2.13/3.4.0/spark-token-provider-kafka-0-10_2.13-3.4.0.jar ...
	[SUCCESSFUL ] org.apache.spark#spark-token-provider-kafka-0-10_2.13;3.4.0!spark-token-provider-kafka-0-10_2.13.jar (257ms)
downloading https://repo1.maven.org/maven2/org/scala-lang/modules/scala-parallel-collections_2.13/1.0.4/scala-parallel-collections_2.13-1.0.4.jar ...
	[SUCCESSFUL ] org.scala-lang.modules#scala-parallel-collections_2.13;1.0.4!scala-parallel-collections_2.13.jar (412ms)
downloading https://repo1.maven.org/maven2/org/apache/kafka/kafka-clients/3.3.2/kafka-clients-3.3.2.jar ...
	[SUCCESSFUL ] org.apache.kafka#kafka-clients;3.3.2!kafka-clients.jar (507ms)
downloading https://repo1.maven.org/maven2/com/google/code/findbugs/jsr305/3.0.0/jsr305-3.0.0.jar ...
	[SUCCESSFUL ] com.google.code.findbugs#jsr305;3.0.0!jsr305.jar (251ms)
downloading https://repo1.maven.org/maven2/org/apache/commons/commons-pool2/2.11.1/commons-pool2-2.11.1.jar ...
	[SUCCESSFUL ] org.apache.commons#commons-pool2;2.11.1!commons-pool2.jar (259ms)
downloading https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-client-runtime/3.3.4/hadoop-client-runtime-3.3.4.jar ...
	[SUCCESSFUL ] org.apache.hadoop#hadoop-client-runtime;3.3.4!hadoop-client-runtime.jar (1515ms)
downloading https://repo1.maven.org/maven2/org/lz4/lz4-java/1.8.0/lz4-java-1.8.0.jar ...
	[SUCCESSFUL ] org.lz4#lz4-java;1.8.0!lz4-java.jar (263ms)
downloading https://repo1.maven.org/maven2/org/xerial/snappy/snappy-java/1.1.9.1/snappy-java-1.1.9.1.jar ...
	[SUCCESSFUL ] org.xerial.snappy#snappy-java;1.1.9.1!snappy-java.jar(bundle) (286ms)
downloading https://repo1.maven.org/maven2/org/slf4j/slf4j-api/2.0.6/slf4j-api-2.0.6.jar ...
	[SUCCESSFUL ] org.slf4j#slf4j-api;2.0.6!slf4j-api.jar (253ms)
downloading https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-client-api/3.3.4/hadoop-client-api-3.3.4.jar ...
	[SUCCESSFUL ] org.apache.hadoop#hadoop-client-api;3.3.4!hadoop-client-api.jar (1012ms)
downloading https://repo1.maven.org/maven2/commons-logging/commons-logging/1.1.3/commons-logging-1.1.3.jar ...
	[SUCCESSFUL ] commons-logging#commons-logging;1.1.3!commons-logging.jar (254ms)
:: resolution report :: resolve 16074ms :: artifacts dl 5725ms
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
:: retrieving :: org.apache.spark#spark-submit-parent-17f994c4-d2fe-4f7e-b5f0-898c71f6a1aa
	confs: [default]
	12 artifacts copied, 0 already retrieved (57458kB/88ms)
24/02/26 06:10:51 WARN NativeCodeLoader: Unable to load native-hadoop library for your platform... using builtin-java classes where applicable
Setting default log level to "WARN".
To adjust logging level use sc.setLogLevel(newLevel). For SparkR, use setLogLevel(newLevel).

```

*spark*

```python
streaming_df = spark.read\
    .format("kafka") \
    .option("kafka.bootstrap.servers", "133.186.134.165:19092") \
    .option("subscribe", "spark-topic") \
    .option("startingOffsets", "earliest") \
    .load()

streaming_df.printSchema()
streaming_df.show(truncate=False)
```

### error: java.lang.NoClassDefFoundError: org/apache/commons/pool2/impl/GenericKeyedObjectPoolConfig

*spark*
```python
from pyspark.sql import SparkSession
from pyspark.sql.types import StringType, StructField, StructType, ArrayType, LongType

spark = SparkSession \
    .builder \
    .appName("Streaming from Kafka") \
    .config("spark.streaming.stopGracefullyOnShutdown", True) \
    .config('spark.jars.packages', 'org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0') \
    .config("spark.sql.shuffle.partitions", 4) \
    .master("local[*]") \
    .getOrCreate()
```

```python
# Create a static DataFrame to read data from Kafka
streaming_df = spark.read \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "133.186.134.165:19092") \
    .option("subscribe", "spark-topic") \
    .option("startingOffsets", "earliest") \
    .load()

# Print the schema of the static DataFrame
streaming_df.printSchema()

# Display a few records from the static DataFrame
streaming_df.show(truncate=False)

```

### 🔑 Jar 파일 추가 (Dockerfile)

jar 파일을 보니 common-pool 1밖에 없어서 2 를 찾아 다운 받은 후 컨테이너를 다시 만들었다.

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

RUN curl -o /opt/bitnami/spark/jars/commons-pool2-2.11.0.jar https://repo1.maven.org/maven2/org/apache/commons/commons-pool2/2.11.0/commons-pool2-2.11.0.jar

RUN pip install py4j==0.10.9.5

USER 1001
```

> output 

```bash
root
 |-- key: binary (nullable = true)
 |-- value: binary (nullable = true)
 |-- topic: string (nullable = true)
 |-- partition: integer (nullable = true)
 |-- offset: long (nullable = true)
 |-- timestamp: timestamp (nullable = true)
 |-- timestampType: integer (nullable = true)

+----+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-----------+---------+------+-----------------------+-------------+
|key |value                                                                                                                        |topic      |partition|offset|timestamp              |timestampType|
+----+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-----------+---------+------+-----------------------+-------------+
|null|[7B 22 65 76 65 6E 74 49 64 22 3A 20 22 65 33 63 62 32 36 64 33 2D 34 31 62 32 2D 34 39 61 32 2D 38 34 66 33 2D 30 31 35 36 65 64 38 64 37 35 30 32 22 2C 20 22 65 76 65 6E 74 4F 66 66 73 65 74 22 3A 20 31 30 30 30 31 2C 20 22 65 76 65 6E 74 50 75 62 6C 69 73 68 65 72 22 3A 20 22 64 65 76 69 63 65 22 2C 20 22 63 75 73 74 6F 6D 65 72 49 64 22 3A 20 22 43 49 30 3031 30 33 22 2C 20 22 64 61 74 61 22 3A 20 7B 22 64 65 76 69 63 65 73 22 3A 20 5B 7B 22 64 65 76 69 63 65 49 64 22 3A 20 22 44 30 30 31 22 2C 20 22 74 65 6D 70 65 72 61 74 75 72 65 22 3A 20 31 35 2C 20 22 6D 65 61 73 75 72 65 22 3A 20 22 43 22 2C 20 22 73 74 61 74 75 73 22 3A 20 22 45 52 52 4F 52 22 7D 2C 20 7B 22 64 65 76 69 63 65 49 64 22 3A 20 22 44 30 30 32 22 2C 20 22 74 65 6D 70 65 72 61 74 75 72 65 22 3A 20 31 36 2C 20 22 6D 65 61 73 75 72 65 22 3A 20 22 43 22 2C 20 22 73 74 61 74 75 73 22 3A 20 22 53 55 43 43 45 53 53 22 7D 5D 7D 2C 20 22 6576 65 6E 74 54 69 6D 65 22 3A 20 22 32 30 32 33 2D 30 31 2D 30 35 20 31 31 3A 31 33 3A 35 33 2E 36 34 33 33 36 34 22 7D]|spark-topic|0        |0     |2024-02-26 06:09:53.129|0  |
|null|[7B 22 65 76 65 6E 74 49 64 22 3A 20 22 65 33 63 62 32 36 64 33 2D 34 31 62 32 2D 34 39 61 32 2D 38 34 66 33 2D 30 31 35 36 65 64 38 64 37 35 30 32 22 2C 20 22 65 76 65 6E 74 4F 66 66 73 65 74 22 3A 20 31 30 30 30 31 2C 20 22 65 76 65 6E 74 50 75 62 6C 69 73 68 65 72 22 3A 20 22 64 65 76 69 63 65 22 2C 20 22 63 75 73 74 6F 6D 65 72 49 64 22 3A 20 22 43 49 30 3031 30 33 22 2C 20 22 64 61 74 61 22 3A 20 7B 22 64 65 76 69 63 65 73 22 3A 20 5B 7B 22 64 65 76 69 63 65 49 64 22 3A 20 22 44 30 30 31 22 2C 20 22 74 65 6D 70 65 72 61 74 75 72 65 22 3A 20 31 35 2C 20 22 6D 65 61 73 75 72 65 22 3A 20 22 43 22 2C 20 22 73 74 61 74 75 73 22 3A 20 22 45 52 52 4F 52 22 7D 2C 20 7B 22 64 65 76 69 63 65 49 64 22 3A 20 22 44 30 30 32 22 2C 20 22 74 65 6D 70 65 72 61 74 75 72 65 22 3A 20 31 36 2C 20 22 6D 65 61 73 75 72 65 22 3A 20 22 43 22 2C 20 22 73 74 61 74 75 73 22 3A 20 22 53 55 43 43 45 53 53 22 7D 5D 7D 2C 20 22 6576 65 6E 74 54 69 6D 65 22 3A 20 22 32 30 32 33 2D 30 31 2D 30 35 31 31 3A 31 33 3A 35 33 2E 36 34 33 33 36 34 22 7D]   |spark-topic|0        |1     |2024-02-26 06:59:10.056|0  |
|null|[7B 22 65 76 65 6E 74 49 64 22 3A 20 22 65 33 63 62 32 36 64 33 2D 34 31 62 32 2D 34 39 61 32 2D 38 34 66 33 2D 30 31 35 36 65 64 38 64 37 35 30 32 22 2C 20 22 65 76 65 6E 74 4F 66 66 73 65 74 22 3A 20 31 30 30 30 31 2C 20 22 65 76 65 6E 74 50 75 62 6C 69 73 68 65 72 22 3A 20 22 64 65 76 69 63 65 22 2C 20 22 63 75 73 74 6F 6D 65 72 49 64 22 3A 20 22 43 49 30 3031 30 33 22 2C 20 22 64 61 74 61 22 3A 20 7B 22 64 65 76 69 63 65 73 22 3A 20 5B 7B 22 64 65 76 69 63 65 49 64 22 3A 20 22 44 30 30 31 22 2C 20 22 74 65 6D 70 65 72 61 74 75 72 65 22 3A 20 31 35 2C 20 22 6D 65 61 73 75 72 65 22 3A 20 22 43 22 2C 20 22 73 74 61 74 75 73 22 3A 20 22 45 52 52 4F 52 22 7D 2C 20 7B 22 64 65 76 69 63 65 49 64 22 3A 20 22 44 30 30 32 22 2C 20 22 74 65 6D 70 65 72 61 74 75 72 65 22 3A 20 31 36 2C 20 22 6D 65 61 73 75 72 65 22 3A 20 22 43 22 2C 20 22 73 74 61 74 75 73 22 3A 20 22 53 55 43 43 45 53 53 22 7D 5D 7D 2C 20 22 6576 65 6E 74 54 69 6D 65 22 3A 20 22 32 30 32 33 2D 30 31 2D 30 35 31 31 3A 31 33 3A 35 33 2E 36 34 33 33 36 34 22 7D]   |spark-topic|0        |2     |2024-02-26 06:59:11.871|0  |
|null|[7B 22 65 76 65 6E 74 49 64 22 3A 20 22 65 33 63 62 32 36 64 33 2D 34 31 62 32 2D 34 39 61 32 2D 38 34 66 33 2D 30 31 35 36 65 64 38 64 37 35 30 32 22 2C 20 22 65 76 65 6E 74 4F 66 66 73 65 74 22 3A 20 31 30 30 30 31 2C 20 22 65 76 65 6E 74 50 75 62 6C 69 73 68 65 72 22 3A 20 22 64 65 76 69 63 65 22 2C 20 22 63 75 73 74 6F 6D 65 72 49 64 22 3A 20 22 43 49 30 3031 30 33 22 2C 20 22 64 61 74 61 22 3A 20 7B 22 64 65 76 69 63 65 73 22 3A 20 5B 7B 22 64 65 76 69 63 65 49 64 22 3A 20 22 44 30 30 31 22 2C 20 22 74 65 6D 70 65 72 61 74 75 72 65 22 3A 20 31 35 2C 20 22 6D 65 61 73 75 72 65 22 3A 20 22 43 22 2C 20 22 73 74 61 74 75 73 22 3A 20 22 45 52 52 4F 52 22 7D 2C 20 7B 22 64 65 76 69 63 65 49 64 22 3A 20 22 44 30 30 32 22 2C 20 22 74 65 6D 70 65 72 61 74 75 72 65 22 3A 20 31 36 2C 20 22 6D 65 61 73 75 72 65 22 3A 20 22 43 22 2C 20 22 73 74 61 74 75 73 22 3A 20 22 53 55 43 43 45 53 53 22 7D 5D 7D 2C 20 22 6576 65 6E 74 54 69 6D 65 22 3A 20 22 32 30 32 33 2D 30 31 2D 30 35 31 31 3A 31 33 3A 35 33 2E 36 34 33 33 36 34 22 7D]   |spark-topic|0        |3     |2024-02-26 06:59:12.843|0  |
|null|[7B 22 65 76 65 6E 74 49 64 22 3A 20 22 65 33 63 62 32 36 64 33 2D 34 31 62 32 2D 34 39 61 32 2D 38 34 66 33 2D 30 31 35 36 65 64 38 64 37 35 30 32 22 2C 20 22 65 76 65 6E 74 4F 66 66 73 65 74 22 3A 20 31 30 30 30 31 2C 20 22 65 76 65 6E 74 50 75 62 6C 69 73 68 65 72 22 3A 20 22 64 65 76 69 63 65 22 2C 20 22 63 75 73 74 6F 6D 65 72 49 64 22 3A 20 22 43 49 30 3031 30 33 22 2C 20 22 64 61 74 61 22 3A 20 7B 22 64 65 76 69 63 65 73 22 3A 20 5B 7B 22 64 65 76 69 63 65 49 64 22 3A 20 22 44 30 30 31 22 2C 20 22 74 65 6D 70 65 72 61 74 75 72 65 22 3A 20 31 35 2C 20 22 6D 65 61 73 75 72 65 22 3A 20 22 43 22 2C 20 22 73 74 61 74 75 73 22 3A 20 22 45 52 52 4F 52 22 7D 2C 20 7B 22 64 65 76 69 63 65 49 64 22 3A 20 22 44 30 30 32 22 2C 20 22 74 65 6D 70 65 72 61 74 75 72 65 22 3A 20 31 36 2C 20 22 6D 65 61 73 75 72 65 22 3A 20 22 43 22 2C 20 22 73 74 61 74 75 73 22 3A 20 22 53 55 43 43 45 53 53 22 7D 5D 7D 2C 20 22 6576 65 6E 74 54 69 6D 65 22 3A 20 22 32 30 32 33 2D 30 31 2D 30 35 31 31 3A 31 33 3A 35 33 2E 36 34 33 33 36 34 22 7D]   |spark-topic|0        |4     |2024-02-26 06:59:13.75 |0  |
+----+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-----------+---------+------+-----------------------+-------------+

```

그러니까 넘어갔다..

*spark*

json으로 바꿔주는 코드를 추가한다.

```python
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

kafka-console-producer --topic devices --bootstrap-server broker:9092


{"eventId": "e3cb26d3-41b2-49a2-84f3-0156ed8d7502", "eventOffset": 10001, "eventPublisher": "device", "customerId": "CI00104", "data": {"devices": [{"deviceId": "D001", "temperature": 15, "measure": "C", "status": "ERROR"}, {"deviceId": "D002", "temperature": 16, "measure": "C", "status": "SUCCESS"}]}, "eventTime": "2023-01-0511:13:53.643364"}

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
      KAFKA_ADVERTISED_LISTENERS: 'INTERNAL://broker:9092,EXTERNAL://133.186.134.165:19092'
      KAFKA_INTER_BROKER_LISTENER_NAME: INTERNAL
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_TRANSACTION_STATE_LOG_MIN_ISR: 1
      KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 1
      KAFKA_GROUP_INITIAL_REBALANCE_DELAY_MS: 0
    networks:
      - common-network

```

```bash
docker network create common-network
```

 성공 해버린 파이선 코드 ;;
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
    "kafka.bootstrap.servers": "133.186.134.165:19092",
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


# Kafka to Spark


> kafka 

```bash
[appuser@broker ~]$ kafka-console-producer --topic devices --bootstrap-server broker:9092
>{"eventId": "e3cb26d3-41b2-49a2-84f3-0156ed8d7502", "eventOffset": 10001, "eventPublisher": "device", "customerId": "CI00103", "data": {"devices": [{"deviceId": "D001", "temperature": 15, "measure": "C", "status": "ERROR"}, {"deviceId": "D002", "temperature": 16, "measure": "C", "status": "SUCCESS"}]}, "eventTime": "2023-01-0511:13:53.643364"}
[2024-02-26 08:49:39,817] WARN [Producer clientId=console-producer] Error while fetching metadata with correlation id 3 : {devices=LEADER_NOT_AVAILABLE} (org.apache.kafka.clients.NetworkClient)
>^C[appuser@broker ~]$ kafka-console-producer --topic devices --bootstrap-server broker:9092
>{"eventId": "e3cb26d3-41b2-49a2-84f3-0156ed8d7502", "eventOffset": 10001, "eventPublisher": "device", "customerId": "CI00104", "data": {"devices": [{"deviceId": "D001", "temperature": 15, "measure": "C", "status": "ERROR"}, {"deviceId": "D002", "temperature": 16, "measure": "C", "status": "SUCCESS"}]}, "eventTime": "2023-01-0511:13:53.643364"}
>^C[appuser@broker ~]$
[appuser@broker ~]$
[appuser@broker ~]$ kafka-console-producer --topic devices --bootstrap-server broker:9092
>{"eventId": "e3cb26d3-41b2-49a2-84f3-0156ed8d7502", "eventOffset": 10001, "eventPublisher": "device", "customerId": "CI00104", "data": {"devices": [{"deviceId": "D001", "temperature": 15, "measure": "C", "status": "ERROR"}, {"deviceId": "D002", "temperature": 16, "measure": "C", "status": "SUCCESS"}]}, "eventTime": "2023-01-0511:13:53.643364"}
>{"eventId": "e3cb26d3-41b2-49a2-84f3-0156ed8d7502", "eventOffset": 10001, "eventPublisher": "device", "customerId": "CI00104", "data": {"devices": [{"deviceId": "D001", "temperature": 15, "measure": "C", "status": "ERROR"}, {"deviceId": "D002", "temperature": 16, "measure": "C", "status": "SUCCESS"}]}, "eventTime": "2023-01-0511:13:53.643364"}
>
>{"eventId": "e3cb26d3-41b2-49a2-84f3-0156ed8d7502", "eventOffset": 10001, "eventPublisher": "device", "customerId": "CI00104", "data": {"devices": [{"deviceId": "D001", "temperature": 15, "measure": "C", "status": "ERROR"}, {"deviceId": "D002", "temperature": 16, "measure": "C", "status": "SUCCESS"}]}, "eventTime": "2023-01-0511:13:53.643364"}
>{"eventId": "e3cb26d3-41b2-49a2-84f3-0156ed8d7502", "eventOffset": 10001, "eventPublisher": "device", "customerId": "CI00104", "data": {"devices": [{"deviceId": "D001", "temperature": 15, "measure": "C", "status": "ERROR"}, {"deviceId": "D002", "temperature": 16, "measure": "C", "status": "SUCCESS"}]}, "eventTime": "2023-01-0511:13:53.643364"}
>{"eventId": "e3cb26d3-41b2-49a2-84f3-0156ed8d7502", "eventOffset": 10001, "eventPublisher": "device", "customerId": "CI00104", "data": {"devices": [{"deviceId": "D001", "temperature": 15, "measure": "C", "status": "ERROR"}, {"deviceId": "D002", "temperature": 16, "measure": "C", "status": "SUCCESS"}]}, "eventTime": "2023-01-0511:13:53.643364"}
>{"eventId": "e3cb26d3-41b2-49a2-84f3-0156ed8d7502", "eventOffset": 10001, "eventPublisher": "device", "customerId": "CI00104", "data": {"devices": [{"deviceId": "D001", "temperature": 15, "measure": "C", "status": "ERROR"}, {"deviceId": "D002", "temperature": 16, "measure": "C", "status": "SUCCESS"}]}, "eventTime": "2023-01-0511:13:53.643364"}
>{"eventId": "e3cb26d3-41b2-49a2-84f3-0156ed8d7502", "eventOffset": 10001, "eventPublisher": "device", "customerId": "CI00104", "data": {"devices": [{"deviceId": "D001", "temperature": 15, "measure": "C", "status": "ERROR"}, {"deviceId": "D002", "temperature": 16, "measure": "C", "status": "SUCCESS"}]}, "eventTime": "2023-01-0511:13:53.643364"}
>{"eventId": "e3cb26d3-41b2-49a2-84f3-0156ed8d7502", "eventOffset": 10001, "eventPublisher": "device", "customerId": "CI00104", "data": {"devices": [{"deviceId": "D001", "temperature": 15, "measure": "C", "status": "ERROR"}, {"deviceId": "D002", "temperature": 16, "measure": "C", "status": "SUCCESS"}]}, "eventTime": "2023-01-0511:13:53.643364"}
>^C[appuser@broker ~]$

```

> spark


```bash
-------------------------------------------
Batch: 1
-------------------------------------------
+--------------------+-----------+--------------+----------+--------------------+--------------------+
|             eventId|eventOffset|eventPublisher|customerId|                data|           eventTime|
+--------------------+-----------+--------------+----------+--------------------+--------------------+
|e3cb26d3-41b2-49a...|      10001|        device|   CI00104|{[{D001, 15, C, E...|2023-01-0511:13:5...|
|                null|       null|          null|      null|                null|                null|
+--------------------+-----------+--------------+----------+--------------------+--------------------+

-------------------------------------------
Batch: 2
-------------------------------------------
+--------------------+-----------+--------------+----------+--------------------+--------------------+
|             eventId|eventOffset|eventPublisher|customerId|                data|           eventTime|
+--------------------+-----------+--------------+----------+--------------------+--------------------+
|e3cb26d3-41b2-49a...|      10001|        device|   CI00104|{[{D001, 15, C, E...|2023-01-0511:13:5...|
+--------------------+-----------+--------------+----------+--------------------+--------------------+

-------------------------------------------
Batch: 3
-------------------------------------------
+--------------------+-----------+--------------+----------+--------------------+--------------------+
|             eventId|eventOffset|eventPublisher|customerId|                data|           eventTime|
+--------------------+-----------+--------------+----------+--------------------+--------------------+
|e3cb26d3-41b2-49a...|      10001|        device|   CI00104|{[{D001, 15, C, E...|2023-01-0511:13:5...|
+--------------------+-----------+--------------+----------+--------------------+--------------------+

-------------------------------------------
Batch: 4
-------------------------------------------
+--------------------+-----------+--------------+----------+--------------------+--------------------+
|             eventId|eventOffset|eventPublisher|customerId|                data|           eventTime|
+--------------------+-----------+--------------+----------+--------------------+--------------------+
|e3cb26d3-41b2-49a...|      10001|        device|   CI00104|{[{D001, 15, C, E...|2023-01-0511:13:5...|
+--------------------+-----------+--------------+----------+--------------------+--------------------+

-------------------------------------------
Batch: 5
-------------------------------------------
+--------------------+-----------+--------------+----------+--------------------+--------------------+
|             eventId|eventOffset|eventPublisher|customerId|                data|           eventTime|
+--------------------+-----------+--------------+----------+--------------------+--------------------+
|e3cb26d3-41b2-49a...|      10001|        device|   CI00104|{[{D001, 15, C, E...|2023-01-0511:13:5...|
+--------------------+-----------+--------------+----------+--------------------+--------------------+

-------------------------------------------
Batch: 6
-------------------------------------------
+--------------------+-----------+--------------+----------+--------------------+--------------------+
|             eventId|eventOffset|eventPublisher|customerId|                data|           eventTime|
+--------------------+-----------+--------------+----------+--------------------+--------------------+
|e3cb26d3-41b2-49a...|      10001|        device|   CI00104|{[{D001, 15, C, E...|2023-01-0511:13:5...|
+--------------------+-----------+--------------+----------+--------------------+--------------------+

-------------------------------------------
Batch: 7
-------------------------------------------
+--------------------+-----------+--------------+----------+--------------------+--------------------+
|             eventId|eventOffset|eventPublisher|customerId|                data|           eventTime|
+--------------------+-----------+--------------+----------+--------------------+--------------------+
|e3cb26d3-41b2-49a...|      10001|        device|   CI00104|{[{D001, 15, C, E...|2023-01-0511:13:5...|
+--------------------+-----------+--------------+----------+--------------------+--------------------+


```