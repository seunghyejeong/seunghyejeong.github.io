
## Table of Contents
---
1. 문서 개요
    1. 목적
    2. 범위
    3. 시스템 구성도
    4. 참고자료
2. Prerequisite
    - Python 설치
3. Airflow 설치
    - 3.2.1 가상환경에서 실행 폴더 지정해주기
    - 3.2.2 DB init 
    -  3.3.3 User 생성
        - 3.3.4 WebServer 실행하기    
            - 3.3.4.1 Web Server 실행
            - 3.3.4.2 Scheduler를 실행 
4. 웹 크롤링을 위한 설정 
    - 4.1 Config File 작성
    - 4.2 ChromeDriver 설치
        - 4.2.1 Chrome 버전 확인하기 
        - 4.2.2 Google-Chrome 설치하기
        - 4.2.3 ChromeDriver 다운로드 받기
5. 데이터 파이프라인 구성
    - 5.1 작업 폴더 생성하기
    - 5.2 Dag 파일 생성하기
    - 5.3 webcraw 폴더 구성하기
        - 5.3.1  Task 설명 
            - 5.3.1.1 Elements 값 추출 
            - 5.3.1.2 Data 출력 경로 지정      
        - 5.3.2 Task 코드 작성하기        
6. Web Server 활용 
7. 참고 사항

## 1. 문서 개요
---
### 1.1 목적
본 문서는 airflow를 설치하고 데이터 파이프라인을 설정하는 방법을 기술하였다.
### 1.2 범위
설치 범위는 ubuntu 22.04, *가상환경*에서 진행하였다.
        1### 1.3 시스템 구성도

![[airflow_arc.png]]
### 1.4 참고자료
> [Airflow Official](https://airflow.apache.org/)
> [Airflow 튜토리얼 따라하기](https://velog.io/@clueless_coder/Airflow-%EC%97%84%EC%B2%AD-%EC%9E%90%EC%84%B8%ED%95%9C-%ED%8A%9C%ED%86%A0%EB%A6%AC%EC%96%BC-%EC%99%95%EC%B4%88%EC%8B%AC%EC%9E%90%EC%9A%A9)
> [ChromeDriver_Official](https://chromedriver.chromium.org/getting-started)

### 1.5 Version
- Airflow v2.8.1
- Python v3.11
- ChromDriver v121.0.6167.85


## 2. Prerequisite
---
본 설치 가이드는 Ubuntu 22.04 환경에서 설치하는 것을 기준으로 작성하였다.
### 2.1 Python 설치 
- Python v3.8


## 3. Airflow 설치
---
### 3.1 Python Dependency 설치

- 작업 디렉토리 생성 및 이동한다.
```bash
mkdir $HOME/airflow && cd $HOME/airflow
```

- python 설치
```bash
sudo apt-get update
sudo apt install python3-pip
```


---
- `virtualenv`를 설치한다.
```bash
pip install virtualenv
```

- 가상 환경 폴더를 구성한다.
- [!] 작업 디렉토리에서 진행되어야 한다.
```bash
virtualenv env
```

- `virtualenv`를 활성화 한다.
```bash
source env/bin/activate
```


- [i] `virtualenv` 비활성화
```bash
source env/bin/activate
```


---

- 설치를 진행할 Dependency 스크립트 작성 , 실행 한다.
```bash
vi install.sh
```

- install.sh
```bash
# Airflow needs a home. `~/airflow` is the default, but you can put it
# somewhere else if you prefer (optional)
export AIRFLOW_HOME=~/airflow
export PATH=$PATH:/home/ubuntu/.local/bin
# Install Airflow using the constraints file
AIRFLOW_VERSION=2.3.4
PYTHON_VERSION="$(python --version | cut -d " " -f 2 | cut -d "." -f 1-2)"
# For example: 3.7
CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"
# For example: https://raw.githubusercontent.com/apache/airflow/constraints-2.3.4/constraints-3.7.txt
pip install "apache-airflow==${AIRFLOW_VERSION}" --constraint "${CONSTRAINT_URL}"
```


- 스크립트 실행
```bash
source install.sh
```

### JAVA 설치

```
sudo apt install openjdk-8-jdk
```

### 환경 변수를 추가한다

```bash
vi ~/.bashrc
```

```sh
export AIRFLOW_HOME=~/airflow
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
export SPARK_HOME=
export PATH=$PATH:/home/ubuntu/.local/bin:$JAVA_HOME/bin:
```

```sh
source ~/.bashrc
echo $PATH
```

#### 3.2.1 Airflow 작업 Directory 구성하기

- 작업 디렉토리로 이동한다.
```bash
cd $HOME/airflow
```

- 폴더 생성
```bash
mkdir dags
mkdir plugins
mkdir data
```

- requirements
```bash
vi requirements.txt
```

- requirements.txt
```
pandas==1.3.5
requests==2.31.0
selenium==4.17.2
beautifulsoup4==4.12.3
lxml==5.1.0
virtualenv
kafka-python==2.0.2
apache-airflow-providers-apache-kafka==1.3.1
confluent-kafka==2.3.0
apache-airflow-providers-apache-spark==2.1.0
py4j==0.10.9.5
grpcio-status>=1.59.0
```

```
pip install -r requirements.txt
```

# 3. Spark 설치

### 다운로드 

```sh
cd ~
wget https://archive.apache.org/dist/spark/spark-3.3.0/spark-3.3.0-bin-hadoop3.tgz
mv spark-3.3.0-bin-hadoop3.tgz/ spark/
```

###  필요한 jar 파일 다운로드
```sh
cd ~/spark/jars
```

```sh
curl -o kafka-clients-3.3.0.jar https://repo1.maven.org/maven2/org/apache/kafka/kafka-clients/3.3.0/kafka-clients-3.3.0.jar
curl -o spark-token-provider-kafka-0-10_2.12-3.3.0.jar https://repo1.maven.org/maven2/org/apache/spark/spark-token-provider-kafka-0-10_2.12/3.3.0/spark-token-provider-kafka-0-10_2.12-3.3.0.jar
curl -o spark-sql-kafka-0-10_2.12-3.3.0.jar https://repo1.maven.org/maven2/org/apache/spark/spark-sql-kafka-0-10_2.12/3.3.0/spark-sql-kafka-0-10_2.12-3.3.0.jar
curl -o commons-pool2-2.11.0.jar https://repo1.maven.org/maven2/org/apache/commons/commons-pool2/2.11.0/commons-pool2-2.11.0.jar
curl -o spark-streaming-kafka-0-10_2.12-3.3.0.jar https://repo1.maven.org/maven2/org/apache/spark/spark-streaming-kafka-0-10_2.12/3.3.0/spark-streaming-kafka-0-10_2.12-3.3.0.jar
```



#### 3.2.4 WebServer 실행하기
- 각자 진행할 VM창을 따로 열어 진행해준다.
- server와 scheduler는 동시에 실행되고 있어야 한다.
- 작업 디렉토리에서 진행한다.
##### 3.3.4.1 Web Server 실행
#### 3.2.3 User 생성
- Webserver를 이용할 유저를 생성한다
```bash
airflow users create -u admin -p admin -f admin -l admin -r Admin -e admin@admin.com
```

-  포트를 연결해 Web Server를 실행한다.
```bash
airflow webserver -p 8080
```

#### 3.2.2 DB init 
- airflow의 데이터베이스를 초기화한다. 
```bash
airflow db init
```
##### 3.3.4.2 scheduler를 실행 

- scheduler를 실행한다.
```bash
airflow scheduler
```