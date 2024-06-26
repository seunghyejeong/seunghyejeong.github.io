---
title: Install Kafka&Airflow by Docker
author: bami jeong
categories: Startups
layout: post
comments: true
tags: 
  - Airflow
---


# Contents:

## Airflow: Docker 설치 
> library 설치 할 때에는 컨테이너를 접속해서 설치 해 주어야 한다.
> 

### airflow 설치

```bash
curl -LfO 'https://airflow.apache.org/docs/apache-airflow/2.8.1/docker-compose.yaml'
```

- 환경 설정
```bash
mkdir -p ./dags ./logs ./plugins ./config
echo -e "AIRFLOW_UID=$(id -u)" > .env
```

```bash
AIRFLOW_UID=50000
```

- 데이터베이스 초기화
```bash
sudo docker compose up airflow-init
```

- output
```bash
airflow-init-1  | [2024-02-05T00:52:45.573+0000] {override.py:1820} INFO - Added Permission menu access on Permission Pairs to role Admin
airflow-init-1  | [2024-02-05T00:52:46.675+0000] {override.py:1458} INFO - Added user airflow
airflow-init-1  | User "airflow" created with role "Admin"
airflow-init-1  | 2.8.1
airflow-init-1 exited with code 0

```

- Airflow 실행
```bash
sudo docker compose up
```

> ID : airflow
>PW: airflow

### CLI 설치

- 설치 
```bash
sudo docker compose run airflow-worker airflow info
```

- 추가 스크립트
```bash
curl -LfO 'https://airflow.apache.org/docs/apache-airflow/2.8.1/airflow.sh'
chmod +x airflow.sh
```

- 사용 
```bash
sudo ./airflow.sh info
sudo ./airflow.sh bash
sudo ./airflow.sh python
```

### 삭제 

- 파일을 다운로드한 디렉터리에서 명령을 실행하세요 .`docker compose down --volumes --remove-orphans``docker-compose.yaml`
    
- `docker-compose.yaml`파일을 다운로드한 전체 디렉터리를 제거합니다.`rm -rf '<DIRECTORY>'`
    
- `docker-compose.yaml`파일 을 다시 다운로드하여 처음부터 이 가이드를 실행해 보세요


## Kakfa: Docker 설치

