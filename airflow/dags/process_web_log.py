from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from processors.web_log_processor import WebLogProcessor

load_dotenv()


default_args = {
    "owner": os.getenv('AIRFLOW_OWNER', 'admin1'),
    "start_date": datetime(
        int(os.getenv('AIRFLOW_START_YEAR', '2025')),
        int(os.getenv('AIRFLOW_START_MONTH', '10')),
        int(os.getenv('AIRFLOW_START_DAY', '30'))
    ),
    "email": [os.getenv('AIRFLOW_EMAIL', 'admin1@mail.com')],
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": int(os.getenv('AIRFLOW_RETRIES', '1')),
    "retry_delay": timedelta(minutes=int(os.getenv('AIRFLOW_RETRY_DELAY_MINUTES', '5'))),
    "depends_on_past": False
}

dag = DAG(
    dag_id="process_web_log",
    default_args=default_args,
    description="Process web server logs: extract, transform and archive daily",
    schedule_interval="@daily",
    catchup=False,
    max_active_runs=1
)

data_dir = os.getenv('AIRFLOW_DATA_DIR', os.path.join(os.path.dirname(__file__), "files"))
processor = WebLogProcessor(data_dir)

extract_data_task = PythonOperator(
    task_id="extract_data",
    python_callable=processor.extract_data,
    dag=dag
)

transform_data_task = PythonOperator(
    task_id="transform_data",
    python_callable=processor.transform_data,
    dag=dag
)

load_data_task = PythonOperator(
    task_id="load_data",
    python_callable=processor.load_data,
    dag=dag
)

extract_data_task >> transform_data_task >> load_data_task
