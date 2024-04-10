---
title: Airflow Use Guide
author: bami jeong
categories:
  - Airflow
  - Guide
tags:
  - Airflow
  - Data Pipeline
  - Guide
---

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
### 1.3 시스템 구성도

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
- Python v3.11


## 3. Airflow 설치
---
### 3.1 Python Dependency 설치

- 작업 디렉토리 생성 및 이동한다.
```bash
mkdir $HOME/airflow && cd $HOME/airflow
```

- 설치를 진행할 Dependency 스크립트 작성 , 실행 한다.
```bash
vi install.sh
```

- install.sh
```bash
AIRFLOW_VERSION=2.8.1

# Extract the version of Python you have installed. If you're currently using a Python version that is not supported by Airflow, you may want to set this manually.
# See above for supported versions.
PYTHON_VERSION="$(python --version | cut -d " " -f 2 | cut -d "." -f 1-2)"

CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"
# For example this would install 2.8.1 with python 3.8: https://raw.githubusercontent.com/apache/airflow/constraints-2.8.1/constraints-3.8.txt

pip install "apache-airflow==${AIRFLOW_VERSION}" --constraint "${CONSTRAINT_URL}"
```

- python 설치
```bash
sudo apt install python3-pip
```

- 스크립트 실행
```bash
source install.sh
```

- 실습용 데이터 파이프라인을 위헤 추가적으로 필요한 모듈을 설치한다. 
```bash
pip install pandas
pip install requests
pip install selenium
pip install beautifulsoup4
pip install beautifulsoup4 lxml
```

### 3.2 Airflow 사전 설정하기
airflow db initls
- 환경 변수를 추가한다
```bash
echo $PATH
export AIRFLOW_HOME=/home/ubuntu/.local
export PATH=$PATH:$AIRFLOW_HOME/bin
echo $PATH
```

#### 3.2.1 가상환경에서 실행 폴더 지정해주기
- [!] Python을 가상환경에서 실행할 때에는 작업 디렉토리에 `virtualenv` 모듈을 활성화 해주어야 한다.

- 작업 디렉토리로 이동한다.
```bash
cd $HOME/airflow
```

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

#### 3.2.2 DB init 
- airflow의 데이터베이스를 초기화한다. 
```bash
airflow db init
```

#### 3.2.3 User 생성
- Webserver를 이용할 유저를 생성한다
```bash
airflow users create -u admin -p admin -f admin -l admin -r Admin -e admin@admin.com
```

#### 3.2.4 WebServer 실행하기
- 각자 진행할 VM창을 따로 열어 진행해준다.
- server와 scheduler는 동시에 실행되고 있어야 한다.
- 작업 디렉토리에서 진행한다.
##### 3.3.4.1 Web Server 실행

-  포트를 연결해 Web Server를 실행한다.
```bash
airflow webserver -p 8080
```
##### 3.3.4.2 scheduler를 실행 

- scheduler를 실행한다.
```bash
airflow scheduler
```

- [k] 서버 실행 화면![[Pasted image 20240130170955.png]]

- [k] Web Server UI 화면
    *{MASTER_NODE_IP}:8080 접속*![[default_instance_name_configuration.png]]


## 4. 웹 크롤링을 위한 설정
---
- [*] *이하 모든 과정은 `virtualenv`가 실행중인 폴더, 즉 작업 폴더에서 진행한다*

### 4.1 Config File 작성

```bash
vi airflow.cfg
```
- Dags 폴더가 작업 폴더와 일치한지 확인한다.![[Pasted image 20240130171841.png]]
- Web Server에서 실습용 Dag 파일만 보일 수 있게 설정한다.![[Pasted image 20240130171722.png]]

### 4.2 ChromeDriver 설치
#### 4.2.1 Chrome 버전 확인하기 
- Chrome에 접속하여 현재 버전을 확인한다.
- 최신 버전이 아니라면 *최신 버전으로 업데이트*를 진행한다. 
> Web-Chrome 접속 > 더보기 클릭 > 설정 > Chrome 정보![[스크린샷 2024-01-31 오전 10.46.35.png]]

