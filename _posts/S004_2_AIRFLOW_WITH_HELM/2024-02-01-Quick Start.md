- kafka 설치
> [linux_ubuntu22.04_설치](https://firststep-de.tistory.com/11)



1. downloading binaries,
2. 클라우드 환경에서는 `confluent-kafka` 인데 유료다 ! 그리고 서비스를 이용하려면 무료 이용료를 써야하는거고 ,, 그래서 로컬에서 설치하나보다 
   > [conflouent배포](https://docs.confluent.io/cloud/current/get-started/free-trial.html#free-trial)


---

## 설치

- [i] version 
> kafka_2.13-3.6.1, local
> java 11+
> Python 3.10.12
> airflow version 2.8.1

- [b] REF
> [wget.exe](https://eternallybored.org/misc/wget/)

- [!] issue
> [kafka_zookeeper_중단?](https://www.ciokorea.com/news/235594)

### KAFKA
 위의 issue로 인해 zookeeper를 사용하지 않고 kraft를 사용해 설치

- [b] REF
> kafka official docs getting start](https://kafka.apache.org/documentation/#quickstart)
> [kafka 다운로드 url](https://www.apache.org/dyn/closer.cgi?path=/kafka/3.6.1/kafka_2.13-3.6.1.tgz)
> [kafka_설치_가이드_블로그](https://hoing.io/archives/4029#KRaft)

##### Kafka with KRaft

- kafka 다운로드
```bash
wget https://dlcdn.apache.org/kafka/3.6.1/kafka_2.13-3.6.1.tgz
```

- 경로 지정
```bash
sudo tar xvf kafka_2.13-3.6.1.tgz -C /usr/local
cd /usr/local
sudo ln -s kafka_2.13-3.6.1 kafka
```

- log 디렉토리 만들기
```bahs
/usr/local/kafka/kraft-combined-logs
```

- 환경 변수
```bash
export KAFKA_HEAP_OPTS="-Xms512m -Xmx512m"
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64/
```

Generate a Cluster UUID

```bash
KAFKA_CLUSTER_ID="$(bin/kafka-storage.sh random-uuid)"
```

```bash
ubuntu@bami:/usr/local/kafka$ ./bin/kafka-storage.sh random-uuid
sMOs4RnKRY2nsh41ZjrKNQ
```

Format Log Directories

```bash
bin/kafka-storage.sh format -t $KAFKA_CLUSTER_ID -c config/kraft/server.properties
```

Start the Kafka Server

```bash
bin/kafka-server-start.sh config/kraft/server.properties
```



##### confluent kafka witn KRaft

```bash
sudo su 
curl -O https://packages.confluent.io/archive/7.5/confluent-community-7.5.3.tar.gz
```

```bash
export CONFLUENT_HOME=/usr/local/confluent
```

```bash
export PATH=$PATH:$CONFLUENT_HOME/bin
```
### AIRFLOW

- [b] REF
> [[Airflow 활용 Guide]]


