from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import pickle
import os
import threading



def check_csv(ruta):
    if os.path.exists(ruta):
        if os.path.isfile(ruta):
            if ruta.endswith('.csv'):
                return True
    return False

def load_data():
    lock.acquire()
    import pandas as pd
    from minio import Minio
    import urllib3
    from pathlib import Path


    _http = urllib3.PoolManager(
            timeout=600,
            maxsize=600,
            retries=urllib3.Retry(
            total=10,
            backoff_factor=0.2,
            status_forcelist=[500, 502, 503, 504]
            )
        )
    minio_url = "minio-cli.minio.svc.cluster.local:9000" #Cambiar por valor de dentro del k8s
    minio_user = "sdg-user"
    minio_pass = "sdg-password"
    MINIO_BUCKET = "sdg"
    dataset = "dataset.csv"

    minioClient = Minio(minio_url,
                        access_key = minio_user,
                        secret_key = minio_pass,
                        secure = False,
                        http_client =_http,
                        region = "es")

    buckets = minioClient.list_buckets()
    for bucket in buckets:
        print(bucket.name, bucket.creation_date)

    path_to_data="/tmp/dataset.csv"



    if check_csv(path_to_data):
        print(f"El archivo {path_to_data} existe y es un archivo CSV.")
    else:
        print(f"El archivo {path_to_data} no existe o no es un archivo CSV.")
        Path(path_to_data).parent.mkdir(parents=True, exist_ok=True)
        
        minioClient.fget_object(MINIO_BUCKET, dataset, path_to_data)
    
    
    lock.release()

# Función para cargar el conjunto de datos
def preprocess_data():
    lock.acquire()

    import pandas as pd
    from sklearn.linear_model import LinearRegression
    # Ruta del archivo en el contenedor de Airflow
    path = '/tmp/dataset.csv'
    df = pd.read_csv(path, sep=';')

    # Realiza operaciones con el dataset
    # Por ejemplo, puedes imprimir las primeras filas del dataset
    print(df.head())
    print("The DataFrame is formed", df.shape[0], "Rows.")
    print("The DataFrame is formed", df.shape[1], "features.")
    num_rows_with_nan = df.isna().any(axis=1).sum()
    print("Number of NaN:", num_rows_with_nan)


    
    print("Modify , for .")
    df = df.apply(lambda x: x.str.replace(',', '.', regex=False) if x.dtype == 'object' else x)
    df = df.apply(pd.to_numeric, errors='ignore')


    for columna in df.columns:
        if df[columna].dtype == 'object':  # Verificar si la columna contiene valores de tipo string
            df[columna] = pd.factorize(df[columna])[0]


            
    # Identificar las columnas que contienen valores faltantes
    columnas_con_nan = df.columns[df.isnull().any()].tolist()

    # Dividir los datos en dos conjuntos: uno con valores completos y otro con valores faltantes
    df_con_valores_completos = df.dropna()
    df_con_valores_faltantes = df[df.isnull().any(axis=1)]

    # Separar características y etiquetas para el conjunto con valores completos
    X_train = df_con_valores_completos.drop(columns=columnas_con_nan)
    y_train = df_con_valores_completos[columnas_con_nan]

    # Entrenar un modelo de regresión lineal
    modelo_regresion = LinearRegression()
    modelo_regresion.fit(X_train, y_train)

    # Utilizar el modelo para predecir los valores faltantes en el conjunto con valores faltantes
    X_test = df_con_valores_faltantes.drop(columns=columnas_con_nan)
    valores_faltantes_predichos = modelo_regresion.predict(X_test)

    # Asignar los valores predichos al DataFrame original
    df.loc[df.isnull().any(axis=1), columnas_con_nan] = valores_faltantes_predichos

    df.to_csv('/tmp/preprocess-dataset.csv', index=False)
    lock.release()

  

def feature_analysis():
    lock.acquire()
    from sklearn.decomposition import PCA
    from sklearn.preprocessing import StandardScaler

    # Dividir el conjunto de datos en características (X) y variable objetivo (y)
    df = pd.read_csv('/tmp/preprocess-dataset.csv')
    print("hola")
    # Separar las características de la variable objetivo
    X = df.drop(columns=['churn'])  # características
    y = df['churn']  # variable objetivo
    print("hola1")
    # Estandarizar las características
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    print("hola2")
    # Aplicar PCA
    pca = PCA()
    X_pca = pca.fit_transform(X_scaled)

    # Identificar las componentes principales que explican la mayor varianza
    componentes_principales_importantes = pca.components_[:40]  # por ejemplo, selecciona las primeras 5 componentes principales

    # Obtener las cargas de las características en estas componentes principales
    cargas_caracteristicas = pd.DataFrame(componentes_principales_importantes, columns=X.columns)
    print("hola3")
    # Seleccionar las características con las mayores cargas absolutas en las componentes principales
    selected_features = cargas_caracteristicas.abs().max().nlargest(40).index
    lock.release()
    print("final")
    return selected_features.tolist()



