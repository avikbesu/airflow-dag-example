from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.utils.trigger_rule import TriggerRule
from datetime import datetime
import time
import logging

def print_dagrun_metrics(**context):
    logger = logging.getLogger("airflow.task")
    logger.setLevel(logging.DEBUG)
    dag_run = context['dag_run']
    logger.debug("Waiting for all tasks to complete...")
    try:
        while any(
            ti.state not in ['success', 'failed', 'upstream_failed', 'skipped']
            for ti in dag_run.get_task_instances()
            if ti.task_id != context['task'].task_id
        ):
            # group tasks by state
            task_states = {ti.task_id: ti.state for ti in dag_run.get_task_instances() if ti.task_id != context['task'].task_id}
            logger.debug(f"Current task states: {task_states}")
            time.sleep(1)
        logger.info("All tasks completed.")
        # Print DAG run metrics
        logger.info(f"DAG Run Metrics:")
        logger.info(f"DAG Run ID: {dag_run.run_id}")
        # Calculate state based on other tasks
        if any(ti.state == 'failed' for ti in dag_run.get_task_instances() if ti.task_id != context['task'].task_id):
            state = 'failed'
        else:
            state = 'success'
        logger.info(f"State: {state}")
        logger.info(f"Execution Date: {dag_run.execution_date}")
        logger.info(f"Start Date: {dag_run.start_date}")
        # Calculate Airflow lag
        if dag_run.start_date and dag_run.execution_date:
            lag = (dag_run.start_date - dag_run.execution_date).total_seconds()
            logger.info(f"Airflow Lag: {lag} seconds")
        else:
            logger.warning("Airflow Lag: N/A")
        # Calculate end date as the max end_date of all other tasks
        end_dates = [ti.end_date for ti in context['dag_run'].get_task_instances() if ti.task_id != context['task'].task_id and ti.end_date]
        max_end_date = max(end_dates) if end_dates else None
        logger.info(f"End Date: {max_end_date}")
        # Calculate duration
        duration = (max_end_date - dag_run.start_date).total_seconds() if max_end_date else 0
        logger.info(f"Duration: {duration} seconds")
    except Exception as e:
        logger.error(f"Error while collecting DAG run metrics: {e}", exc_info=True)

with DAG(
    dag_id="capture_log_sample_dag",
    start_date=datetime(2024, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=[
      "type=example",
      "user=avikmandal",
      "example=capture_log",
    ],
) as dag:

    task1 = EmptyOperator(task_id="task1")

    task2 = BashOperator(
        task_id="task2",
        bash_command="sleep 10"
    )

    task3 = BashOperator(
        task_id="task3",
        bash_command="exit 1"  # Always fails
    )

    task4 = EmptyOperator(task_id="task4")

    task5 = PythonOperator(
        task_id="task5",
        python_callable=print_dagrun_metrics,
        trigger_rule=TriggerRule.ALL_DONE  # Runs after all upstream tasks are done
    )

    # Set dependencies
    task1 >> [task2, task3]
    [task2, task3] >> task4

    # task5 runs after all other tasks are done (except itself)
    # [task1, task2, task3, task4] >> task5