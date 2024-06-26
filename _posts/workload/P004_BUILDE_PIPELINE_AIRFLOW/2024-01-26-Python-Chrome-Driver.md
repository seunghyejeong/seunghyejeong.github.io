---
title: Web crawling - Chrome Driver
author: bami jeong
categories: Basic
layout: post
comments: true
tags:
---

## import file 

1. 같은 선상에 있는 폴더 내 파일 import

```bash
- F1
|- aaa.py
|- bbb.py

--F2
|-- ccc.py

--F3
|-- ddd.py
```

ccc.py에서 ddd.py를 불러오고 싶을 때,

```python
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from F3 import ddd
```

: 코드 받아오는건 나도 잘 모르겠다 .. . . . 결국 이 형식으로 받아오긴 함..
![[스크린샷 2024-01-26 오후 5.36.35.png]]

~~## Chrome 연결~~
~~> REF: [Chrome Driver](https://chromedriver.chromium.org/getting-started)
> Chrome 버전에 맞는 Driver 사용.  드라이버는 같은 폴더 안에 위치시킨다.~~

이건 실패한 코드.

```python
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time,os,requests
import warnings
warnings.filterwarnings(action="ignore")
import datetime
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

def get_url_list(**kwargs) :
    service.start()
    browser = webdriver.Remote(service.service_url)

    browser.get("https://github.com/")
    time.sleep(5)
    browser.auit()
```


## ChromeDriver ERROR 
> 이때는 해당 코드가 Chrome 버전을 무조건 최신으로 받아와 코드가 실행 될 때 설치 하는 코드로 이루어져 있음.![[스크린샷 2024-01-26 오후 5.32.51.png]]


- error

```bash
[2024-01-25T16:34:21.560+0900] {taskinstance.py:2698} ERROR - Task failed with exception
Traceback (most recent call last):
  File "/home/ubuntu/.local/lib/python3.10/site-packages/airflow/models/taskinstance.py", line 433, in _execute_task
    result = execute_callable(context=context, **execute_callable_kwargs)
  File "/home/ubuntu/.local/lib/python3.10/site-packages/airflow/operators/python.py", line 199, in execute
    return_value = self.execute_callable()
  File "/home/ubuntu/.local/lib/python3.10/site-packages/airflow/operators/python.py", line 216, in execute_callable
    return self.python_callable(*self.op_args, **self.op_kwargs)
  File "/home/ubuntu/airflow/dags/../crawling/crawling_velog.py", line 16, in get_url_list
    browser = webdriver.Chrome(options = chrome_options)
  File "/home/ubuntu/.local/lib/python3.10/site-packages/selenium/webdriver/chrome/webdriver.py", line 45, in __init__
    super().__init__(
  File "/home/ubuntu/.local/lib/python3.10/site-packages/selenium/webdriver/chromium/webdriver.py", line 61, in __init__
    super().__init__(command_executor=executor, options=options)
  File "/home/ubuntu/.local/lib/python3.10/site-packages/selenium/webdriver/remote/webdriver.py", line 208, in __init__
    self.start_session(capabilities)
  File "/home/ubuntu/.local/lib/python3.10/site-packages/selenium/webdriver/remote/webdriver.py", line 292, in start_session
    response = self.execute(Command.NEW_SESSION, caps)["value"]
  File "/home/ubuntu/.local/lib/python3.10/site-packages/selenium/webdriver/remote/webdriver.py", line 347, in execute
    self.error_handler.check_response(response)
  File "/home/ubuntu/.local/lib/python3.10/site-packages/selenium/webdriver/remote/errorhandler.py", line 229, in check_response
    raise exception_class(message, screen, stacktrace)
selenium.common.exceptions.SessionNotCreatedException: Message: session not created: Chrome failed to start: exited normally.
  (session not created: DevToolsActivePort file doesn't exist)
  (The process started from chrome location /home/ubuntu/.cache/selenium/chrome/linux64/121.0.6167.85/chrome is no longer running, so ChromeDriver is assuming that Chrome has crashed.)
[[Stacktrace]]:
#0 0x5587ec794d93 <unknown>
#1 0x5587ec478337 <unknown>
#2 0x5587ec4acbc0 <unknown>
#3 0x5587ec4a8765 <unknown>
#4 0x5587ec4f2b7c <unknown>
#5 0x5587ec4e61e3 <unknown>
#6 0x5587ec4b6135 <unknown>
#7 0x5587ec4b713e <unknown>
#8 0x5587ec758e4b <unknown>
#9 0x5587ec75cdfa <unknown>
#10 0x5587ec7456d5 <unknown>
#11 0x5587ec75da6f <unknown>
#12 0x5587ec72969f <unknown>
#13 0x5587ec782098 <unknown>
#14 0x5587ec782262 <unknown>
#15 0x5587ec793f34 <unknown>
#16 0x7f387b79fac3 <unknown>
```

: chrome driver가 이중으로 실행되고 있을 경우..

```bash
pkill -f chomre
```

## Chrome 최신 버전으로 다운
> dags 폴더 안에 같이 위치 해야함
> 위의 코드가 자꾸 에러가 나서 최신 드라이버를 다운 받아 진행함.
> REF: [ChromeDriver](https://chromedriver.chromium.org/getting-started)
> [최신드라이버](https://googlechromelabs.github.io/chrome-for-testing/)

- 여기서는 코드를 좀 수정함. 위의 Ref를 참조

```bash
wget https://chromedriver.storage.googleapis.com/99.0.4844.51/chromedriver_linux64.zip
unzip chromedriver_linux64.zip
sudo mv chromedriver /usr/local/bin/
```


## 가상 환경에서 수행 중일때는 virtualenv 

> REF: [가상환경 시작하기](https://jaemunbro.medium.com/python-virtualenv-venv-%EC%84%A4%EC%A0%95-aaf0e7c2d24e),[Virtualenv 설치](https://jaemunbro.medium.com/python-virtualenv-venv-%EC%84%A4%EC%A0%95-aaf0e7c2d24e)
    #airflow_install #airflow_chrome #airflow_vm

- Python을 가상환경 즉 VM에서 활용 할 때는 *꼭 꼭 !!!!* 가상 환경 설정을 해주어야한다.
- 내가 가상환경으로 사용 할 Directory로 이동해 실행해준다.

1. 가상 환경 설치 

```bash
python3 -m pip install --user -U virtualenv
```

2. Python 환경 만들기

```bash
cd {WANNABE_VIRTUAL_ENV_DIR}
virtualenv env
## env를 실행하면 해당 폴더에 /env 폴더가 생성된다.
```

3. 활성화

```bash
source /env/bin/activate
```

4. 비활성화

```bash
source /env/bin/dectivate
```

**바로 받아와버리기!!!!!!**
![[스크린샷 2024-01-26 오후 5.02.49.png]]

## selenium capabilities = options.to_capabilities() AttributeError: 'NoneType' object has no attribute 'to_capabilities' chrome

- Tasks.py에 Chrome관련 옵션을 다 제외하고 실행했는데 (연결이 잘 안돼서 연결부터 하고보자..)    ![[스크린샷 2024-01-26 오후 5.23.33.png]]
- 위의 에러가 발생하길래 해석해봤다 ![[스크린샷 2024-01-26 오후 5.25.05.png]]
- 아마.. 옵션값이 없어서 그런가 . . 했더니 진짜였음ㅋ

## Web Crawling

- 내가 받아오고 싶은 부분![[스크린샷 2024-01-26 오후 5.18.16.png]]
- Elments값 찾기![[스크린샷 2024-01-26 오후 5.19.34.png]]![[스크린샷 2024-01-26 오후 5.21.06.png]]
- css코드 

```css
<a title="architecture" aria-label="architecture, (Directory)" class="Link--primary" href="/K-PaaS/container-platform/tree/master/architecture">architecture</a>
```

- 그렇게 해서 작성된 코드

```python
url_list = browser.find_elements(By.CLASS_NAME, 'Link--primary')
link = url.get_attribute('href')
```



오늘 까지 성공 화면

![[스크린샷 2024-01-26 오후 5.34.03.png]]