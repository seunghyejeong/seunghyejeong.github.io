---
title: Airflow and DataFrame
author: bami jeong
categories: Basic
layout: post
comments: true
tags:
---


I only want to get text from this html source, but please make a code that brings multiple titles in a repetition sentence use python 

```html
<a title="Readme.md" aria-label="Readme.md, (File)" class="Link--primary" href="/K-PaaS/container-platform/blob/master/architecture/Readme.md">Readme.md</a>
```

### TypeError: 'module' object is not callable
> REF: [TypeError해결법](https://wotres.tistory.com/entry/python-error-%ED%95%B4%EA%B2%B0%EB%B2%95-TypeError-module-object-is-not-callable)
![[스크린샷 2024-01-30 오전 9.43.59.png]]

⚙️  호출을 한단계 더 들어가서 해줌 
- webcraw.py![[스크린샷 2024-01-30 오전 9.46.04.png]]
- dags.py![[스크린샷 2024-01-30 오전 9.46.32.png]]
 - error 난 부분 수정 ![[스크린샷 2024-01-30 오전 9.47.30.png]]



# NoneType callable, all arrays must be of same length

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
    table_of_contents = page.find_elements(By.CLASS_NAME, "link--primary")
    titles = []
    if table_of_contents.get('aria-label') in ['file', 'Directory']:
        for title in table_of_contents:
            name = title.get_attribute('title').text
        print(f"---------{name}-----")
        titles.append(name)
    titles = list(set(titles))
    return titles


def crawling(**kwargs):
    url_list = kwargs['task_instance'].xcom_pull(key='url_list')
    titles, links = [], []
    for l in url_list:
        try:
            links.append(l)
            page = open_page(l)
            time.sleep(1)

            titles = get_title(page)
            titles.extend(titles)

            print(f"Titles for {l}: {titles}")
        except Exception as e:
            print(f"Error processing {l}: {e}")

    print(f"All Titles: {titles}")
    print(f"All Links: {links}")

    data = pd.DataFrame({'title': titles, 'link': links})
    date_today = datetime.datetime.now().strftime("%Y%m%d")
    data.to_csv(f"/home/ubuntu/airflow/data/git_{date_today}.csv", index=False)
    kwargs['task_instance'].xcom_push(key=f'git_csv', value=f"/home/ubuntu/airflow/data/git_{date_today}.csv")
```

- NoneType error가 날 때 Values ![[스크린샷 2024-01-30 오후 4.36.24.png]]![[스크린샷 2024-01-30 오후 4.35.29.png]]
- PRINT를 찍어봤을 때 Values 값이 비어 있다. (java의 Null과 비슷한 느낌인듯.)
- 그런데 자바 처럼 Null이라고 입력되어 뜨지 않고 아예 동작이 멈추어 버린다.
- 그리고 dataForm 자체에 규칙이 있어 lenght를 맞추어야 하는 이쓔가 있었음.
    ref: [dataform](https://velog.io/@cbkyeong/Dataframe%EA%B0%9C%EC%88%98%EA%B0%80-%EB%8B%A4%EB%A5%B8-list%EB%93%A4-dataframe%EC%9C%BC%EB%A1%9C-%EB%A7%8C%EB%93%A4%EA%B8%B0ValueError-arrays-must-all-be-same-length),[dataform_형식](https://undeadkwandoll.tistory.com/14),
# href success
```python
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

    h3_elements = browser.find_elements(By.CSS_SELECTOR, '.overflow-hidden h3')
    WebDriverWait(browser, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'Link--primary')))
    result = set()

    for h3_element in h3_elements:
        # Find the anchor tag within the "h3" element
        anchor_tag = h3_element.find_element(By.CSS_SELECTOR, 'a[href]')

        aria_label = anchor_tag.get_attribute('aria-label')
       # print(f"aria_label = {aria_label}")
        href_value = anchor_tag.get_attribute('href')
       # print(f"href_value : {href_value}")

        if 'File' in aria_label or 'Directory' in aria_label:
            print(f'Aria Label: {aria_label}, Href: {href_value}')
            result.add(href_value)

    kwargs['task_instance'].xcom_push(key='url_list', value = result)
    browser.quit()
```

# title info suc
```python

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

    WebDriverWait(browser, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'Link--primary')))


    # Find all a elements within the given structure
    a_elements = browser.find_elements(By.CSS_SELECTOR, 'tr.react-directory-row td div h3 a')

    for a_element in a_elements:
        title = a_element.get_attribute('title')
        print(f'Title: {title}')

    browser.quit()

