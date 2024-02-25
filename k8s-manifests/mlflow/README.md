# How to deploy mlflow in a kubernetes cluster

Please read the .env file in order to parametrize the deployment
Once variables have been set in the .env file then the deployment can be done deploying manifest by manifest.
All manifests are sorted based on their order of deployment (000.., 010.., 025...).

To deploy a manifest (manifest `045-ingress-route.yaml` for example) please execute:
````
$ source .env; envsubst < 045-ingress-route.yaml | kubectl apply -f - 
````
You need to execute this command per manifest.

The last 3 manifests (035, 040, 045) are optional, since 035 & 040 are used to integrate mlflow in kubeflow (optional) and 045 is used to create an ingress-route if a traefik proxy server has been deployed previously.

So you can deploy from 000 to 030 (both included) and you could access mlflow by portforwarding:
````
$ kubectl port-forward svc/mlflow-service -n <NAMESPACE_NAME> 5000:5000
````
And the access `http://localhost:5000` and a user and password are required (basic auth pop up).
If so, by default username=admin and password=password. You can change this password by using mlflow api -> `https://mlflow.org/docs/latest/auth/python-api.html#mlflow.server.auth.client.AuthServiceClient.update_user_password`
