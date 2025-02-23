from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.utils.task_group import TaskGroup
from datetime import datetime

# Function to create a TaskGroup dynamically
def create_task_group(group_id, task_names):
    with TaskGroup(group_id) as tg:
        tasks = [EmptyOperator(task_id=task_name) for task_name in task_names]
        # Define internal dependencies (sequential execution)
        for i in range(len(tasks) - 1):
            tasks[i] >> tasks[i + 1]
    return tg  # Return the TaskGroup

# Define the DAG
with DAG(
    dag_id="dynamic_taskgroup_dag",
    start_date=datetime(2024, 1, 1),
    schedule_interval="@daily",
    catchup=False,
    tags=[
      "type=example",
      "user=avikmandal",
      "example=tasks_group",
    ],
) as dag:

    start = EmptyOperator(task_id="start")

    # Dynamically create TaskGroups
    group_1 = create_task_group("group_1", ["task_a", "task_b", "task_c"])
    group_2 = create_task_group("group_2", ["task_x", "task_y"])

    end = EmptyOperator(task_id="end")

    # Define dependencies
    start >> group_1 >> group_2 >> end