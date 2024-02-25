helm repo add bitnami https://charts.bitnami.com/bitnami
helm show values bitnami/minio > minio.yaml
helm install minio bitnami/minio -n minio --create-namespace --values minio.yaml
echo "create ingressroute
apiVersion: traefik.containo.us/v1alpha1
kind: IngressRoute
metadata:
  name: minio
  namespace: minio
spec:
  entryPoints:
    - websecure
  routes:
    - match: Host(`minio-console.apps.emeralds.ari-aidata.eu`) #########################################
      kind: Rule
      services:
        - name: minio
          port: 9001
    - match: Host(`minio-api.apps.emeralds.ari-aidata.eu`) #########################################
      kind: Rule
      services:
        - name: minio
          port: 9000
  tls:
    certResolver: letsencrypt
"
