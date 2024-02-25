# MinIO Deployment on Kubernetes

This README provides instructions for deploying MinIO on a Kubernetes cluster under a dedicated namespace.

## Prerequisites

- A Kubernetes cluster
- `kubectl` tool installed and configured

## Instructions

### Step 1: Create the Namespace

Before deploying MinIO, create a new namespace called `minio`:

```shell
kubectl create namespace minio
```

### Step 2: Deploy MinIO Manifests

Deploy the MinIO manifests to your Kubernetes cluster using `kubectl`. Ensure that the manifests are located in the `k8s-manifests/minio/` directory of your repository.

```shell
kubectl apply -f k8s-manifests/minio/ -n minio
```

### Step 3: Verify the Deployment

After deploying the MinIO manifests, it's important to verify that the application is running correctly. You can check the status of the pods to ensure they are active and healthy:

```shell
kubectl get pods -n minio
```