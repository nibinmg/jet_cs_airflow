from airflow.sdk import dag, task
from airflow.sdk.bases.sensor import PokeReturnValue
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.standard.operators.trigger_dagrun import TriggerDagRunOperator

import requests
from datetime import datetime, timezone

# Some default settings
base_url = f"https://xkcd.com/"
polling_timeout = 7200
polling_interval = 300
comic_extract_per_run = 2

def get_latest_comic_number():
    response = requests.get(f"{base_url}info.0.json")

    if response.status_code == 200:
        xkcd_data = response.json()
    else:
        xkcd_data = None

    return xkcd_data['num']

def extract_data(latest_number):
    url = f"{base_url}{latest_number}/info.0.json"
    response = requests.get(url)
    if response.status_code == 200:
        xkcd_data = response.json()
    else:
        xkcd_data = None
    return xkcd_data

def last_success_num():
    hook = PostgresHook(postgres_conn_id="dwh_postgres")
    sql="""
            CREATE TABLE IF NOT EXISTS raw.xkcd_data (
            num INTEGER PRIMARY KEY,
            day TEXT,
            month TEXT,
            year TEXT,
            title TEXT,
            safe_title TEXT,
            transcript TEXT,
            alt TEXT,
            link TEXT,
            news TEXT,
            img TEXT,
            load_ts TIMESTAMP DEFAULT NOW()
        );

        SELECT 
            CASE WHEN 
                EXISTS(
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'raw' 
                    AND table_name = 'xkcd_data'
                ) 
                THEN (SELECT COALESCE(MAX(num),0) as lastComicNr FROM "raw".xkcd_data)   
            ELSE 0
            END AS lastComicNr
    """
    result = hook.get_first(sql)
    return result[0]

def load_data(xkcd_data):
    if xkcd_data is None:
        print("No comic data returned")
    else:
        hook = PostgresHook(postgres_conn_id="dwh_postgres")
        sql="""
            INSERT INTO raw.xkcd_data (num,day,month,year,title,safe_title,transcript,alt,link,news,img,load_ts)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (num) DO NOTHING;
        """
        values = (
            xkcd_data['num'],
            xkcd_data['day'],
            xkcd_data['month'],
            xkcd_data['year'],
            xkcd_data['title'],
            xkcd_data['safe_title'],
            xkcd_data['transcript'],
            xkcd_data['alt'],
            xkcd_data['link'],
            xkcd_data['news'],
            xkcd_data['img'],
            datetime.now(timezone.utc)
        )
        hook.run(sql, parameters=values)

@dag(
        dag_id="jet_xkcd_daily",
        schedule="0 6 * * 1,3,5",
        start_date=datetime(2025,10,28),
        catchup=False
)
def jet_xkcd_daily():

    @task
    def start_task():
        pass

    @task.sensor(poke_interval=polling_interval, timeout=polling_timeout)
    def is_comic_available_task() -> PokeReturnValue:

        latest_comic_number = get_latest_comic_number()
        print(f"Latest comic number = {latest_comic_number}")

        last_run_comic_number = last_success_num()
        print(f"Last successfully loaded comic number = {last_run_comic_number}")

        if latest_comic_number and latest_comic_number > last_run_comic_number:
            condition = True
        else:
            condition = False

        return PokeReturnValue(is_done=condition)
    
    @task
    def identify_comic_number_task():
        
        latest_comic_number = get_latest_comic_number()
        print(f"Latest comic number = {latest_comic_number}")

        last_run_comic_number = last_success_num()
        print(f"Last successfully loaded comic number = {last_run_comic_number}")

        if latest_comic_number == last_run_comic_number:
            print("No new XKCD comic data to extract")
        elif latest_comic_number > last_run_comic_number:
            if (latest_comic_number - last_run_comic_number) > comic_extract_per_run:
                list_comic_number = list(range(last_run_comic_number+1,last_run_comic_number+comic_extract_per_run+1))
            else:
                list_comic_number = list(range(last_run_comic_number+1,latest_comic_number+1))
        
        return list_comic_number

    @task
    def extract_data_task(num: int):
        
        xkcd_data = extract_data(num)
        return xkcd_data
    
    @task
    def load_data_task(xkcd_data: dict):
        load_data(xkcd_data)

    trigger_dwh_dag = TriggerDagRunOperator(
        task_id = "trigger_dwh_dag",
        trigger_dag_id = "jet_dwh"
    )
    
    @task 
    def end_task():
        pass

    # Step 1: Define your tasks
    start = start_task()
    check_api = is_comic_available_task()
    identify = identify_comic_number_task()
    extract = extract_data_task.expand(num=identify)
    load = load_data_task.expand(xkcd_data=extract)
    end = end_task()

    # Step 2: Chain them properly
    start >> check_api
    check_api >> identify
    identify >> extract
    extract >> load
    load >> trigger_dwh_dag
    trigger_dwh_dag >> end


jet_xkcd_daily()