---
title: Use Kafka Function
author: bami jeong
categories: Startups
layout: post
comments: true
tags: 
  - Airflow
---

## Project Name: 로컬에 설치..해보기.

- [b] REF
> [차근차근 카프가 설치와 실헹](https://velog.io/@qlgks1/%EC%B9%B4%ED%94%84%EC%B9%B4-%EC%84%A4%EC%B9%98%EC%99%80-%EC%8B%A4%ED%96%89)
> [window_설치](https://docs.docker.com/desktop/install/windows-install/): 설치 진행 과정
> [[window docker 설치]] : 설치 에러 참고 

- [*] Requirement 
> Docker , Docker-compose 

*- Docker 설치 및 과정은 생략, 위의 파일 링크 참고*
*- 설치의 과정은 `Window 설치`의 보통의 과정을 따름*

---

# INSTALL

## Kafka 맛보기 

1. docker-compose.yaml
```yaml
version: '2'
services:
  zookeeper:
    image: wurstmeister/zookeeper
    ports:
      - "2181:2181"
    restart: unless-stopped
  kafka:
    image: bitnami/kafka:latest
    ports:
      - "9092:9092"
    environment:
      DOCKER_API_VERSION: 1.44
      KAFKA_ADVERTISED_HOST_NAME: 127.0.0.1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    restart: unless-stopped
```

- 설치
```bash
docker-compose up -d
```

- 상태 확인
```bash
docker container ls
```

![[Pasted image 20240202103417.png]]


- kafka 동작 테스트 

> 영어 5자리는 Container ID 앞 다섯 글자 
```bash
docker exec -it ffe4a /bin/bash 
```

- Topic 생성 
```bash
$ cd /bin # 원활한 test를 위해 우선 bin 디렉토리로 가자
$ kafka-topics.sh --create --topic quickstart-events --bootstrap-server localhost:9092
$ kafka-topics.sh --describe --topic quickstart-events --bootstrap-server localhost:9092 
```

---
- [i] --create: 새로운 토픽 생성 만들 때 사용하는 옵션
- [i] --topic: Topic명, Topic은 (")로 묶고 정규식 사용이 가능하므로 \로 escape한다 (?)
- [i] --describe: 운영에 필요한 Topic 상세정보 보기
- [i] --bootstrap-server: 연결할 Kafka 서버 (host:port), 이 옵션이 추가되면 직접 Zookeeper에 연결하지 않아도 된다.
- [i] --replication-fator: Partition의 복제 수. 지정 안 할 시 Defalt 값
    - [i] `server.properties`의 `default.replication.facor`에서 설정 가능
    - [*] partition이란 Topic을 여러 Broker에 분산 저장 시 분산 저장된 Topic을 Partition이라 한다.
---

- 출력
```bash
Topic: quickstart-events        TopicId: G1OMQcJqSF2Y4_AhL1j09A PartitionCount: 1       ReplicationFactor: 1    Configs:
        Topic: quickstart-events        Partition: 0    Leader: 1001    Replicas: 1001  Isr: 1001
```

- kafka 서버에게 Topic에 해당하는 Event 추가
> 생성된 "Topic"을 Kafka server에서는 "Event"라고 부른다

Topic명: quickstart-events
- Kafka에게 이벤트 발생시키는 `producer`
```bash
kafka-console-producer.sh --topic quickstart-events --bootstrap-server localhost:9092 # 얘를 치면 서버 접속해서 '>' 만 뜨게 되어 있다. 당황하지 말고 추가할 이벤트 추가해보자.
```

보낸 이벤트
```bash
>this is my first event bami
>bami is my friend
```


- Topic을 구독하고 얻어낸 이벤트를 처리하는 `consumer `
```bash
kafka-console-consumer.sh --topic quickstart-events --from-beginning --bootstrap-server localhost:9092 # 얘를 치면 위에서 서버에 접속 해서 보낸 event를 확인할 수 있다. 
```

구독한 토픽에서 얻어낸 이벤트
```bash
I have no name!@ffe4ab99902c:/bin$ kafka-console-consumer.sh --topic quickstart-events --from-beginning --bootstrap-server localhost:9092
this is my first event bami
bami is my friend
```





## 실습: Cluster 만들기

- 고가용성(HA)를 위해 최소 3개의 클러스터 만들기를 권장하지만 먼저 standAlone으로 구성 해볼 것 임.
- Python으로 작성한다.

- [b] REF
> [카프카-클러스터-설정하기](https://velog.io/@qlgks1/%EC%B9%B4%ED%94%84%EC%B9%B4-%ED%81%B4%EB%9F%AC%EC%8A%A4%ED%84%B0%EC%99%80-%ED%8C%8C%EC%9D%B4%EC%8D%AC)

---

1. Docker-compose.yaml 작성하기

    - Zookeeper Container , Kafka Cluster 총 두 가지의 컨테이너를 만든다.
    - Zookeeper와 Cluster를 1:1 매칭 (필수는 아니지만 하나의 클러스터를 모니터링 하기 위해서 1:1 매칭을 권장한다.)
### docker-compose

- Zookeeper
```yaml
version: "3.5"
## 빈칸 꼭 필요함 ## 
services:
  bami-zoo:
    image: zookeeper:3.9.1-jre-11
    hostname: bami-zoo
    container_name: bami-zoo
    ports:
      - "2181:2181"
    volumes:
      - ../zookeeper/data/1:/data
      - ../zookeeper/datalog/1:/datalog
      - ../zookeeper/logs/1:/logs
    networks:
      - bami-kafka-cluster-network
    environment:
      ZOOKEEPER_SERVER_ID: 1
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_SERVERS: server.1=bami-zoo:2888:3888
```

- `Default ports`는 `2181`이고 추가 될 때마다 `+1` 된다.
- `ZOOKEEPER_SERVER`란 *데이터 동기화 및 쿼럼 유지를 위해* 서로 통신하는 데에 사용된다.
    - Quorum(쿼럼)은 분산 시스템에서 작업을 수행하기 위해 분산 트랜잭션이 얻어야 하는 최소 득표 수.
    - 외부에 공개될 필요 없고 인터넷 네트워크에서만 서로 포트에 접근할 수 있으면 된다.
    - Zookeeper의 Quorum은 "리더"와 "팔로워"를 선출하는 개념에서 시작해 리더주키퍼가 공유 데이터 및 업데이트 사항을 팔로워 주키퍼에게 보도한다.
        - 이 때 사용하는 포트가 2888:3888 이며 리더와 팔로워가 통신하는 상태라고 보면 된다
        - 이는 즉 *ZOOKEEPER가 각자의 상태를 동기화* 한다고 보면 된다. 
        - 이 때 값이 같은지 상태를 체크하게 되고 그러므로 이 포트는 동시에 작동하게 된다.
---

- Kafka
```yaml
  bami-kafka:
    image: wurstmeister/kafka:2.13-2.8.1
    hostname: bami-kafka
    container_name: bami-kafka
    ports:
      - "9092:9092"
      - "19092"
    volumes:
      - ../kafka/logs/1:/kafka/logs
    networks:
      - bami-kafka-cluster-network
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_PRODUCER_MAX_REQUEST_SIZE: 536870912
      CONNECT_PRODUCER_MAX_REQUEST_SIZE: 536870912
      KAFKA_LISTENERS: INSIDE://bami-kafka:19092,OUTSIDE://0.0.0.0:9092
      KAFKA_ADVERTISED_LISTENERS: INSIDE://bami-kafka:19092,OUTSIDE://127.0.0.1:9092
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: INSIDE:PLAINTEXT,OUTSIDE:PLAINTEXT
      KAFKA_INTER_BROKER_LISTENER_NAME: INSIDE
      KAFKA_ZOOKEEPER_CONNECT: "bami-zoo:2181"
      KAFKA_LOG_DIRS: "/kafka/logs"
      KAFKA_LOG4J_LOGGERS: "kafka.controller=INFO,kafka.producer.async.DefaultEventHandler=INFO,state.change.logger=INFO"
      KAFKA_JMX_OPTS: "-Dcom.sun.management.jmxremote -Dcom.sun.management.jmxremote.authenticate=false -Dcom.sun.management.jmxremote.ssl=false -Djava.rmi.server.hostname=bami-kafka -Dcom.sun.management.jmxremote.rmi.port=9992"
      JMX_PORT: 9992
    depends_on:
      - bami-zoo

networks:
  bami-kafka-cluster-network:
    driver: bridge
```

- Image **wurstmeister/kafka:latest**를 사용한다. `confluentinc` image는 full-featured kafka installation이라 하여 Kafka Connect, Kafka Stream 등 모든 서비스는 제공하는 이미지로, 대규모 엔터프라이즈 환경을 구성할 때 사용된다.
- **Kafka env 값은 중요하다.**
    - KAFKA_BROKER_ID: Kafka 클러스터에서 broker를 위한 Unique 값
    - KAFKA_PRODUCER_MAX_REQUEST_SIZE
    - CONNECT_PRODUCER_MAX_REQUEST_SIZE
    - LISTENERS
        - *분산 시스템*: producer와 cunsumer(즉, Client)는 분산된 파티션에 접근하여 `wirte/read`를 수행한다. 
        - 클러스터로 묶인 경우에는 단 하나의 클러스터만이 `wirte/read` 권한이 있다.
        - VM이나 Docker를 이용하는 `Cloud 환경`을 사용할 경우 네트워크의 설정이 복잡해지며 IN-OUT의 경로가 달라져야 한다.
        - 그래서 내부에서는 `plaintext`로 외부에서는 `ssl`로 통신 하도록 하는 **구분**이 필요하다.
            - KAFKA_LISTENERS(listners)
                - 카프카 브로커가 내부적으로 바인딩 하는 주소
                - `CLIENT:...`, `INTERNAL:...`, `INSIDE...`라는 명칭을 많이 쓴다.
                - *같은 네트워크 환경*에서 *내부적*으로 통신 할 때 쓰인다.
            - KAFKA_ADVERTISED_LISTENERS(advertised.listeners)
                - Kafka Client에게 노출 할 주소 
                - *다른 네트워크 환경*에서 *외부적*으로 통신 할 때 쓰인다.
            - KAFKA_LISTENER_SECURITY_PROTOCOL_MAP
                - *내부*, *외부*에서 사용하려는 프로토콜을 명시한다.
                - 내부에서는 plaintext, 외부에서는 ssl을 원할 때 쓰인다.
                - 현 예제에서는 모두 plaintext를 사용한다.
            - KAFKA_INTER_BROKER_LISTENER_NAME
                - Kafka 브로커가 내부적으로 바인딩 하는 주소에서 사용하는 `이름값`이다 
                - 필수는 아니지만 KAFKA_LISTENER에서 다양한 이름을 사용 하기 때문에 따로 추가 설정을 하는 것
                - *LISTENER*들의 이름은 모두 **모두 통일 해야 한다**
    - KAFKA_ZOOKEEPER_CONNECT
        - Kafka Cluster에서 사용하는 zookeeper의 List를 모두 명시해야 한다
        - (,)와 `<hostname>:<port>`로 구분한다

- [?] AirFlow 연결 시 필요 할 것 같은데 , ,
![[Pasted image 20240202131650.png]]

### Event 만들기 
> Kafka에서 진행 

- kafka shell 기반으로 이벤트 만들기기

```bash
docker exec -it bami-kafka /bin/bash
```

```bash
kafka-topics.sh --create --zookeeper bami-zoo:2181 --replication-factor 1 --partitions 1 --topic my-topic
```

#### error
![[Pasted image 20240202143305.png]]
에러가 나서 블로그 글을 자세히 읽어보니 .. 
![[Pasted image 20240202143328.png]]

그래서 docker-compose.ymal의 `JMX_PORT`를 주석처리 후 재설치 진행했다.

- image 삭제 후 재작동
```bash
docker-compose up --remove-orphans -d
```
- [i] 포트삭제: [[Window CMD 명령어]]
- Topic 생성
```bash
root@bami-kafka:/# kafka-topics.sh --create --zookeeper bami-zoo:2181 --replication-factor 1 --partitions 1 --topic my-topic
Created topic my-topic.
```

- event 생성 
> producer 
```bash
kafka-console-producer.sh --broker-list localhost:9092 --topic my-topic
```

```bash
root@bami-kafka:/# kafka-console-producer.sh --broker-list localhost:9092 --topic my-topic
>bami
>cute
>mine
```

- event 받기 
> consumer 

```bash 
kafka-console-consumer.sh --topic my-topic --from-beginning --bootstrap-server localhost:9092 ** Cluster를 하나만 만들었기 때문에 
```

```bash
root@bami-kafka:/# kafka-console-consumer.sh --topic my-topic --from-beginning --bootstrap-server localhost:9092
bami
cute
mine
```





--- 
# Python & Kafa Cluster
## Python library를 활용한다

- [*] Requirement
> python 3.10.11
>REF: [python 코드까지 완벽](https://velog.io/@qlgks1/%EC%B9%B4%ED%94%84%EC%B9%B4-%ED%81%B4%EB%9F%AC%EC%8A%A4%ED%84%B0%EC%99%80-%ED%8C%8C%EC%9D%B4%EC%8D%AC)
1. library 설치
```bash
pip install kafka-python
```





---



# Airflow와의 통합 .. 

> Airflow config에 `localhost:9092`는.. 자기 자신의 9092를 찌르는 것이랑 같기 때문에,, 로컬에 설치된 kafka와는 통신이 안될거..같다..?!

- [b] REF
> [airflow-kafka Docs](https://airflow.apache.org/docs/apache-airflow-providers-apache-kafka/stable/index.html)
> [네트워크 연결 ](https://www.confluent.io/blog/kafka-listeners-explained/)



```yaml
  bami-kafka:
    image: wurstmeister/kafka:2.13-2.8.1
    hostname: bami-kafka
    container_name: bami-kafka
    ports:
      - "9092:9092"
      - "19092"
    volumes:
      - ../kafka/logs/1:/kafka/logs
    networks:
      - bami-kafka-cluster-network
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_PRODUCER_MAX_REQUEST_SIZE: 536870912
      CONNECT_PRODUCER_MAX_REQUEST_SIZE: 536870912
      KAFKA_LISTENERS: INTERNAL://0.0.0.0:19092,EXTERNAL://0.0.0.0:9092
      KAFKA_ADVERTISED_LISTENERS: INTERNAL://bami-kafka:19092,EXTERNAL://0.0.0.0:9092
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: INTERNAL:PLAINTEXT,EXTERNAL:PLAINTEXT
      KAFKA_INTER_BROKER_LISTENER_NAME: INTERNAL
      KAFKA_ZOOKEEPER_CONNECT: "bami-zoo:2181"
      KAFKA_LOG_DIRS: "/kafka/logs"
      KAFKA_LOG4J_LOGGERS: "kafka.controller=INFO,kafka.producer.async.DefaultEventHandler=INFO,state.change.logger=INFO"
      KAFKA_JMX_OPTS: "-Dcom.sun.management.jmxremote -Dcom.sun.management.jmxremote.authenticate=false -Dcom.sun.management.jmxremote.ssl=false -Djava.rmi.server.hostname=bami-kafka -Dcom.sun.management.jmxremote.rmi.port=9992"
      JMX_PORT: 9992
    depends_on:
      - bami-zoo

networks:
  bami-kafka-cluster-network:
    driver: bridge
```