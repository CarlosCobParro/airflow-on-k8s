# prometheusflow deployment using Helm


### In order to deploy prometheusflow we are going to use the helm installer. There are several ways to install in your machine, for this tutorial we've used from script.

```console
$ curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3
$ chmod 700 get_helm.sh
$ ./get_helm.sh

```


Afer that we add the prometheusflow repo at our helm and deploying in our cluster. 

```helm repo add prometheus-community https://prometheus-community.github.io/helm-charts```


```helm upgrade --install prometheus prometheus-community/prometheus --namespace monitoring --create-namespace```