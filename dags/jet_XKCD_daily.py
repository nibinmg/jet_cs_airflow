from airflow.sdk import dag, task
from airflow.sdk.bases.sensor import PokeReturnValue
from airflow.providers.postgres.hooks.postgres import PostgresHook

from datetime import datetime, timezone

current_comic_url = f"https://xkcd.com/info.0.json"

def get_latest_comic_number():
    import requests
    response = requests.get(current_comic_url)

    if response.status_code == 200:
        xkcd_data = response.json()
    else:
        xkcd_data = None

    return xkcd_data['num']

def extract_data(latest_number):
    url = f"https://xkcd.com/{latest_number}/info.0.json"
    import requests
    response = requests.get(url)
    if response.status_code == 200:
        xkcd_data = response.json()
    else:
        xkcd_data = None
    return xkcd_data

def last_success_num():
    hook = PostgresHook(postgres_conn_id="postgres_local")
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
        hook = PostgresHook(postgres_conn_id="postgres_local")
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

@dag
def jet_XKCD_daily():

    @task
    def start_task():
        pass

    @task.sensor(poke_interval=30, timeout=300)
    def is_api_available() -> PokeReturnValue:
        import requests
        response = requests.get(current_comic_url)

        if response.status_code == 200:
            condition = True
        else:
            condition = False

        return PokeReturnValue(is_done=condition)

    @task()
    def extract_load_data():

        latest_comic_number = get_latest_comic_number()
        print(f"Latest comic number = {latest_comic_number}")

        last_run_comic_number = last_success_num()
        print(f"Last successfully loaded comic number = {last_run_comic_number}")

        if latest_comic_number == last_run_comic_number:
            print("No new XKCD comic data to extract")
        else:
            for num in range(last_run_comic_number+1,latest_comic_number+1):
                print(f"Extracting comic number {num}")
                xkcd_data = extract_data(num)

                print(f"Loading comic number {num}")
                load_data(xkcd_data)

                print(f"Loading completed for comic number {num}")

    @task 
    def end_task():
        pass

    start_task() >> is_api_available() >> extract_load_data() >> end_task()

jet_XKCD_daily()