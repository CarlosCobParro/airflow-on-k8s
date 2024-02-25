#/bin/bash

echo "Modify the "menulLinks" section and add the follow component:

        {
          "type": "item",
          "link": "/mlflow/",
          "text": "MLFlow",
          "icon": "device:wifi-tethering"
        }

"
kubectl edit cm centraldashboard-config -n kubeflow