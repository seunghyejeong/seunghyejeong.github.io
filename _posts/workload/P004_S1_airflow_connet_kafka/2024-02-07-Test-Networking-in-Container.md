---
title: Test networking between each Container
author: bami jeong
categories: Startups
layout: post
comments: true
tags: 
  - Airflow
---


- [b] REF
> [python docs](https://pypi.org/project/airflow-provider-kafka/)

- [*] 짱 좋은 REF  
> [airflow의 모든 provider,modules](https://registry.astronomer.io/providers/apache-airflow-providers-apache-kafka/versions/1.3.1)![[Pasted image 20240207094048.png]]![[Pasted image 20240207094117.png]]
> [useage](https://www.youtube.com/watch?v=UzGQ8R4F6z4)



## python library for airflow 

#airflowpip #airflowlibrary

#### 문제
> airflow ui > connection에 있는 `conn type`에 `apache kafka`가 없음.

- 위의 링크에서 찾은 라이브러리를 추가해줌 

```bassh
pip install airflow-provider-kafka
pip install apache-airflow-providers-apache-kafka==1.3.1
pip install confluent-kafka
```

#### 해결쓰
- 드루와

![[Pasted image 20240207105155.png]]
#### error 

bash: 
```python 
airflow webserver -p 8080
```

get error:
```bash
TypeError: SqlAlchemySessionInterface.__init__() missing 4 required positional arguments: 'sequence', 'schema', 'bind_key', and 'sid_length'

```
![[Pasted image 20240207095631.png]]

solve:
```python
pip install Flask-Session==0.5.0 
```

## network check

- [b] REF from GTP
#networkcheck #nc_vz #telnet
```markdown
**Test Communication**: 
Once you have the IP addresses, you can test communication between the containers. You can use tools like `curl` or `telnet` to test connectivity over specific ports.

For example, on vm1, you can run:
`curl <vm2_container_ip>:<port>`

And on vm2, you can run:
`curl <vm1_container_ip>:<port>`

Replace `<vm2_container_ip>` and `<port>` with the IP address and port of the container in vm2, and `<vm1_container_ip>` and `<port>` with the IP address and port of the container in vm1.

**Netcat Test**:

- Install netcat (`nc`) on both vm1 and vm2 if not already installed.
- From vm2, run `nc -zv <vm1_public_ip> <container1_port>`.
- If you see a successful connection message, it confirms that the communication is established.
- ```

### 1. vm1 🔗 vm2
```bash
$ telnet {VM1orVM2_MASTER_IP} 22
```

- airflow vm에서 kafka vm 통신 체크 

```bash
$ telnet 133.186.240.216 22
Trying 133.186.240.216...
Connected to 133.186.240.216.
Escape character is '^]'.
SSH-2.0-OpenSSH_8.9p1 Ubuntu-3ubuntu0.4
```

- kafka vm에서 airflow vm 통신 체크

```bash
$ telnet 133.186.155.37 22
Trying 133.186.155.37...
Connected to 133.186.155.37.
Escape character is '^]'.
SSH-2.0-OpenSSH_8.9p1 Ubuntu-3ubuntu0.4

```

### 2. vm1 - vm2's docker container 

```bash
$ nc -vz {vm2_MASTER_IP} {OPENPORT} #내가 확인하고 싶은 포트
```

- airflow vm에서 kafka의 컨테이너 포트로 연결 확인

```bash
nc -vz 133.186.240.216 19092
Connection to 133.186.240.216 19092 port [tcp/*] succeeded!
```

- kafka container 안에서 airflow vm

```bash
nc -vz 133.186.155.37 8080
Ncat: Version 7.92 ( https://nmap.org/ncat )
Ncat: Connected to 133.186.155.37:8080.
Ncat: 0 bytes sent, 0 bytes received in 0.01 seconds.
```


# ⭐ Kafka Container 안에서 bootstrap-server connect


```bash
[appuser@broker ~]$ kafka-topics --list --bootstrap-server 133.186.240.216:19092
__consumer_offsets
my-topic

[appuser@broker ~]$ kafka-topics --list --bootstrap-server broker:9092
__consumer_offsets
my-topic
```

## python Example (최종)

```python
AwaitKafkaMessageOperator
ConsumeFromTopicOperator
    pip install apache-airflow-providers-apache-kafka==1.3.1
ProduceToTopicOperator
    pip install apache-airflow-providers-apache-kafka==1.3.1
PythonOperator
```

kafka-console-producer --topic my-topic --bootstrap-server 133.186.240.216:19092

kafka-console-consumer --topic my-topic --bootstrap-server 133.186.240.216:19092

```python
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from kafka import KafkaProducer, KafkaConsumer
from kafka.admin import KafkaAdminClient, NewTopic
from datetime import datetime
from airflow.models import TaskInstance

# Define Kafka broker
bootstrap_servers = '133.186.240.216:19092'
topic_name = 'airflowtopic6'

# Function to create Kafka topic
def create_topic():
    admin_client = KafkaAdminClient(bootstrap_servers=bootstrap_servers)
    topic = NewTopic(name=topic_name, num_partitions=1, replication_factor=1)
    admin_client.create_topics([topic])

# Function to check if Kafka is connected
def check_connected():
    try:
        producer = KafkaProducer(bootstrap_servers=bootstrap_servers)
        consumer = KafkaConsumer(topic_name, bootstrap_servers=bootstrap_servers)
        return True
    except Exception as e:
        print(f"Error connecting to Kafka: {str(e)}")
        return False

# Function to produce a message to Kafka
def produce_message():
    producer = KafkaProducer(bootstrap_servers=bootstrap_servers)
    message = f"Hello from Airflow. Message produced at {datetime.now()}"
    producer.send(topic_name, message.encode())
    producer.flush()

# Function to consume a message from Kafka
def consume_message(**context):
    consumer = KafkaConsumer(topic_name, bootstrap_servers=bootstrap_servers, auto_offset_reset='earliest')
    try:
        message = next(consumer)
        print(f"Message consumed: {message.value.decode()}")
        # Mark the task as success
        context['task_instance'].log.info("Message consumed successfully")
        context['task_instance'].state = "success"
    except StopIteration:
        # No message available, mark the task as failed
        context['task_instance'].log.info("No message available to consume")
        context['task_instance'].state = "failed"
    finally:
        # Close the consumer to release resources
        consumer.close()



# Function to finish
def finish():
    print("All tasks completed.")

# Define the DAG
default_args = {
    'owner': 'admin',
    'depends_on_past': False,
    'start_date': datetime(2024, 2, 7),
    'retries': 1,
}

dag = DAG(
    'airflow_kafka_interworking',
    default_args=default_args,
    description='DAG for testing interworking of Airflow and Kafka',
    schedule_interval=None,
)

# Define tasks
create_topic_task = PythonOperator(
    task_id='create_topic',
    python_callable=create_topic,
    dag=dag,
)

check_connected_task = PythonOperator(
    task_id='check_connected',
    python_callable=check_connected,
    dag=dag,
)

produce_message_task = PythonOperator(
    task_id='produce_message',
    python_callable=produce_message,
    dag=dag,
)

consume_message_task = PythonOperator(
    task_id='consume_message',
    python_callable=consume_message,
    dag=dag,
)

finish_task = PythonOperator(
    task_id='finish',
    python_callable=finish,
    dag=dag,
)

# Define task dependencies
create_topic_task >> check_connected_task >> produce_message_task >> consume_message_task >> finish_task

```
---
# 끝~
#### 살펴보면 좋은 글 ref: [kafka의 데이터 저장](https://gunju-ko.github.io/kafka/2019/03/16/%EC%B9%B4%ED%94%84%EC%B9%B4%EA%B0%80%EB%8D%B0%EC%9D%B4%ED%84%B0%EB%A5%BC%EC%A0%80%EC%9E%A5%ED%95%98%EB%8A%94%EB%B0%A9%EB%B2%95.html)

> 마치며..
```
network가 어떻게 돌아가는지 이미지를 연상하여 루트를 그려 볼 것.
통신 테스트를 하는 workflow를 보고 있으니 일단 내부 아이피로 외부에서 접근 하려는 시도도 있고, 외부 아이피가 어디서 쓰이는지, 어떤걸 대변하는지도 잘 몰랐던 것 같음.
외부에서 접근 할 수 있는 public ip는 해당 vm의 내부 아이피를 대변 하는 것 이다.
airflow나 kafka나 설정 하는 것은 그닥 어렵지 않았는데 네트쿼그가 문제라고 생각했지..ㅋ
그리고 python 간단한 예제는 만들 수 있는 정도로 배우고 싶다. gtp말고 ㅠㅠ
```
