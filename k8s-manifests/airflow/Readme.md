
## Deploying Airflow on Kubernetes with Helm

This guide walks you through the process of deploying Apache Airflow on a Kubernetes cluster using Helm.

1. **Add the Airflow Helm Repository**:
   Begin by adding the Apache Airflow Helm repository. This repository contains all the necessary charts to deploy Airflow on Kubernetes.
   ```bash
   helm repo add apache-airflow https://airflow.apache.org
    ```
2. **Create a Namespace for Airflow:**
    Before installing Airflow, create a dedicated namespace in your Kubernetes cluster. This isolates your Airflow deployment from other applications.

    ```bash
    kubectl create namespace airflow
    ```

3. **Install Airflow:**
    Finally, deploy Airflow into the airflow namespace using the Helm chart. The -f values.yaml argument allows you to customize the deployment according to your configuration specified in the values.yaml file.

    ```bash
    helm install airflow apache-airflow/airflow --namespace airflow -f values.yaml
    ```


## Mounting DAGs from a Private GitHub Repo Using Git-Sync Sidecar

To synchronize DAGs from a private GitHub repository into Airflow using a Git-Sync sidecar, follow these steps:

1. **Create a Private GitHub Repository**:
   If you haven't already, create a private repository on GitHub to store your DAGs.

2. **Generate SSH Keys**:
   Create SSH keys to secure the connection between the Git-Sync sidecar and your private repository.
   ```bash
   ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
    ```
    Add your public SSH key to your GitHub repository under Settings > Deploy keys.

3. **Convert Your Private SSH Key to Base64:**
    Convert your private SSH key to a base64 string to securely store it in Kubernetes.

    ```bash
    base64 <path-to-your-private-ssh-key> -w 0 > temp.txt
    ```
    Copy the base64 string from temp.txt for later use.

4. **Prepare override-values.yaml:**
    Create an override-values.yaml file to specify your Git-Sync settings and include your base64-encoded private SSH key.

    ```yaml
    dags:
    gitSync:
        enabled: true
        repo: git@github.com:<username>/<private-repo-name>.git
        branch: <branch-name>
        subPath: ""
        sshKeySecret: airflow-ssh-secret
    extraSecrets:
    airflow-ssh-secret:
        data: |
        gitSshKey: '<base64-converted-ssh-private-key>'
    ```
5. **Deploy Airflow with Helm:**
    Use Helm to deploy Airflow, applying your override-values.yaml to configure Git-Sync.

    ```bash
    helm upgrade --install airflow apache-airflow/airflow -f override-values.yaml
    ```
