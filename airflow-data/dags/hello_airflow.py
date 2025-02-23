from datetime import datetime

from airflow import DAG
from airflow.decorators import task
from airflow.operators.bash import BashOperator
# from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import ShortCircuitOperator
from airflow.operators.weekday import BranchDayOfWeekOperator
from airflow.utils.edgemodifier import Label
from airflow.utils.weekday import WeekDay
from airflow.utils.trigger_rule import TriggerRule

import json

def _is_empty(data, **kwargs):
    print(data)
    # fixed_data = json.load(data)
    # print("data: " + fixed_data)
    # print("length: " + str(len(fixed_data)))
    # print("flag: " + str(fixed_data['flag']))
    return data['flag']

# A DAG represents a workflow, a collection of tasks
with DAG(
    dag_id="sample_demo_dag",
    start_date=datetime(2022, 1, 1),
    schedule=None,
    tags=[
      "type=example",
      "user=avikmandal",
      "example=sample_demo_dag",
    ],
) as dag:

    # Tasks are represented as operators
    hello = BashOperator(task_id="hello", bash_command="echo hello")

    @task()
    def airflow():
        print("hello user!!")
        
    empty_1 = EmptyOperator(task_id="empty_task")
    empty_2 = EmptyOperator(task_id="another_empty_task")
    
    # DeprecationWarning: The `airflow.operators.dummy_operator.DummyOperator` class is deprecated. Please use `'airflow.operators.empty.EmptyOperator'`.
    dummy_task = EmptyOperator(task_id='dummy_task', trigger_rule=TriggerRule.ALL_DONE) # DummyOperator(task_id='dummy_task')
    
    branch_weekday = BranchDayOfWeekOperator(
        task_id="make_weekday_choice",
        follow_task_ids_if_true="branch_mid_week",
        follow_task_ids_if_false="branch_weekend",
        week_day={WeekDay.MONDAY, WeekDay.TUESDAY, WeekDay.WEDNESDAY, WeekDay.THURSDAY, WeekDay.FRIDAY},
    )
    
    weekend = EmptyOperator(task_id="branch_weekend")
    weekday = EmptyOperator(task_id="branch_mid_week")
    

    # Set dependencies between tasks
    hello >> Label("Greeting") >> airflow() >> [empty_1, empty_2] >> branch_weekday
    branch_weekday >> Label("Weekday") >> weekday >> dummy_task
    branch_weekday >> Label("Weekend") >> weekend >> dummy_task


    @task(multiple_outputs=True)
    def list_sftp_files():
        return {"flag": True, "model": 'Mustang'}
    
    is_empty = ShortCircuitOperator(
        task_id='is_empty',
        python_callable=_is_empty,
        op_kwargs={'data': '{{ti.xcom_pull(task_ids="list_sftp_files")}}'}
    )
    @task
    def process():
        print('process')
    list_sftp_files() >> is_empty >> process() #TODO