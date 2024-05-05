---
title: APP Develop - IoT Sensor
author: bami jeong
categories: development
layout: post
comments: true
tags:
  - iot
  - develop
---

# Flask를 사용해 Python으로 개발

### 배경
- 아이폰 (=단말기, IoT Sensor)이 데이터를 수집한다.
- `iot-collector`는 `edge` 노드에 `container`로 띄워져 있다. 
    - `iot-collector`는 Go 언어로 개발되어 MQTT를 수행하고 데이터를 저장하는 기능을 하는 소스이다.
    - web으로 구현되어 있으며 `post`로 조회 할 수 있다. 

### Goals
- `iot-collector`를 `python`화 한다
    - [x] `iot-collector`가 하는 기능을 python 코드로 구현 한다.
    - [x] web구현은 `Flask`를 이용한다.
    - [ ] 기능 구현 후 `container화` 한다.
- 기능 구현 
    - [ ] 현재는 가속도 센서만 데이터가 수집되고 있으니 Location 데이터도 함께 수집 되도록 한다.
    - [ ] 데이터를 받으면 Kafka Topic으로 MQTT를 실행한다.

### 개발 환경 
1. 개발 환경 Setting 
    - [x] Flask 설치 - vscode

### 필요한 PyPI

> paho-mqtt
> Flas
> pymysq
> configparser

### REF
> [paho.mqtt Gitnub](https://github.com/eclipse/paho.mqtt.python)

# TransCompiler

1. `mosquitto`:  broker server
2. `paho.mqtt` python package: broker와 연결 하기 위한 코드


# python code

1. Flask를 활용한 앱 코드는 unittest를 사용한다.
2. unittest에서 제공하는 test method가 따로 있다.
3. 테스트 하기 위해서는 main에서 정의한 app을 가지고 와야한다.
4. client는 unittest에서 `test_client`를 제공한다.

# Configmap

```
kubectl create configmap mariadb-init-db --from-file=init-db.sql
```

