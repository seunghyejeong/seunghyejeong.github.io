---
title: The long adventure to success Pipeline...4) going to be crazy. Spakr is already exsist on Docker!
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


Docker image
spark 1:0
kafka 1:0
airflow 2.0

openjdk-8-jdk

자바를 수동으로 설치.. 

# Airflow 설치 

```dockerfile
FROM apache/airflow:2.8.1

ENV AIRFLOW_HOME=/home/airflow/.local
ENV JAVA_HOME=/usr/lib/jvm/jdk1.8.0_401
ENV SPARK_HOME=/home/airflow/.local/assembly/target/scala-2.12
ENV PATH="$PATH:${AIRFLOW_HOME}/bin:${JAVA_HOME}/bin:${SPARK_HOME}/bin"

USER root

RUN mkdir /usr/lib/jvm

COPY jdk-1.8.tar.gz /opt/airflow
RUN tar xvf jdk-1.8.tar.gz /usr/lib/jvm \
&& rm jdk-1.8.tar.gz

COPY requirements.txt /

RUN apt-get update \
  && apt-get install -y --no-install-recommends \
        vim \
        openjdk-8-jdk \
        wget \
        net-tools \
        dnsutils \
        iputils-ping \
        netcat \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/airflow/.local/assembly/target 

RUN wget https://archive.apache.org/dist/spark/spark-3.3.0/spark-3.3.0-bin-hadoop3-scala2.13.tgz && \
    tar xvf spark-3.3.0-bin-hadoop3-scala2.13.tgz --transform='s,^spark-3.3.0-bin-hadoop3-scala2.13,scala-2.12,' -C /home/airflow/.local/assembly/target && \
    rm spark-3.3.0-bin-hadoop3-scala2.13.tgz \ 

RUN curl -o /home/airflow/.local/assembply/target/jars/kafka-clients-3.3.0.jar https://repo1.maven.org/maven2/org/apache/kafka/kafka-clients/3.3.0/kafka-clients-3.3.0.jar

# Download Spark Kafka connector JAR
RUN curl -o /home/airflow/.local/assembply/target/jars/spark-token-provider-kafka-0-10_2.13-3.3.0.jar https://repo1.maven.org/maven2/org/apache/spark/spark-token-provider-kafka-0-10_2.13/3.3.0/spark-token-provider-kafka-0-10_2.13-3.3.0.jar

# Download Spark SQL Kafka connector JAR
RUN curl -o /home/airflow/.local/assembply/target/jars/spark-sql-kafka-0-10_2.12-3.3.0.jar https://repo1.maven.org/maven2/org/apache/spark/spark-sql-kafka-0-10_2.13/3.3.0/spark-sql-kafka-0-10_2.13-3.3.0.jar

RUN curl -o /home/airflow/.local/assembply/target/jars/commons-pool2-2.11.0.jar https://repo1.maven.org/maven2/org/apache/commons/commons-pool2/2.11.0/commons-pool2-2.11.0.jar

USER airflow

COPY requirements.txt /
RUN pip install --no-cache-dir "apache-airflow==2.8.1" -r /requirements.txt
```

```txt
pandas~=2.0.3
requests~=2.31.0
selenium~=4.17.2
beautifulsoup4~=4.12.3
lxml~=5.1.0
virtualenv
kafka-python~=2.0.2
apache-airflow-providers-apache-kafka~=1.3.1
confluent-kafka~=2.3.0
apache-airflow-providers-apache-spark[cncf.kubernetes]
py4j==0.10.9.5
pyspark
grpcio-status>=1.59.0
```


[spark와 airflow의 연결을 확인하는 코드 작성하기]
1. 하나의 파일로만 생성할것 ( 파일을 분리하지 마라 )
2. 네트워크 통신 확인만 하는 간단한 파이선 코드 
3. airflow connections에 정의된 spark 정보를 받아 올 것 

# Spark Connect 코드 
```python
import pyspark
from airflow.providers.apache.spark.hooks.spark_connect import SparkConnectHook

def check_spark_airflow_connection():
    # Load Airflow connections
    airflow_spark_connection = SparkConnectHook.get_connection(conn_id='spark_default')

    if airflow_spark_connection:
        spark_master_url = airflow_spark_connection.host
        spark_app_name = airflow_spark_connection.extra_dejson.get('extra__spark__submit__appName')

        # Check Spark connection
        try:
            spark_session = pyspark.sql.SparkSession.builder \
                .master(spark_master_url) \
                .appName(spark_app_name) \
                .getOrCreate()
            
            spark_context = spark_session.sparkContext
            spark_version = spark_session.version

            print("Successfully connected to Spark!")
            print(f"Spark Version: {spark_version}")
            print(f"Spark Master URL: {spark_master_url}")
            print(f"Spark App Name: {spark_app_name}")

        except Exception as e:
            print("Failed to connect to Spark:", e)

    else:
        print("Spark connection not found in Airflow connections.")

if __name__ == "__main__":
    check_spark_airflow_connection()

```

