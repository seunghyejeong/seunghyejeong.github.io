---
title: Deploy Status
author: bami jeong
categories: development
layout: post
comments: true
tags:
  - iot
  - apps
  - develop
---


# mosquitto 배포, 통신

- [b] REF
> [Ingress-nginx mosquitto](https://www.enabler.no/blog/mosquitto-mqtt-broker-in-kubernetes)


- [check] 참고

```
kubectl create configmap mariadb-init-db --from-file=dbconfig.ini 
```


- websocket: mosquitto conf 설정
    - mosquitto configmap: `mosquitto.conf`
    - listener, protocol 설정

```
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mosquitto
spec:
  replicas: 1
  selector:
    matchLabels:
      app: mosquitto
  template:
    metadata:
      labels:
        app: mosquitto
    spec:
      containers:
      - name: mosquitto
        image: eclipse-mosquitto
        ports:
        - containerPort: 8883
        - containerPort: 9001
        volumeMounts:
        - mountPath: /mosquitto/config/mosquitto.conf
          subPath: mosquitto.conf
          name: config
        - mountPath: /mosquitto/certs/
          name: certs
      volumes:
      - name: config
        configMap:
          name: mosquitto-config
      - name: certs
        secret:
          secretName: mosquitto-certs
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: mosquitto-config
data:
  mosquitto.conf: |
    # DO NOT USE IN PRODUCTION
    allow_anonymous true

    # MQTT with TLS (MQTTS)
    listener 8883
    protocol mqtt

    # Fetch the generated certificates
    cafile /etc/ssl/certs/ca-certificates.crt
    keyfile /mosquitto/certs/tls.key
    certfile /mosquitto/certs/tls.crt
---
apiVersion: v1
kind: Service
metadata:
  name: mosquitto-mqtts
spec:
  type: ClusterIP
  selector:
    app: mosquitto  
  ports:
  - port: 8883
```

> [!question] 
> websocket 필요? (해당 부분에 대한 configure가 들어갔는지 ) : listener, protocol
>     해줬음
> go.mod에 있는 websockets는 뭔지 
>     모든 Web 모듈에는 있는게 websockets 이라고 함

### mosquitto 외부 설정 
1. mosquitto configmap을 생성하여 deployment에 volume mount를 진행 한다.

> configmap
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: mosquitto-config
data:
  mosquitto.conf: |
    listener 1883
    listener 9001
    protocol websockets
    allow_anonymous true
```

> deployment
```yaml
    spec:
      containers:
      - name: mosquitto
        image: eclipse-mosquitto:latest
        ports:
        - containerPort: 1883
          name: mqtt
        - containerPort: 9001
          name: websockets
        volumeMounts:
        - name: mosquitto-config-volume
          mountPath: /mosquitto/config/mosquitto.conf
          subPath: mosquitto.conf
          readOnly: false
      volumes:
      - name: mosquitto-config-volume
        configMap:
          name: mosquitto-config
```

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mosquitto
spec:
  replicas: 1
  selector:
    matchLabels:
      app: mosquitto
  template:
    metadata:
      labels:
        app: mosquitto
    spec:
      containers:
        - name: mosquitto
          image: eclipse-mosquitto:latest
          ports:
            - containerPort: 1883
              name: mqtt
            - containerPort: 9001
              name: websockets
          volumeMounts:            # Moved volumeMounts inside the containers section
            - name: mosquitto-config-volume
              mountPath: /mosquitto/config/mosquitto.conf
              subPath: mosquitto.conf
              readOnly: false
      volumes:
        - name: mosquitto-config-volume
          configMap:
            name: mosquitto-config
---
apiVersion: v1
kind: Service
metadata:
  name: mosquitto
spec:
  type: NodePort
  ports:
    - port: 1883
      targetPort: mqtt
      nodePort: 30000
      name: mqtt
    - port: 9001
      targetPort: websockets
      nodePort: 30001
      name: websockets
  selector:
    app: mosquitto
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: mosquitto-config
data:
  mosquitto.conf: |
    listener 1883
    listener 9001
    protocol websockets
    allow_anonymous true
```
- [b] REF
> https://bradheo.tistory.com/entry/MQTT-PubSub-Python

# Collector가 하는 일 다시 생각


- 배경
    - main.py를 배포 하는데 자꾸 에러가 나는거임. 
    ```bash
    Traceback (most recent call last):
      File "/build/main.py", line 81, in <module>
        run()
      File "/build/main.py", line 76, in run
        client = connect_mqtt()
      File "/build/main.py", line 38, in connect_mqtt
        client.connect(host=host, port=port)
      File "/usr/local/lib/python3.10/site-packages/paho/mqtt/client.py", line 1435, in connect
        return self.reconnect()
      File "/usr/local/lib/python3.10/site-packages/paho/mqtt/client.py", line 1598, in reconnect
        self._sock = self._create_socket()
      File "/usr/local/lib/python3.10/site-packages/paho/mqtt/client.py", line 4609, in _create_socket
        sock = self._create_socket_connection()
      File "/usr/local/lib/python3.10/site-packages/paho/mqtt/client.py", line 4640, in _create_socket_connection
        return socket.create_connection(addr, timeout=self._connect_timeout, source_address=source)
      File "/usr/local/lib/python3.10/socket.py", line 845, in create_connection
        raise err
      File "/usr/local/lib/python3.10/socket.py", line 833, in create_connection
        sock.connect(sa)
    TimeoutError: timed out
    ```
    - 그래서 mosquitto가 통신이 되지 않아서 그런가? 해서 mosquitto 통신 문제를 해결함.
    - 하고 deploy 했는데 여전히 똑같은 에러.ㅠㅠ 그래서 차장님께 여쭈어 봤다.


- [?] iot-sensor-collector가 하는일이 뭐야 !? 
>  collector가 connect을 해야 할 이유가 있나 ? 
>  collector는 모바일 데이터의 수집된 데이터를 edge 노드로 옮겨오는 행위를 하는 collector이다.
>  edge node로 온 data는 client node에서 또 가공 될 수 있다. 이게 스토리 보드.


![[Pasted image 20240430164528.png]]

