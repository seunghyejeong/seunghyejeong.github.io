
Airflow Server설치 
kafka , spark Docker Container 설치 
## dag.py

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime as dt
from datetime import timedelta
from kafka_streaming import kafka_streaming

default_args = {
    'owner': 'admin',
    'depends_on_past': False,
    'start_date': dt(2024, 1, 1),
    'retries': 1,
    'provide_context': True,
    'retry_delay': timedelta(minutes=1)
}

with DAG('pipeline', default_args=default_args, schedule_interval=None) as dag:
    kafka_streaming_task = PythonOperator(
        task_id='kafka_streaming',
        python_callable=kafka_streaming,
        dag=dag,
    )
    kafka_streaming_task
```

## kafka_streaming.py
```python
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError
import time
import uuid
import random
from datetime import datetime as dt
import json
from kafka import KafkaProducer
import requests
import os, sys

bootstrap_servers = '125.6.40.10:19092'
topic_name = 'devices'

def create_topic():
    try:
        admin_client = KafkaAdminClient(bootstrap_servers=bootstrap_servers)
        existing_topics = admin_client.list_topics()

        if topic_name in existing_topics:
            print(f"Topic '{topic_name}' already exists.")
        else:
            topic = NewTopic(name=topic_name)
            try:
                admin_client.create_topics([topic])
                print(f"Topic '{topic_name}' created successfully.")
                time.sleep(8)
            except TopicAlreadyExistsError:
                print(f"Topic '{topic_name}' already exists.")

    except Exception as e:
        print(f"Error connecting to Kafka: {str(e)}")

def devices(offset=0):

    device_id = [1, 2, 3, 4, 5]
    age_list = [23, 3, 7, 35, 37]
    name_list = ["jeong" , "ba", "mi" , "ji" , "won"]

    _event = {
        "eventId": str(uuid.uuid4()),
        "eventOffset": offset,
        "eventPublisher": "device",
        "data": {
            "devices": [
                {
                    "deviceId": random.choice(device_id),
                    "name": random.choice(name_list),
                    "age": random.choice(age_list)
                }
            ],
        },
        "eventTime": str(dt.now())
    }
    time.sleep(10)

    return json.dumps(_event).encode('utf-8')

def kafka_streaming():
    create_topic()
    _offset = 100
    producer = KafkaProducer(bootstrap_servers=bootstrap_servers)
    try:
        while True:
            data = devices(offset=_offset)
            producer.send('devices', key=b'device', value=data)
            producer.flush()
            print("Posted to topic")
            time.sleep(random.randint(0, 5))
            _offset += 1
    except Exception as e:
        print(f"Error: {e}")
    finally:
        producer.close()

if __name__ == "__main__" :
    kafka_streaming()
```

# Spark Docker 
## msg.py

- [?] 파일은 왜 worker에 떨어지는가?
    - [b] https://bcho.tistory.com/1387: 분산 처리 시스템이기 때문
- [?] /tmp 용량이 꽉 차는 것도 아닌데 /tmp에는 저장이 안되고 /tmp/tmp에 저장이 되는가?

```python
import os
from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf
from pyspark.sql.functions import col, pandas_udf, split
import requests
import json
import time

bootstrap_servers = '125.6.40.10:19092'
topic_name = 'devices'
spark_version = '3.3.0'
#os.environ['PYSPARK_SUBMIT_ARGS'] = '--packages org.apache.spark:spark-sql-kafka-0-10_2.12-3.3.0,org.apache.spark:spark-streaming-kafka-0-10_2.12-3.3.0,org.apache.spark:commons-pool2-2.11.0,org.apache.spark:kafka-clients-3.3.0'.format(spark_version)
spark_master_url = '125.6.40.10:7077'