~~- docker-compose.yaml~~
```yaml
version: '3'

services:
  zoo1:
    image: confluentinc/cp-zookeeper:7.3.2
    ports:
      - "2181:2181"
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_SERVER_ID: 1
      ZOOKEEPER_SERVERS: zoo1:2888:3888
    networks:
      - kafka-network
      - airflow-kafka

  kafka1:
    image: confluentinc/cp-kafka:7.3.2
    ports:
      - "9092:9092"
      - "29092:29092"
    environment:
      KAFKA_ADVERTISED_LISTENERS: INTERNAL://kafka1:19092,EXTERNAL://${DOCKER_HOST_IP:-127.0.0.1}:9092,DOCKER://host.docker.internal:29092
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: INTERNAL:PLAINTEXT,EXTERNAL:PLAINTEXT,DOCKER:PLAINTEXT
      KAFKA_INTER_BROKER_LISTENER_NAME: INTERNAL
      KAFKA_ZOOKEEPER_CONNECT: "zoo1:2181"
      KAFKA_BROKER_ID: 1
      KAFKA_LOG4J_LOGGERS: "kafka.controller=INFO,kafka.producer.async.DefaultEventHandler=INFO,state.change.logger=INFO"
      KAFKA_AUTHORIZER_CLASS_NAME: kafka.security.authorizer.AclAuthorizer
      KAFKA_ALLOW_EVERYONE_IF_NO_ACL_FOUND: "true"
    networks:
      - kafka-network
      - airflow-kafka

  kafka2:
    image: confluentinc/cp-kafka:7.3.2
    ports:
      - "9093:9093"
      - "29093:29093"
    environment:
      KAFKA_ADVERTISED_LISTENERS: INTERNAL://kafka2:19093,EXTERNAL://${DOCKER_HOST_IP:-127.0.0.1}:9093,DOCKER://host.docker.internal:29093
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: INTERNAL:PLAINTEXT,EXTERNAL:PLAINTEXT,DOCKER:PLAINTEXT
      KAFKA_INTER_BROKER_LISTENER_NAME: INTERNAL
      KAFKA_ZOOKEEPER_CONNECT: "zoo1:2181"
      KAFKA_BROKER_ID: 2
      KAFKA_LOG4J_LOGGERS: "kafka.controller=INFO,kafka.producer.async.DefaultEventHandler=INFO,state.change.logger=INFO"
      KAFKA_AUTHORIZER_CLASS_NAME: kafka.security.authorizer.AclAuthorizer
      KAFKA_ALLOW_EVERYONE_IF_NO_ACL_FOUND: "true"
    networks:
      - kafka-network
      - airflow-kafka

  kafka3:
    image: confluentinc/cp-kafka:7.3.2
    ports:
      - "9094:9094"
      - "29094:29094"
    environment:
      KAFKA_ADVERTISED_LISTENERS: INTERNAL://kafka3:19094,EXTERNAL://${DOCKER_HOST_IP:-127.0.0.1}:9094,DOCKER://host.docker.internal:29094
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: INTERNAL:PLAINTEXT,EXTERNAL:PLAINTEXT,DOCKER:PLAINTEXT
      KAFKA_INTER_BROKER_LISTENER_NAME: INTERNAL
      KAFKA_ZOOKEEPER_CONNECT: "zoo1:2181"
      KAFKA_BROKER_ID: 3
      KAFKA_LOG4J_LOGGERS: "kafka.controller=INFO,kafka.producer.async.DefaultEventHandler=INFO,state.change.logger=INFO"
      KAFKA_AUTHORIZER_CLASS_NAME: kafka.security.authorizer.AclAuthorizer
      KAFKA_ALLOW_EVERYONE_IF_NO_ACL_FOUND: "true"
    networks:
      - kafka-network
      - airflow-kafka

  kafka-connect:
    image: confluentinc/cp-kafka-connect:7.3.2
    ports:
      - "8083:8083"
    environment:
      CONNECT_BOOTSTRAP_SERVERS: kafka1:19092,kafka2:19093,kafka3:19094
      CONNECT_REST_PORT: 8083
      CONNECT_GROUP_ID: compose-connect-group
      CONNECT_CONFIG_STORAGE_TOPIC: compose-connect-configs
      CONNECT_OFFSET_STORAGE_TOPIC: compose-connect-offsets
      CONNECT_STATUS_STORAGE_TOPIC: compose-connect-status
      CONNECT_KEY_CONVERTER: org.apache.kafka.connect.storage.StringConverter
      CONNECT_VALUE_CONVERTER: org.apache.kafka.connect.storage.StringConverter
      CONNECT_INTERNAL_KEY_CONVERTER: "org.apache.kafka.connect.json.JsonConverter"
      CONNECT_INTERNAL_VALUE_CONVERTER: "org.apache.kafka.connect.json.JsonConverter"
      CONNECT_REST_ADVERTISED_HOST_NAME: 'kafka-connect'
      CONNECT_LOG4J_ROOT_LOGLEVEL: 'INFO'
      CONNECT_LOG4J_LOGGERS: 'org.apache.kafka.connect.runtime.rest=WARN,org.reflections=ERROR'
      CONNECT_PLUGIN_PATH: '/usr/share/java,/usr/share/confluent-hub-components'
    networks:
      - kafka-network
      - airflow-kafka

  schema-registry:
    image: confluentinc/cp-schema-registry:7.3.2
    ports:
      - "8081:8081"
    environment:
      SCHEMA_REGISTRY_KAFKASTORE_BOOTSTRAP_SERVERS: kafka1:19092,kafka2:19093,kafka3:19094
      SCHEMA_REGISTRY_HOST_NAME: schema-registry
      SCHEMA_REGISTRY_LISTENERS: http://0.0.0.0:8081
    networks:
      - kafka-network
      - airflow-kafka

  kafka-ui:
    container_name: kafka-ui-1
    image: provectuslabs/kafka-ui:latest
    ports:
      - 8888:8080 # Changed to avoid port clash with akhq
    depends_on:
      - kafka1
      - kafka2
      - kafka3
      - schema-registry
      - kafka-connect
    environment:
      KAFKA_CLUSTERS_0_NAME: local
      KAFKA_CLUSTERS_0_BOOTSTRAPSERVERS: PLAINTEXT://kafka1:19092,PLAINTEXT_HOST://kafka1:19092
      KAFKA_CLUSTERS_0_SCHEMAREGISTRY: http://schema-registry:8081
      KAFKA_CLUSTERS_0_KAFKACONNECT_0_NAME: connect
      KAFKA_CLUSTERS_0_KAFKACONNECT_0_ADDRESS: http://kafka-connect:8083
      DYNAMIC_CONFIG_ENABLED: 'true'
    networks:
      - kafka-network
      - airflow-kafka

```
❌ : confluentinc 사용 안 하게 됨 
### kafka-network

