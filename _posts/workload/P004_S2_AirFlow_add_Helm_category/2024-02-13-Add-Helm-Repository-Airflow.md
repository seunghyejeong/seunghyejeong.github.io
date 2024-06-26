---
title: Add Helm Repository Airflow
author: bami jeong
categories: SelfImprovement
layout: post
comments: true
tags:
  - Airflow
  - Helm
---

helm repo 등록 완료 
ingress 설정 

# 스크립트 및 Vars 파일 수정

> ingress 적용
> username, password 적용


```yaml
  # In order to expose the service, use the route section below
  ingress:
    enabled: true
    labels: {}
    # traffic: external
    annotations: {}
      # |
      # kubernetes.io/ingress.class: nginx
      # kubernetes.io/tls-acme: "true"
      #   or
      # kubernetes.io/ingress.class: nginx
    # kubernetes.io/tls-acme: "true"

    # Optionally use ingressClassName instead of deprecated annotation.
    # See: https://kubernetes.io/docs/concepts/services-networking/ingress/#deprecated-annotation
    ingressClassName: "{CP_DEFAULT_INGRESS_CLASS_NAME}"

    # As of Kubernetes 1.19, all Ingress Paths must have a pathType configured. The default value below should be sufficient in most cases.
    # See: https://kubernetes.io/docs/concepts/services-networking/ingress/#path-types for other possible values.
    pathType: Prefix

    # When HA mode is enabled and K8s service registration is being used,
    # configure the ingress to point to the Vault active service.
    activeService: true
    hosts:
      - host: {VAULT_INGRESS_HOST}
        paths: []

```

```bash
find ../values -name "*.yaml" -exec sed -i "s/{AIRFLOW_URL}/$AIRFLOW_URL/g" {} \;
find ../values -name "*.yaml" -exec sed -i "s/{AIRFLOW_DEFAULT_USERNAME}/$AIRFLOW_DEFAULT_USERNAME/g" {} \;
find ../values -name "*.yaml" -exec sed -i "s/{AIRFLOW_DEFAULT_PASSWORD}/$AIRFLOW_DEFAULT_PASSWORD/g" {} \;
```

```bash
kubectl create namespace ${NAMESPACE[5]}
$CMD_CREATE_REGISTRY_SECRET -n ${NAMESPACE[5]}
helm install -f ../values/${CHART_NAME[7]}.yaml ${CHART_NAME[7]} $REPOSITORY_PROJECT_NAME/airflow -n ${NAMESPACE[5]}

```


```
helm cm-push --username admin --password Harbor12345 ../charts/cp-airflow.tgz cp-portal-repository

```


### [에러러러러](Ingress.extensions "cp-airflow-ingress" is invalid: spec.rules[0].host: Invalid value: "https://airflow.133.186.218.204.nip.io": a lowercase RFC 1123 subdomain mustconsist of lower case alphanumeric characters, '-' or '.', and must start and end with an alphanumeric character (e.g. 'example.com', regex used for validation is '[a-z0-9]([-a-z0-9]*[a-z0-9])a-z0-9]([-a-z0-9]*[a-z0-9])?)

> ingress의 hosts에 "https://" 어쩌고 들어가는 것은 안 된다는 뜻.

```
find ../values -name "*.yaml" -exec sed -i "s@{VAULT_URL}@$VAULT_URL@g" {} \;
find ../values -name "*.yaml" -exec sed -i "s/{VAULT_INGRESS_HOST}/$(echo $VAULT_URL | awk -F[/:] '{print $4}')/g" {} \;

find ../values -name "*.yaml" -exec sed -i "s@{AIRFLOW_URL}@$AIRFLOW_URL@g" {} \;
find ../values -name "*.yaml" -exec sed -i "s/{AIRFLOW_INGRESS_HOST}/$(echo $AIRFLOW_URL | awk -F[/:] '{print $4}')/g" {} \;
```
> 이렇게 진행 했을 때  ingress.hosts에 "https://airflow.{HOSTDOMAIN}" 로 등록 되어 있음.

##### 해결
![[Pasted image 20240213170800.png]]

#### 아직 'warn'이지만,  결국 해결해야 하는 문제 ? 

```bash
W0213 16:07:34.437604  230656 warnings.go:70] would violate PodSecurity "restricted:v1.27": runAsNonRoot != true (pod or containers "wait-for-airflow-migrations", "webserver"must set securityContext.runAsNonRoot=true), seccompProfile (pod or containers "wait-for-airflow-migrations", "webserver" must set securityContext.seccompProfile.type to "RuntimeDefault" or "Localhost")
W0213 16:07:34.438081  230656 warnings.go:70] would violate PodSecurity "restricted:v1.27": runAsNonRoot != true (pod or container "statsd" must set securityContext.runAsNonRoot=true), seccompProfile (pod or container "statsd" must set securityContext.seccompProfile.type to "RuntimeDefault" or "Localhost")
W0213 16:07:34.438422  230656 warnings.go:70] would violate PodSecurity "restricted:v1.27": runAsNonRoot != true (pod or containers "wait-for-airflow-migrations", "scheduler", "scheduler-log-groomer" must set securityContext.runAsNonRoot=true), seccompProfile (pod or containers "wait-for-airflow-migrations", "scheduler", "scheduler-log-groomer" must set securityContext.seccompProfile.type to "RuntimeDefault" or "Localhost")
W0213 16:07:34.452330  230656 warnings.go:70] would violate PodSecurity "restricted:v1.27": runAsNonRoot != true (pod or container "redis" must set securityContext.runAsNonRoot=true), runAsUser=0 (pod must not set runAsUser=0), seccompProfile (pod or container "redis" must set securityContext.seccompProfile.type to "RuntimeDefault" or "Localhost")
W0213 16:07:34.464485  230656 warnings.go:70] kube violate PodSecurity "restricted:v1.27": runAsNonRoot != true (pod or containers "wait-for-airflow-migrations", "triggerer", "triggerer-log-groomer" must set securityContext.runAsNonRoot=true), seccompProfile (pod or containers "wait-for-airflow-migrations", "triggerer", "triggerer-log-groomer" must set securityContext.seccompProfile.type to "RuntimeDefault" or "Localhost")
W0213 16:07:34.465177  230656 warnings.go:70] would violate PodSecurity "restricted:v1.27": runAsNonRoot != true (pod or containers "wait-for-airflow-migrations", "worker", "worker-log-groomer" must set securityContext.runAsNonRoot=true), seccompProfile (pod or containers "wait-for-airflow-migrations", "worker", "worker-log-groomer" must set securityContext.seccompProfile.type to "RuntimeDefault" or "Localhost")
W0213 16:07:34.885314  230656 warnings.go:70] would violate PodSecurity "restricted:v1.27": runAsNonRoot != true (pod or container "run-airflow-migrations" must set securityContext.runAsNonRoot=true), seccompProfile (pod or container "run-airflow-migrations" must set securityContext.seccompProfile.type to "RuntimeDefault" or "Localhost")

```

