# MLflow Deployment on Kubernetes

Deploy MLflow in your Kubernetes cluster by following these steps. This guide assumes you have a set of Kubernetes manifests in the `k8s-manifest/mlflow` directory for deploying MLflow.

## Prerequisites

- Kubernetes cluster
- kubectl configured to interact with your cluster

## Deployment Steps

### Create the Namespace

First, create a namespace specifically for MLflow:

```shell
kubectl create namespace mlflow
```

### Deploy MLflow Manifests

Deploy the MLflow Kubernetes manifests to your cluster to set up MLflow. Apply these manifests within the dedicated namespace you've created:

```shell
kubectl apply -f k8s-manifests/mlflow/ -n mlflow
```

Adjust the command to point to the correct path where your MLflow manifests are stored.

### Verify the Deployment

Ensure your MLflow deployment is successful and operational:
```shell
kubectl get pods -n mlflow

```

Check the running pods to confirm MLflow components are active. Additionally, inspect the exposed services:

```shell
kubectl get svc -n mlflow

```