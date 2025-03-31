from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from airflow.models import TaskInstance
from airflow.models import Variable
from airflow.utils.context import Context
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from airflow.decorators import task
from datetime import datetime
from kubernetes.client import models as k8s
import yaml

class CustomKubernetesPodOperator(KubernetesPodOperator):
    def __init__(self, *args, config=None, xcom_push=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = config
        self.xcom_push = xcom_push

    def execute(self, context: Context, *args, **kwargs):
        ti: TaskInstance = context["ti"]
        
        init_image_name = ti.xcom_pull(task_ids=f"read_yaml_config", key="init_image")
        init_command = ti.xcom_pull(task_ids=f"read_yaml_config", key="init_command")

        # Ensure init_command is a list
        if isinstance(init_command, str):
            init_command = init_command.split()  # Split the string into a list of arguments
            
        init_container_list = []
        # Modify the init_containers to replace images
        if self.config and "init_containers" in self.config:
            for index, container in enumerate(self.config["init_containers"]):
                container["image"] = init_image_name  # Replace image dynamically
                container["entrypoint"] = init_command  # Replace command dynamically
                init_container_list.append(
                    k8s.V1Container(
                        name=container["name"],
                        image=container["image"],
                        command=container["entrypoint"]
                    )  
                )                
        self.init_containers = init_container_list  # Update the init_containers

        return super().execute(context)


CONFIG_FILE_PATH = "/opt/airflow/dags/configs/config.yaml"  # Update this path accordingly

@task(multiple_outputs=True)
def read_yaml_config():
    """Reads the YAML config file based on the environment stored in an Airflow variable."""
    env = Variable.get("ENVIRONMENT", default_var="dev")  # Read env from Airflow Variable
    with open(CONFIG_FILE_PATH, "r") as file:
        config = yaml.safe_load(file)
    return config.get(env, {})


# DAG Definition
with DAG(
    dag_id="dynamic_init_container_images", 
    start_date=datetime(2024, 1, 1),
    schedule_interval="@daily",
    catchup=False,
    tags=[
      "type=example",
      "user=avikmandal",
      "example=dynamic_init_container_images",
    ],
) as dag:
    
    yaml_config = read_yaml_config()

    # KubernetesPodOperator with predefined init containers
    custom_k8s_task = CustomKubernetesPodOperator(
        task_id="run_custom_pod",
        namespace="airflow",
        image="busybox:latest",  # Main container image
        name="custom-pod",
        config={
            "init_containers": [
                {"name": f"init-container-{i}", "image": "", "entrypoint": []} for i in range(2)
            ]
        },
        on_finish_action="keep_pod",
        # init_containers=[{"name": f"init-container-{i}", "image": "", "entrypoint": []} for i in range(2)
        #     ],
        xcom_push=True
    )

    # Chain tasks
    yaml_config >> custom_k8s_task