# Función para entrenar y guardar el modelo
def train_and_save_model(**kwargs):
    lock.acquire()
    from sklearn.decomposition import PCA
    from sklearn.preprocessing import StandardScaler
    ti = kwargs['ti']
    selected_features = ti.xcom_pull(task_ids='feature_analysis')

    # Dividir el conjunto de datos en características (X) y variable objetivo (y)
    df = pd.read_csv('/tmp/preprocess-dataset.csv')

    # Separar las características de la variable objetivo
    X = df.drop(columns=['churn'])  # características
    y = df['churn']  # variable objetivo

    # Filtrar el DataFrame para incluir solo las características seleccionadas
    X_selected = X[selected_features]
    # Dividir el conjunto de datos en conjuntos de entrenamiento y prueba
    X_train, X_test, y_train, y_test = train_test_split(X_selected, y, test_size=0.2, random_state=42)
    # Entrenar un Random Forest utilizando solo las características seleccionadas
    rf = RandomForestClassifier(min_samples_leaf=1)
    rf.fit(X_train, y_train)

        # Evaluar el modelo en el conjunto de prueba
    accuracy = rf.score(X_test, y_test)
    print("Precisión del modelo:", accuracy)

    with open("/tmp/modelo_rf.pkl", "wb") as f:
        pickle.dump(rf, f)

    print("finish")
    lock.release()
    return accuracy


def upload_model_mlflow(**kwargs):
    import mlflow
    import pickle
    import os
    import boto3
    # Iniciar un experimento de MLflow
    ti = kwargs['ti']
    accuracy = ti.xcom_pull(task_ids='train_and_save_model')
    with open("/tmp/modelo_rf.pkl", "rb") as f:
        model = pickle.load(f)

    minio_user = "sdg-user"
    minio_pass = "sdg-password"
    print("hola")    
    os.environ["MLFLOW_S3_ENDPOINT_URL"] = "minio-cli.minio.svc.cluster.local:9000"
    os.environ["AWS_ACCESS_KEY_ID"] = "sdg-user"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "sdg-password"
    os.environ["MLFLOW_TRACKING_USERNAME"] = "admin"
    os.environ["MLFLOW_TRACKING_PASSWORD"] = "password"
    MLFLOW_TRACKING_URI = "http://mlflow-service.mlflow.svc.cluster.local:5000"

    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    mlflow.set_experiment("random_forest_experiment")
    print("hola")
    # Iniciar una corrida de MLflow
    with mlflow.start_run():
        # Registrar los parámetros y métricas del modelo
        mlflow.log_params({"n_estimators": 100})
        mlflow.log_metric("accuracy", accuracy)
        print("hola")
        # Guardar el modelo
        mlflow.sklearn.log_model(model, "modelo_random_forest")


# Definir el DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2022, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'entrenamiento_modelo',
    default_args=default_args,
    description='DAG para entrenar y evaluar un modelo de analítica avanzada',
    schedule_interval=timedelta(days=1),
    concurrency=1,  # Solo se ejecuta un DAG a la vez
    max_active_runs=1,  # Solo se permite una ejecución activa del DAG
    catchup=False  # Evita la ejecución de tareas pasadas al iniciar el DAG
)

lock = threading.Lock()  
# Definir los operadores del DAG
load_data_op = PythonOperator(
    task_id='load_data',
    python_callable=load_data,
    dag=dag,
)


preprocess_data_op = PythonOperator(
    task_id='data_preparation',
    python_callable=preprocess_data,
    provide_context=True,
    dag=dag,
)


feature_analysis_op = PythonOperator(
    task_id='feature_analysis',
    python_callable=feature_analysis,
    provide_context=True,
    dag=dag,
)

train_and_save_model_op = PythonOperator(
    task_id='train_and_save_model',
    python_callable=train_and_save_model,
    provide_context=True,
    dag=dag,
)

upload_model_mlflow_op = PythonOperator(
    task_id='upload_model_mlflow',
    python_callable=upload_model_mlflow,
    provide_context=True,
    dag=dag,
)


# Definir dependencias entre los operadores
load_data_op  >> preprocess_data_op >> feature_analysis_op>>train_and_save_model_op >>upload_model_mlflow_op