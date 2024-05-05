---
title: Connected Airflow with Kafka (v.Docker)
author: bami jeong
categories: Startups
layout: post
comments: true
tags: 
  - Airflow
---

# Contents:

> 설치 [[2024-02-05-Install-Kafka-Airflow-Docker]]
> [버전 정보](https://log-laboratory.tistory.com/239)

- [i] version
- Docker Compose version v2.24.5
- Docker v2.24
confluentinc 6.1.15
- zookeeper 3.8.3
- kafka 2.7.x
- java 1.8, 11


- [k] airflow 172.16.11.48, 133.186.155.37
- [k] kafka  172.16.11.22, 133.186.240.216

# Kafka

## v1
- docker compose yaml

```yaml
version: '3.8'

networks:
  kafka-default:
    driver: bridge
    
services:
  zookeeper:
    image: bitnami/zookeeper:3.9.1
    ports:
      - "2181:2181"
    environment:
      - ALLOW_ANONYMOUS_LOGIN=yes
  kafka:
    image: bitnami/kafka:3.6.1
    ports:
      - "9093:9093"
    environment: 
      - KAFKA_BROKER_ID=1
      - KAFKA_CFG_ZOOKEEPER_CONNECT=zookeeper:2181 
      - ALLOW_PLAINTEXT_LISTENER=yes 
      - KAFKA_CFG_LISTENER_SECURITY_PROTOCOL_MAP=CLIENT:PLAINTEXT,EXTERNAL:PLAINTEXT 
      - KAFKA_CFG_LISTENERS=CLIENT://:9092,EXTERNAL://:9093 
      - KAFKA_CFG_ADVERTISED_LISTENERS=CLIENT://:9092,EXTERNAL://133.186.155.37:9093 
      - KAFKA_CFG_INTER_BROKER_LISTENER_NAME=CLIENT
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    depends_on: 
      - zookeeper
      
```

# v2

> [dockernetwork](https://log-laboratory.tistory.com/204)
>[Docker compose example](https://log-laboratory.tistory.com/204)
> [Docs](https://developer.confluent.io/faq/apache-kafka/install-and-run/)
>[여러가지 유형의 연결](https://www.confluent.io/blog/kafka-client-cannot-connect-to-broker-on-aws-on-docker-etc/)

- [b] [클라우드배포 listener 설정](https://soobysu.tistory.com/101)
#### 1번 구성 
```yaml
version: "2"

networks:
  default:
    external:
      name: kafka_default


services:
  zookeeper:
    image: confluentinc/cp-zookeeper:6.1.15
    restart: always
    hostname: zookeeper
    ports:
      - "2181:2181"
    environment:
        ZOOKEEPER_CLIENT_PORT: 2181

  broker:
    image: confluentinc/cp-kafka:6.1.15
    hostname: broker
    ports:
      - "9092:9092"
      - "19092:19092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ADVERTISED_LISTENERS: INTERNAL://broker:9092,EXTERNAL://133.186.240.216:19092
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: INTERNAL:PLAINTEXT,EXTERNAL:PLAINTEXT
      KAFKA_INTER_BROKER_LISTENER_NAME: INTERNAL
      KAFKA_ZOOKEEPER_CONNECT: "zookeeper:2181"
      KAFKA_LOG4J_LOGGERS: "kafka.controller=INFO,kafka.producer.async.DefaultEventHandler=INFO,state.change.logger=INFO"
    depends_on:
      - zookeeper

```

```
docker compose -f docker-compose.yaml up -d --remove-orphans
```

#### 2번 구성 (✅ 채택 되었습니다.)
```yaml
version: '2'

networks:
  kafka_default:
    driver: bridge

services:
  zookeeper:
    image: confluentinc/cp-zookeeper:6.1.15
    hostname: zookeeper
    container_name: zookeeper
    ports:
      - "2181:2181"
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181

  broker:
    image: confluentinc/cp-kafka:6.1.15
    hostname: broker
    container_name: broker
    depends_on:
      - zookeeper
    ports:
      - "19092:19092"
      - "9092:9092"
      - "9101:9101"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: 'zookeeper:2181'
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: 'INTERNAL:PLAINTEXT,EXTERNAL:PLAINTEXT'
      KAFKA_ADVERTISED_LISTENERS: 'INTERNAL://broker:9092,EXTERNAL://133.186.240.216:19092'
      KAFKA_INTER_BROKER_LISTENER_NAME: INTERNAL      
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_TRANSACTION_STATE_LOG_MIN_ISR: 1
      KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 1
      KAFKA_GROUP_INITIAL_REBALANCE_DELAY_MS: 0
```


nc -vz broker:9092

#### 토픽 주고받기 

- [b] [토픽 생성](https://www.sktenterprise.com/bizInsight/blogDetail/dev/2565)

- kafka network 
```bash
docker network ls 
```

- 토픽 생성
```
docker compose exec broker kafka-topics --create --topic my-topic --bootstrap-server broker:9092 --replication-factor 1 --partitions 1
```

- 확인하기
```bash
docker-compose exec broker kafka-topics --describe --topic my-topic --bootstrap-server broker:9092 
```

- consumer 실행
```bash
$ docker compose exec broker bash
[appuser@94e94072e1ea ~]$ kafka-console-consumer --topic my-topic --bootstrap-server broker:9092
```

- 프로듀서 실행
```bash
$ docker compose exec broker bash 
[appuser@94e94072e1ea ~]$ kafka-console-producer --topic my-topic --bootstrap-server broker:9092
```

![[Pasted image 20240206155103.png]]


---
##### ref:

# airflow

[[Airflow 활용 Guide]]

pip install confluent-kafka

테스트
```bash
airflow connections test <conn_id>
```

docker-compose exec broker kafka-topics --describe --topic my-topic --bootstrap-server 133.186.240.216:19092

docker compose exec broker kafka-topics --describe --topic external-topic --bootstrap-server 133.186.240.216:19092

docker compose exec broker kafka-topics --create --topic external-topic --bootstrap-server 133.186.240.216:19092 --replication-factor 1 --partitions 1

# cp-kafka Network 

docker inspect 
```bash
                    ],
                    "MacAddress": "02:42:ac:16:00:03",
                    "NetworkID": "6ce489c5617a9f9aa7450e11a47a3c71a2f15903ebf71c758b9516f7ec087f9e",
                    "EndpointID": "b9696b675b56b42194ecf3070d34f0c7daf5dde727e1aa4b64ef63b1e28992c5",
                    "Gateway": "172.22.0.1",
                    "IPAddress": "172.22.0.3",
                    "IPPrefixLen": 16,
                    "IPv6Gateway": "",
                    "GlobalIPv6Address": "",
                    "GlobalIPv6PrefixLen": 0,
                    "DriverOpts": null,
                    "DNSNames": [
                        "broker",
                        "1796d96f4eac"
                    ]

```

ifconfig
```bash
br-6ce489c5617a: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 172.22.0.1  netmask 255.255.0.0  broadcast 172.22.255.255
        inet6 fe80::42:d5ff:fef0:de2c  prefixlen 64  scopeid 0x20<link>
        ether 02:42:d5:f0:de:2c  txqueuelen 0  (Ethernet)
        RX packets 36  bytes 1764 (1.7 KB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 19  bytes 1575 (1.5 KB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

```