try:
    spark = SparkSession \
        .builder \
        .appName("PipelineApp")\
        .master("spark://"+spark_master_url)\
        .config('spark.jars', './jars/spark-sql-kafka-0-10_2.12-3.3.0.jar, ./jars/spark-streaming-kafka-0-10_2.12-3.3.0.jar, ./jars/commons-pool2-2.11.0.jar, ./jars/kafka-clients-3.3.0.jar, ./jars/spark-token-provider-kafka-0-10_2.12-3.3.0.jar')\
        .getOrCreate()

    df = spark.readStream\
        .format("kafka")\
        .option("kafka.bootstrap.servers", bootstrap_servers)\
        .option("startingOffsets", "latest")\
        .option("subscribe", topic_name)\
        .option("group.id", "console-consumer-43849")\
        .load()

    df.printSchema()

    schema = StructType([
        StructField("eventId", StringType(), True),
        StructField("eventOffset", StringType(), True),
        StructField("eventPublisher", StringType(), True),
        StructField("data", StructType([
            StructField("devices", ArrayType(StructType([
                StructField("deviceId", StringType(), True),
                StructField("name", StringType(), True),
                StructField("age", IntegerType(), True)
            ])), True)
        ]), True),
        StructField("eventTime", StringType(), True)
    ])

    jsonSchema = schema

    parsed_df = df.selectExpr("CAST(value AS STRING) as json").select(from_json("json", jsonSchema).alias("data")).select("data.*")

    query = parsed_df \
        .writeStream \
        .format("json") \
        .option("checkpointLocation", "checkpoint") \
        .option("path", "/tmp/data") \
        .trigger(processingTime="30 seconds")\
        .outputMode("append")\
        .start()

#    query = parsed_df.writeStream.format("console").start()
    query.awaitTermination()

except Exception as e:
    print("An error occurred:", e)
```

### msg2.py
```python
import os
from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf
from pyspark.sql.functions import col, pandas_udf, split
import json
import requests


bootstrap_servers = '125.6.40.10:19092'
topic_name = 'devices'
spark_version = '3.3.0'
os.environ['PYSPARK_SUBMIT_ARGS'] = '--packages org.apache.spark:spark-sql-kafka-0-10_2.12-3.3.0,org.apache.spark:spark-streaming-kafka-0-10_2.12-3.3.0,org.apache.spark:commons-pool2-2.11.0,org.apache.spark:kafka-clients-3.3.0'.format(spark_version)
spark_master_url = '125.6.40.10:7077'
spark_data='/opt/bitnami/spark/data'

spark = SparkSession \
        .builder \
        .appName("PipelineApp")\
        .master("spark://"+spark_master_url)\
        .config('spark.jars', './jars/spark-sql-kafka-0-10_2.12-3.3.0.jar')\
        .config("spark.sql.execution.arrow.pyspark.enabled", "true")\
        .getOrCreate()


df = spark.readStream\
        .format("kafka")\
        .option("kafka.bootstrap.servers",bootstrap_servers)\
        .option("failOnDataLoss","False")\
        .option("subscribe",topic_name)\
        .option("group.id", "console-consumer-43849")\
        .load()


df.isStreaming
df.printSchema()
df.withWatermark("timestamp", "1 minute")

schema = StructType([
    StructField("eventId", StringType(), True),
    StructField("eventOffset", StringType(), True),
    StructField("eventPublisher", StringType(), True),
    StructField("data", StructType([
        StructField("devices", ArrayType(StructType([
            StructField("age", IntegerType(), True)
        ])), True)
    ]), True),
    StructField("eventTime", StringType(), True)
])
jsonSchema = schema

parsed_df = df.selectExpr("CAST(value AS STRING) as json").select(from_json("json", jsonSchema).alias("data")).select("data.*")

#query = parsed_df \
#       .writeStream \
#        .format("json") \
#        .option("checkpointLocation", "checkpoint_dir") \
#        .option("path", "result") \
#        .outputMode("append") \
#        .start()

query = parsed_df\
        .writeStream\
        .format("json")\
        .option("path","/tmp")\
        .option("checkpointLocation", checkpoint_dir)\
        .trigger(processingTime="30 seconds")\
        .start()

