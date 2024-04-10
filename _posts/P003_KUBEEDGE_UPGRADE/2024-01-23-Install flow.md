---
title: install
author: bami jeong
categories:
  - Kubeedge
tags:
  - install
  - Kubeedge
  - Migration
  - Workflow
category: kubeedge
---


# MasterNode

### keadm
```bash
wget https://github.com/kubeedge/kubeedge/releases/download/v1.15.1/keadm-v1.15.1-linux-amd64.tar.gz
tar -xvf 
cp keadm-v1.15.1-linux-amd64/keadm/keadm /usr/local/bin/keadm
```
### cloudcore 
```bash
git clone https://github.com/kubeedge/kubeedge.git
cd kubeedge/manifest/charts
```

```bash
helm upgrade --install cloudcore ./cloudcore --namespace kubeedge --create-namespace -f ./cloudcore/values.yaml --set cloudCore.modules.cloudHub.advertiseAddress[0]=133.186.220.206
```


### token
```bash
sudo keadm gettoken
```

### kube-proxy 설치 해제
- kube-proxy daemonset 
```yaml
      affinity:
        nodeAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            nodeSelectorTerms:
            - matchExpressions:
              - key: node-role.kubernetes.io/edge
                operator: DoesNotExist
```
# Edgenode

### cri-o
```bash
wget https://storage.googleapis.com/cri-o/artifacts/cri-o.amd64.v1.26.4.tar.gz
tar xvf cri-o.amd64.v1.26.4.tar.gz 
ls
cd cri-o
ll
./install 
systemctl restart crio
systemctl status crio
```
### keadm
```bash
wget https://github.com/kubeedge/kubeedge/releases/download/v1.15.1/keadm-v1.15.1-linux-amd64.tar.gz
tar -xvf 
cp keadm-v1.15.1-linux-amd64/keadm/keadm /usr/local/bin/keadm
```

### keadm join
```bash
keadm join --cloudcore-ipport="133.186.251.185":30000 --token={$TOKEN}--kubeedge-version=v1.14.1 --remote-runtime-endpoint=unix:///var/run/crio/crio.sock
```

### cri-o config
```bash
vi /etc/containers/registries.conf
```

```bash
unqualified-search-registries = ["docker.io", "quay.io"]
```

### edgecore.yaml
- remote
- cgroup: systemd
- nodeport 
-
# Command
- log
```bash
journalctl -u edgecore.service -xe
```


## Edgemesh

```bash
kubectl taint nodes --all node-role.kubernetes.io/control-plane
```

```bash
kubectl label services kubernetes service.edgemesh.kubeedge.io/service-proxy-name="edgemesh"
```

```bash
helm install edgemesh --namespace kubeedge \
--set agent.psk=tk0DGvIctc8dHI4n1wnC9JiWTZS92i5TYOf9mFe8fXs= \
--set agent.relayNodes[0].nodeName=bamicore1,agent.relayNodes[0].advertiseAddress="{PUBLIC_IP}" \
--set agent.relayNodes[1].nodeName=bamicore2,agent.relayNodes[1].advertiseAddress="{PRIVATE_IP,PUBLIC_IP}" \
--set agent.relayNodes[2].nodeName=edge,agent.relayNodes[2].advertiseAddress="{PRIVATE_IP,PUBLIC_IP}" \
https://raw.githubusercontent.com/kubeedge/edgemesh/main/build/helm/edgemesh.tgz
```

