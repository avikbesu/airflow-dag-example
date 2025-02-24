from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator
from datetime import datetime

# Define the trigged DAG
with DAG(
    dag_id='trigger_target_dag',
    start_date=datetime(2025, 2, 24),
    schedule=None,
    catchup=False,
    tags=[
      "type=example",
      "user=avikmandal",
      "example=triggered_dag",
    ],
) as dag:
  hello = BashOperator(task_id="hello", bash_command="sleep 30")
  some_task = EmptyOperator(
    task_id='some-task',
  )
  
  hello >> some_task