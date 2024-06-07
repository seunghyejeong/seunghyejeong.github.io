---
title: What is Spark?
author: bami jeong
categories: Build
layout: post
comments: true
tags:
  - DataPipeline
  - Spark
  - Airflow
  - Docker
  - Kafka
---


> [!todo] 
> 1. Docker compose로 Kafka, Spark를 구축한다.
>     1. Kafka
>         - Topic 이름 : devices
>         - 내부 연결 DNS: broker
>         - Docker Container 구축 
> 1. Airflow와 연동한다.


## Spark 알아보기


- [b] REF
> [스칼라/스파크 설치](https://robomoan.medium.com/ubuntu-%ED%99%98%EA%B2%BD%EC%97%90%EC%84%9C-apache-spark-%EC%84%A4%EC%B9%98%ED%95%98%EA%B8%B0-c81d0cf332e3)
> [스칼라 다운로드-공식홈페이지](https://spark.apache.org/downloads.html)
> [스파크 3.4.2 버전(스칼라 2.13버전)](https://www.apache.org/dyn/closer.lua/spark/spark-3.4.2/spark-3.4.2-bin-hadoop3-scala2.13.tgz)
> [스파크 버전..](https://archive.apache.org/dist/spark/spark-3.3.0/)


# PySpark - Kafka streaming 이용해 연동한다.

![[Pasted image 20240220164849.png]]

: Kafka Broker에 저장된 토픽을 PySpark를 이용해 실시간 스트리밍하기

- [b] REF
> [Jar파일 다운 받아 스파크 연동](https://velog.io/@statco19/pyspark-kafka-streaming)
> [kafka maven repository](https://mvnrepository.com/artifact/org.apache.spark/spark-sql-kafka-0-10)

# Kafka 연동과 실시간 스트리밍을 위한 jar파일을 알아본다.

1. 필요한 jar 파일 
```
kafka-clients-2.5.0.jar
spark-streaming-kafka-0-10_2.12-3.2.0.jar
spark-streaming_2.12-3.2.0.jar
spark-sql-kafka-0-10_2.12-3.2.0.jar
spark-token-provider-kafka-0-10_2.12-3.2.0.jar
```

*없다면 아래의 Maven Stroage에서 확인 할 수 있다. 위의 필요한 jar 파일을 다운 받는다.*

```bash
https://mvnrepository.com/artifact/org.apache.spark
```

```bash
wget https://repo1.maven.org/maven2/org/apache/kafka/kafka-clients/3.4.1/kafka-clients-3.4.1.jar
```

```bash
wget https://repo1.maven.org/maven2/org/apache/spark/spark-sql-kafka-0-10_2.13/3.4.2/spark-sql-kafka-0-10_2.13-3.4.2.jar
```

```bash
wget https://repo1.maven.org/maven2/org/apache/spark/spark-streaming_2.13/3.4.2/spark-streaming_2.13-3.4.2.jar
```

```bash
wget https://dlcdn.apache.org/spark/spark-3.4.2/spark-3.4.2-bin-hadoop3.tgz
```

```bash
wget https://repo1.maven.org/maven2/org/apache/spark/spark-token-provider-kafka-0-10_2.13/3.4.2/spark-token-provider-kafka-0-10_2.13-3.4.2.jar
```

- Spark 버전에 맞는 jar파일 다운로드 
```bash
kafka-clients-3.4.1.jar
spark-sql-kafka-0-10_2.13-3.4.2.jar
spark-sql_2.13-3.4.2.jar
spark-streaming_2.13-3.4.2.jar
spark-token-provider-kafka-0-10_2.13-3.4.2.jar
```


# Spark가 Kafka에서 Topic을 읽어오는 방식

- [b] REF

> [접근방식](https://knight76.tistory.com/entry/Spark%EC%99%80-Kafka-%EC%97%B0%EB%8F%99)

