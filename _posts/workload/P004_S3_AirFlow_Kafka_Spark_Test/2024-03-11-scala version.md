
![[Pasted image 20240308180051.png]]

```python 
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from pyspark.sql import SparkSession
from kafka import KafkaProducer, KafkaConsumer
from kafka.admin import KafkaAdminClient, NewTopic
from datetime import datetime
from airflow.models import TaskInstance
from kafka.errors import TopicAlreadyExistsError


bootstrap_servers = '180.210.82.237:19092'
spark_master_url = '180.210.82.237:7077'
topic_name = 'devices'

# Function to check if Kafka is connected
def check_connected():
    try:
        spark = SparkSession.builder.appName('first').master("spark://180.210.82.237:7077").getOrCreate()
        print(spark)
        print("Successfully connected to Spark & Kafk!")
        return True

    except Exception as e:
        print(f"Error connecting to Kafka: {str(e)}")
        return False

check_connected()

```

```java
test.py:2 DeprecationWarning: The `airflow.operators.python_operator.PythonOperator` class is deprecated. Please use `'airflow.operators.python.PythonOperator'`.
Setting default log level to "WARN".
To adjust logging level use sc.setLogLevel(newLevel). For SparkR, use setLogLevel(newLevel).
24/03/08 07:08:07 WARN NativeCodeLoader: Unable to load native-hadoop library for your platform... using builtin-java classes where applicable
24/03/08 07:08:08 WARN StandaloneAppClient$ClientEndpoint: Failed to connect to master 180.210.82.237:7077
org.apache.spark.SparkException: Exception thrown in awaitResult:
	at org.apache.spark.util.ThreadUtils$.awaitResult(ThreadUtils.scala:301)
	at org.apache.spark.rpc.RpcTimeout.awaitResult(RpcTimeout.scala:75)
	at org.apache.spark.rpc.RpcEnv.setupEndpointRefByURI(RpcEnv.scala:102)
	at org.apache.spark.rpc.RpcEnv.setupEndpointRef(RpcEnv.scala:110)
	at org.apache.spark.deploy.client.StandaloneAppClient$ClientEndpoint$$anon$1.run(StandaloneAppClient.scala:107)
	at java.util.concurrent.Executors$RunnableAdapter.call(Executors.java:511)
	at java.util.concurrent.FutureTask.run(FutureTask.java:266)
	at java.util.concurrent.ThreadPoolExecutor.runWorker(ThreadPoolExecutor.java:1149)
	at java.util.concurrent.ThreadPoolExecutor$Worker.run(ThreadPoolExecutor.java:624)
	at java.lang.Thread.run(Thread.java:750)
Caused by: java.lang.RuntimeException: java.io.InvalidClassException: org.apache.spark.rpc.netty.RpcEndpointVerifier$CheckExistence; local class incompatible: stream classdesc serialVersionUID = 5378738997755484868, local class serialVersionUID = 7789290765573734431
	at java.io.ObjectStreamClass.initNonProxy(ObjectStreamClass.java:699)
	at java.io.ObjectInputStream.readNonProxyDesc(ObjectInputStream.java:2005)
	at java.io.ObjectInputStream.readClassDesc(ObjectInputStream.java:1852)
	at java.io.ObjectInputStream.readOrdinaryObject(ObjectInputStream.java:2186)
	at java.io.ObjectInputStream.readObject0(ObjectInputStream.java:1669)
	at java.io.ObjectInputStream.readObject(ObjectInputStream.java:503)
	at java.io.ObjectInputStream.readObject(ObjectInputStream.java:461)
	at org.apache.spark.serializer.JavaDeserializationStream.readObject(JavaSerializer.scala:87)
	at org.apache.spark.serializer.JavaSerializerInstance.deserialize(JavaSerializer.scala:123)
	at org.apache.spark.rpc.netty.NettyRpcEnv.$anonfun$deserialize$2(NettyRpcEnv.scala:299)
	at scala.util.DynamicVariable.withValue(DynamicVariable.scala:62)
	at org.apache.spark.rpc.netty.NettyRpcEnv.deserialize(NettyRpcEnv.scala:352)
	at org.apache.spark.rpc.netty.NettyRpcEnv.$anonfun$deserialize$1(NettyRpcEnv.scala:298)
	at scala.util.DynamicVariable.withValue(DynamicVariable.scala:62)
	at org.apache.spark.rpc.netty.NettyRpcEnv.deserialize(NettyRpcEnv.scala:298)
	at org.apache.spark.rpc.netty.RequestMessage$.apply(NettyRpcEnv.scala:646)
	at org.apache.spark.rpc.netty.NettyRpcHandler.internalReceive(NettyRpcEnv.scala:697)
	at org.apache.spark.rpc.netty.NettyRpcHandler.receive(NettyRpcEnv.scala:682)
	at o
	at io.netty.channel.AbstractChannelHandlerContext.invokeChannelRead(AbstractChannelHandlerContext.java:365)
	at io.netty.channel.DefaultChannelPipeline.fireChannelRead(DefaultChannelPipeline.java:919)
	at io.netty.channel.nio.AbstractNioByteChannel$NioByteUnsafe.read(AbstractNioByteChannel.java:166)
	at io.netty.channel.nio.NioEventLoop.processSelectedKey(NioEventLoop.java:722)
	at io.netty.channel.nio.NioEventLoop.processSelectedKeysOptimized(NioEventLoop.java:658)
	at io.netty.channel.nio.NioEventLoop.processSelectedKeys(NioEventLoop.java:584)
	at io.netty.channel.nio.NioEventLoop.run(NioEventLoop.java:496)
	at io.netty.util.concurrent.SingleThreadEventExecutor$4.run(SingleThreadEventExecutor.java:986)
	at io.netty.util.internal.ThreadExecutorMap$2.run(ThreadExecutorMap.java:74)
	at io.netty.util.concurrent.FastThreadLocalRunnable.run(FastThreadLocalRunnable.java:30)
	at java.lang.Thread.run(Thread.java:750)


	at io.netty.channel.nio.AbstractNioByteChannel$NioByteUnsafe.read(AbstractNioByteChannel.java:166)
	at io.netty.channel.nio.NioEventLoop.processSelectedKey(NioEventLoop.java:722)
	at io.netty.channel.nio.NioEventLoop.processSelectedKeysOptimized(NioEventLoop.java:658)
	at io.netty.channel.nio.NioEventLoop.processSelectedKeys(NioEventLoop.java:584)
	at io.netty.channel.nio.NioEventLoop.run(NioEventLoop.java:496)
	at io.netty.util.concurrent.SingleThreadEventExecutor$4.run(SingleThreadEventExecutor.java:986)
	at io.netty.util.internal.ThreadExecutorMap$2.run(ThreadExecutorMap.java:74)
	at io.netty.util.concurrent.FastThreadLocalRunnable.run(FastThreadLocalRunnable.java:30)
	... 1 more
24/03/08 07:08:28 WARN StandaloneAppClient$ClientEndpoint: Failed to connect to master 180.210.82.237:7077
org.apache.spark.SparkException: Exception thrown in awaitResult:
	at org.apache.spark.util.ThreadUtils$.awaitResult(ThreadUtils.scala:301)
	at org.apache.spark.rpc.RpcTimeout.awaitResult(RpcTimeout.scala:75)
	at org.apache.spark.rpc.RpcEnv.setupEndpointRefByURI(RpcEnv.scala:102)
	at org.apache.spark.rpc.RpcEnv.setupEndpointRef(RpcEnv.scala:110)
	at org.apache.spark.deploy.client.StandaloneAppClient$ClientEndpoint$$anon$1.run(StandaloneAppClient.scala:107)
	at java.util.concurrent.Executors$RunnableAdapter.call(Executors.java:511)
	at java.util.concurrent.FutureTask.run(FutureTask.java:266)
	at java.util.concurrent.ThreadPoolExecutor.runWorker(ThreadPoolExecutor.java:1149)
	at java.util.concurrent.ThreadPoolExecutor$Worker.run(ThreadPoolExecutor.java:624)
	at java.lang.Thread.run(Thread.java:750)
Caused by: java.lang.RuntimeException: java.io.InvalidClassException: org.apache.spark.rpc.netty.RpcEndpointVerifier$CheckExistence; local class incompatible: stream classdesc serialVersionUID = 5378738997755484868, local class serialVersionUID = 7789290765573734431
	at java.io.ObjectStreamClass.initNonProxy(ObjectStreamClass.java:699)
	at java.io.ObjectInputStream.readNonProxyDesc(ObjectInputStream.java:2005)
	at java.io.ObjectInputStream.readClassDesc(ObjectInputStream.java:1852)
	at java.io.ObjectInputStream.readOrdinaryObject(ObjectInputStream.java:2186)
	at java.io.ObjectInputStream.readObject0(ObjectInputStream.java:1669)
	at java.io.ObjectInputStream.readObject(ObjectInputStream.java:503)
	at java.io.ObjectInputStream.readObject(ObjectInputStream.java:461)
	at org.apache.spark.serializer.JavaDeserializationStream.readObject(JavaSerializer.scala:87)
	at org.apache.spark.serializer.JavaSerializerInstance.deserialize(JavaSerializer.scala:123)
	at org.apache.spark.rpc.netty.NettyRpcEnv.$anonfun$deserialize$2(NettyRpcEnv.scala:299)
	at scala.util.DynamicVariable.withValue(DynamicVariable.scala:62)
	at org.apache.spark.rpc.netty.NettyRpcEnv.deserialize(NettyRpcEnv.scala:352)
	at org.apache.spark.rpc.netty.NettyRpcEnv.$anonfun$deserialize$1(NettyRpcEnv.scala:298)
	at scala.util.DynamicVariable.withValue(DynamicVariable.scala:62)
	at org.apache.spark.rpc.netty.NettyRpcEnv.deserialize(NettyRpcEnv.scala:298)
	at org.apache.spark.rpc.netty.RequestMessage$.apply(NettyRpcEnv.scala:646)
	at org.apache.spark.rpc.netty.NettyRpcHandler.internalReceive(NettyRpcEnv.scala:697)
	at org.apache.spark.rpc.netty.NettyRpcHandler.receive(NettyRpcEnv.scala:682)
	at 
	at io.netty.channel.nio.AbstractNioByteChannel$NioByteUnsafe.read(AbstractNioByteChannel.java:166)
	at io.netty.channel.nio.NioEventLoop.processSelectedKey(NioEventLoop.java:722)
	at io.netty.channel.nio.NioEventLoop.processSelectedKeysOptimized(NioEventLoop.java:658)
	at io.netty.channel.nio.NioEventLoop.processSelectedKeys(NioEventLoop.java:584)
	at io.netty.channel.nio.NioEventLoop.run(NioEventLoop.java:496)
	at io.netty.util.concurrent.SingleThreadEventExecutor$4.run(SingleThreadEventExecutor.java:986)
	at io.netty.util.internal.ThreadExecutorMap$2.run(ThreadExecutorMap.java:74)
	at io.netty.util.concurrent.FastThreadLocalRunnable.run(FastThreadLocalRunnable.java:30)
	at java.lang.Thread.run(Thread.java:750)

	at 
	at io.netty.channel.nio.AbstractNioByteChannel$NioByteUnsafe.read(AbstractNioByteChannel.java:166)
	at io.netty.channel.nio.NioEventLoop.processSelectedKey(NioEventLoop.java:722)
	at io.netty.channel.nio.NioEventLoop.processSelectedKeysOptimized(NioEventLoop.java:658)
	at io.netty.channel.nio.NioEventLoop.processSelectedKeys(NioEventLoop.java:584)
	at io.netty.channel.nio.NioEventLoop.run(NioEventLoop.java:496)
	at io.netty.util.concurrent.SingleThreadEventExecutor$4.run(SingleThreadEventExecutor.java:986)
	at io.netty.util.internal.ThreadExecutorMap$2.run(ThreadExecutorMap.java:74)
	at io.netty.util.concurrent.FastThreadLocalRunnable.run(FastThreadLocalRunnable.java:30)
	... 1 more
24/03/08 07:08:48 WARN StandaloneAppClient$ClientEndpoint: Failed to connect to master 180.210.82.237:7077
org.apache.spark.SparkException: Exception thrown in awaitResult:
	at org.apache.spark.util.ThreadUtils$.awaitResult(ThreadUtils.scala:301)
	at org.apache.spark.rpc.RpcTimeout.awaitResult(RpcTimeout.scala:75)
	at org.apache.spark.rpc.RpcEnv.setupEndpointRefByURI(RpcEnv.scala:102)
	at org.apache.spark.rpc.RpcEnv.setupEndpointRef(RpcEnv.scala:110)
	at org.apache.spark.deploy.client.StandaloneAppClient$ClientEndpoint$$anon$1.run(StandaloneAppClient.scala:107)
	at java.util.concurrent.Executors$RunnableAdapter.call(Executors.java:511)
	at java.util.concurrent.FutureTask.run(FutureTask.java:266)
	at java.util.concurrent.ThreadPoolExecutor.runWorker(ThreadPoolExecutor.java:1149)
	at java.util.concurrent.ThreadPoolExecutor$Worker.run(ThreadPoolExecutor.java:624)
	at java.lang.Thread.run(Thread.java:750)
Caused by: java.lang.RuntimeException: java.io.InvalidClassException: org.apache.spark.rpc.netty.RpcEndpointVerifier$CheckExistence; local class incompatible: stream classdesc serialVersionUID = 5378738997755484868, local class serialVersionUID = 7789290765573734431
	at java.io.ObjectStreamClass.initNonProxy(ObjectStreamClass.java:699)
	at java.io.ObjectInputStream.readNonProxyDesc(ObjectInputStream.java:2005)
	at java.io.ObjectInputStream.readClassDesc(ObjectInputStream.java:1852)
	at java.io.ObjectInputStream.readOrdinaryObject(ObjectInputStream.java:2186)
	at java.io.ObjectInputStream.readObject0(ObjectInputStream.java:1669)
	at java.io.ObjectInputStream.readObject(ObjectInputStream.java:503)
	at java.io.ObjectInputStream.readObject(ObjectInputStream.java:461)
	at org.apache.spark.serializer.JavaDeserializationStream.readObject(JavaSerializer.scala:87)
	at org.apache.spark.serializer.JavaSerializerInstance.deserialize(JavaSerializer.scala:123)
	at org.apache.spark.rpc.netty.NettyRpcEnv.$anonfun$deserialize$2(NettyRpcEnv.scala:299)
	at scala.util.DynamicVariable.withValue(DynamicVariable.scala:62)
	at org.apache.spark.rpc.netty.NettyRpcEnv.deserialize(NettyRpcEnv.scala:352)
	at org.apache.spark.rpc.netty.NettyRpcEnv.$anonfun$deserialize$1(NettyRpcEnv.scala:298)
	at scala.util.DynamicVariable.withValue(DynamicVariable.scala:62)
	at org.apache.spark.rpc.netty.NettyRpcEnv.deserialize(NettyRpcEnv.scala:298)
	at org.apache.spark.rpc.netty.RequestMessage$.apply(NettyRpcEnv.scala:646)
	at org.apache.spark.rpc.netty.NettyRpcHandler.internalReceive(NettyRpcEnv.scala:697)
	at org.apache.spark.rpc.netty.NettyRpcHandler.receive(NettyRpcEnv.scala:682)
	at io.netty.channel.DefaultChannelPipeline.fireChannelRead(DefaultChannelPipeline.java:919)
	io.netty.channel.nio.AbstractNioByteChannel$NioByteUnsafe.read(AbstractNioByteChannel.java:166)
	at io.netty.channel.nio.NioEventLoop.processSelectedKey(NioEventLoop.java:722)
	at io.netty.channel.nio.NioEventLoop.processSelectedKeysOptimized(NioEventLoop.java:658)
	at io.netty.channel.nio.NioEventLoop.processSelectedKeys(NioEventLoop.java:584)
	at io.netty.channel.nio.NioEventLoop.run(NioEventLoop.java:496)
	at io.netty.util.concurrent.SingleThreadEventExecutor$4.run(SingleThreadEventExecutor.java:986)
	at io.netty.util.internal.ThreadExecutorMap$2.run(ThreadExecutorMap.java:74)
	at io.netty.util.concurrent.FastThreadLocalRunnable.run(FastThreadLocalRunnable.java:30)

```