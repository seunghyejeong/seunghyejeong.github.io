---
title: Make CustomResources for Airflow Image
author: bami jeong
categories: SelfImprovement
layout: post
comments: true
tags:
  - Airflow
  - Helm
---

## Project Name: Helm Chart로 설치하기 
#### Date: 2024-02-15 09:45 
#### Tag:
---
# Contents:

- [i] 사전 설치 
- Docker

- [!] Version
> Helm airflow-1.12.0 

# Pre

- workspace 만들기 
```bash
mkdir $HOME/airflow && cd airflow 
```

- Dag 저장소 만들기
```bash
mkdir dags && cd dags
```

- kafkatest.py 생성하기
```bash
vi kafkatest.py
```

```bash
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from kafka import KafkaProducer, KafkaConsumer
from kafka.admin import KafkaAdminClient, NewTopic
from datetime import datetime
from airflow.models import TaskInstance
from kafka.errors import TopicAlreadyExistsError

# Define Kafka broker
bootstrap_servers = '133.186.240.216:19092'
topic_name = 'airflow-topic'

# Function to check if Kafka is connected
def check_connected():
    try:
        producer = KafkaProducer(bootstrap_servers=bootstrap_servers)
        consumer = KafkaConsumer(topic_name, bootstrap_servers=bootstrap_servers)
        return True
    except Exception as e:
        print(f"Error connecting to Kafka: {str(e)}")
        return False
        
# Function to create Kafka topic
def create_topic():
    admin_client = KafkaAdminClient(bootstrap_servers=bootstrap_servers)
    existing_topics = admin_client.list_topics()
    # 토픽이 이미 생성 되어 있다면 생성 되어 있는 토픽을 가져온다.
    if topic_name in existing_topics:
        print(f"Topic '{topic_name}' already exists.")
    else:
        topic = NewTopic(name=topic_name, num_partitions=1, replication_factor=1)
        try:
            admin_client.create_topics([topic])
            print(f"Topic '{topic_name}' created successfully.")
        except TopicAlreadyExistsError:
            print(f"Topic '{topic_name}' already exists.")


# Function to produce a message to Kafka
def produce_message():
    producer = KafkaProducer(bootstrap_servers=bootstrap_servers,linger_ms=20)#실시간 스트리밍이 아닌 20초 간격으로 메세지를 전송한다.
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
check_connected_task >> create_topic_task  >> produce_message_task >> consume_message_task >> finish_task
```


