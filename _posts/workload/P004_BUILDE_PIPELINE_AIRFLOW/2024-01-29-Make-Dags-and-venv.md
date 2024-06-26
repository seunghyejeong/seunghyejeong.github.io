---
title: Make Dags, python venv
author: bami jeong
categories: Basic
layout: post
comments: true
tags:
---


# Index
1. dags / pipeline source 다듬고 시작

- dags
```python
import sys
import os
from datetime import timedelta, datetime
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.utils.trigger_rule import TriggerRule

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
print(sys.path)
from webcraw.gitcraw import get_url_list

# 결과 출력용 함수 정의
def print_result(**kwargs):
    r = kwargs["task_instance"].xcom_pull(key='result_msg')
    print("message : ", r)

default_args = {
    'owner': 'admin',
    'depends_on_past': False,
    'email': ['admin@admin.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=30),
    'start_date': datetime(2024, 1, 25)
}

# dag의 id, arguments, 설명, 실행 간격, 시작 일자, 태그 등을 지정
dag_args = dict(
    dag_id="cp-dags",
    default_args=default_args,
    description='tutorial DAG ml',
    schedule_interval=timedelta(minutes=50),
    tags=['cp-test-bami'],
)

with DAG( **dag_args ) as dag:
    start = BashOperator(
        task_id='start',
        bash_command='echo "start!"',
    )

    get_url = PythonOperator(
        task_id='get_url',
        python_callable=get_url_list,
    )

start >> get_url
```

- craws
```python
import pandas as pd
import time,os,requests
import warnings
warnings.filterwarnings(action="ignore")
import datetime
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
# error "from webdriver_manager.chrome import ChromeDriverManager" : 못찾는다고 에러가 나길래 뺐더니 실행이 됨..

def get_url_list(**kwargs) :
    service = Service('/home/ubuntu/airflow/webcraw/chromedriver')
    service.start()
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    browser = webdriver.Remote(service.service_url, options = chrome_options)

    browser.get("https://github.com/k-paas/container-platform")
    time.sleep(5)

    url_list = browser.find_elements(By.CLASS_NAME, 'Link--primary')
    result = []
    for url in url_list :
        link = url.get_attribute('href')
        print(f"######{link}######")
        result.append(link)
    result = list(set(result))
    kwargs['task_instance'].xcom_push(key='url_list', value = result)
    return "end get url lis"
    browser.quit()
```

## chrome driver 
> #chromedriver #python_chrome #chrome 
- error
```
[2024-01-29, 01:27:18 UTC] {taskinstance.py:1138} INFO - Marking task as UP_FOR_RETRY. dag_id=cp-dags, task_id=get_url, execution_date=20240125T000000, start_date=20240129T012717, end_date=20240129T012718 [2024-01-29, 01:27:18 UTC] {standard_task_runner.py:107} ERROR - Failed to execute job 6 for task get_url (Message: session not created: This version of ChromeDriver only supports Chrome version 99 Current browser version is 121.0.6167.85 with binary path /usr/bin/google-chrome
```

1. 일단 Chrome이 없어서 ? : 크롬을 설치한다..
```bash
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb

sudo apt install ./google-chrome-stable_current_amd64.deb

(env) ubuntu@bami:~/airflow/dags$ google-chrome --version
Google Chrome 121.0.6167.85
``` 
![[스크린샷 2024-01-29 오전 10.35.30.png]]
🙅🏻 이게 맞는 방법이긴 한데, 버전이 안맞아서 Chromedirver와 chrome이 버전이 맞지 않다고 오류가 남.

