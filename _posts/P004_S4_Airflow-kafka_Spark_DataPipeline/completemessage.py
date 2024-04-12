```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, window, to_timestamp, to_date, avg, explode
from pyspark.sql.types import StringType, StructField, StructType, ArrayType, LongType

bootstrap_servers = '133.186.251.199:19092'
spark_master_url = '133.186.251.199:7077'
topic_name = 'devices'
data_path = '/tmp'

spark = SparkSession \
    .builder \
    .appName("Streaming from Kafka") \
    .config("spark.streaming.stopGracefullyOnShutdown", True) \
    .config('spark.jars.packages', 'org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0') \
    .config("spark.sql.shuffle.partitions", 4) \
    .master("spark://" + spark_master_url) \
    .getOrCreate()
# Define Kafka connection properties
kafka_params = {
    "kafka.bootstrap.servers": "133.186.251.199:19092",
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
# Apply watermarking
watermarked_df = flattened_df.withColumn("eventTime", to_timestamp("eventTime")) \
    .withWatermark("eventTime", "1 day")

# Aggregate the dataframes to find the average temperature per Customer per device throughout the day for SUCCESS events
agg_df = watermarked_df.where("status = 'SUCCESS'") \
    .withColumn("eventDate", to_date("eventTime", "yyyy-MM-dd")) \
    .groupBy("customerId", "deviceId", "eventDate") \
    .agg(avg("temperature").alias("avg_temp"))

# Write the output to console sink to check the output
writing_df = agg_df.writeStream \
    .format("console") \
    .option("checkpointLocation","checkpoint_dir") \
    .outputMode("complete") \
    .start()

writing_df.awaitTermination()

```


```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, window, to_timestamp, to_date, avg, explode, col
from pyspark.sql.types import StringType, StructField, StructType, ArrayType, LongType
from airflow import DAG
from airflow.operators.python import PythonOperator
from kafka import KafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError
import json
import time
from pyspark.sql.types import StringType, StructField, StructType, ArrayType, LongType, TimestampType, IntegerType
import uuid
import random
from datetime import datetime as dt

# Kafka and Spark configurations
bootstrap_servers = '133.186.251.199:19092'
spark_master_url = '133.186.251.199:7077'
topic_name = 'devices'

# Absolute paths for data and checkpoint locations
data_path = '/mnt'
checkpoint_location = 'https://kr1-api-object-storage.nhncloudservice.com/v1/AUTH_9ea3a098cb8e49468ac2332533065184'


import time  # Make sure to import the 'time' module

def create_topic():
    try:
        admin_client = KafkaAdminClient(bootstrap_servers=bootstrap_servers)
        existing_topics = admin_client.list_topics()

        if topic_name in existing_topics:
            print(f"Topic '{topic_name}' already exists.")
        else:
            topic = NewTopic(name=topic_name, num_partitions=1, replication_factor=1)
            try:
                admin_client.create_topics([topic])
                print(f"Topic '{topic_name}' created successfully.")
                time.sleep(8)
            except TopicAlreadyExistsError:
                print(f"Topic '{topic_name}' already exists.")
    except Exception as e:
        print(f"Error connecting to Kafka: {str(e)}")

# Function to send message to Kafka
def devices(offset=0):

    device_id = [1, 2, 3, 4, 5]
    age_list = [23, 3, 7, 35, 37]
    name_list = ["jeong" , "ba", "mi" , "ji" , "won", "hye"]

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
                } for _ in range(random.randint(1, 3))
            ],
        },
        "eventTime": str(dt.now())
    }
    return json.dumps(_event).encode('utf-8')

def send_to_kafka():
    _offset = 100
    while True:
        data = devices(offset=_offset)
        producer = KafkaProducer(bootstrap_servers=bootstrap_servers)
        producer.send('devices', key=b'device', value=data)
        producer.flush()
        producer.close()
        print("Posted to topic")
        time.sleep(random.randint(0, 5))  # Corrected indentation
        _offset += 1

def write_to_directory(batch_df, batch_id):
    try:
        # Parquet 파일로 배치 데이터 저장
        batch_df.write.mode("append").parquet(data_path)
        print(f"Batch {batch_id} written to directory successfully.")
    except Exception as e:
        print(f"Error writing batch {batch_id} to directory: {str(e)}")

def messaging(batch_df=None):
    spark = SparkSession \
        .builder \
        .appName("first") \
        .config("spark.streaming.stopGracefullyOnShutdown", True) \
        .config('spark.jars.packages', 'org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0') \
        .master("spark://" + spark_master_url) \
        .getOrCreate()

    # Define JSON Schema
    json_schema = StructType([
        StructField("eventId", StringType()),
        StructField("eventOffset", IntegerType()),
        StructField("eventPublisher", StringType()),
        StructField("data", StructType([
            StructField("devices", ArrayType(StructType([
                StructField("deviceId", IntegerType()),
                StructField("name", StringType()),
                StructField("age", IntegerType())
            ])))
        ])),
        StructField("eventTime", TimestampType())
    ])
    # Read Kafka messages
    kafka_streaming_df = spark.readStream.format("kafka").option("kafka.bootstrap.servers", bootstrap_servers).option("subscribe", topic_name).load()

    # Parse JSON messages
    parsed_df = kafka_streaming_df.selectExpr("CAST(value AS STRING) AS value") \

    # Assuming parsed_df is your DataFrame containing the Kafka messages
    json_df = parsed_df.select(from_json(col("value"), json_schema).alias("value")).select("value.*")

    json_df.printSchema()

#    exploded_df = json_expanded_df \
#               .select("eventId", "eventTime", "eventOffset", "eventPublisher", "eventTime", "data") \
#                .withColumn("devices", explode("data.devices")) \
#                .drop("data")

#    flattened_df = exploded_df \
#            .selectExpr("eventId", "eventOffset", "eventPublisher", "cast(eventTime as timestamp) as eventTime","devices.deviceId as deviceId", "devices.name as name", "devices.age as age")

#    flattened_df.printSchema()

#    filtered_df = flattened_df.filter(col("eventOffset").isNotNull())

 #   filtered_df.printSchema()

    query = json_df.writeStream.foreachBatch(write_to_directory).start()
    query.awaitTermination(timeout=30)

# Function to write batch data to Kafka and directory
default_args = {
    'owner': 'admin',
    'depends_on_past': False,
    'start_date': dt(2024, 1, 1),
    'retries': 1,
    'provide_context': True
}

with DAG('pipeline', default_args=default_args, schedule=None) as dag:
    create_topic_task = PythonOperator(
        task_id='create_topic',
        python_callable=create_topic,
        dag=dag,
    )
    send_to_kafka_task = PythonOperator(
        task_id='send_to_kafka',
        python_callable=send_to_kafka,
        dag=dag,
    )
    messaging_task = PythonOperator(
        task_id='messaging',
        python_callable=messaging,
        dag=dag,
    )

    create_topic_task >> send_to_kafka_task
    messaging_task

```


