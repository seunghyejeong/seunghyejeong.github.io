---
title: The long adventure to designing Pipeline...1) Edit & Analyst DataProccess Source
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

> [!warning] 
> 
> 🫠 매우 긴 챌린지가 시작됩니다.
> A Lengthy Challenge Begins...



- [b] REF
> [예제 코드](https://medium.com/swlh/using-airflow-to-schedule-spark-jobs-811becf3a960)
> [postgres에 연동하여 data 저장하기](https://velog.io/@newnew_daddy/SPARK10)

⬇️ 소스 변경 ⬇️
1. ✅produce 하기: smaple JSON 파일 examplemsg.sh 실행 
2. ✅spark 서버에서 consume 실행: 데이터 가공 스크립트를 수정한다. 
3. ✅실행 값 받아오기 
4. ✅data 저장하기 ( postgres )

# Sketch

1. airflow 이미지 다시 말기 
    1. spark에 대한 python package 빌드업 필요
```txt
pandas~=2.0.3
requests~=2.31.0
selenium~=4.17.2
beautifulsoup4~=4.12.3
lxml~=5.1.0
kafka-python~=2.0.2
apache-airflow-providers-apache-kafka~=1.3.1
confluent-kafka~=2.3.0
+
add please
```

2. spark 서버에서 자동 consume 실행
> spark.py
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

> device_events
```python
# Generate random events data
import datetime
import time
import uuid
import random
import json

event_status: list = ["SUCCESS", "ERROR", "STANDBY"] + [None]
device_id: list = ['D' + str(_id).rjust(3, '0') for _id in range(1, 6)] + [None]
customer_id: list = ["CI" + str(_id).rjust(5, '0') for _id in range(100, 121)]


# Generate event data from devices
def generate_events(offset=0):
    _event = {
        "eventId": str(uuid.uuid4()),
        "eventOffset": offset,
        "eventPublisher": "device",
        "customerId": random.choice(customer_id),
        "data": {
            "devices": [
                {
                    "deviceId": random.choice(device_id),
                    "temperature": random.randint(0, 30),
                    "measure": "C",
                    "status": random.choice(event_status)
                } for i in range(random.randint(0, 3))
            ],
        },
        "eventTime": str(datetime.datetime.now())
    }

    return json.dumps(_event)



if __name__ == "__main__":
    _offset = 10000
    while True:
        print(generate_events(offset=_offset))
        time.sleep(random.randint(0, 5))
        _offset += 1
```

> post-to-kafka.py
```python
# Method posts events to Kafka Server
# run command in kafka server to create topic : 
# ./usr/bin/kafka-topics --create --topic device_data --bootstrap-server kafka:9092 
from kafka import KafkaProducer, KafkaConsumer
import time
import random
from device_events import generate_events

__bootstrap_server = "kafka:29092"


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

> read_from_kafka.py
```python
# Method posts events to Kafka Server
from kafka import KafkaProducer, KafkaConsumer

__bootstrap_server = "kafka:29092"


def read_from_kafka():
    print("Reading through consumer")
    consumer = KafkaConsumer('devices', bootstrap_servers = __bootstrap_server)
    consumer.poll(timeout_ms=2000)
    for m in consumer:
        msg = str(m.value.decode('utf-8'))
        print('getting->' + msg)


if __name__ == "__main__":
    read_from_kafka()
```

3.  Kafka code 수정 
> kafka consume을 spark consume으로 수정 

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
.
.
.
```

### 데이터 가공 스크립트 중 ERROR 

1. 가공이 잘못 돼서 그럼.. ㅎ 

```bash
pyspark.sql.utils.AnalysisException: Column 'customerId' does not exist. Did you mean one of the following? [devices];
'Project ['customerId, 'eventId, 'eventOffset, 'eventPublisher, 'eventTime, 'data]
+- Project [data#29.devices AS devices#37]
   +- Project [data#23.eventId AS eventId#25, data#23.eventOffset AS eventOffset#26L, data#23.eventPublisher AS eventPublisher#27, data#23.customerId AS customerId#28, data#23.data AS data#29, data#23.eventTime AS eventTime#30]
      +- Project [from_json(StructField(eventId,StringType,true), StructField(eventOffset,LongType,true), StructField(eventPublisher,StringType,true), StructField(customerId,StringType,true), StructField(data,StructType(StructField(devices,ArrayType(StructType(StructField(deviceId,StringType,true),StructField(temperature,LongType,true),StructField(measure,StringType,true),StructField(status,StringType,true)),true),true)),true), StructField(eventTime,StringType,true), json#21, Some(Etc/UTC)) AS data#23]
         +- Project [cast(value#8 as string) AS json#21]
            +- StreamingRelationV2 org.apache.spark.sql.kafka010.KafkaSourceProvider@59ed64f9, kafka, org.apache.spark.sql.kafka010.KafkaSourceProvider$KafkaTable@2dd28f33, [startingOffsets=earliest, kafka.bootstrap.servers=125.6.40.186:19092, subscribe=devices], [key#7, value#8, topic#9, partition#10, offset#11L, timestamp#12, timestampType#13], StreamingRelation DataSource(org.apache.spark.sql.SparkSession@3b89c20b,kafka,List(),None,List(),None,Map(kafka.bootstrap.servers -> 125.6.40.186:19092, subscribe -> devices, startingOffsets -> earliest),None), kafka, [key#0, value#1, topic#2, partition#3, offset#4L, timestamp#5, timestampType#6]


```

##### 코드 공부 

```python
exploded_df.printSchema()
exploded_df.show
```

`spark.py`에서 보면 저런 코드들로 출력하면서 상태를 확인하는데 

```
root
 |-- customerId: string (nullable = true)
 |-- eventId: string (nullable = true)
 |-- eventOffset: long (nullable = true)
 |-- eventPublisher: string (nullable = true)
 |-- eventTime: timestamp (nullable = true)
 |-- deviceId: string (nullable = true)
 |-- measure: string (nullable = true)
 |-- status: string (nullable = true)
 |-- temperature: long (nullable = true)
```

요것이 저 코드 중 하나다. 
이게 코드를 진행하면서 가공된 형태인데 아래의 형식처럼 DataFrame이 어떻게 바뀌어 가는지, 즉 Schema 형태가 어떻게 변형되어 가는지 보여주는 코드임! 

```bash
root
 |-- devices: array (nullable = true)
 |    |-- element: struct (containsNull = true)
 |    |    |-- deviceId: string (nullable = true)
 |    |    |-- measure: string (nullable = true)
 |    |    |-- status: string (nullable = true)
 |    |    |-- temperature: long (nullable = true)
```
⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️
```bash
root
 |-- customerId: string (nullable = true)
 |-- data: struct (nullable = true)
 |    |-- devices: array (nullable = true)
 |    |    |-- element: struct (containsNull = true)
 |    |    |    |-- deviceId: string (nullable = true)
 |    |    |    |-- measure: string (nullable = true)
 |    |    |    |-- status: string (nullable = true)
 |    |    |    |-- temperature: long (nullable = true)
 |-- eventId: string (nullable = true)
 |-- eventOffset: long (nullable = true)
 |-- eventPublisher: string (nullable = true)
 |-- eventTime: string (nullable = true)
```
⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️
```bash
root
 |-- customerId: string (nullable = true)
 |-- eventId: string (nullable = true)
 |-- eventOffset: long (nullable = true)
 |-- eventPublisher: string (nullable = true)
 |-- eventTime: string (nullable = true)
 |-- devices: struct (nullable = true)
 |    |-- deviceId: string (nullable = true)
 |    |-- measure: string (nullable = true)
 |    |-- status: string (nullable = true)
 |    |-- temperature: long (nullable = true)
```

{"eventId": "e3cb26d3-41b2-49a2-84f3-0156ed8d7502", "eventOffset": 10001, "eventPublisher": "device", "customerId": "CI00103", "data": {"devices": [{"deviceId": "D001", "temperature": 15, "measure": "C", "status": "ERROR"}, {"deviceId": "D002", "temperature": 16, "measure": "C", "status": "SUCCESS"}]}, "eventTime": "2023-01-05 11:13:53.643364"}

# Spark.py 데이터 가공 스크립트 최종
#SPARK_PY

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
    StructField('customerId', StringType(), True),
    StructField('data', StructType([
        StructField('devices', ArrayType(StructType([
            StructField('deviceId', StringType(), True),
            StructField('measure', StringType(), True),
            StructField('status', StringType(), True),
            StructField('temperature', LongType(), True)
        ]), True), True)
    ]), True),
    StructField('eventId', StringType(), True),
    StructField('eventOffset', LongType(), True),
    StructField('eventPublisher', StringType(), True),
    StructField('eventTime', StringType(), True)
])

