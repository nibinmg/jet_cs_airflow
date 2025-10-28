# JET case study

A brief description of your project and what it does.

This project uses **Apache Airflow** for workflow orchestration, and is containerized with **Docker Compose** for easy setup and development.

---

## Prerequisites

Make sure you have the following installed:

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/)

- in Windows, install Docker Desktop

---

## Getting Started

Follow these steps to set up the project for the first time:

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
