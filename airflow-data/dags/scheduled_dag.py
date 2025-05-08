from datetime import datetime
import pendulum

from airflow import DAG
from airflow.decorators import task
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator

# Define the IST timezone
ist_tz = pendulum.timezone("Asia/Kolkata")

# Create a timezone-aware datetime object for start_date
start_date = pendulum.datetime(*map(int, "2023-01-01".split("-")), tz=ist_tz)

# A DAG represents a workflow, a collection of tasks
with DAG(
    dag_id="scheduled_dag",
    start_date=start_date,
    schedule="20 23 * * *",
    tags=[
      "type=example",
      "user=avikmandal",
      "example=scheduled_dag",
    ],
    catchup=False
) as dag:
    hello = BashOperator(task_id="hello", bash_command="echo hello")
    empty_1 = EmptyOperator(task_id="empty_task")
    empty_2 = EmptyOperator(task_id="another_empty_task")
    
    hello >> empty_1
    hello >> empty_2