# Script 파일 수정본

> cp-portal-vars.sh

```bash
NAMESPACE=(
"vault"
"harbor"
"mariadb"
"keycloak"
"cp-portal"
"airflow" #add
)
---
CHART_NAME=(
"cp-vault"
"cp-harbor"
"cp-mariadb"
"cp-keycloak"
"cp-portal-resource"
"cp-portal-app"
"cp-cert-setup"
"cp-airflow" #add
)
---
# add
# AIRFLOW
AIRFLOW_URL="https://airflow.${HOST_DOMAIN}"
AIRFLOW_DEFAULT_USERNAME="cp-admin"
AIRFLOW_DEFAULT_PASSWORD="admin"
```

> deploy-cp-portal.sh

```bash
find ../values -name "*.yaml" -exec sed -i "s@{AIRFLOW_URL}@$AIRFLOW_URL@g" {} \;
find ../values -name "*.yaml" -exec sed -i "s/{AIRFLOW_DEFAULT_USERNAME}/$AIRFLOW_DEFAULT_USERNAME/g" {} \;
find ../values -name "*.yaml" -exec sed -i "s/{AIRFLOW_DEFAULT_PASSWORD}/$AIRFLOW_DEFAULT_PASSWORD/g" {} \;
find ../values -name "*.yaml" -exec sed -i "s/{AIRFLOW_STORAGECLASS}/$K8S_STORAGECLASS/g" {} \;
---

#add 0. deploy the airflow
kubectl create namespace ${NAMESPACE[5]}
$CMD_CREATE_REGISTRY_SECRET -n ${NAMESPACE[5]}
helm install -f ../values/${CHART_NAME[7]}.yaml ${CHART_NAME[7]} $REPOSITORY_PROJECT_NAME/airflow -n ${NAMESPACE[5]}
```

> cp-airflow.yaml(./values_origin/cp-airflow.yaml)

```yaml
# Ingress configuration
ingress:
  enabled: false
  web:
    enabled: true
    path: "/"
    pathType: "ImplementationSpecific"
    host: ""
    hosts:
      - name: airflow.{HOST_DOMAIN}  #add
    ingressClassName: "{CP_DEFAULT_INGRESS_CLASS_NAME}" #add
    tls:
      enabled: false
      secretName: ""
    precedingPaths: []
    succeedingPaths: []

# Persistence
  persistence:
    enabled: true
    size: 100Gi
    storageClassName: "{AIRFLOW_STORAGECLASS}"
    fixPermissions: false
    annotations: {}
```


# *추가적으로 values 값을 변경 해야 하는 것 LIST*
## 1. PyPI package 설치

- [b] REF
> [airflow_helmchart_docs](https://github.com/airflow-helm/charts/blob/main/charts/airflow/docs/faq/configuration/extra-python-packages.md)
> [airflow docs](https://airflow.apache.org/docs/helm-chart/stable/quick-start.html#install-kind-and-create-a-cluster)
- [i] Version
> image: apache/airflow:2.8.1

### Dockerfile을 만들어 image를 빌드 한 후 chart의 values.yaml에 추가 시키기
- [?] 이 Dockerfile을... Harbor에 올리나 ?

- example
```dockerfile
FROM apache/airflow:2.8.1

# install pip packages for airflow example
RUN pip install --no-cache-dir \
    pandas~
    requests~
    selenium~ 
    beautifulsoup4~
    beautifulsoup4 lxml~

# install pip packages for kafka 
RUN pip install --no-cache-dir \
    kafka-python~
    airflow-provider-kafka~ 
    apache-airflow-providers-apache-kafka~==1.3.1 
    confluent-kafka~
```


## 2. Dag 사용

- [b] REF
> [how to git sync](https://airflow.apache.org/docs/helm-chart/stable/manage-dags-files.html)

```yaml

```
## 3. Log 저장

- [b] REF
> [how to manage logs](https://airflow.apache.org/docs/helm-chart/stable/manage-logs.html)


## 4. Example Dags 로딩 안하기

> values.yaml
```bash
  --set-string "env[0].name=AIRFLOW__CORE__LOAD_EXAMPLES" \
  --set-string "env[0].value=True"
```

## 5. Config Allow

> values.yaml
```yaml
config:
  webserver:
    expose_config: 'True'  # by default this is 'False'
```

