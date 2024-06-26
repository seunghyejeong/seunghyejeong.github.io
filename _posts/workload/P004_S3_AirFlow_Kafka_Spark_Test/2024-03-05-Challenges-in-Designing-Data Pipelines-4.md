---
title: The long adventure to success Pipeline...4
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



Connetion type: spark_conn

```python
from __future__ import annotations

import typing import Any, Callable

import pendulum
@dag(
    schedule=None,
    start_date=pendulum.datetime(2021, 1, 1, tz="UTC"),
    catchup=False,
    tags=["example"],
)

def example_pyspark():
    @task.pyspark(conn_id="spark-default")
    def spark_task(spark: SparkSession, sc: SparkContext) -> pd.DataFrame:
        df = spark.createDataFrame(
            [
                (1, "John Doe", 21),
                (2, "Jane Doe", 22),
                (3, "Joe Bloggs", 23),
            ],
            ["id", "name", "age"],
        )
        df.show()
        return df.toPandas()
    @task
    def print_df(df: pd.DataFrame):
        print(df)
    df = spark_task()
    print_df(df)
# work around pre-commit
dag = example_pyspark()  # type: ignore
test_run = get_test_run(dag)


from __future__ import annotations

import logging
import os
from datetime import timedelta
from typing import TYPE_CHECKING, Callable

from tabulate import tabulate

from airflow.utils.state import State

if TYPE_CHECKING:
    from airflow.utils.context import Context

def get_test_run(dag):
    def callback(context: Context):
        try:
            ti = context["dag_run"].get_task_instances()
            if not ti:
                logging.warning("Could not retrieve tasks that ran in the DAG, cannot display a summary")
                return

            ti.sort(key=lambda x: x.end_date)

            headers = ["Task ID", "Status", "Duration (s)"]
            results = []
            prev_time = ti[0].end_date - timedelta(seconds=ti[0].duration)
            for t in ti:
                results.append([t.task_id, t.state, f"{(t.end_date - prev_time).total_seconds():.1f}"])
                prev_time = t.end_date

            logging.info("EXECUTION SUMMARY:\n" + tabulate(results, headers=headers, tablefmt="fancy_grid"))
        except Exception as e:
            logging.error(f"Error occurred during callback execution: {e}")

    def add_callback(current: List[Callable], new: Callable) -> List[Callable]:
        return current + [new]

    def test_run():
        dag.on_failure_callback = add_callback(dag.on_failure_callback or [], callback)
        dag.on_success_callback = add_callback(dag.on_success_callback or [], callback)
        dag.clear(dag_run_state=State.QUEUED)
        dag.run()

    return test_run

def get_test_env_id(env_var_name: str = "SYSTEM_TESTS_ENV_ID"):
    return os.environ.get(env_var_name)
```

```
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

export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export PATH=$PATH:$JAVA_HOME/bin
```terminal
export PYSPARK_SUBMIT_ARGS="--master local[3] pyspark-shell"
```


spark..
client, cluster mode,

connection type: sql, submit, jdbc..


```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json
from pyspark.sql.types import StringType, StructField, StructType, ArrayType, LongType

def initialize_spark_session():
    spark = SparkSession \
        .builder \
        .appName("pipeline") \
        .config("spark.streaming.stopGracefullyOnShutdown", True) \
        .config('spark.jars.packages', 'org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0') \
        .config("spark.sql.shuffle.partitions", 4) \
        .master("local[*]") \
        .getOrCreate() 

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 3, 5),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Instantiate the DAG
dag = DAG(
    'spark_data_pipeline',
    default_args=default_args,
    description='A DAG to process data from Kafka using Spark',
    schedule_interval=None,
)

# Define tasks
initialize_spark_task = PythonOperator(
    task_id='initialize_spark_session',
    python_callable=initialize_spark_session,
    dag=dag,
)


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

writing_df.awaitTermination()
```


```python
airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
```

Please make a python code to connect the spark in airflow. Information about the spark is registered in the connection of airflow, so use it

# Umm..

17:00
이제까지 생각을 잘 못 한듯. . . 
Airflow Dockerfile 이미지를 생성 할 때부터 이미 Airflow의 web-server에는 Spark가 설치 된 것..? 
그래서 Kafka가 설치된 node2에 대해서 연결을 하려고 하면 port에 대한 관련 오류가 뜨기도 하고 .. 
Java가 어쩌고 저쩌고 ($JAVA_HOME이 잘 못 설정되어 있기도 함.) 
문제는 나는 node2에 spark를 띄워 놓고 또 띄우려고 한 것인 셈이다.  Kafka를 node2에 설치하고 거기서 메세지를 받아오는 형식으로 구축하다 보니 헷갈린 것 같다.  지금도 Dag pipeline을 실행하려니 오류가 뜨기는 하지만. .

17:20
master를 node2의 7077으로 하니까 *Fail connect to master*가 뜸. 
그러면 Spark master, Spark worker는 띄워져 있어야 한다는 건데 ,

## Caused by: java.lang.RuntimeException: java.io.InvalidClassException: org.apache.spark.rpc.netty.RpcEndpointVerifier$CheckExistence; local class incompatible: stream classdesc serialVersionUID = 5378738997755484868, local class serialVersionUID = 7789290765573734431
*spark가 겹칠 때*

https://repo1.maven.org/maven2/org/apache/spark/spark-core_2.12/3.3.0/spark-core_2.12-3.3.0.jar

아 아무튼 버전 묹네인거같다 자바 버전
