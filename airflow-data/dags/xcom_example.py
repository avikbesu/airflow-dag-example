# from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator
from airflow.utils.dates import days_ago
from airflow.models.dag import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

def create_kube_pod_operator(task_id, image, command_template, namespace="default"):
    """
    Creates a KubernetesPodOperator dynamically and supports Jinja templating for command args.
    
    :param task_id: Unique ID for the task
    :param image: Docker image to run in the pod
    :param command_template: Jinja template string to be rendered at runtime
    :param namespace: Kubernetes namespace to run the pod in
    :return: KubernetesPodOperator instance
    """
    
    xcom_value = "{{ ti.xcom_pull(task_ids='push_xcom', key='example_key') }}"
    print(f'xcom_value: {xcom_value}')
    print(f'data type: {type(xcom_value)}')
    
    print(f'command_template: {command_template}')
    print(f'data type: {type(command_template)}')
    
    # iterate command_template and 
    
    return BashOperator(
        task_id=task_id,
        bash_command=f'{command_template};echo "Xcom: {xcom_value}"', # Jinja template will be rendered by Airflow 
 
    )
    
    # return KubernetesPodOperator(
    #     task_id=task_id,
    #     name=task_id,
    #     namespace=namespace,
    #     image=image,
    #     cmds=["sh", "-c"],
    #     arguments=[command_template],  # Jinja template will be rendered by Airflow
    #     get_logs=True,
    #     do_xcom_push=True,  # Ensure XCom values can be retrieved
    # )

default_args = {"owner": "airflow", "start_date": days_ago(1)}

with DAG(
    "dynamic_operator_using_xcom", 
    default_args=default_args, 
    schedule_interval=None,
    catchup=False,
    tags=[
      "type=example",
      "user=avikmandal",
      "example=xcom_example",
    ],
  ) as dag:

    def push_to_xcom(**kwargs):
        kwargs['ti'].xcom_push(key="example_key", value="Hello from XCom!")

    push_task = PythonOperator(
        task_id="push_xcom",
        python_callable=push_to_xcom,
        provide_context=True,
    )

    # Jinja template for KubernetesPodOperator (fetching value from XCom)
    jinja_command = 'echo "Retrieved Value: {{ ti.xcom_pull(task_ids=\'push_xcom\', key=\'example_key\') }}"'

    kube_task = create_kube_pod_operator(
        task_id="run_pod_with_xcom",
        image="busybox",
        command_template=jinja_command
    )

    push_task >> kube_task  # Ensure push runs before pod execution
