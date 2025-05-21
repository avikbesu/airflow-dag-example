
from airflow.models import Variable
from airflow import DAG
from airflow.decorators import task
from datetime import datetime
from airflow.operators.empty import EmptyOperator


@task
def get_var():
    """Reads the YAML config file based on the environment stored in an Airflow variable."""
    env = Variable.get("ENVIRONMENT", default_var="dev")  # Read env from Airflow Variable

    return env


# DAG Definition
with DAG(
    dag_id="variable_example", 
    start_date=datetime(2024, 1, 1),
    schedule_interval="@daily",
    catchup=False,
    tags=[
      "type=example",
      "user=avikmandal",
      "example=variable_example",
    ],
) as dag:
    start = EmptyOperator(task_id="start")
    
    get_var = get_var()


    # Chain tasks
    start >> get_var
