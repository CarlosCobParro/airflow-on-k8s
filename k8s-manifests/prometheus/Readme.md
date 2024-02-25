# Prometheusflow and Grafana deployment using Helm


In order to deploy prometheusflow we are going to use the helm installer. There are several ways to install in your machine, for this tutorial we've used from script.

```console
$ curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3
$ chmod 700 get_helm.sh
$ ./get_helm.sh

```


## Monitoring Setup with Prometheus and Grafana

To ensure comprehensive monitoring of our Kubernetes environment, we employ Prometheus for metric collection and Grafana for visualization. The setup involves the following steps:

1. **Add Prometheus Helm Repository**: 
   We begin by adding the official Prometheus Community Helm repository. This repository contains the necessary Helm charts to deploy Prometheus on Kubernetes.
   ```shell
   helm repo add prometheus-community https://prometheus-community.github.io/helm-charts

2. **Install Prometheus:**
    Using Helm, we then install Prometheus into our cluster. We specify the monitoring namespace for organizational purposes and create it if it doesn't already exist.
    
    ```shell
    helm upgrade --install prometheus prometheus-community/prometheus --namespace monitoring --create-namespace

3. **Install Grafana:**
    Lastly, Grafana is installed, also within the monitoring namespace. The grafana-values.yaml file is provided to customize the Grafana deployment according to our specific needs.
    ```shell
    helm install grafana prometheus-community/grafana --namespace monitoring -f grafana-values.yaml