query.awaitTermination()

```

token.py

```python
import json
import requests
import os, sys

def get_token(auth_url, tenant_id, username, password):

    token_url = auth_url + '/tokens'
    req_header = {'Content-Type': 'application/json'}
    req_body = {
        'auth': {
            'tenantId': tenant_id,
            'passwordCredentials': {
                'username': username,
                'password': password
            }
        }
    }

    response = requests.post(token_url, headers=req_header, json=req_body)
    return response.json()

class ObjectService:
    def __init__(self, storage_url, token_id):
        self.storage_url = storage_url
        self.token_id = token_id

    def _get_url(self, container, object):
        return '/'.join([self.storage_url, container, object])

    def _get_request_header(self):
        return {'X-Auth-Token': self.token_id}

    def upload(self, container, object, object_path):
        req_url = self._get_url(container, object)
        req_header = self._get_request_header()

        path = '/'.join([object_path, object])
        with open(path, 'rb') as f:
            return requests.put(req_url, headers=req_header, data=f.read())

if __name__ =="__main__":

    AUTH_URL = 'https://api-identity-infrastructure.nhncloudservice.com/v2.0'
    TENANT_ID = '9ea3a098cb8e49468ac2332533065184'
    USERNAME = 'minkyu.lee'
    PASSWORD = 'PaaS-TA@2024!'

    token = get_token(AUTH_URL, TENANT_ID, USERNAME, PASSWORD)
    #Token값 
    token_value=(token["access"]["token"]["id"])

    STORAGE_URL = 'https://kr1-api-object-storage.nhncloudservice.com/v1/AUTH_9ea3a098cb8e49468ac2332533065184'
    TOKEN_ID = token_value
    CONTAINER_NAME = 'cp-object-storage'
#    OBJECT_NAME = 'part-0000dd0-2f0f45cd-9194-48eb-ac34-0aac8f045288-c000.json'
    OBJECT_PATH = r'/tmp/data'
    directory = '/tmp/data'

    #파일에 있는 모든 로그 한번에 보내기 
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            file_path = os.path.join(directory, filename)
            OBJECT_NAME=filename
            obj_service = ObjectService(STORAGE_URL, TOKEN_ID)
            obj_service.upload(CONTAINER_NAME, OBJECT_NAME, OBJECT_PATH)
```




root@84e7c42d60c1:/tmp/data# python obj.py
{
    "access": {
        "token": {
            "id": "gAAAAABmBP4deAOEcfUUmCbplHYEyefMOZI-Pz4MRPw8l6_ur_hwGsyNXK152j3o1IZeS9n2eTskf6Unq8mSS9MZKy-HY6tpXjefR_SfFVBZbON4Fw5h12bN1h5HBk_ww7IDpemVOH0ao2bv6BiRZpMqj4jYjlumYCqx1NXUXqKVnnvCrhfaC0M",

```python

#1. json 읽기
read_json = json.load(token)
#2. 값 위치 찾기
tokenGetFromJson = e['token'][0]['id'] d['access']
#3. 불러 오기 
print(tokenGetFromJson)

```

## 스토리지로  보내기(코드 합친거)

```python
import os
from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf
from pyspark.sql.functions import col, pandas_udf, split
import requests
import json
import time

bootstrap_servers = '125.6.40.10:19092'
topic_name = 'devices'
spark_version = '3.3.0'
#os.environ['PYSPARK_SUBMIT_ARGS'] = '--packages org.apache.spark:spark-sql-kafka-0-10_2.12-3.3.0,org.apache.spark:spark-streaming-kafka-0-10_2.12-3.3.0,org.apache.spark:commons-pool2-2.11.0,org.apache.spark:kafka-clients-3.3.0'.format(spark_version)
spark_master_url = '125.6.40.10:7077'

