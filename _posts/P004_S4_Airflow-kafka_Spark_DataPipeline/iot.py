from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from pyspark.sql import SparkSession
from kafka import KafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError
from pyspark.sql.functions import from_json
from pyspark.sql.types import StringType, StructField, StructType, LongType
import json
import time

# Kafka and Spark configurations
bootstrap_servers = '125.6.39.99:19092'
spark_master_url = '125.6.39.99:7077'
topic_name = 'devices'

# Absolute paths for data and checkpoint locations
data_path = '/opt/airflow/data'
checkpoint_location = '/opt/airflow/checkpoint'

# Function to check if Kafka is connected
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
            except TopicAlreadyExistsError:
                print(f"Topic '{topic_name}' already exists.")

        return True

    except Exception as e:
        print(f"Error connecting to Kafka: {str(e)}")
        return False

# Function to send message to Kafka
def send_to_kafka(producer, topic_name):
    try:
        message = {
            "id": 3,
            "name": "bami",
            "age": "7"
        }
        
        while True:
            producer.send(topic_name, json.dumps(message).encode('utf-8'))
            producer.flush()
            print("Message sent to Kafka successfully.")
            
    except Exception as e:
        print(f"Error sending message to Kafka: {str(e)}")

        
# Function to write data to Kafka and directory
def write_data(batch_df, batch_id):
    try:
        # Write to Kafka
        producer = KafkaProducer(bootstrap_servers=bootstrap_servers, linger_ms=20)
        for row in batch_df.collect():
            message = json.dumps(row.asDict()).encode('utf-8')
            producer.send(topic_name, message)
        producer.flush()
        print(f"Batch {batch_id} sent to Kafka successfully.")

        # Write to directory
        batch_df.write.mode("append").parquet(data_path)
        print(f"Batch {batch_id} written to directory successfully.")
        
    except Exception as e:
        print(f"Error processing batch {batch_id}: {str(e)}")      
                 
# Function to send message to Kafka and process it with Spark
def messaging():
    if create_topic():
        try:
            # Define JSON schema
            schema = StructType([
                StructField('id', LongType(), True),
                StructField('name', StringType(), True),
                StructField('age', StringType(), True)
            ])

           # Start Spark session
            spark = SparkSession.builder.appName('first').master("spark://"+spark_master_url) \
                    .config("spark.streaming.stopGracefullyOnShutdown", True) \
                    .config('spark.jars.packages', 'org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0') \
                    .getOrCreate()

            if spark:
                print("Spark is running:", spark)

                # Send message to Kafka every 10 seconds
                producer = KafkaProducer(bootstrap_servers=bootstrap_servers, linger_ms=20)
                send_to_kafka(producer, topic_name)

                # Read messages from Kafka and process with Spark
                kafka_streaming_df = spark.readStream.format("kafka").option("kafka.bootstrap.servers", bootstrap_servers) \
                    .option("subscribe", topic_name).load()

                json_df = kafka_streaming_df.selectExpr("CAST(value AS STRING) AS json").select(from_json("json", schema).alias("value")).select("value.*")

                print("Successfully read from Kafka and processed with Spark.")

                # Start Spark streaming query
                query = json_df.writeStream \
                        .foreachBatch(write_data) \
                        .start()

                query.awaitTermination()

        except Exception as e:
            print(f"Error: {str(e)}")

# Run the messaging function
#if __name__ == "__main__":
#    messaging()

default_args = {
    'owner': 'admin',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'retries': 1,
}

with DAG('pipeline', default_args=default_args, schedule=None) as dag:
    create_topic_task = PythonOperator(
        task_id='create topic to kafka',
        python_callable=create_topic,
        dag=dag,
    )
    send_to_kafka_task = PythonOperator(
        tasi_id='send message to kafka',
        python_callable=send_to_kafka,
        dag=dag,
    )
    
    messaging_task = PythonOperator(
        task_id='consume message spark',
        python_callable=messaging,
        dag=dag,
    )
    write_data_tas = PythonOperator(
        task_id='store object storage',
        python_callable=write_data,
        dag=dag
    )
    