# Read Kafka messages
streaming_df = spark \
    .readStream \
    .format("kafka") \
    .options(**kafka_params) \
    .load()

# Parse JSON messages
json_df = streaming_df.selectExpr("CAST(value AS STRING) AS value") \

json_expanded_df = json_df.withColumn("value", from_json(json_df["value"], json_schema)).select("value.*")

#print(json_schema)
#json_expanded_df.printSchema()

###############################################

from pyspark.sql.functions import explode, col


exploded_df = json_expanded_df \
    .select("customerId", "eventId", "eventOffset", "eventPublisher", "eventTime", "data") \
    .withColumn("devices", explode("data.devices")) \
    .drop("data")

#exploded_df.printSchema()
#exploded_df.show

flattened_df = exploded_df \
    .selectExpr("customerId", "eventId", "eventOffset", "eventPublisher", "cast(eventTime as timestamp) as eventTime",
                "devices.deviceId as deviceId", "devices.measure as measure",
                "devices.status as status", "devices.temperature as temperature")

#flattened_df.printSchema()


# Aggregate the dataframes to find the average temparature
# per Customer per device throughout the day for SUCCESS events
from pyspark.sql.functions import to_date, avg

agg_df = flattened_df.where("STATUS = 'SUCCESS'") \
    .withColumn("eventDate", to_date("eventTime", "yyyy-MM-dd")) \
    .groupBy("customerId","deviceId","eventDate") \
    .agg(avg("temperature").alias("avg_temp"))