def messaging():
    spark = SparkSession \
        .builder \
        .appName("PipelineApp")\
        .master("spark://"+spark_master_url)\
        .config('spark.jars', './jars/spark-sql-kafka-0-10_2.12-3.3.0.jar, ./jars/spark-streaming-kafka-0-10_2.12-3.3.0.jar, ./jars/commons-pool2-2.11.0.jar, ./jars/kafka-clients-3.3.0.jar, ./jars/spark-token-provider-kafka-0-10_2.12-3.3.0.jar')\
        .getOrCreate()

    df = spark.readStream\
        .format("kafka")\
        .option("kafka.bootstrap.servers", bootstrap_servers)\
        .option("startingOffsets", "latest")\
        .option("subscribe", topic_name)\
        .option("group.id", "console-consumer-43849")\
        .load()

    df.printSchema()
    print("read schema from kafka!")
    
    schema = StructType([
        StructField("eventId", StringType(), True),
        StructField("eventOffset", StringType(), True),
        StructField("eventPublisher", StringType(), True),
        StructField("data", StructType([
            StructField("devices", ArrayType(StructType([
                StructField("deviceId", StringType(), True),
                StructField("name", StringType(), True),
                StructField("age", IntegerType(), True)
            ])), True)
        ]), True),
        StructField("eventTime", StringType(), True)
    ])

    jsonSchema = schema
    
    parsed_df = df.selectExpr("CAST(value AS STRING) as json").select(from_json("json", jsonSchema).alias("data")).select("data.*")

    query = parsed_df \
        .writeStream \
        .format("json") \
        .option("checkpointLocation", "checkpoint") \
        .option("path", "/tmp/tmp") \
        .trigger(processingTime="30 seconds")\
        .outputMode("append")\
        .start()

    print("Wait for Streaming...")
#    query = parsed_df.writeStream.format("console").start()
    query.awaitTermination()

def get_token(auth_url, tenant_id, username, password):

    token_url = auth_url + '/tokens'
    req_header = {'Content-Type': 'application/json'}
    req_body = {
        'auth': {
            'tenantId': tenant_id,
            'passwordCredentials': {
                'username': username,
                'password': password
            }
        }
    }

    response = requests.post(token_url, headers=req_header, json=req_body)
    return response.json()

class ObjectService:
    def __init__(self, storage_url, token_id):
        self.storage_url = storage_url
        self.token_id = token_id

    def _get_url(self, container, object):
        return '/'.join([self.storage_url, container, object])

    def _get_request_header(self):
        return {'X-Auth-Token': self.token_id}

    def upload(self, container, object, object_path):
        req_url = self._get_url(container, object)
        req_header = self._get_request_header()

        path = '/'.join([object_path, object])
        with open(path, 'rb') as f:
            return requests.put(req_url, headers=req_header, data=f.read())

if __name__ =="__main__":

    AUTH_URL = 'https://api-identity-infrastructure.nhncloudservice.com/v2.0'
    TENANT_ID = '9ea3a098cb8e49468ac2332533065184'
    USERNAME = 'minkyu.lee'
    PASSWORD = 'PaaS-TA@2024!'

    token = get_token(AUTH_URL, TENANT_ID, USERNAME, PASSWORD)
    #Token값 
    token_value=(token["access"]["token"]["id"])
    print("get token successful")

    STORAGE_URL = 'https://kr1-api-object-storage.nhncloudservice.com/v1/AUTH_9ea3a098cb8e49468ac2332533065184'
    TOKEN_ID = token_value
    CONTAINER_NAME = 'cp-object-storage'
#    OBJECT_NAME = 'part-0000dd0-2f0f45cd-9194-48eb-ac34-0aac8f045288-c000.json'
    OBJECT_PATH = r'/tmp/data'
    
    #파일에 있는 모든 로그 한번에 보내기 
    directory = '/tmp/data'
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            file_path = os.path.join(directory, filename)
            OBJECT_NAME=filename
            obj_service = ObjectService(STORAGE_URL, TOKEN_ID)
            obj_service.upload(CONTAINER_NAME, OBJECT_NAME, OBJECT_PATH)
            
    print("upload complete")
```