```python
from airflow.operators.dagrun_operator import TriggerDagRunOperator
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime as dt
from kafka import KafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError
import json
import time
import uuid
import random
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, ArrayType, LongType
from pyspark.sql.functions import from_json, col, explode
import time

# Kafka and Spark configurations
bootstrap_servers = '133.186.251.60:19092'
spark_master_url = '133.186.251.60:7077'
topic_name = 'devices'

# Absolute paths for data and checkpoint locations
data_path = '/tmp'


def create_topic():
    try:
        admin_client = KafkaAdminClient(bootstrap_servers=bootstrap_servers)
        existing_topics = admin_client.list_topics()

        if topic_name in existing_topics:
            print(f"Topic '{topic_name}' already exists.")
        else:
            topic = NewTopic(name=topic_name, num_partitions=1, replication_factor=1)
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

def send_to_kafka():
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

def messaging():
    spark = SparkSession \
        .builder \
        .config("spark.streaming.stopGracefullyOnShutdown", True) \
        .config('spark.jars.packages', 'org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0') \
        .master("spark://" + spark_master_url) \
        .getOrCreate()

    # Define JSON Schema
    json_schema = StructType([
        StructField("eventId", StringType()),
        StructField("eventOffset", LongType()),
        StructField("eventPublisher", StringType()),
        StructField("data", StructType([
            StructField("devices", ArrayType(StructType([
                StructField("deviceId", LongType()),
                StructField("name", StringType()),
                StructField("age", LongType())
            ])))
        ])),
        StructField("eventTime", LongType())
    ])

    # Read Kafka messages
    kafka_streaming_df = spark.readStream \
            .format("kafka")\
            .option("kafka.bootstrap.servers", bootstrap_servers)\
            .option("subscribe", "devices")\
            .load()

    json_df = kafka_streaming_df.selectExpr("CAST(value AS STRING) AS value") \

    json_expanded_df = json_df.withColumn("value", from_json(json_df["value"], json_schema)).select("value.*")

    json_expanded_df.printSchema()

#    flattened_df = exploded_df \
#        .selectExpr("eventId", "eventOffset", "eventPublisher", "cast(eventTime/1000000000 as timestamp) as eventTime",
#                "devices.deviceId as deviceId", "devices.name as name",
#                "devices.age as age")

#writeStream
    query = json_expanded_df\
            .writeStream\
            .format("par")\
            .option("kafka.bootstrap.servers", bootstrap_servers)\
            .option("topic", topic_name)\
            .option("checkpointLocation", "checkpoint_dir")\
            .start()

    query.awaitTermination()


default_args = {
    'owner': 'admin',
    'depends_on_past': False,
    'start_date': dt(2024, 1, 1),
    'retries': 1,
    'provide_context': True,
}

with DAG('pipeline', default_args=default_args, schedule=None) as dag:
    create_topic_task = PythonOperator(
        task_id='create_topic',
        python_callable=create_topic,
        dag=dag,
    )
    send_to_kafka_task = PythonOperator(
        task_id='send_to_kafka',
        python_callable=send_to_kafka,
        dag=dag,
    )
    messaging_task = PythonOperator(
        task_id='messaging',
        python_callable=messaging,
        dag=dag,
    )
    create_topic_task >> send_to_kafka_task
    messaging_task
```

(env) ubuntu@bami:~/airflow/dags