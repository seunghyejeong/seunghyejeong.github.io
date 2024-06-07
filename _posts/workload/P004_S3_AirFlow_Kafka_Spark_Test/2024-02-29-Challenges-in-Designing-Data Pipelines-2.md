---
title: The long adventure to success Pipeline...2) Rebuild
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

# *Airflow 구축 목적은 한 곳에서 여러 Job을 관리하기 위함*

- [?] 지금까지는 Kafka와 Spark를 테스트 하기 위에서 Cluster2의 각 Container에 접속하여 코드를 실행했음. 그리고 Spark와 Kafka가 잘 연동 되는 것을 확인 후 airflow에 Pipeline을 작성 하려고 하는데 Airflow에서 Spark와 Kafka를 관리 하는 데에서 궁금했던 것이, *Airflow에서 Kafka와 Spark의 코드를 모두 가져와서 실행 하는 건지?* 아니면 *Airflow에서는 실행하라는 명령을 날린 후 Kafka, Spark 각 컨테이너에서 작업을 수행 하는 건지* .. 
- [k] 그러나 담은 전자. 왜냐면 Airflow Pipeline Dag을 작성하는 이유 자체가 하나의 관리 폼에서 여러 Job을 수행하기 위함인 것이고, 유지 보수를 위해서는 무조건 한 곳에서 가능해야 하기 때문, 후자는 유지보수를 하기 위해서는 만약 코드 하나를 바꾸기 위해서 어떤 컨테이너에 접속하여 수정을 한 후 테스트를 해야 하는 번거로움이 있음.  그래서  `Spark`, `Kafka`를 위해 Airflow의 `Dockerfile`, `requirements.txt`를 다시 커스텀 하여 진행 하는것이 *맞음*! 
# Airflow Packaging

## Dockerfile 

```Dockerfile
FROM apache/airflow:2.8.1

RUN echo $PATH
# Set AIRFLOW_HOME environment variable
ENV AIRFLOW_HOME=/home/airflow/.local
# Set JAVA_HOME environment variable
ENV JAVA_HOME=/usr
# Set SPARK_HOME environment variable
ENV SPARK_HOME=/home/airflow/.local
# Set SPARK_HOME enviroment variable
ENV PATH="$PATH:${AIRFLOW_HOME}/bin$:${JAVA_HOME}/bin:${SPARK_HOME}/bin"
RUN echo $PATH

USER root
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
        vim \
        openjdk-17-jdk

RUN cp /etc/hosts /etc/hosts.bak
RUN echo "125.6.40.186 bami-cluster2" >> /etc/hosts

USER airflow
COPY requirements.txt /
RUN pip install --no-cache-dir "apache-airflow==2.8.1" -r /requirements.txt

```

### add
```dockerfile
RUN curl -o /home/ubuntu/kafka-clients-3.3.0.jar https://repo1.maven.org/maven2/org/apache/kafka/kafka-clients/3.3.0/kafka-clients-3.3.0.jar

# Download Spark Kafka connector JAR
RUN curl -o /home/ubuntu/spark-token-provider-kafka-0-10_2.13-3.3.0.jar https://repo1.maven.org/maven2/org/apache/spark/spark-token-provider-kafka-0-10_2.13/3.3.0/spark-token-provider-kafka-0-10_2.13-3.3.0.jar

# Download Spark SQL Kafka connector JAR
RUN curl -o /home/ubuntu/spark-sql-kafka-0-10_2.12-3.3.0.jar https://repo1.maven.org/maven2/org/apache/spark/spark-sql-kafka-0-10_2.13/3.3.0/spark-sql-kafka-0-10_2.13-3.3.0.jar

RUN curl -o/home/ubuntu/commons-pool2-2.11.0.jar https://repo1.maven.org/maven2/org/apache/commons/commons-pool2/2.11.0/commons-pool2-2.11.0.jar
```

