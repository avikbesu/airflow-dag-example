import yaml
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.models import Variable
from airflow.utils.dates import days_ago
from docker.types import Mount

CONFIG_FILE_PATH = "/opt/airflow/configs/config.yaml"  # Update this path accordingly

def read_yaml_config():
    """Reads the YAML config file based on the environment stored in an Airflow variable."""
    env = Variable.get("ENVIRONMENT", default_var="dev")  # Read env from Airflow Variable
    with open(CONFIG_FILE_PATH, "r") as file:
        config = yaml.safe_load(file)
    return config.get(env, {})

def push_docker_image_to_xcom(**kwargs):
    """Simulates retrieving a Docker image and pushing it to XCom."""
    docker_image = "busybox:latest"  # Replace with actual logic if needed
    kwargs['ti'].xcom_push(key="docker_image", value=docker_image)

def create_docker_operator(config):
    task_id = f"docker_{config['name']}"
    image = config['image']  # Using Jinja to fetch XCom value dynamically
    command = config["command"]
    
    """Dynamically creates a DockerOperator task."""
    return BashOperator(
        task_id=task_id,
        bash_command=f'{command};echo "Docker image: {image}"', # Jinja template will be rendered by
    )
    
    # return DockerOperator(
    #     task_id=task_id,
    #     image=image,
    #     api_version='auto',
    #     auto_remove='force',
    #     command=command,
    #     docker_url= "tcp://172.22.193.33:2375", #"unix://var/run/docker.sock", # Replace <WSL_IP_ADDRESS> with the actual IP address
    #     network_mode="bridge",
    #     mounts=[Mount(source="/tmp", target="/tmp", type="bind")],  # Example mount
    # )

default_args = {"owner": "airflow", "start_date": days_ago(1)}

with DAG(
    "dynamic_docker_operator_dag", 
    default_args=default_args, 
    schedule_interval=None,
    catchup=False,
    tags=[
      "type=example",
      "user=avikmandal",
      "example=dynamic_docker_operator_example",
    ],
  ) as dag:
    
    # Step 1: Push Docker image to XCom
    push_image_task = PythonOperator(
        task_id="push_docker_image",
        python_callable=push_docker_image_to_xcom,
        provide_context=True,
    )

    # Step 2: Read YAML config
    yaml_config = read_yaml_config()
    container_configs = yaml_config.get("container_configs", [])

    # Step 3: Create DockerOperator tasks dynamically
    docker_tasks = []
    for config in container_configs:
        jinja_command = "{{ ti.xcom_pull(task_ids='push_docker_image', key='docker_image') }}"
        task = create_docker_operator(
            config=config,
        )
        push_image_task >> task  # Ensures image is pushed before running containers
        docker_tasks.append(task)
