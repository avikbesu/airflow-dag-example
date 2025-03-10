from airflow import DAG
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator
from datetime import datetime

# Function to have dynamic dag triger operator
def dag_trigger_operator(dag, task_id, trigger_dag_id, conf, wait_for_completion, allowed_states, failed_states, poke_interval):
  return TriggerDagRunOperator(
      task_id=task_id,
      trigger_dag_id=trigger_dag_id,
      conf=conf,
      wait_for_completion=wait_for_completion,
      allowed_states=allowed_states,
      failed_states=failed_states,
      poke_interval=poke_interval,
  )
  
def dynamic_dag_trigger_operator(dag, config, previous_task=None):
  for i, conf in enumerate(config):
    trigger = dag_trigger_operator(
        dag,
        f'trigger_target_dag_{conf.get("key")}',
        'trigger_target_dag',
        conf,
        True,
        ['success'],
        ['failed'],
        10
    )
    # trigger = TriggerDagRunOperator(
    #     task_id=f'trigger_target_dag_{conf.get("key")}',
    #     trigger_dag_id='trigger_target_dag',  # Replace with the actual DAG ID you want to trigger
    #     conf=conf,  # Configuration dictionary to pass to the triggered DAG
    #     wait_for_completion=True,  # Wait for the triggered DAG to complete
    #     allowed_states=['success'],  # Continue only if the triggered DAG succeeds
    #     failed_states=['failed'],  # Fail if the triggered DAG fails
    #     poke_interval=10,  # Check the status every 10 seconds
    # )
    
    if previous_task:
        previous_task >> trigger
    previous_task = trigger
  return previous_task


# Define the controller DAG
with DAG(
    dag_id='wait_triggered_dag',
    start_date=datetime(2025, 2, 24),
    schedule=None,
    catchup=False,
    tags=[
      "type=example",
      "user=avikmandal",
      "example=triggered_dag",
    ],
) as dag:
    config = [
        {'key': 'value11', "key2": "value21"},
        {'key': 'value12', "key2": "value22"},
        {'key': 'value13', "key2": "value23"},
    ]
  
    # Define the TriggerDagRunOperator to trigger the target DAG having each value for config
    # previous_task = None
    previous_task = dynamic_dag_trigger_operator(dag, config)
    # for i, conf in enumerate(config):
    #     trigger = TriggerDagRunOperator(
    #         task_id=f'trigger_target_dag_{conf.get("key")}',
    #         trigger_dag_id='trigger_target_dag',  # Replace with the actual DAG ID you want to trigger
    #         conf=conf,  # Configuration dictionary to pass to the triggered DAG
    #         wait_for_completion=True,  # Wait for the triggered DAG to complete
    #         allowed_states=['success'],  # Continue only if the triggered DAG succeeds
    #         failed_states=['failed'],  # Fail if the triggered DAG fails
    #         poke_interval=10,  # Check the status every 10 seconds
    #     )
        
    #     if previous_task:
    #         previous_task >> trigger
    #     previous_task = trigger
    
    some_other_task = EmptyOperator(
        task_id='some-other-task',
    )
    
    previous_task >> some_other_task


  