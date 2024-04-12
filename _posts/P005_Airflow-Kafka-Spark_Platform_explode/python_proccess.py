from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from kubernetes.client import model as k8s
import datetime as dt
from datetime import timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.apache.kafka import KafkaProducerOperator 
from kubernetes.client import models as k8s 
import uuid
from kubernetes.client.models import V1ReplicaSetSpec, V1LabelSelector, V1LabelSelectorRequirement

# default_args = {
#     'owner': 'admin',
#     'depends_on_past': False,
#     'start_date': dt(2024, 1, 1),
#     'retries': 1,
#     'provide_context': True,
#     'retry_delay': timedelta(minutes=1)
# }

# with DAG(
#     dag_id='pipeline', 
#     default_args=default_args, 
#     schedule_interval=None
#     ) as dag:
    
#     replicas = k8s.V1ReplicaSetSpec(replicas=1)
#     replicas_spec = V1ReplicaSetSpec(replicas=3)

#     label_selector_requirement = V1LabelSelectorRequirement(key="strimzi.io/cluster", operator="In", values=["bami"])

#     label_selector = V1LabelSelector(match_labels={"strimzi.io/cluster": "bami"}, match_expressions=[label_selector_requirement])
#     replicas_spec.selector = label_selector
#     print (replicas_spec)
    
    
#     send_to_kafka_message = KubernetesPodOperator(
#         kubernetes_conn_id="kubernetes_default",
#         task_id="send_to_kafka_message",
#         name="kafka-topic",
#         namespace="kafka",
#         replicas=replicas,
#         arguments=["kubectl apply -f /home/ubuntu/kafka-topic.yaml"],
#         get_logs=True,
#         dag=dag,
#         is_delete_operator_pod=False,
#     )
   

#     full_container_spec = k8s.V1Container(
#         image="confluentinc/cp-kafka:7.6.0",
#         command=["sh", "-c", "exec tail -f /dev/null"],
#     )
    
#     deploy_kafka_client = KubernetesPodOperator(
#         kubernetes_conn_id="kubernetes_default",
#         name="kafka-client",
#         task_id = "deploy_kafka_client",
#         dag=dag,
#         namespace="kafka",
#         get_log=True,
#         is_delete_operator_pod=False,
#         full_container_spec=full_container_spec,
#     )
    
#     streaming_kafka_message = KafkaProducerOperator(
#         task_id='streaming_kafka_message',
#         topic='kafka-topic',  
#         bootstrap_servers='125.6.37.91:19092',  
#         messages=["Message 1", "Message 2", "Message 3"],
#         dag=dag,
#     )
    
def test():
    replicas_spec = V1ReplicaSetSpec(replicas=3)

    label_selector_requirement = V1LabelSelectorRequirement(key="strimzi.io/cluster", operator="In", values=["bami"])

    label_selector = V1LabelSelector(match_labels={"strimzi.io/cluster": "bami"}, match_expressions=[label_selector_requirement])
    replicas_spec.selector = label_selector
    print (replicas_spec.selector)
    
if __name__ == "__main__" :
 test()