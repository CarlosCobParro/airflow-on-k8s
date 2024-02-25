# Airflow on Kubernetes (airflow-on-k8s)

This repository is designed for a code test with the aim of deploying Apache Airflow on Kubernetes. It focuses on automating and deploying AI models using Airflow as the task orchestrator.

## Repository Structure

-  **AI-part**: This folder contains a Jupyter notebook that delves into the detailed analysis of the data provided for the code test. It includes processes for data cleaning, updating, and adjusting to prepare the data for training artificial intelligence models. Additionally, the datasets used for training the models are also included, allowing for a comprehensive environment to develop and test AI models effectively.

- **airflow-local**:  Includes a Docker Compose file with configurations necessary to deploy the entire required infrastructure for Airflow to function locally. The Docker Compose is also set up to connect to the cluster when port forwarding is enabled. Additionally, a DAG is provided to execute locally, ensuring proper connections to the cluster's port forwarding, facilitating a seamless integration for testing and development purposes.

- **airflow/dags**: This directory is designated for uploading DAGs, which are then fetched by Airflow deployed on EKS for execution. The setup for this process utilizes a configuration as described at [Managing DAGs in Airflow with Helm](https://airflow.apache.org/docs/helm-chart/stable/manage-dags-files.html#mounting-dags-from-a-private-github-repo-using-git-sync-sidecar). This method connects Airflow to GitHub, enabling dynamic and simplified deployments through the use of a Git-Sync sidecar for continuously syncing DAGs from the repository.


- **k8s-manifests**: Contains Kubernetes manifests for each component within the cluster, along with instructions on how to deploy them. These manifests are crucial for setting up and managing the infrastructure required for Airflow to run efficiently in a Kubernetes environment.

## Detailed Architecture Overview

This architecture outlines a sophisticated setup for orchestrating machine learning (ML) workflows on Amazon EKS, leveraging several key technologies:

![Architecture Diagram](/figures/architecture.png)



- **GitHub**: A repository for version control that houses the DAGs for Airflow, with a GitSync sidecar container to synchronize updates.
- **Apache Airflow**: An open-source tool that orchestrates complex computational workflows and data processing pipelines. Within the EKS ecosystem, Airflow manages the scheduling and execution of the DAGs.
- **MinIO**: An object storage service that is API-compatible with Amazon S3. It is used here to store datasets and acts as the artifact repository for ML models.
- **MLflow**: An ML lifecycle management tool that logs experiments, stores model artifacts, and helps with model deployment.
- **Grafana**: A multi-platform open-source analytics and interactive visualization web application that provides charts, graphs, and alerts when connected to supported data sources, in this case, possibly Prometheus through a Kubernetes exporter.
- **k8s Exporter**: This likely refers to a Prometheus exporter that is used for monitoring Kubernetes cluster metrics, which Grafana can visualize.

In essence, this architecture allows for a seamless ML workflow where models are developed, tracked, and deployed efficiently, with robust monitoring and version control mechanisms in place.
