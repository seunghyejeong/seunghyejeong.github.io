---
title: Install Spark in Local
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
> [scala,spark,maven 설치(linux환경)](https://it-sunny-333.tistory.com/10)
> [spark consumer로 활용하기](https://taaewoo.tistory.com/32)
> [spark 간단 구축하기](https://ampersandor.tistory.com/11)
> [HDFS에 데이터 구축하기(origins)](https://taaewoo.tistory.com/32?category=887744)



# Docker build

1. java
```bash
sudo apt install openjdk-17-jdk
```


2. scala , spark 설치 후 환경 변수 설정 

> 설치
```bash
wget https://www.apache.org/dyn/closer.lua/spark/spark-3.4.2/spark-3.4.2-bin-hadoop3-scala2.13.tgz
```

```bash
tar xvf spark-3.4.2-bin-hadoop3-scala2.13.tgz
sudo mv ./spark-3.4.2-bin-hadoop3-scala2.13.tgz /opt/spark
```

>환경 변수

```bash
$ vim ~/.bashrc
export SPARK_HOME=/opt/spark  
export PATH=$PATH:$SPARK_HOME/bin:$SPARK_HOME/sbin
source ~/.bashrc
```

```bash
docker build -t spark:3.4.2 -f kubernetes/dockerfiles/spark/Dockerfile .
```

## Custom Dockerfile

### 1차 시도: Spark 공식 Docs에 있는 이미지를 받아와 만들었다. 

> Dockerfile
```Dockerfile
version: "3.5"
services:
  spark-master:
    image: spark:3.4.2
    ports:
      - "9090:8080"
      - "7077:7077"
    volumes:
       - ./jars:/opt/jars
       - ./data:/opt/data
    environment:
      - SPARK_MASTER_HOST="spark://spark-master:7077" 
      - SPARK_MASTER_WEBUI_PORT=8080 
      - SPARK_PUBLIC_DNS={MASTER_IP}
      - SPARK_LOCAL_IP=172.16.11.59
      - SPARK_LOG_DIR=/opt/spark/logs
```

> spark default conf
```sh
spark.master                     spark://master:7077
spark.eventLog.enabled           true
spark.eventLog.dir               hdfs://namenode:8021/directory
spark.serializer                 org.apache.spark.serializer.KryoSerializer
spark.driver.memory              5g
spark.executor.extraJavaOptions  -XX:+PrintGCDetails -Dkey=value -Dnumbers="one two three"
```

> spark env
```sh
SPARK_MASTER_PORT=7077 \  
SPARK_MASTER_WEBUI_PORT=8080 \  
SPARK_LOG_DIR=/opt/spark/logs \  
SPARK_WORKER_WEBUI_PORT=8080 \  
SPARK_WORKER_PORT=7000 \  
SPARK_MASTER_HOST="spark://spark-master:7077" 
SPARK_LOCAL_IP, to set the IP address Spark binds to on this node
SPARK_PUBLIC_DNS, to set the public DNS name of the driver program

```

> [!fail] 
> 이 도커파일에는 spark-worker가 없다. 그리고 굳이 필요 없는 환경 변수 값을 넣었다. docker compose의 enviroment를 설정 했으면 default conf, spark env를 설정 할 필요 없다.



# ❌❌❌❌❌StandAlone

```bash
./sbin/start-worker.sh 133.186.217.113:8080
```

spark://bami-cluster2.novalocal:7077

https://taaewoo.tistory.coㅋㅌㅊ 퓨m/18?category=887744
'
akfhrmpTd미ㅏㄹ얼미ㅏ넝ㄹ니ㅏㅇ'ㅓㄹ

접속하면 되기는 한데;


# docker comp ose by bitnami

```dockerfile
# Copyright VMware, Inc.
# SPDX-License-Identifier: APACHE-2.0

version: '2'

services:
  spark:
    image: docker.io/bitnami/spark:3.4.2
    environment:
      - SPARK_MODE=master
      - SPARK_RPC_AUTHENTICATION_ENABLED=no
      - SPARK_RPC_ENCRYPTION_ENABLED=no
      - SPARK_LOCAL_STORAGE_ENCRYPTION_ENABLED=no
      - SPARK_SSL_ENABLED=no
      - SPARK_USER=spark
    ports:
      - '8080:8080'
  spark-worker:
    image: docker.io/bitnami/spark:3.4.2
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

# 최종 Dockerfile 

> kafka , image를 사용하기 위해서는 ,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,, image를 따로 만들어야하나 ..................................................................모르겠어 

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

```

```
docker build --no-cache -t seunghyejeong/spark:1.0 .
docker push seunghyejeong/spark:1.0
```

>docker compose.yaml
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

133.186.217.113:19092
spark://spark:7077

spark-sql_2.12-3.4.2.jar
spark-sql-kafka-0-10_2.13-3.4.2.jar
./spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.13:3.4.2 consume_topic.py 

```python
# consume_topic.py
 
from pyspark.sql import SparkSession
 
sc = SparkSession.builder.getOrCreate()
 
sc.sparkContext.setLogLevel('ERROR')
 
# Read stream
log = sc.readStream.format("kafka") \
.option("kafka.bootstrap.servers", "133.186.217.113:19092") \
.option("subscribe", "test1") \
.option("startingOffsets", "earliest") \
.load()
 
# Write stream - console
query = log.selectExpr("CAST(value AS STRING)") \
.writeStream \
.format("console") \
.option("truncate", "false") \
.start()
 
# Write stream - HDFS
query2 = log.selectExpr("CAST(value AS STRING)") \
.writeStream \
.format("parquet") \
.outputMode("append") \
.option("checkpointLocation", "/check") \
.option("path", "/test") \
.start()
 
query.awaitTermination()
query2.awaitTermination()

```