# JET case study

As part of this case study, I designed and implemented a data pipeline that integrates data from the [XKCD Comics API](https://xkcd.com/json.html), models it for analytics, and exposes it after applying business transformations. 
The pipeline leverages Apache **Airflow** for data integration and orchestration, and **dbt** for data modelling, transformation, and testing. And PostgreSQL as the data warehouse. 

This repository holds Airlow dags to integrate data on a schedule and dag to execute dbt models which models and transforms data. 

---
## Technical overview

![technical overview](images/overview.png)

The data modelling and transformation logic, implemented using dbt, is maintained in a separate GitHub repository [jet_cs_dbt](https://github.com/nibinmg/jet_cs_dbt.git). During each Airflow DAG run, a dedicated task synchronizes the dbt repository into the Airflow runtime environment and executes the defined dbt models.

---
## Prerequisites

Make sure you have the following installed:

- Python

- [PostgreSQL](https://www.postgresql.org/download/) 

     I chose PostgreSQL as the data warehouse for this project. To better simulate a real-world deployment, the data warehouse instance is hosted outside the Airflow container, representing an external production database.

     While Airflow also uses PostgreSQL as its metadata database, that instance runs inside the Docker container and is separate from the external data warehouse used for analytical workloads.

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) 

     Includes Docker and Docker Compose. Ensure Docker Desktop is running before using any `docker compose` commands. 

---

## Getting Started with Airflow

Follow these steps to set up the Airflow for the first time:

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd <your-repo-folder>
   ```

2. **Create .env file**

     Create .env file in the Airflow root folder. 
     Add the following variables for dbt to connect to postgeres from the Airflow container. 

     DBT_HOST= "host.docker.internal" or < IP >
     DBT_USER= < postgres user name >
     DBT_PASSWORD= < postgres password > 

3. **Build docker image**
     ```bash
     docker compose build
     ```

4. **Initialize Airflow database**
     ```bash
     docker compose up airflow-init
     ```

5. **Start Airflow services**
    
    to run the in foreground
     ```bash
     docker compose up 
     ```
     to run the in background
     ```bash
     docker compose up -d
     ```

Wait till the containers are up. Once up the dags can be viewed from the [Airflow UI](http://localhost:8080/) (username: airflow, password: airflow). 

6. **Other Airflow commands**
     
     Stop the airflow
     ```bash
     docker compose down 
     ```

     Stop and remove the volumes
     ```bash
     docker compose down -v
     ```
## Setup DWH(Postgres)

     In the postgres, create database "jet_db"

## Add connection to DWH(Postgres) in Airflow 

     From Airflow UI, Admin -> Connection
     Add connection. 

     Connection name: "dwh_postgres"
     connection type: select postgres
     host: "host.docker.internal" or <IP>
     user: < postgres user name>
     password: < postgres pwd>
     database: "jet_db"

## Lets run the DAGs

This project includes three Airflow DAGs, each responsible for a specific stage of the pipeline:

1. **jet_xkcd_daily**

This DAG is scheduled to extract data from the XKCD API every Monday, Wednesday, and Friday.
The job starts at 6:00 AM and checks for new comics every 5 minutes for the next 2 hours.

It also supports historical data extraction, although performance is limited in the local setup.
To avoid long runtimes, the historical fetch is restricted to max two records at a run.

Following variable in the dag can be updated:

     How should the job check for new comic before failure
     ```bash
     polling_timeout = 7200
     ```

     At what interval job check for new comic
     ```bash
     polling_interval = 300
     ```

     Maximum number of comic to be extracted in each run
     ```bash
     comic_extract_per_run = 2
     ```

2. **jet_dwh**

Once data is extracted, this DAG is triggered to model, transform, and load the data into the data warehouse (PostgreSQL).
It includes tasks that sync the dbt repository into the Airflow runtime environment and execute the dbt models for transformation.

3. **jet_xkcd**

This is an auxiliary DAG created specifically for historical data extraction.
Since *jet_xkcd_daily* is optimized for scheduled incremental loads and faces performance limitations in local environments, this job handles larger historical loads separately. 