[[workflow(240229)#모든게 완벽했는데,,, *scala가 없구나?*]]
### Scala를 설치해보자.

```dockerfile
FROM apache/airflow:2.8.1

ENV AIRFLOW_HOME=/home/airflow/.local
ENV JAVA_HOME=/usr
ENV SPARK_HOME=/home/airflow/.local
ENV PATH="$PATH:${AIRFLOW_HOME}/bin:${JAVA_HOME}/bin:${SPARK_HOME}/bin"

USER root

RUN apt-get update \
  && apt-get install -y --no-install-recommends \
        vim \
        openjdk-17-jdk \
        wget \
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
## requirements_kafka.txt

```txt
pandas~=2.0.3
requests~=2.31.0
selenium~=4.17.2
beautifulsoup4~=4.12.3
lxml~=5.1.0
kafka-python~=2.0.2
apache-airflow-providers-apache-kafka~=1.3.1
confluent-kafka~=2.3.0
apache-airflow-providers-apache-spark==4.7.1
```

### add

```bash
py4j==0.10.9.5
apache-airflow-providers-apache-spark==4.7.1
```

## /etc/hosts

```
127.0.0.1 localhost localhost.localdomain
125.6.40.186 bami-cluster2
```

1. 이녀석을 Dockerfile로 삽입 하려고 하니 Read-only 파일이라 생성이 안됨. 
    1. 처음에는 같은 폴더에 hosts 파일을 만들어 ip를 지정해 주고 Dockerfile의 COPY를 통해 /etc/hosts로 복사 하려고 했으나 안되더라  .
    2. echo 명령어로 >> /etc/hosts 하려고 했더니 이것도 안되더라.
2. 그래서 local의 /etc/hosts 파일을 컨테이너에 마운트 하는 방법을 했음 
    ```yaml
    webserver:
      extraVolumeMounts:
        - name: hosts-volume
          mountPath: /etc/hosts
          subPath: hosts
      extraVolumes:
        - name: hosts-volume
          hostPath:
            path: /etc/hosts
```

    1. 근데  *어떤 노드에 배포되는지에 따라 다른 /etc/hosts*라서 master cluster에 정의된 /etc/hosts가 마운트 되지 않아..ㅎㅎ 그래 nodeselector를 이용해준다..
   ```yaml
   webserver:
     nodeSelector: node-role.kubernetes.io/control-plane: ""
    ```

## Dag

```python
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from kafka import KafkaProducer
from pyspark.sql import SparkSession
from datetime import datetime

# Define Kafka broker and Spark master

spark_master = 'bami-cluster2:7077'

# Define functions to check connections
def check_connected_kafka():
    try:
        producer = KafkaProducer(bootstrap_servers=bootstrap_servers)
        print("####SUCCESS CONNECTING KAFKA#######")
        return True
    except Exception as e:
        print(f"Error connecting to Kafka: {str(e)}")
        return False

def check_connected_spark():
    try:
        spark = SparkSession.builder \
            .appName("Streaming from Kafka") \
            .master(spark_master) \
            .getOrCreate()
        spark.stop()
        print("#####SUCCESS CONNECTING SPARK#######")
        return True
    except Exception as e:
        print(f"Error connecting Spark: {str(e)}")
        return False

# Define the DAG
default_args = {
    'owner': 'admin',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'retries': 1,
}

with DAG(
    'airflow_kafka_spark_interworking',
    default_args=default_args,
    description='DAG for testing interworking of Airflow, Kafka, and Spark',
    schedule_interval=None,
) as dag:
    # Define tasks
    check_connected_kafka_task = PythonOperator(
        task_id='check_connected_kafka',
        python_callable=check_connected_kafka,
        dag=dag,
    )

    check_connected_spark_task = PythonOperator(
        task_id='check_connected_spark',
        python_callable=check_connected_spark,
        dag=dag,
    )
```

```
helm upgrade airflow apache-airflow/airflow --namespace airflow -f custom_values.yaml
```

## custom-values.yaml

```yaml
# Custom Images (include PyPI Packages)
images:
  airflow:
    repository: seunghyejeong/airflow
    tag: "2.0"
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
  extraVolumeMounts:
    - name: hosts-volume
      mountPath: /etc/hosts
      subPath: hosts
  extraVolumes:
    - name: hosts-volume
      hostPath:
        path: /etc/hosts
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

# 모든게 완벽했는데,,,  *scala가 없구나?*
[[workflow(240220)]]
docker compose로 하다보니까.. 이 scala를 깔아줘야하는걸 까먹었구나 승혜야
대단하구나\\\

- [Q] 너무 웃기지 않나 ?  자동으로 배포하기 위해서 컨테이너로 띄우는건데 이 '자동'을 위해서 scala를 기본적으로 배포 해야 한다는거.. 너무 비효율 적이라고 생각한다.  