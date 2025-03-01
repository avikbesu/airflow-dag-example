from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from datetime import datetime, timedelta

# Define default arguments
default_args = {
    "owner": "airflow",
    "start_date": datetime(2023, 1, 1),
    "retries": 3,
    "retry_delay": timedelta(minutes=5)
}

# Create a DAG
with DAG(
    "docker_example_dag",
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
    tags=[
      "type=example",
      "user=avikmandal",
      "example=docker_example",
    ],
) as dag:

    # DockerOperator task
    docker_task = DockerOperator(
        task_id="run_docker_command",
        image="ubuntu:latest",
        command=["echo", "Hello from Docker!"],
        auto_remove=True,
        network_mode="bridge"
    )