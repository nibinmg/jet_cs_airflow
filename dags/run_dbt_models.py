from airflow.sdk import dag, task

# from dotenv import load_dotenv
# import os

# load_dotenv()

# GIT_USERNAME = os.getenv("GIT_USERNAME")
# GIT_TOKEN = os.getenv("GIT_TOKEN")

git_repo = f"https://nibin1990:glpat-gd7cLgq7vlxC2yaHjc0hn286MQp1OmczY3UyCw.01.121jybqq7@gitlab.com/myprojects4101914/learn_dbt.git"

dbt_dir = "/opt/airflow/dbt"

@dag
def run_dbt_models():
    
    @task
    def start_task():
        pass

    @task.bash
    def git_sync():
        return f"""
        if [ -d {dbt_dir}/.git ]; then
            cd {dbt_dir} && git fetch && git reset --hard origin/dev
        else 
            git clone {git_repo} {dbt_dir}
        fi
        """
    
    @task.bash
    def dbt_debug():
        return f"cd {dbt_dir} && dbt debug --profiles-dir {dbt_dir}"
    
    @task.bash
    def dbt_deps():
        return f"cd {dbt_dir} && dbt deps"
    
    @task.bash
    def dbt_seed():
        return f"cd {dbt_dir} && dbt seed --profiles-dir {dbt_dir}"



    start_task() >> git_sync() >> dbt_debug() >> dbt_deps() >> dbt_seed()

run_dbt_models()