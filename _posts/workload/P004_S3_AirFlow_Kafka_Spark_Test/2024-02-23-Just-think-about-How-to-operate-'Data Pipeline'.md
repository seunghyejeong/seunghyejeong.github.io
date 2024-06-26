---
title: Just think about How to operate 'Data Pipeline'
author: bami jeong
categories: mumbling
layout: post
comments: true
tags:
  - DataPipeline
  - Spark
  - Airflow
  - Docker
  - Kafka
---


- [b] REF
> [kafka-spark-구축 운영기](https://medium.com/team-joon/%EC%B4%88%EB%8B%B9-10000%EA%B1%B4%EC%9D%98-%EB%A1%9C%EA%B7%B8%EB%A5%BC-%EC%B2%98%EB%A6%AC%ED%95%B4%EB%B3%B4%EC%9E%90-edc9a3c620f1)
> [우아한형제 Kafka 운영환경 유튜브](https://www.youtube.com/watch?v=XyuqoWUCdGA)
> [kafka 6.2.14](https://docs.confluent.io/platform/6.2/installation/installing_cp/zip-tar.html)

# ...
Airflow는 하나의 클러스터 (1 Master / 2 Worker) 환경에 pod로 올리고 kafka와 zookeeper는 하나의 클러스터 다른 Node에 Docker container로 띄움.
운영 환경에서 적합한가 ? 를 생각해보게 됨. 
(의미있나..싶기도함..)

# test
- 각 다른 Node에 Spark도 서버로 설치하는 것으로 하고 , Kafka Spark를 함꼐 설치 해볼것임

## Kafka

이전에 설치했던 버전을 그대로 사용함 [[Airflow & Kafka 연동 가이드 v2]]

- confluentic kafka 

```bash
curl -O https://packages.confluent.io/archive/6.2/confluent-6.2.14.tar.gz
```

- ubuntu 
```
wget -qO - https://packages.confluent.io/deb/6.2/archive.key | sudo apt-key add -
```

```
sudo add-apt-repository "deb [arch=amd64] https://packages.confluent.io/deb/6.2 stable main"
```

```
sudo apt-get update && sudo apt-get install confluent-community-2.13
```

- 로그 보기
```bash
journalctl -xefu confluent-kafka
```

# Meet Errrrrrrr 1)

> [!failure] 
> 
> requirement failed: advertised.listeners listener names must be equal to or a subset of the ones defined in listeners. Found INTERNAL,EXTERNAL. The valid options base of the ones defined in listeners. Found INTERNAL,EXTERNAL. The valid options based on the current configuration are INTERNAL

- 아래와 같이 파일을 수정해 주었다.
```yaml
 KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_LISTENERS: LISTENER_BOB://kafka0:29092,LISTENER_FRED://kafka0:9092,LISTENER_ALICE://kafka0:29094
      KAFKA_ADVERTISED_LISTENERS: LISTENER_BOB://kafka0:29092,LISTENER_FRED://localhost:9092,LISTENER_ALICE://never-gonna-give-you-up:29094
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: LISTENER_BOB:PLAINTEXT,LISTENER_FRED:PLAINTEXT,LISTENER_ALICE:PLAINTEXT
      KAFKA_INTER_BROKER_LISTENER_NAME: LISTENER_BOB
```

# Meet Errrrrrrr 2)

> [!failure] 
> 
> Socket server failed to bind to 133.186.221.113:19092: Cannot assign requested address
> 
> Loaded: loaded (/lib/systemd/system/confluent-kafka.service; disabled; vendor preset: enabled)
> Active: failed (Result: exit-code) since Fri 2024-02-23 15:58:07 KST; 9s ago
> Docs: http://docs.confluent.io/
> Process: 383956 ExecStart=/usr/bin/kafka-server-start /etc/kafka/server.properties (code=exited, status=127)
   Main PID: 383956 (code=exited, status=127)
   >
   Feb 23 15:58:07 bami-cluster3 systemd[1]: Started Apache Kafka - broker.
Feb 23 15:58:07 bami-cluster3 kafka-server-start[383956]: /usr/bin/kafka-run-class: line 345: exec: java: not found
Feb 23 15:58:07 bami-cluster3 systemd[1]: confluent-kafka.service: Main process exited, code=exited, status=127/
> 

- 이유:  Java가 없었다.
# Meet Errrrrrrr 3)

> [!failure] 
> 
advertised.listeners listener names must be equal to or a subset of the ones defined in listeners. Found INTERNAL,EXTERNAL. The valid options based on the current configuration are INTERNAL

- 이유: listener에도 advertised.listenr에 정의한 Internal, External 모두 기입 하여야 함.