# Custom Image 만들기
## 😂
> [[2024-02-15-Make-Custom-Images-forAirflow#Dockerfile..🧐]] 에 뒤이어 작성 했음..

- requirements.txt 작성하기 

```txt
pandas~=2.0.3
requests~=2.31.0
selenium~=4.17.2
beautifulsoup4~=4.12.3
lxml~=5.1.0
kafka-python~=2.0.2
apache-airflow-providers-apache-kafka~=1.3.1
confluent-kafka~=2.3.0
```

- Dockerfile
```dockerfile
FROM apache/airflow:2.8.1  
COPY requirements.txt .

USER root
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
         gcc \
         heimdal-dev \
         default-libmysqlclient-dev \
         pkg-config \
  && apt-get autoremove -yqq --purge \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

USER airflow
RUN pip install --upgrade --no-deps --force-reinstall -r requirements.txt
RUN pip uninstall -y argparse  

EXPOSE 8080  
EXPOSE 8793  
EXPOSE 5555
```

```bash
docker build --no-cache -t seunghyejeong/airflow:1.0 .
docker push seunghyejeong/airflow:1.0
```

# Install by helm (default)

```bash
helm repo add apache-airflow https://airflow.apache.org
helm pull apache-airflow/airflow
helm upgrade --install airflow apache-airflow/airflow --namespace airflow --create-namespace
helm delete airflow --namespace airflow
```

# Custom Values 

1. Custom Image 사용 
```yaml
images:
  airflow:
    repository: seunghyejeong/airflow
    tag: "1.0"
    digest: ~
    pullPolicy: IfNotPresent
```

2. Example 예제 불러오기
```yaml
extraEnv: |
  - name: AIRFLOW__CORE__LOAD_EXAMPLES
    value: 'True'
```

3. Log를 Storage Class에 추가
```yaml
logs:
  persistence:
    enabled: true
    storageClassName: cp-stroageclass
dags:
  persistence:
    enabled: true
    storageClassName: cp-storageclass
```

4. user 설정
```yaml
webserver:
  defaultUser:
    enabled: true
    role: Admin
    username: admin
    email: admin@example.com
    firstName: admin
    lastName: user
    password: admin
```


## Dags files shared by PVC

- [b] REF
> [moung 방법](https://velog.io/@kunheekimkr/Kubernetes-%ED%99%98%EA%B2%BD-%EC%9C%84%EC%97%90-Airflow-%EB%B0%B0%ED%8F%AC%ED%95%98%EA%B8%B0)
> [pvc/pv mount](https://swalloow.github.io/airflow-on-kubernetes-1/)

- PV, PVC 생성 

> PV는 필요 없었네 
~~apiVersion: v1
kind: PersistentVolume
metadata:
  name: airflow-dags
  namespace: airflow
  labels:
    heritage: Helm
    release: airflow
    tier: airflow
spec:
  capacity:
    storage: 20Gi
  accessModes:
    - ReadWriteMany
  nfs:
    server: 172.16.11.19
    path: /home/share/nfs
  persistentVolumeReclaimPolicy: Retain~~ 
  
```yaml
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  annotations:
    volume.beta.kubernetes.io/storage-provisioner: cp-nfs-provisioner
    volume.kubernetes.io/storage-provisioner: cp-nfs-provisioner 
  name: airflow-dags
  namespace: airflow
  labels:
    heritage: Helm
    release: airflow
    tier: airflow
spec:
  storageClassName: "cp-storageclass"
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 10Gi
  volumeMode: Filesystem
```

- Custom Values.yaml 수정 

```yaml
dags:
  persistence:
    enabled: true
    existingClaim: "airflow-dags"
    accessMode: ReadWriteMany
    size: 5Gi
```

# Custom Image, values 적용 하여 설치하기


>설치
```bash
helm upgrade --install airflow apache-airflow/airflow --namespace airflow --create-namespace -f custom_values.yaml
```

> 삭제 
```bash
helm delete airflow --namespace airflow 
```

> custom_values.yaml

```yaml
airflowHome: /home/ubuntu/airflow

# Custom Images (include PyPI Packages)
images:
  airflow:
    repository: seunghyejeong/airflow
    tag: "1.0"
    pullPolicy: IfNotPresent
# Load Examples
extraEnv: |
  - name: AIRFLOW__CORE__LOAD_EXAMPLES
    value: 'True'

# logs bind with stroageClass
logs:
  persistence:
    enabled: true
    storageClassName: cp-stroageclass

# Webserver user configure
webserver:
  defaultUser:
    enabled: true
    role: Admin
    username: admin
    email: admin@example.com
    firstName: admin
    lastName: user
    password: admin            

# dags bind w strogaeClass 
dags:
  persistence:
    enabled: true
    existingClaim: "airflow-dags"
    accessMode: ReadWriteMany
    size: 5Gi

# ingress
ingress:
  enabled: true
  web:
    enabled: true
    annotations: {}
    path: "/"
    pathType: "ImplementationSpecific"
    host: airflow.nip.io
    ingressClassName: "nginx"

webserver:
  service:
    ports:
      - name: airflow-ui
        port: 80
        targetPort: 8080
---
webserver:
  service:
    type: NodePort
    ports:
      - name: airflow-ui
        port: 8080
        targetPort: 8080
        nodePort: 31151

```

```bash
helm install airflow apache-airflow/airflow --namespace airflow -f custom_values.yaml
```


# Dockerfile..🧐

- [b] REF
> [공식 Docs의 Airflow Dockerfile](https://airflow.apache.org/docs/docker-stack/build.html)

? 
```Dockerfile
FROM apache/airflow:2.6.1
USER root
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
     	vim \
  && apt-get autoremove -yqq --purge \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*
USER "${AIRFLOW_UID:-50000}:0"
```

ㅠㅠ
```Dockerfile
FROM apache/airflow:2.8.1
COPY requirements.txt /
USER root
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
         vim \
  && apt-get autoremove -yqq --purge \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*
USER airflow
RUN pip install --no-cache-dir "apache-airflow==2.8.1" -r /requirements.txt
```

### 에러 로그
![[Pasted image 20240215153047.png]]

1. Chart의 Values.yaml을 Original version으로 배포 
- 배포된 `webserver`의  image 를 봤는데 Container에서 'airflow' CLI를 사용하는 것 같다.
```yaml
      containers:
      - args:
        - bash
        - -c
        - exec airflow webserver
        image: apache/airflow:2.8.1
        imagePullPolicy: IfNotPresent
      initContainers:
      - args:
        - airflow
        - db
        - check-migrations
        - --migration-wait-timeout=60
        image: apache/airflow:2.8.1
        imagePullPolicy: IfNotPresent

```

2. 컨테이너 안에 들어와서 echo PATH를 했더니
![[Pasted image 20240215153237.png]]

### 그래서 혹시나 환경 변수 .. ?
```Dockerfile
FROM apache/airflow:2.8.1
RUN echo $PATH
ENV PATH="$PATH:/home/airflow/.local/bin"
RUN echo $PATH
COPY requirements.txt /
RUN pip install --no-cache-dir "apache-airflow==2.8.1" -r /requirements.txt
```

*했더니 설치가 되긴 함;*

끄ㅏㅇㅇㅇㅇㅇㅇㅇㅇㅇㅇㅇㅇㅇㅇㅇㅇㅇㅇㅇㅇㅇㅇㅇㅇㅇㅇㅇㅇㅇㅇㅇㅇㅇㅇㅇㅇㅇㅇㅇㅇㅇㅇㅇㅇㅇㅇㅇㅇㅇㅇㅇㅇㅇㅇㅇㅇㅇㅇㅇㅇㅇㅇㅇㅇㅇㅇㅇㅇㅇㅇㅇㅇ드디어됐어 ㅡㅡ 열받아
![[Pasted image 20240215153507.png]]

*아 home/ubuntu/airflow랑 mount하려 했더니 에러가 자꾸 나서 귀찮아 그래서 log랑 home디렉토리는 defulat로 진행할려 ㅎ* 

- 던져주었습니다 
```bash
kubectl cp ./dags/kafkatest.py airflow-webserver-b744c4466-8tpz8:/opt/airflow/dags/kafkatest.py -n airflow 
```


# 최최최최최최최최ㅗ치치치ㅗ치최종.zip

> 4.2 AirFlow Helm Catalog Repo 추가 > Helm Resource > airflow DIR에 옮겨 놓음


근데 Example dag가 안올라온담.. 암로라라리ㅏ얼ㄴㅇ

```yaml
#airflowHome: /home/ubuntu/airflow
# Custom Images (include PyPI Packages)
images:
  airflow:
    repository: seunghyejeong/airflow
    tag: "1.0"
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