# Write the output to console sink to check the output
writing_df = agg_df.writeStream \
    .format("console") \
    .option("checkpointLocation","checkpoint_dir") \
    .outputMode("complete") \
    .start()

# Start the streaming application to run until the following happens
# 1. Exception in the running program
# 2. Manual Interruption
writing_df.awaitTermination()


#query = flattened_df \
#    .writeStream \
#    .outputMode("append") \
#    .format("console") \
#    .start()

# Wait for the termination of the query
#query.awaitTermination()

```

# *AIRFLOW*
## airflow spark 연동

### airflow의 requirements.txt에 pip 추가
> `apache-airflow-providers-apache-spark==4.7.1`

### SPARK_HOME, JAVA_HOME 환경변수 처리

#### ERROR: ![[Pasted image 20240228160941.png]]
: 하지만 requirements.txt에 spark 관련 패키지 설치를 이미 한 상태
그래서 이 때는 `pyspark` CLI를 찾지 못해서 그렇다고 함.

1. 컨테이너로 들어가서 환경 변수를 잡아줌

```bash
sbin$ which pyspark
/home/airflow/.local/bin/pyspark
airflow@airflow-webserver-66d5f4b595-c4l2g:/sbin$ export SPARK_HOME=/home/airflow/.local/bin
airflow@airflow-webserver-66d5f4b595-c4l2g:/sbin$ export SPARK_HOME=/home/airflow/.local
airflow@airflow-webserver-66d5f4b595-c4l2g:/sbin$ export PATH=$PATH:$SPARK_HOME/bin:$SPARK_HOME/sbin
```

2. 그런데 이번에는 JAVA_HOME이 없다고 에러
```
/home/airflow/.local/bin/load-spark-env.sh: line 68: ps: command not found
JAVA_HOME is not set
```

3. 환경 변수나 필요한 패키지를 설치 하도록 만들어진 Dockerfile을 수정해줌
```Dockerfile
FROM apache/airflow:2.8.1

RUN echo $PATH

# Set AIRFLOW_HOME environment variable
ENV AIRFLOW_HOME=/home/airflow/.local/bin
# Set JAVA_HOME environment variable
ENV JAVA_HOME=/home/airflow/.local/bin

# Set SPARK_HOME environment variable
ENV SPARK_HOME=/home/airflow/.local/bin

# Set SPARK_HOME enviroment variable
ENV PATH="$PATH:${AIRFLOW_HOME}$:${JAVA_HOME}:${SPARK_HOME}"

RUN echo $PATH

USER root
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
        vim \
        openjdk-17-jdk