#### 4.2.2 Google-Chrome 설치하기
- 최신 버전의 Chrome을 다운로드 받는다.
```bash
sudo wget -q -O - [https://dl-ssl.google.com/linux/linux_signing_key.pub](https://dl-ssl.google.com/linux/linux_signing_key.pub) | sudo apt-key add -  
```

```bash
sudo sh -c 'echo "deb [arch=amd64] [http://dl.google.com/linux/chrome/deb/](http://dl.google.com/linux/chrome/deb/) stable main" >> /etc/apt/[sources.list.d/google.list'](https://league-cat.tistory.com/sources.list.d/google.list')
```

```bash
sudo apt-get update
sudo apt-get install google-chrome-stable
```

*웹 버전과 같은 버전인지 확인한다.*
```bash
(env) ubuntu@bami:~/airflow/dags$ google-chrome --version
Google Chrome 121.0.6167.85
```

#### 4.2.3 ChromeDriver 다운로드 받기
> [ChromeDriver Download](https://googlechromelabs.github.io/chrome-for-testing/)
- 위의 링크를 통해 Web Chrome, Google-Chrome과 같은 버전의 Driver를 다운 받고 실행 시켜준다.
```bash
wget https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/121.0.6167.85/linux64/chromedriver-linux64.zip
```

```bash
cd airflow/chromedriver-linux64/chromeDirver
$ ./ChromeDirver
```


## 5. 데이터 파이프라인 구성
---
### 5.1 작업 폴더 생성하기

- dag: Dag 파일(`cp-dags.py)`이 저장될 디렉토리
- webcraw: Task가 정의된 파일(`gitcraw.py`)과 `ChromeDriver`가 위치 할 디렉토리
- data: 파이프라인 진행 후 최종 데이터가 저장될 디렉토리

```bash
mkdir dag
mkdir webcraw
mkdir data
```

- 최종 파일구조 (주요파일만 출력, 이하 env,python lib 등 생략 )
```bash
./airflow/
├── airflow-webserver.pid
├── airflow.cfg
├── airflow.db
├── dags
│   ├── __pycache__
│   │   └── cp-dags.cpython-310.pyc
│   └── cp-dags.py
├── data
│   ├── git_20240129.csv
│   └── git_20240130.csv
├── webcraw
│   ├── __pycache__
│   │   └── gitcraw.cpython-310.pyc
│   ├── chromedriver
│   └── gitcraw.py
└── webserver_config.py
```

### 5.2 Dag 파일 생성하기
- Dag 폴더로 이동 후 `cp-dags.py` 파일을 생성한다.
- 프로세스의 추가 설명은 주석을 참고한다.

> cp-dags.py
```python
import sys
import os
from datetime import timedelta, datetime
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.utils.trigger_rule import TriggerRule

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from webcraw.gitcraw import get_folder_info

def print_result(**kwargs):
    r = kwargs["task_instance"].xcom_pull(key='result_msg')
    print("message:", r)

# Dag의 이름, 이메일 등 Dag Arguments를 정의한다.(Default)
default_args = {
    'owner': 'admin',
    'depends_on_past': False,
    'email': ['admin@admin.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=30),
    'start_date': datetime(2024, 1, 30),
}
# Dag Arguments 추가 설정 
dag_args = dict(
    dag_id="cp-dags",
    default_args=default_args,
    description='tutorial DAG ml',
    schedule_interval=timedelta(minutes=50),
    tags=['cp-test-bami'],
)

# Dag 객체를 정의한다. Dag 객체 안에는 실행될 task들이 선언되어 있다.
with DAG(**dag_args) as dag:
    start = BashOperator(
        task_id='start',
        bash_command='echo "start!"',
    )

    get_folder_info_task = PythonOperator(
        task_id='get_folder_info',
        python_callable=get_folder_info,
    )

# Task의 실행 순서 그래프를 지정한다.
    start >> get_folder_info_task
```

### 5.3 webcraw 폴더 구성하기
#### 5.3.1  Task 설명 
##### 5.3.1.1 Elements 값 추출 
- 가져올 데이터를 정하고 그에 해당하는 Element 값을 찾는다.![[Pasted image 20240131112838.png]]
##### 5.3.1.2 Data 출력 경로 지정
- 해당 값을 Table 형식으로 바꾼 뒤 `/data`폴더에 `.csv` 파일로 저장한다.
#### 5.3.2 Task 코드 작성하기
- `webcraw` 폴더로 이동 후 `gitcraw.py`를 생성한다.
- 프로세스의 추가 설정은 주석을 참고한다.
```python
import pandas as pd
import time
import datetime
import warnings
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

warnings.filterwarnings(action="ignore")


def get_folder_info(**kwargs):
    service = Service('/home/ubuntu/airflow/webcraw/chromedriver')
    service.start()
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    browser = webdriver.Remote(service.service_url, options=chrome_options)
    #Chrome dirver를 통해 browser를 읽어온다.
    browser.get("https://github.com/k-paas/container-platform")
    time.sleep(5)

    # 아래의 DataFrame function을 사용시 값의 길이 제약이나 NoneType 발생을 막기 위해 key값을 먼저 만들고 dataForm 형식을 지정해 주었다. 
    folder_ids = ['folder-row-0', 'folder-row-1', 'folder-row-2', 'folder-row-3', 'folder-row-4', 'folder-row-5', 'folder-row-6']
    data = {'Folder ID': [], 'Title': [], 'Aria Label': [], 'Data Pjax Title': [], 'Relative Time': []}

    for folder_id in folder_ids:
    # 위에서 찾아낸 Elements에 해당하는 값을 찾는다. 
        a_element = browser.find_element(By.CSS_SELECTOR, f'tr#{folder_id} td div h3 a')
        title = a_element.get_attribute('title')
        aria_label = a_element.get_attribute('aria-label')

        data_pjax_title_element = browser.find_element(By.CSS_SELECTOR, f'tr#{folder_id} a[data-pjax="true"]')
        data_pjax_title = data_pjax_title_element.get_attribute('title')
        relative_time = browser.find_element(By.CSS_SELECTOR, f'tr#{folder_id} relative-time').get_attribute('title')

        data['Folder ID'].append(folder_id)
        data['Title'].append(title)
        data['Aria Label'].append(aria_label)
        data['Data Pjax Title'].append(data_pjax_title)
        data['Relative Time'].append(relative_time)

    # DataFrame을 사용해 table 형태로 정렬한다.
    df = pd.DataFrame(data)
    print(df)

    date_today = datetime.datetime.now().strftime("%Y%m%d")
    df.to_csv(f"/home/ubuntu/airflow/data/git_{date_today}.csv", index=False)

    browser.quit()
```

- DataFrame 결과물![[Pasted image 20240131135225.png]]


## 6. Web Server 활용 
---

-  Web-server 접속 화면![[Pasted image 20240130170357.png]]

- cp-dags 둘러보기 ![[Pasted image 20240130170450.png]]

- Dags 파일에 정의된 task들의 Graph view![[Pasted image 20240130170537.png]]

- Task 수행에 실패 할 경우 Log를 볼 수 있다.![[Pasted image 20240130170557.png]]

- 정의된 Dag의 Tasks들이 성공화면 `success`가 출력된다.![[Pasted image 20240130170616.png]]



## 7. 참고 사항

- [i] Web-Server에서 Dag를 실행해보지 않아도 airflow CLI를 통해 로그를 미리 볼 수 있다.
- Dag에 정의된 Task 살펴보기 
```bash
airflow tasks list {DAG_NAME} --tree
```

- Task 미리 실행해보기 
```bash
airflow tasks test {DAG_ID} {TASK_ID} {START_DATE}
```

- [i] 웹서버 강제 종료 후 Server 중지 시키기
- 이미 웹서버가 동작 중일경우 실행이 안될 수 있다.
- 아래 표시된 두 개의 이름을 가진 Pid를 종료시킨다.![[Pasted image 20240130171055.png]]![[Pasted image 20240130171117.png]]
```bash
kill {PID_NUM}
```

- Chrome Server 중지 시키기
```bash
pkill chrome
```