# 실패 요인 ..
이미 나는 스파크 마스터가 컨테이너로 띄워져 있었기 때문에 생성이 안되는거였다 .ㅋ 
도커로 다른 노드에 스파크를 실행 시켰으면  이미 만들었으면 그 생성된 스파크를 가지고 왔어야 했다
하ㅏㅎ하ㅏㅎㅎㅎㅎㅎㅎㅎㅎㅎㅎㅎㅎㅎㅎㅎㅎㅎㅎㅎㅎㅎㅎㅎㅎㅎㅎㅎㅎㅎㅎㅎㅎㅎㅎㅎㅎㅎㅎㅎㅎㅎㅎㅎㅎㅎㅎㅎㅎ하하ㅏ하하하하하하하하하하핳하ㅏㅏㅏㅏㅏㅏㅏㅏㅏㅏㅏㅏㅏㅏㅏㅏㅏㅏㅏ CRAZY
https://sparkbyexamples.com/pyspark/pyspark-what-is-sparksession/
# 최최최뢰최치최초ㅗ치치ㅗ초초치ㅗ치ㅗ치종

#AIRFLOW_DOCKERFILE 
```dockerfile
FROM apache/airflow:2.8.1

ENV AIRFLOW_HOME=/home/airflow/.local
ENV JAVA_HOME=/usr/lib/jvm/jdk1.8.0_401
ENV SPARK_HOME=/home/airflow/.local/assembly/target/scala-2.12
ENV PATH="$PATH:${AIRFLOW_HOME}/bin:${JAVA_HOME}/bin:${SPARK_HOME}/bin"

USER root

RUN mkdir /usr/lib/jvm

COPY jdk-1.8.tar.gz /opt/airflow
RUN tar xvf jdk-1.8.tar.gz /usr/lib/jvm \
&& rm jdk-1.8.tar.gz

COPY requirements.txt /

RUN apt-get update \
  && apt-get install -y --no-install-recommends \
        vim \
        openjdk-8-jdk \
        wget \
        net-tools \
        dnsutils \
        iputils-ping \
        netcat \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/airflow/.local/assembly/target

RUN wget https://archive.apache.org/dist/spark/spark-3.3.0/spark-3.3.0-bin-hadoop3-scala2.13.tgz && \
    tar xvf spark-3.3.0-bin-hadoop3-scala2.13.tgz --transform='s,^spark-3.3.0-bin-hadoop3-scala2.13,scala-2.12,' -C /home/airflow/.local/assembly/target && \
    rm spark-3.3.0-bin-hadoop3-scala2.13.tgz \

RUN curl -o /home/airflow/.local/assembply/target/jars/kafka-clients-3.3.0.jar https://repo1.maven.org/maven2/org/apache/kafka/kafka-clients/3.3.0/kafka-clients-3.3.0.jar

# Download Spark Kafka connector JAR
RUN curl -o /home/airflow/.local/assembply/target/jars/spark-token-provider-kafka-0-10_2.13-3.3.0.jar https://repo1.maven.org/maven2/org/apache/spark/spark-token-provider-kafka-0-10_2.13/3.3.0/spark-token-provider-kafka-0-10_2.13-3.3.0.jar

# Download Spark SQL Kafka connector JAR
RUN curl -o /home/airflow/.local/assembply/target/jars/spark-sql-kafka-0-10_2.12-3.3.0.jar https://repo1.maven.org/maven2/org/apache/spark/spark-sql-kafka-0-10_2.13/3.3.0/spark-sql-kafka-0-10_2.13-3.3.0.jar

RUN curl -o /home/airflow/.local/assembply/target/jars/commons-pool2-2.11.0.jar https://repo1.maven.org/maven2/org/apache/commons/commons-pool2/2.11.0/commons-pool2-2.11.0.jar

USER airflow

RUN pip install --no-cache-dir "apache-airflow==2.8.1" -r /requirements.txt
```

#REQUIREMENTS
```txt
pandas~=2.0.3
requests~=2.31.0
selenium~=4.17.2
beautifulsoup4~=4.12.3
lxml~=5.1.0
virtualenv
kafka-python~=2.0.2
apache-airflow-providers-apache-kafka~=1.3.1
confluent-kafka~=2.3.0
apache-airflow-providers-apache-spark[cncf.kubernetes]
py4j==0.10.9.5
pyspark
grpcio-status>=1.59.0
```


#SPARK_AIRFLOW_DAG
```python
import pyspark
from pyspark.sql import SparkSession
from airflow.providers.apache.spark.hooks.spark_connect import SparkConnectHook

def check_spark_airflow_connection():
    # Create an instance of the SparkConnectHook
    #spark_hook = SparkConnectHook(conn_id='spark_default')

    # Get the Spark connection information
    #spark_master_url = spark_hook.get_connection_url()

    spark_master_url = "spark://133.186.134.16:7077"
    # Check Spark connection
    try:
        spark_session = SparkSession.builder.getOrCreate()
        print(spark_session)

        spark_context = spark_session.sparkContext
        spark_version = spark_session.version

        print("Successfully connected to Spark!")
        print(f"Spark Version: {spark_version}")
        print(f"Spark Master URL: {spark_master_url}")
       # print(f"Spark App Name: {spark_app_name}")

    except Exception as e:
        print("Failed to connect to Spark:", e)

if __name__ == "__main__":
    check_spark_airflow_connection()
```

# 여기까지 진행 했을 때 
`pyspark` 명령어 및  `spark_submit` 명령어가 *중복* 으로 실행되었다. 
SparkSession으로도 설치가 되고 Airflow에도 설치가 되고 Local에도 설치가 되었기 때문이다.