```




```
<tr class="react-directory-row undefined" id="folder-row-0"><td class="react-directory-row-name-cell-small-screen" colspan="2"><div class="react-directory-filename-column"><svg aria-hidden="true" focusable="false" role="img" class="icon-directory" viewBox="0 0 16 16" width="16" height="16" fill="currentColor" style="display: inline-block; user-select: none; vertical-align: text-bottom; overflow: visible;"><path d="M1.75 1A1.75 1.75 0 0 0 0 2.75v10.5C0 14.216.784 15 1.75 15h12.5A1.75 1.75 0 0 0 16 13.25v-8.5A1.75 1.75 0 0 0 14.25 3H7.5a.25.25 0 0 1-.2-.1l-.9-1.2C6.07 1.26 5.55 1 5 1H1.75Z"></path></svg><div class="overflow-hidden"><h3><div class="react-directory-truncate"><a title="architecture" aria-label="architecture, (Directory)" class="Link--primary" href="/K-PaaS/container-platform/tree/master/architecture">architecture</a></div></h3></div></div></td><td class="react-directory-row-name-cell-large-screen" colspan="1"><div class="react-directory-filename-column"><svg aria-hidden="true" focusable="false" role="img" class="icon-directory" viewBox="0 0 16 16" width="16" height="16" fill="currentColor" style="display: inline-block; user-select: none; vertical-align: text-bottom; overflow: visible;"><path d="M1.75 1A1.75 1.75 0 0 0 0 2.75v10.5C0 14.216.784 15 1.75 15h12.5A1.75 1.75 0 0 0 16 13.25v-8.5A1.75 1.75 0 0 0 14.25 3H7.5a.25.25 0 0 1-.2-.1l-.9-1.2C6.07 1.26 5.55 1 5 1H1.75Z"></path></svg><div class="overflow-hidden"><h3><div class="react-directory-truncate"><a title="architecture" aria-label="architecture, (Directory)" class="Link--primary" href="/K-PaaS/container-platform/tree/master/architecture">architecture</a></div></h3></div></div></td><td class="react-directory-row-commit-cell"><div><div class="react-directory-commit-message"><a data-pjax="true" title="Renaming K-PaaS" class="Link--secondary" href="/K-PaaS/container-platform/commit/3b9c417d770cf5498607aaee64835159ba54d5ee">Renaming K-PaaS</a></div></div></td><td><div class="react-directory-commit-age"><relative-time class="RelativeTime-sc-lqbqy3-0" datetime="2023-09-06T13:05:55.000+09:00" tense="past" title="Sep 6, 2023, 1:05 PM GMT+9"></relative-time></div></td></tr>
```
> i wanna get tr > td > div > h3 > a`s titls....


```
<tr class="react-directory-row undefined" id="folder-row-0"><td class="react-directory-row-name-cell-small-screen" colspan="2"><div class="react-directory-filename-column"><svg aria-hidden="true" focusable="false" role="img" class="icon-directory" viewBox="0 0 16 16" width="16" height="16" fill="currentColor" style="display: inline-block; user-select: none; vertical-align: text-bottom; overflow: visible;"><path d="M1.75 1A1.75 1.75 0 0 0 0 2.75v10.5C0 14.216.784 15 1.75 15h12.5A1.75 1.75 0 0 0 16 13.25v-8.5A1.75 1.75 0 0 0 14.25 3H7.5a.25.25 0 0 1-.2-.1l-.9-1.2C6.07 1.26 5.55 1 5 1H1.75Z"></path></svg><div class="overflow-hidden"><h3><div class="react-directory-truncate"><a title="architecture" aria-label="architecture, (Directory)" class="Link--primary" href="/K-PaaS/container-platform/tree/master/architecture">architecture</a></div></h3></div></div></td><td class="react-directory-row-name-cell-large-screen" colspan="1"><div class="react-directory-filename-column"><svg aria-hidden="true" focusable="false" role="img" class="icon-directory" viewBox="0 0 16 16" width="16" height="16" fill="currentColor" style="display: inline-block; user-select: none; vertical-align: text-bottom; overflow: visible;"><path d="M1.75 1A1.75 1.75 0 0 0 0 2.75v10.5C0 14.216.784 15 1.75 15h12.5A1.75 1.75 0 0 0 16 13.25v-8.5A1.75 1.75 0 0 0 14.25 3H7.5a.25.25 0 0 1-.2-.1l-.9-1.2C6.07 1.26 5.55 1 5 1H1.75Z"></path></svg><div class="overflow-hidden"><h3><div class="react-directory-truncate"><a title="architecture" aria-label="architecture, (Directory)" class="Link--primary" href="/K-PaaS/container-platform/tree/master/architecture">architecture</a></div></h3></div></div></td><td class="react-directory-row-commit-cell"><div><div class="react-directory-commit-message"><a data-pjax="true" title="Renaming K-PaaS" class="Link--secondary" href="/K-PaaS/container-platform/commit/3b9c417d770cf5498607aaee64835159ba54d5ee">Renaming K-PaaS</a></div></div></td><td><div class="react-directory-commit-age"><relative-time class="RelativeTime-sc-lqbqy3-0" datetime="2023-09-06T13:05:55.000+09:00" tense="past" title="Sep 6, 2023, 1:05 PM GMT+9"></relative-time></div></td></tr>
```

> i wanna a's title values aria-label=Directory or Files
> and a data-pjax="true"'s  titles
> and relateive=time's date time 

tr folders as folder-row-0 ~ 6

## 정말 도움이된 .. chatGPT와의 대화,, 결론 
> [너이름이뭐니](https://chat.openai.com/share/3b62864a-fbbd-40e6-8c8a-86648fdadf36)

- 결론적으로 내가 참고한 벨로그 처럼 URL을 받아와 해당 페이지를 열어 원하는 데이터 값을 불러오는 것이었는데, 
- 정말 어려웠고 ,, 
- 그래서 마지막에는 내가 요청한 url 페이지의 한 부분을 표의 형식에 맞게 데이터로 불러오는 형태로 바꾸었다. 

그리고 GPT가 다했음...

- 중간 중간 Print값으로 값이 잘 들어가있는지 Debug 하는 것이 중요하고 
- 암튼 힘들었다.

# 가이드에 쓸 UI 캡쳐
![[Pasted image 20240130170357.png]]

![[Pasted image 20240130170450.png]]

![[Pasted image 20240130170537.png]]



![[Pasted image 20240130170557.png]]



![[Pasted image 20240130170616.png]]


![[Pasted image 20240130170955.png]]
![[Pasted image 20240130172025.png]]
- kill 
![[Pasted image 20240130171055.png]]
![[Pasted image 20240130171117.png]]
chrome
`pkill chrome`




- 파일구조 (주요파일만 출력, 이하 env,python lib 생략 )
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

- cfg 
![[Pasted image 20240130171841.png]]

![[Pasted image 20240130171722.png]]

![[Pasted image 20240130171907.png]]


