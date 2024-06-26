---
title: Airflow-WebCrawling
author: bami jeong
categories: Basic
layout: post
comments: true
tags:
---

ref: [왕초보_가이드](https://velog.io/@clueless_coder/Airflow-%EC%97%84%EC%B2%AD-%EC%9E%90%EC%84%B8%ED%95%9C-%ED%8A%9C%ED%86%A0%EB%A6%AC%EC%96%BC-%EC%99%95%EC%B4%88%EC%8B%AC%EC%9E%90%EC%9A%A9) 

---

## Index
1. Data 생성
2. Data 긁어오기
3. Dag 설정
4. 파이프라인 생성
5. 결과값 출력 


## AIRFLOW 설치 

- dependency 추가 및 airflow 설치 스크립트

```bash
AIRFLOW_VERSION=2.8.1

# Extract the version of Python you have installed. If you're currently using a Python version that is not supported by Airflow, you may want to set this manually.
# See above for supported versions.
PYTHON_VERSION="$(python --version | cut -d " " -f 2 | cut -d "." -f 1-2)"

CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"
# For example this would install 2.8.1 with python 3.8: https://raw.githubusercontent.com/apache/airflow/constraints-2.8.1/constraints-3.8.txt

pip install "apache-airflow==${AIRFLOW_VERSION}" --constraint "${CONSTRAINT_URL}"
```

- 환경 변수 추가 

```bash
echo $PATH
export PATH=$PATH:/home/ubuntu/.local/bin
echo $PATH
```

- DB init

```shell
airflow db init
```

- 유저 생성 
```bash
airflow users create -u admin -p admin -f admin -l admin -r Admin -e admin@admin.com
```

- 포트 연결
```bash
airflow webserver -p 8080
```

- scheduler 실행 

> Server와 함께 터미널이 실행 되어 있는 상태여야 함

```bash
airflow scheduler
```

#### "PythonVirtualenvOperator requires virtualenv. please installed it"

- vertualenv 설치

```bash
pip install virtualenv
```

- airflow 프로젝트가 있는 디렉터리로 이동 후 명령어 실행

```bash
virtualenv venv
```


그 외 다른 Dependency: [[0. Project(2024)/4. airflow를 통한 데이터 파이프라인 구축/python resource/cp-dags.py|cp-dags.py]]


## AIRFLOW 적용해보기

> REF: [airflow 적용해보기](https://velog.io/@me529/%EB%8D%B0%EC%9D%B4%ED%84%B0%EC%97%94%EC%A7%80%EB%8B%88%EC%96%B4%EB%A7%81-Airflow-%EC%A0%81%EC%9A%A9%ED%95%B4%EB%B3%B4%EA%B8%B0)[머신러닝 DEEP](https://lsjsj92.tistory.com/633)

### command

- task 살펴보기

```bash
airflwo tasks list {DAT_NAME} --tree
```

- task  미리 실행해보기 

```bash
 airflow tasks test {DAG_ID} {TASK_ID} {START_DATE}
```

## 전체 순서도

> 코드가 동작되는 순서를 정리하고, 이에 따라 Task를 구성한다.

1. github main homepage에 접속되는지 확인한다.
2. 메인페이지에 접속 한다면 selenium으로 container-platform url을 받아와서 csv로 저장한다
3. airflow XCom에 csv파일을 저장한다.
4. 각 url에 접속해 내용을 긁어와 csv로 저장한다
5. url이 저장된 csv를 XCom에 저장한다
6. ObjectStroage 종료

*예제 샘플 코드가 출력되지 않기 위한 설정*
![[스크린샷 2024-01-25 오후 2.01.21.png]]

- 샘플 데이터 예제: 빅쿼리 공개 데이터셋 
> REF: [뭔가고수느낌](https://whitechoi.tistory.com/50)


![[스크린샷 2024-01-25 오후 2.28.33.png]]![[스크린샷 2024-01-25 오후 2.29.48.png]]

## Chrome Driver 

- chromedriver 

```bash
# Example of downloading ChromeDriver version 99.0.4844.51
wget https://chromedriver.storage.googleapis.com/99.0.4844.51/chromedriver_linux64.zip
```

```bash
unzip chromedriver_linux64.zip
```

```bash
sudo mv chromdirver ~/airflow/dags
```

## Code

`cp-dags.py` [[cp-dags.py]]
`tasks/tasks.py` [[task.py]]
