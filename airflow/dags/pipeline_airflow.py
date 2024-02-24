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
    print("Number of rows", df.shape[0], "filas.")
    print("Number of features", df.shape[1])
    num_rows_with_nan = df.isna().any(axis=1).sum()
    print("Number of NaN rows:", num_rows_with_nan)


    
    df = df.apply(lambda x: x.str.replace(',', '.', regex=False) if x.dtype == 'object' else x)
    df = df.apply(pd.to_numeric, errors='ignore')
    df=df.drop(columns=['Customer_ID'])


    for columna in df.columns:
        if df[columna].dtype == 'object':  # Verificar si la columna contiene valores de tipo string
            df[columna] = pd.factorize(df[columna])[0]


                
    # Identify the columns containing missing values.
    columns_with_nan = df.columns[df.isnull().any()].tolist()

    # Split the data into two sets: one with complete values and another with missing values.
    df_without_missing_values = df.dropna()
    df_with_missing_values = df[df.isnull().any(axis=1)]

    # Separate features and labels for the dataset with complete values.
    X_train = df_without_missing_values.drop(columns=columns_with_nan)
    y_train = df_without_missing_values[columns_with_nan]

    # Train a linear regression model.
    model_reg = LinearRegression()
    model_reg.fit(X_train, y_train)

    # Use the model to predict the missing values in the dataset with missing values.
    X_test = df_with_missing_values.drop(columns=columns_with_nan)
    predicted_values = model_reg.predict(X_test)

    # Assign the predicted values to the original DataFrame.
    df.loc[df.isnull().any(axis=1), columns_with_nan] = predicted_values

    df.to_csv('/tmp/preprocess-dataset.csv', index=False)
    lock.release()

  

def feature_analysis():
    lock.acquire()
    from sklearn.decomposition import PCA
    from sklearn.preprocessing import StandardScaler

    # Dividir el conjunto de datos en características (X) y variable objetivo (y)
    df = pd.read_csv('/tmp/preprocess-dataset.csv')

    # Calculate the correlation matrix

    correlation_matrix = df.corr()

    # Extract the correlations with the churn variable
    churn_correlation = correlation_matrix['churn'].drop('churn')

    # Sort the correlations by absolute value
    churn_correlation_sorted = churn_correlation.abs().sort_values(ascending=False)

    corr_target =abs(correlation_matrix['churn'])

    features_high_corr = corr_target[corr_target> 0.00800].index.tolist()

    features_high_corr.remove('churn')


    print(len(features_high_corr))
    lock.release()
    print("final")
    return features_high_corr



# Función para entrenar y guardar el modelo
def train_and_save_model(**kwargs):
    lock.acquire()
    from sklearn.decomposition import PCA
    from sklearn.preprocessing import StandardScaler
    from xgboost import XGBClassifier
    from sklearn.metrics import accuracy_score
    ti = kwargs['ti']
    selected_features = ti.xcom_pull(task_ids='feature_analysis')

    # Dividir el conjunto de datos en características (X) y variable objetivo (y)
    df = pd.read_csv('/tmp/preprocess-dataset.csv')

    # Separar las características de la variable objetivo
    X = df.drop(columns=['churn'])  
    y = df['churn']  
    X_train, X_test, y_train, y_test = train_test_split(X[selected_features], y, test_size=0.3, random_state=42)

    model_cor = XGBClassifier(learning_rate=0.5, n_estimators=400, max_depth=7,objective='binary:logistic',
                    silent=False, nthread=2)


    model_cor.fit(X_train, y_train)  


    y_pred = model_cor.predict(X_test)
    predictions = [round(value) for value in y_pred]
    # evaluate predictions
    accuracy_corr = accuracy_score(y_test, predictions)
    print("Model_corr accuracy", accuracy_corr)

    importances = model_cor.feature_importances_
    importances = model_cor.feature_importances_
    feature_names = X_train.columns.to_list() 
    feature_importance_df = pd.DataFrame({'Feature': feature_names, 'Importance': importances})
    feature_importance_df = feature_importance_df.sort_values(by='Importance', ascending=False)
    
    threshold = 0.010 # Por ejemplo, puedes elegir un umbral del 10%

    selected_features = feature_importance_df[feature_importance_df['Importance'] > threshold]['Feature'].tolist()

    X = df.drop(columns=['churn'])  # características
    y = df['churn']  # variable objetivo
    X_train, X_test, y_train, y_test = train_test_split(X[selected_features], y, test_size=0.3, random_state=42)

    model_cor_sel_fea = XGBClassifier(learning_rate=0.5, n_estimators=400, max_depth=7,objective='binary:logistic',
                    silent=False, nthread=2)
    
    model_cor_sel_fea.fit(X_train, y_train)

    y_pred = model_cor_sel_fea.predict(X_test)
    predictions = [round(value) for value in y_pred]
    # evaluate predictions
    accuracy_corr_fea = accuracy_score(y_test, predictions)
    print("Model_correlation and feature selection accuracy", accuracy_corr_fea)

    with open("/tmp/modelo_XG_corr.pkl", "wb") as f:
        pickle.dump(model_cor, f)

    with open("/tmp/modelo_XG_fea.pkl", "wb") as f:
        pickle.dump(model_cor_sel_fea, f)        

    print("finish")
    lock.release()
    return [accuracy_corr,accuracy_corr_fea]


def upload_model_mlflow(**kwargs):
    import mlflow
    import pickle
    import os
    # Iniciar un experimento de MLflow
    ti = kwargs['ti']
    accuracy = ti.xcom_pull(task_ids='train_and_save_model')
    with open("/tmp/modelo_XG_corr.pkl", "rb") as f:
        model_cor = pickle.load(f)

    with open("/tmp/modelo_XG_fea.pkl", "rb") as f:
        model_cor_sel_fea = pickle.load(f)

    print("hola")    
    os.environ["MLFLOW_S3_ENDPOINT_URL"] = "http://minio-cli.minio.svc.cluster.local:9000"
    os.environ["AWS_ACCESS_KEY_ID"] = "sdg-user"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "sdg-password"
    os.environ["MLFLOW_TRACKING_USERNAME"] = "admin"
    os.environ["MLFLOW_TRACKING_PASSWORD"] = "password"
    MLFLOW_TRACKING_URI = "http://mlflow-service.mlflow.svc.cluster.local:5000"

    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    mlflow.set_experiment("XG-Boost")
    print("hola")
    # Iniciar una corrida de MLflow
    with mlflow.start_run():
        mlflow.log_params({"n_estimators": 100})
        mlflow.log_metric("accuracy", accuracy[0])
        mlflow.sklearn.log_model(model_cor, "modelo_random_forest")

    with mlflow.start_run():
        mlflow.log_params({"n_estimators": 100})
        mlflow.log_metric("accuracy", accuracy[1])
        print("hola")
        # Guardar el modelo
        mlflow.sklearn.log_model(model_cor, "modelo_random_forest")


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