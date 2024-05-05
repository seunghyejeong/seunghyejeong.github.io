---
title: CoCoaPods
author: bami jeong
categories: development
layout: post
comments: true
tags:
  - iot
  - apps
  - develop
---

# public ip

```
133.186.220.16
```
# Deploy

```Dockerfile
FROM python:3.10-slim

RUN apt-get update \
    && apt-get install -y \
        gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY main.py .
COPY *.ini .
COPY requirements.txt .
COPY database.py .

RUN pip install -r requirements.txt

CMD ["python", "main.py"]
```

```
docker build --no-cache -t seunghyejeong/iot-sensor-collector-python:1.0 .
```

```
docker push seunghyejeong/iot-sensor-collector-python:1.0
```

```
seunghyejeong/iot-sensor-collector-python:1.0
```

```
docker system prune --all --force --volumes
```
### docker cache 현상
    
코드를 수정 후 다시 이미지를 생성 하였는데도 이전의 코드를 참조한다.
-> 이 현상을 도커 캐시 현상이라고 한다.

따라서 여러분이 main.py를 /app 폴더에 복사하여 이미지를 빌드할 때, Docker는 이 단계를 캐싱합니다. 그런데 main.py의 내용이 변경되어 다시 이미지를 빌드하더라도, Docker는 이미지 빌드 과정에서 /app 폴더에 해당 파일이 복사되는 부분을 캐시된 결과를 사용합니다. 이는 Docker가 파일이 변경되지 않았다고 판단하여 이전의 main.py를 계속해서 참조하는 현상을 발생시킵니다.

이를 해결하기 위해서는 Docker가 main.py가 변경되었다고 판단하게끔 하거나, 또는 캐시를 비활성화하여 강제로 이미지를 재빌드할 수 있습니다. 다음은 이를 수행하는 몇 가지 방법입니다:

1. **도커 빌드 캐시 무효화**: 이미지를 빌드할 때 `--no-cache` 플래그를 사용하여 Docker에게 모든 캐시를 무효화하고 새로운 이미지를 빌드하도록 지시할 수 있습니다. 예를 들면 다음과 같이 사용할 수 있습니다:
    ```
    docker build --no-cache -t 이미지_이름:태그 .
    ```
    
2. **파일 수정 시간 변경**: main.py를 수정한 후에 해당 파일의 수정 시간을 변경하여 Docker가 파일이 변경되었다고 인식하도록 할 수 있습니다. 예를 들어, 다음과 같이 touch 명령어를 사용하여 파일의 수정 시간을 변경할 수 있습니다:
    
    ```
    touch main.py
    ```
1. **파일 추가 후 재빌드**: 파일을 수정할 때가 아니라 파일을 추가하거나 삭제하여 Docker가 새로운 이미지를 빌드하도록 할 수도 있습니다. 이렇게 하면 Docker가 해당 단계를 캐시하지 않고 새로운 이미지를 빌드합니다.


# 코드 수정

1. Flask에서 모든 host를 Listen하기 위한 코드
```python
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=8080)
```

2. collector는 connect를 하지 않아도 된다.
```python

def connect_mqtt() -> mqtt.Client :
.
.
.                   
    client = mqtt.Client(client_id=client_id, clean_session=True, userdata=None, callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
    #client.on_connect = on_connect
    #client.on_disconnect = on_disconnect
    #client.on_log=on_log
    
    # client.connect_async(host=broker, port=port)
```

3. Connection이 된 모습
```bash
$kubectl logs -f iot-sensor-collector-5bbc5787f9-vtchc
 * Serving Flask app 'main'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:8080
 * Running on http://10.233.93.151:8080
Press CTRL+C to quit
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 970-880-350
```

## Error

```bash
  File "/usr/local/lib/python3.10/site-packages/flask/app.py", line 1498, in __call__
    return self.wsgi_app(environ, start_response)
  File "/usr/local/lib/python3.10/site-packages/flask/app.py", line 1476, in wsgi_app
    response = self.handle_exception(e)
  File "/usr/local/lib/python3.10/site-packages/flask/app.py", line 1473, in wsgi_app
    response = self.full_dispatch_request()
  File "/usr/local/lib/python3.10/site-packages/flask/app.py", line 882, in full_dispatch_request
    rv = self.handle_user_exception(e)
  File "/usr/local/lib/python3.10/site-packages/flask/app.py", line 880, in full_dispatch_request
    rv = self.dispatch_request()
  File "/usr/local/lib/python3.10/site-packages/flask/app.py", line 865, in dispatch_request
    return self.ensure_sync(self.view_functions[rule.endpoint])(**view_args)  # type: ignore[no-any-return]
  File "/app/main.py", line 52, in postAcceleration
    acceleration_data = AccelerationData(data['x'],data['y'],data['z'])
TypeError: 'property' object is not subscriptable
```

: 이건 내가 request.json을 Reponse.json으로 받아서 생긴 에러.

위의 과정까지 진행 했을 때 올바른? 데이터 값을 받음
```bash
 * Serving Flask app 'main'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:8080
 * Running on http://172.16.11.71:8080
Press CTRL+C to quit
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 125-806-988


Received data: {'z': -0.991790771484375, 'x': -0.0091094970703125, 'y': -0.038482666015625}
211.234.181.95 - - [02/May/2024 14:49:12] "POST /acceleration HTTP/1.1" 500 -
```

어쨌든 mobile에서 edge로 넘어올 때는 `RESTAPI`를 사용하는데 이 api는 2hz로 전송해오는 데이터를 한번에 받지 못하는 API이다.  그래서 내가 구성해야 하는 것은 아래와 같다 

# sub/pub on edge

![[Pasted image 20240502153007.png]]

1. mobile에서 수집된 데이터가 mosquitto가 받는다.(mosquitto=broker)
2. broker는 데이터를 받아 publish 한다.
3. publish한 데이터는 collector에서 수집(`subscribe`)된다.
4. 여기서 데이터의 평균치를 내던 어떠한 가공을 거쳐 Master의 어떤 기능을 수행하는 pod로 전달 된다.


> [!todo] 작업
> 1. swift 코드에서 REST API가 아닌 mqtt 서버로 전달하는 코드로 바꾸기
> 2. mosquitto log로 메세지가 들어오는지 확인하기.
> 3. mosquitto의 데이터를 iot-collector에서 수집하기 . iot-collector 소스를 변경하기 


# 작업1

## CocoaPods 설치
: swift library를 설치하는 tool
1. `sudo gem install cocoapods`
2. swift project 폴더로 이동 
3. `pod init`
4. `Podfile` 파일이 생성 된 것을 알 수 있음.
5. 아래와 같이 입력
```
platform :ios, '9.0'
use_frameworks!

target 'Iot02' do
    pod 'CocoaMQTT'
end
```
6. `pod install` 로 라이브러리를 설치한다.
