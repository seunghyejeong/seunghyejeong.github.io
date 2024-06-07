---
title: Ingress, customValues, mount etc.
author: bami jeong
categories: SelfImprovement
layout: post
comments: true
tags:
  - Airflow
  - Helm
---

## Project Name: Airflow Helm Chart Config 
#### Date: 2024-02-14 09:20 
#### Tag: #airflowhelm
---
# Contents:

- [b] REF
> [[2024-02-13-Add-Helm-Repository-Airflow#*추가적으로 values 값을 변경 해야 하는 것 LIST*]]

- [!] version
> apache-airflow                           2.8.1
> apache-airflow-providers-apache-kafka    1.3.1
> confluent-kafka                          2.3.0
> kafka-python                             2.0.2
> beautifulsoup4                           4.12.3
> pandas                                   2.2.0
> selenium                                 4.17.2
> lxml                                     5.1.0
> requests                                 2.31.0
> virtualenv                               20.25.0

# airflow에 필요한 도커 파일을 만든다. 도커 파일은 Airflow 운영에 필요한 PyPI 패키지 설치가 포함 되어 있다. 
# 또한 Ingress를 적용하여 Container Platform의 Portal에 연동 되도록 수정 하였다.

## Install PyPI package

```Dockerfile
FROM apache/airflow:2.8.1

# Install pip packages for airflow example
RUN pip install --no-cache-dir \
    pandas~=2.2.0 \
    requests~=2.31.0 \
    selenium~=4.17.2 \
    beautifulsoup4~=4.12.3 \
    lxml~=5.1.0
# Install pip packages for kafka
    kafka-python~=2.0.2 \
    apache-airflow-providers-apache-kafka~=1.3.1 \
    confluent-kafka~=2.3.0
```

```Dockerfile
FROM apache/airflow:2.8.1

# Install pip packages for airflow example and kafka
RUN pip install --no-cache-dir \
    pandas~=2.2.0 \
    requests~=2.31.0 \
    selenium~=4.17.2 \
    beautifulsoup4~=4.12.3 \
    lxml~=5.1.0 \
    kafka-python~=2.0.2 \
    apache-airflow-providers-apache-kafka~=1.3.1 \
    confluent-kafka~=2.3.0
```

### imagePullBackError
- [b] REF
> [Airflow Custom DockerImage](https://eng-sohee.tistory.com/138)
- 그냥 package만 설치하고 airflow에 대한 설치는 안헤서 그런듯.

---
~~Dockerfile
FROM apache/airflow:2.8.1
Define environment variables
ENV AIRFLOW_VERSION=2.8.1
ENV PYTHON_VERSION="$(python --version | cut -d " " -f 2 | cut -d "." -f 1-2)"
ENV CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"
RUN apt-get update 
Install Apache Airflow and additional dependencies
RUN pip install --no-cache-dir \
    pandas~=2.2.0 \
    requests~=2.31.0 \
    selenium~=4.17.2 \
    beautifulsoup4~=4.12.3 \
    lxml~=5.1.0 \
    kafka-python~=2.0.2 \
    apache-airflow-providers-apache-kafka~=1.3.1 \
    confluent-kafka~=2.3.0 \
    "apache-airflow==${AIRFLOW_VERSION}" --constraint "${CONSTRAINT_URL}"~~

---

### requirement 파일 생성 후 Build

- [!] requirement.txt file 
> https://raw.githubusercontent.com/apache/airflow/constraints-2.8.1/constraints-3.8.txt

```Dockerfile
FROM apache/airflow:2.8.1

COPY requirements.txt .

RUN pip install -r requirements.txt

```


### Command ‘krb5-config –libs gssapi’ returned non-zero exit status 

- [b] REF
> [User 설정을 해줘야 한다고](https://forums.docker.com/t/cant-figure-out-this-error-command-krb5-config-libs-gssapi-returned-non-zero-exit-status-127/135633)


```Dockerfile
FROM apache/airflow:2.8.1-python3.10
ADD requirements.txt .
USER root
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
         gcc \
         heimdal-dev \
  && apt-get autoremove -yqq --purge \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*
USER airflow
RUN pip install -r requirements.txt
RUN pip uninstall -y argparse
```

```bash
sudo podman build --tag harbor.133.186.240.216.nip.io/cp-portal-repository/cp-airflow:v1 .

sudo podman push harbor.133.186.240.216.nip.io/cp-portal-repository/cp-airflow:v1
```

##### pip package 삭제
```bash
pip uninstall -r requirements.txt -y
```
##### upgrade 없이 설치 
```bash
pip install --upgrade --no-deps --force-reinstall -r requirements.txt
```

### pkg-config not found .. mysqlclient

```Dockerfile
FROM apache/airflow:2.8.1-python3.10
ADD requirements.txt .
USER root
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
         gcc \
         heimdal-dev \
         default-libmysqlclient-dev \
         pkg-config
  && apt-get autoremove -yqq --purge \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*
USER airflow
RUN pip install -r requirements.txt
RUN pip uninstall -y argparse
```

---

- cp-airflow.yaml
```yaml
images:
  airflow:
    repository: localhost:5000/container-platform/$REPOSITORY_HOST/$REPOSITORY_PROJECT_NAME/airflow
    tag: "v1"
```

- deploy-cp-portal.sh
```sh
cd ../airflow
sudo podman build --tag airflow $REPOSITORY_HOST/$REPOSITORY_PROJECT_NAME/cp-airflow:v1 .
sudo podman push $REPOSITORY_HOST/$REPOSITORY_PROJECT_NAME/cp-airflow:v1
cd ../script
```


### ㅠㅠ  모르ㅔㄱ썽;;

- requirements.txt

```text
pandas~=2.2.0
requests~=2.31.0
selenium~=4.17.2
beautifulsoup4~=4.12.3
lxml~=5.1.0
kafka-python~=2.0.2
apache-airflow-providers-apache-kafka~=1.3.1
confluent-kafka~=2.3.0
```

```bash
helm cm-push --username admin --password Harbor12345 ../charts/cp-airflow.tgz cp-portal-repository
```

```bash
helm install -f ../values/cp-airflow.yaml cp-airflow cp-portal-repository/cp-airflow -n airflow
```

```bash
ubuntu@bami1:~/workspace/container-platform/cp-portal-deployment/values$ helm install -f ../values/cp-airflow.yaml cp-airflow cp-portal-repository/airflow -n airflow
```

![[Pasted image 20240214173951.png]]
## Enable Logcs

`logs.persistence.enabled=True`

- cp-airflow.yaml
```yaml
logs:
  # Configuration for empty dir volume (if logs.persistence.enabl[ed == false)
  # emptyDirConfig:
  #   sizeLimit: 1Gi
  #   medium: Memory

  persistence:
    # Enable persistent volume for storing logs
    enabled: true
    # Volume size for logs
    size: 100Gi
    # Annotations for the logs PVC
    annotations: {}
    # If using a custom storageClass, pass name here
    storageClassName: "{AIRFLOW_STORAGECLASS}"
    ## the name of an existing PVC to use
    existingClaim:
```


## Example Dags Load

- cp-airflow.yaml
```yaml
extraEnv: |
  - name: AIRFLOW__CORE__LOAD_EXAMPLES
    value: 'True'

```


## Mounting Dags w. Persistence Volume

- [b] REF
> [Management Dags](https://airflow.apache.org/docs/helm-chart/stable/manage-dags-files.html)

cp-airflow.yaml
```yaml
dags:
  # Where dags volume will be mounted. Works for both persistence and gitSync.
  # If not specified, dags mount path will be set to $AIRFLOW_HOME/dags
  mountPath: ~
  persistence:
    # Annotations for dags PVC
    annotations: {}
    # Enable persistent volume for storing dags
    enabled: True
    # Volume size for dags
    size: 1Gi
    # If using a custom storageClass, pass name here
    storageClassName: "{AIRFLOW_STORAGECLASS}"
    # access mode of the persistent volume
    accessMode: ReadWriteOnce
    ## the name of an existing PVC to use
    existingClaim:
    ## optional subpath for dag volume mount
    subPath: ~
  gitSync:
    enabled: false
```