COPY ./dags/*.py /opt/airflow/dags/
USER airflow
COPY requirements.txt /
RUN pip install --no-cache-dir "apache-airflow==2.8.1" -r /requirements.txt
```

```bash
docker build -t seunghyejeong/airflow:1.0 .
docker push seunghyejeong/airflow:1.0
```

#### ERROR You need to build Spark with the target "package" before running this program.
```bash
/home/airflow/.local/bin/load-spark-env.sh: line 68: ps: command not found
/home/airflow/.local/bin/load-spark-env.sh: line 68: ps: command not found
Failed to find Spark jars directory (/home/airflow/.local/assembly/target/scala-2.12/jars).
You need to build Spark with the target "package" before running this program.
```

그래도 여전히 에러가 나는데 .. ,, [[workflow(240228)#❌❌❌❌❌❌❌❌❌❌❌❌❌]]

### Airflow UI에서 Connection 만들기 

1. 위의 python 패키지 설치로 Spark 항목이 생겼음
    - connection type: Spark
    - Host: spark://master
    - port: 7077
### Docker image build 후 airflow upgrade 해주기 

```bash
helm upgrade airflow apache-airflow/airflow --namespace airflow -f custom_values.yaml
```

- ui
```
http://133.186.244.202:31151/
```

![[Pasted image 20240228151625.png]]


![[Pasted image 20240228151809.png]]
## pipeline dag 작성

```python
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from kafka import KafkaProducer, KafkaConsumer
from kafka.admin import KafkaAdminClient, NewTopic
from datetime import datetime
from airflow.models import TaskInstance
from kafka.errors import TopicAlreadyExistsError
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json
from pyspark.sql.types import StringType, StructField, StructType, ArrayType, LongType

# Define Kafka broker
bootstrap_servers = '125.6.40.186:19092'
spark_master = 'bami-cluster2:7077'
topic_name = 'devices'


# Check with Kafka
def check_connected_kafka():
    try:
        producer = KafkaProducer(bootstrap_servers=bootstrap_servers)
        consumer = KafkaConsumer(topic_name, bootstrap_servers=bootstrap_servers)
        print(f"#####SUCCESS CONNECTING WITH KAFKA#######")
        return True
    except Exception as e:
        print(f"Error connecting to Kafka: {str(e)}")
        return False

# Check with Spark
def check_connedted_spark():
    try:
    spark = SparkSession \
        .builder \
        .appName("Streaming from Kafka") \
        .config("spark.streaming.stopGracefullyOnShutdown", True) \
        .config('spark.jars.packages', 'org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0') \
        .config("spark.sql.shuffle.partitions", 4) \
        .master(spark_master) \
        .getOrCreate()
        return True
    except Exception as e:
        print(f"FAIL..............FAIL SPARK........: {str{e}}")
        return False
# Define the DAG
default_args = {
    'owner': 'admin',
    'depends_on_past': False,
    'start_date': datetime(2024, 2, 27),
    'retries': 1,
}
dag = DAG(
    'airflow_kafka_spark_interworking',
    default_args=default_args,
    description='DAG for testing interworking of Airflow and Kafka and Spark',
    schedule_interval=None,
)

# Define tasks
check_connected_kafka_task = PythonOperator(
    task_id='check_connected_kafka',
    python_callable=check_connected_kafka,
    dag=dag,
)

check_connedted_spark_task = PythonOperator(
    task_id='check_connedted_spark',
    python_callable=check_connedted_spark,
    dag=dags,
)
```

# ❌❌❌❌❌❌❌❌❌❌❌❌❌

**DOCKER FILE이나 SPAKR 관련 Package를 빌드하는게 아닌거같아 .............................
airflow에서는 spark connect만 하고 
spark container에서 Spark Session 실행 하는 거 아닐까.;;;;;;;;;;;;;;;;;;;;;;;;*

정답은 : [[workflow(240229)]]






```python
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from kafka import KafkaProducer, KafkaConsumer
from kafka.admin import KafkaAdminClient, NewTopic
from datetime import datetime
from airflow.models import TaskInstance
from kafka.errors import TopicAlreadyExistsError
from airflow.contrib.hooks.spark_submit_hook import SparkSubmitHook
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator 


# Define Kafka broker
bootstrap_servers = '125.6.40.186:19092'
spark_master = 'bami-cluster2:7077'
topic_name = 'devices'


# Check with Kafka
def check_connected_kafka():
    try:
        producer = KafkaProducer(bootstrap_servers=bootstrap_servers)
        consumer = KafkaConsumer(topic_name, bootstrap_servers=bootstrap_servers)
        print(f"#####SUCCESS CONNECTING WITH KAFKA#######")
        return True
    except Exception as e:
        print(f"Error connecting to Kafka: {str(e)}")
        return False

with DAG(dag_id='check_connected_kafka', start_date=datetime(2023, 1, 1)) as dag: 
    submit_spark_app = SparkSubmitOperator( 
        task_id='check_connected_kafka', 
        conn_id='spark_default', 
        application='/opt/bitnami/spark.py', 
        name='Streaming_from_Kafka'
    ) 

# Define the DAG
default_args = {
    'owner': 'admin',
    'depends_on_past': False,
    'start_date': datetime(2024, 2, 27),
    'retries': 1,
}
dag = DAG(
    'airflow_kafka_spark_interworking',
    default_args=default_args,
    description='DAG for testing interworking of Airflow and Kafka and Spark',
    schedule_interval=None,
)

# Define tasks
check_connected_kafka_task = PythonOperator(
    task_id='check_connected_kafka',
    python_callable=check_connected_kafka,
    dag=dag,
)

check_connedted_spark_task = PythonOperator(
    task_id='check_connedted_spark',
    python_callable=check_connedted_spark,
    dag=dags,
)


```