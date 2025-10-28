# JET case study

A brief description of your project and what it does.

This project uses **Apache Airflow** for workflow orchestration, and is containerized with **Docker Compose** for easy setup and development.

---

## Prerequisites

Make sure you have the following installed:

- [PostgreSQL](https://www.postgresql.org/download/) 

     (since the data warehouse is setup in PostgreSQL. Airflow will also install postgres for maintaining metadata. This outside the docker container)

- Install [Docker Desktop](https://www.docker.com/products/docker-desktop/) 

     (includes Docker and Docker Compose)
- Ensure Docker Desktop is running before using any `docker compose` commands

---

## Getting Started with Airflow

Follow these steps to set up the Airflow for the first time:

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd <your-repo-folder>

2. **Build docker image**
     ```bash
     docker compose build
     ```

3. **Initialize Airflow database**
     ```bash
     docker compose up airflow-init
     ```

4. **Start Airflow services**
    
    to run the in foreground
     ```bash
     docker compose up 
     ```
     to run the in background
     ```bash
     docker compose up -d
     ```

4. **Other Airflow commands**
     
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
     user: <postgres user name>
     password: <postgres pwd>
     database: "jet_db"