- [b] REF
> [docker network ls](https://medium.com/@underwater2/kafka-docker-compose%EB%A1%9C-%EA%B5%AC%EC%84%B1%EB%90%9C-kafka-cluster%EC%97%90-schema-registry-%EC%B6%94%EA%B0%80%ED%95%98%EA%B8%B0-011700ed488d)
> [Docker_host ip](https://github.com/docker/compose/issues/2915)

### kafka install by Docker

- [b] REF
> [wurstmeister](https://github.com/wurstmeister/kafka-docker.git)
> [public ip 설정](https://velog.io/@divan/kafka-docker-%EB%A1%9C%EC%BB%AC-%EC%84%B8%ED%8C%85)
```bash
git clone https://github.com/wurstmeister/kafka-docker.git
```

```bash
vim docker-compose-single-broker.yml
```

- docker-compose-single-broker.yml
```yaml
version: '2'
services:
  zookeeper:
    image: wurstmeister/zookeeper
    ports:
      - "2181:2181"
  kafka:
    build: .
    ports:
      - "9092:9092"
    environment:
      KAFKA_BROKER_ID: 1
      #KAFKA_ADVERTISED_HOST_NAME: 127.0.0.1
      KAFKA_CREATE_TOPICS: "test:1:1"
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://133.186.217.113:9092 #통신을 위
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock

```

- 컨테이너 접속
```bash
docker exec -ti {CONTAINER_NUM} /bin/bash
```

- advertised Listeners 확인 
```bash
cd /opt/kafka/config
vi server.properties

# 127.0.0.1 이어야 함 
```

- Topic list 확인
```bash
kafka-topics.sh --list --bootstrap-server  127.0.0.1:9092
```

- topic 생성
```bash
 ./kafka-console-producer.sh --bootstrap-server 127.0.0.1:9092 --topic msg_test
```

- 메세지 생성
```bash
 ./kafka-console-producer.sh --bootstrap-server 127.0.0.1:9092 --topic msg_test
```

- 메세지 받기
```bash
./kafka-console-consumer.sh --bootstrap-server 127.0.0.1:9092 --topic msg_test --from-beginning
```

~~## Python 예제~~

- producer.py

```python
from kafka import KafkaProducer
from json import dumps
import time

producer = KafkaProducer(
    acks=0,
    compression_type="gzip",
    bootstrap_servers=['133.186.217.113:9092'],
    api_version=(2, 8, 1),  # Set this to match your Kafka broker version
    value_serializer=lambda x: dumps(x).encode("utf-8")
)

start = time.time()

for i in range(10):
    data = {'str' : 'result'+str(i)}
    producer.send('msg_test', value=data)
    producer.flush()

print('[Done]:', time.time() - start)

```

- consumer.py

```python 
from kafka import KafkaConsumer
from json import loads

consumer = KafkaConsumer(
    'msg_test', # 토픽명
    bootstrap_servers=['133.186.217.113:9092'], # 카프카 브로커 주소 리스트
    auto_offset_reset='earliest', # 오프셋 위치(earliest:가장 처음, latest: 가장 최근)
    enable_auto_commit=True, # 오프셋 자동 커밋 여부
    group_id='test-consumer-group', # 컨슈머 그룹 식별자
    value_deserializer=lambda x: loads(x.decode('utf-8')), # 메시지의 값 역직렬화
    consumer_timeout_ms=1000 # 데이터를 기다리는 최대 시간
)

print('[Start] get consumer')

for message in consumer:
    print(f'Topic : {message.topic}, Partition : {message.partition}, Offset : {message.offset}, Key : {message.key}, value : {message.value}')

print('[End] get consumer')

```


# 2023-02-06 할일 


- [b] https://github.com/wurstmeister/kafka-docker/blob/master/README.md
- [ ] 
## Listener Configuration

It may be useful to have the [Kafka Documentation](https://kafka.apache.org/documentation/) open, to understand the various broker listener configuration options.

Since 0.9.0, Kafka has supported [multiple listener configurations](https://issues.apache.org/jira/browse/KAFKA-1809) for brokers to help support different protocols and discriminate between internal and external traffic. Later versions of Kafka have deprecated `advertised.host.name` and `advertised.port`.

**NOTE:** `advertised.host.name` and `advertised.port` still work as expected, but should not be used if configuring the listeners.

```yaml
version: '2'
services:
  zookeeper:
    image: wurstmeister/zookeeper
    ports:
      - "2181:2181"
  kafka:
    build: .
    ports:
      - "9092:9092"
      - "19092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_MESSAGE_MAX_BYTES: 2000000
      KAFKA_CREATE_TOPICS: "kafkatopic:1:1"
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_LISTENERS: INSIDE://:9092,OUTSIDE://:19092
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: INSIDE:PLAINTEXT,OUTSIDE:PLAINTEXT
      KAFKA_ADVERTISED_LISTENERS: INSIDE://:9092,OUTSIDE://133.186.217.113:19092 
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
```

```
HOSTNAME_COMMAND: curl http://169.254.169.254/latest/meta-data/public-hostname
KAFKA_ADVERTISED_LISTENERS: INSIDE://:9092,OUTSIDE://_{HOSTNAME_COMMAND}:9094
KAFKA_LISTENERS: INSIDE://:9092,OUTSIDE://:9094
KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: INSIDE:PLAINTEXT,OUTSIDE:PLAINTEXT
KAFKA_INTER_BROKER_LISTENER_NAME: INSIDE
```

```yaml
  daa-kafka1:
    image: wurstmeister/kafka:2.13-2.8.1
    hostname: daa-kafka1
    container_name: daa-kafka1
    ports:
      - "9092:9092"
      - "19092"
    volumes:
      - ../kafka/logs/1:/kafka/logs
    networks:
      - daa-kafka-cluster-network
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_PRODUCER_MAX_REQUEST_SIZE: 536870912
      CONNECT_PRODUCER_MAX_REQUEST_SIZE: 536870912
      KAFKA_LISTENERS: INSIDE://daa-kafka1:19092,OUTSIDE://0.0.0.0:9092
      KAFKA_ADVERTISED_LISTENERS: INSIDE://daa-kafka1:19092,OUTSIDE://127.0.0.1:9092
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: INSIDE:PLAINTEXT,OUTSIDE:PLAINTEXT
      KAFKA_INTER_BROKER_LISTENER_NAME: INSIDE
      KAFKA_ZOOKEEPER_CONNECT: "daa-zoo1:2181,daa-zoo2:2182,daa-zoo3:2183"
      KAFKA_LOG_DIRS: "/kafka/logs"
      KAFKA_LOG4J_LOGGERS: "kafka.controller=INFO,kafka.producer.async.DefaultEventHandler=INFO,state.change.logger=INFO"
      KAFKA_JMX_OPTS: "-Dcom.sun.management.jmxremote -Dcom.sun.management.jmxremote.authenticate=false -Dcom.sun.management.jmxremote.ssl=false -Djava.rmi.server.hostname=daa-kafka1 -Dcom.sun.management.jmxremote.rmi.port=9992"
      JMX_PORT: 9992
    depends_on:
      - daa-zoo1
      - daa-zoo2
      - daa-zoo3
```