from airflow.sdk import dag, task

git_repo = f"https://github.com/nibinmg/jet_cs_dbt.git"

dbt_dir = "/opt/airflow/dbt"

@dag
def jet_dwh():
    
    @task
    def start_task():
        pass

    @task.bash
    def git_sync():
        return f"""
        if [ -d {dbt_dir}/.git ]; then
            cd {dbt_dir} && git fetch && git reset --hard origin/main
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
    def dbt_build():
        return f"cd {dbt_dir} && dbt build --profiles-dir {dbt_dir}"


    start_task() >> git_sync() >> dbt_debug() >> dbt_deps() >> dbt_build()

jet_dwh()