3. Driver 버전이 안맞아서?
> Ref: [chrome_driver](https://googlechromelabs.github.io/chrome-for-testing/)
```bash
wget https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/121.0.6167.85/linux64/chromedriver-linux64.zip
```
🙅🏻 버전은 잘 맞았다.

## 해결
1. 가상 환경에서 시작한다 
    1. `vertualenv` > `source ./activate`
2. ChromeDirver는 실행시켜 주어야 한다 
    `{PATH}/chromdriver`
2. google chrome이 설치되어 있어야 한다.
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

![[스크린샷 2024-01-29 오전 11.15.25.png]]



---

## get_info_task

```python
import sys
import os
from datetime import timedelta, datetime
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.utils.trigger_rule import TriggerRule

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
print(sys.path)
from webcraw.gitcraw import get_url_list

# 결과 출력용 함수 정의
def print_result(**kwargs):
    r = kwargs["task_instance"].xcom_pull(key='result_msg')
    print("message : ", r)

default_args = {
    'owner': 'admin',
    'depends_on_past': False,
    'email': ['admin@admin.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=30),
    'start_date': datetime(2024, 1, 25)
}

# dag의 id, arguments, 설명, 실행 간격, 시작 일자, 태그 등을 지정
dag_args = dict(
    dag_id="cp-dags",
    default_args=default_args,
    description='tutorial DAG ml',
    schedule_interval=timedelta(minutes=50),
    tags=['cp-test-bami'],
)

with DAG( **dag_args ) as dag:
    start = BashOperator(
        task_id='start',
        bash_command='echo "start!"',
    )

    get_url = PythonOperator(
        task_id='get_url',
        python_callable=get_url_list,
    )

start >> get_url 
```

```python
import pandas as pd
import time,os,requests
import warnings
warnings.filterwarnings(action="ignore")
import datetime
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
# error "from webdriver_manager.chrome import ChromeDriverManager" : 못찾는다고 에러가 나길래 뺐더니 실행이 됨..

def get_url_list(**kwargs) :
    service = Service('/home/ubuntu/airflow/webcraw/chromedriver')
    service.start()
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    browser = webdriver.Remote(service.service_url, options = chrome_options)

    browser.get("https://github.com/k-paas/container-platform")
    time.sleep(5)

    
    url_list = browser.find_elements(By.CLASS_NAME, 'Link--primary')
    result = []
    for url in url_list :
        link = url.get_attribute('href')
        print(f"######{link}######")
        result.append(link)
    result = list(set(result))
    kwargs['task_instance'].xcom_push(key='url_list', value = result)
    return "end get url lis"
    browser.quit()

def open_page(url) :
    req=requests.get(url).text
    page=bs(req,"html.parser")
    return page
:q
def get_title(page) :
    title = page.find('div', {'class':'head-wrapper'})
    title = title.find('h1').text
    return title
```

```python
def get_writer(page) :
    writer = page.find('a',{'class' : 'user-logo'}).text
    return writer

def get_text(page) :
    text_all = page.find_all(['p','h1','h2','h3','li'])
    text=""
    for t in text_all :
        text += t.text
    return text

def crawling(**kwargs) :
    url_list = kwargs['task_instance'].xcom_pull(key = 'url_list')
    title, writer, img, text, link = [], [], [], [], []
    for l in url_list :
        link.append(l)
        page = open_page(l)
        time.sleep(1)
        title.append( get_title(page) )
        writer.append( get_writer(page) )
        img.append( get_thumnail(page) )
        text.append( get_text(page) )
        print(title)
    data = pd.DataFrame({'title' : title, 'writer' : writer, 'img' : img, 'text' : text, 'link' : link})
    date = datetime.datetime.now().strftime("%Y%m%d")
    data.to_csv(f"/home/ubuntu/airflow/airflow/data/velog_{date}.csv", index=False)
    kwargs['task_instance'].xcom_push(key = f'velog_csv', value= f"/home/ubuntu/airflow/airflow/data/velog_{date}.csv")
    kwargs['task_instance'].xcom_push(key='result_msg', value= f"total number of blogs this week : {len(data)}")

```


```python
def crawling(**kwargs):
    url_list = kwargs['task_instance'].xcom_pull(key='url_list')
    titles, messages, dates, links = [], [], [], [] 
    for l in url_list:
        links.append(l)  
        page = open_page(l)
        time.sleep(1)
        titles.append(get_title(page))
        messages.append(get_message(page)) 
        dates.append(get_date(page))  
        print(titles)

    data = pd.DataFrame({'title': titles, 'message': messages, 'date': dates, 'link': links}) 
    date_today = datetime.datetime.now().strftime("%Y%m%d")
    data.to_csv(f"/home/ubuntu/airflow/airflow/data/git_{date_today}.csv", index=True)
    kwargs['task_instance'].xcom_push(key=f'git_csv', value=f"/home/ubuntu/airflow/airflow/data/git_{date_today}.csv")

```




# 240129
https://github.com/oxylabs/Python-Web-Scraping-Tutorial
- cp-dags.py
```python
import sys
import os
from datetime import timedelta, datetime
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.utils.trigger_rule import TriggerRule

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
print(sys.path)
from webcraw.gitcraw import get_url_list, crawling

# 결과 출력용 함수 정의
def print_result(**kwargs):
    r = kwargs["task_instance"].xcom_pull(key='result_msg')
    print("message : ", r)

default_args = {
    'owner': 'admin',
    'depends_on_past': False,
    'email': ['admin@admin.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=30),
    'start_date': datetime(2024, 1, 25)
}

# dag의 id, arguments, 설명, 실행 간격, 시작 일자, 태그 등을 지정
dag_args = dict(
    dag_id="cp-dags",
    default_args=default_args,
    description='tutorial DAG ml',
    schedule_interval=timedelta(minutes=50),
    tags=['cp-test-bami'],
)

with DAG( **dag_args ) as dag:
    start = BashOperator(
        task_id='start',
        bash_command='echo "start!"',
    )

    get_url = PythonOperator(
        task_id='get_url',
        python_callable=get_url_list,
    )

    get_info_task = PythonOperator(
        task_id='get_info_task',
        python_callable=crawling,
        op_kwargs={'url_list':"url_list"}
    )
start >> get_url >> get_info_task
```


- gitcraw.py
```python
import pandas as pd
import time,os,requests
import warnings
warnings.filterwarnings(action="ignore")
import datetime
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def get_url_list(**kwargs) :
    service = Service('/home/ubuntu/airflow/webcraw/chromedriver')
    service.start()
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    browser = webdriver.Remote(service.service_url, options = chrome_options)

    browser.get("https://github.com/k-paas/container-platform")
    time.sleep(5)

    url_list = browser.find_elements(By.CLASS_NAME, 'Link--primary')
    result = []
    for url in url_list :
        link = url.get_attribute('href')
        print(f"######{link}######")
        result.append(link)
    result = list(set(result))
    kwargs['task_instance'].xcom_push(key='url_list', value = result)
    return "end get url lis"
    browser.quit()

def open_page(url) :
    req=requests.get(url).text
    page=bs(req,"html.parser")
    return page
    
def get_title(page):
    titles = []
    title_elements = page.find_all('div', {'class': 'react-directory-truncate'})
    for title_element in title_elements:
        title = title_element.find('a').get('title')
        titles.append(title)
    return titles

def get_message(page):
    messages = []
    message_elements = page.find_all('div', {'class':'react-directory-commit-message'})
    for message_element in message_elements:
        message = message_element.find('a').get('title')
        messages.append(message)
    return messages

def get_date(page):
    dates = []
    date_elements = page.find_all('div', {'class':'react-directory-commit-age'})
    for date_element in date_elements:
        date = date_element.find('relative-time').get('title')
        dates.append(date)
    return dates

```