---
title: Airflow's Permission
author: bami jeong
categories: SelfImprovement
layout: post
comments: true
tags:
  - Airflow
  - Helm
---

#AIRFLOW_HELM_CMD

```bash
helm repo add apache-airflow https://airflow.apache.org
helm pull apache-airflow/airflow
helm upgrade --install airflow apache-airflow/airflow --namespace airflow --create-namespace -f custom_values.yaml

```

```
helm delete airflow apache-airflow/airflow --namespace airflow 
```

```bash
helm upgrade --install airflow apache-airflow/airflow --namespace airflow --create-namespace -f custom_values.yaml
```

```bash
helm upgrade airflow apache-airflow/airflow --namespace airflow -f custom_values.yaml
```



# webserver mount

> custom_values.yaml
```yaml
#airflowHome: /home/ubuntu/airflow
# Custom Images (include PyPI Packages)
images:
  airflow:
    repository: seunghyejeong/airflow
    tag: "1.0"
    digest: ~
    pullPolicy: IfNotPresent

# Load Examples
extraEnv: |
  - name: AIRFLOW__CORE__LOAD_EXAMPLES
    value: 'True'

# Webserver configure
webserver:
  defaultUser:
    enabled: true
    role: Admin
    username: admin
    email: admin@example.com
    firstName: admin
    lastName: user
    password: admin
  service:
    type: NodePort
    ports:
      - name: airflow-ui
        port: 8080
        targetPort: 8080
        nodePort: 31151
  # Mount additional volumes into webserver. 
%%   extraVolumeMounts: # container
     - name: d ags
       mountPath: /opt/airflow/dags
       readOnly: true  
  extraVolumes: # local
     - name: airflow-webserver-dags
       persistentVolumeClaim:
         claimName: airflow-webserver-dags %%

  extraVolumeMounts: # container
     - name: airflow-dags
       mountPath: /opt/airflow/dags
  extraVolumes: # local
     - name: airflow-dags
       persistentVolumeClaim:
         claimName: airflow-dags
# bind w strogaeClass
dags:
  persistence:
    enabled: true
    storageClassName: cp-storageclass
    accessMode: ReadWriteMany
    size: 5Gi
workers:
  persistence:
    enabled: true
    storageClassName: cp-storageclass
    size: 5Gi
logs:
  persistence:
    enabled: true
    storageClassName: cp-storageclass    
```

```yaml
  # Mount additional volumes into webserver. 
     extraVolumes:
       - name: airflow-webserver-dags
         persistentVolumeClaim:
           claimName: airflow-webserver-dags
      extraVolumeMounts:
       - name: airflow-webserver-dags
         mountPath: /opt/airflow/dags
         readOnly: true
```

```bash
kubectl cp ./dags/kafkatest.py aairflow-scheduler-65dcd77cbc-rtng9:/opt/airflow/dags/kafkatest.py -n airflow 
```


```bash
docker build --no-cache -t seunghyejeong/airflow:1.0 .
docker push seunghyejeong/airflow:1.0
```


# 와나 걍 포기하려 했는데 ;ㅁ;ㅁㅁ;ㅁ;ㅁ 드디어 example 예제가 웹서버에 ㅠ

일단 도커파일을 먼저 바꿈

```Dockerfile
FROM apache/airflow:2.8.1
RUN echo $PATH
ENV PATH="$PATH:/home/airflow/.local/bin"
RUN echo $PATH
USER root
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
        vim
COPY ./dags/*.py /opt/airflow/dags/
USER airflow
COPY requirements.txt /
RUN pip install --no-cache-dir "apache-airflow==2.8.1" -r /requirements.txt
```

dag 파일이 root 권한으로 폴더가 옮겨져야 하는 것 같다는 생각에 위치를 바꿨고 

```yaml
#airflowHome: /home/ubuntu/airflow
# Custom Images (include PyPI Packages)
images:
  airflow:
    repository: seunghyejeong/airflow
    tag: "1.0"
    digest: ~
    pullPolicy: IfNotPresent

# Load Examples
extraEnv: |
  - name: AIRFLOW__CORE__LOAD_EXAMPLES
    value: 'True'

# Webserver configure
webserver:
  defaultUser:
    enabled: true
    role: Admin
    username: admin
    email: admin@example.com
    firstName: admin
    lastName: user
    password: admin
  service:
    type: NodePort
    ports:
      - name: airflow-ui
        port: 8080
        targetPort: 8080
        nodePort: 31151
  # Mount additional volumes into webserver. 
  extraVolumeMounts: # container
     - name: airflow-dags
       mountPath: /opt/airflow/dags
  extraVolumes: # local
     - name: airflow-dags
       persistentVolumeClaim:
         claimName: airflow-dags
# bind w strogaeClass
dags:
  persistence:
    enabled: true
    storageClassName: cp-storageclass
    accessMode: ReadWriteMany
    size: 5Gi
workers:
  persistence:
    enabled: true
    storageClassName: cp-storageclass
    size: 5Gi
logs:
  persistence:
    enabled: true
    storageClassName: cp-storageclass    
```

webserver에 dag폴더가 있는게 자꾸 마운트가 안되길래 보니 `extraVolume`을 사용해야 하는 것이었음. 
그래서 webserver도 `airflow-dag`와 마운트 시켜줌.

그러니까 컨테이너 안의 /opt/airflow/dag이 scheduler, worker ..등등의 컨테이너와 마운트 되어 공유 되더라. 

아무튼 다했따 !



