from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.trigger_rule import TriggerRule
from airflow.utils.timezone import make_naive
from datetime import datetime, timedelta
import pymysql
import pymongo
import pandas as pd
import logging
from pymongo import MongoClient 

# Configuración de conexión
MYSQL_CONFIG = {
    "host": "host.docker.internal",
    "user": "root",
    "password": "r62af79a",
    "database": "ventas_db",
    "port": 3306
}

MONGO_URI = "mongodb://host.docker.internal:27017/"
MONGO_DB = "etl_resultados"
MONGO_COLLECTION = "ventas_transformadas"

# Función de extracción
def extraer_datos(**kwargs):
    connection = pymysql.connect(**MYSQL_CONFIG)
    query = "SELECT * FROM ventas_historicas"
    df = pd.read_sql(query, connection)
    connection.close()
    df.to_json("/tmp/ventas_raw.json", orient="records", lines=True)
    return "success"

# Función de transformación
def transformar_datos(**kwargs):
    df = pd.read_json("/tmp/ventas_raw.json", lines=True)
    df['fecha_venta'] = pd.to_datetime(df['fecha_venta']).dt.strftime('%Y-%m-%dT%H:%M:%SZ')
    df['monto_con_iva'] = df['monto'] * 1.12
    df.to_json("/tmp/ventas_transformadas.json", orient="records", lines=True)
    return "success"

def cargar_en_mongo(**kwargs):
    cliente = pymongo.MongoClient(MONGO_URI)
    db = cliente[MONGO_DB]
    coleccion = db[MONGO_COLLECTION]
    with open("/tmp/ventas_transformadas.json") as f:
        datos = [eval(line) for line in f]
        coleccion.insert_many(datos)
    cliente.close()
    return "success"

def registrar_ejecucion(**kwargs):
    cliente = MongoClient(MONGO_URI)
    db = cliente[MONGO_DB]
    coleccion = db["ejecuciones_etl"]

    ti = kwargs['ti']
    dag_run = kwargs['dag_run']

    fecha_inicio = make_naive(dag_run.start_date)
    fecha_fin = datetime.utcnow()
    duracion = (fecha_fin - fecha_inicio).total_seconds()

    # Consultar retornos vía XCom
    estados_previos = [
        ti.xcom_pull(task_ids='extraer_datos'),
        ti.xcom_pull(task_ids='transformar_datos'),
        ti.xcom_pull(task_ids='cargar_en_mongo')
    ]

    estado = "éxito" if all(e == 'success' for e in estados_previos) else "fallo"

    coleccion.insert_one({
        "fecha_ejecucion": fecha_fin.isoformat(),
        "duracion": duracion,
        "estado": estado,
        "mensaje": f"Ejecución del DAG {dag_run.dag_id} finalizada con estado {estado}"
    })

    cliente.close()

# DAG
default_args = {
    'owner': 'airflow',
    'retries': 0,
    'retry_delay': timedelta(seconds=5),
}

with DAG(
    dag_id='etl_ventas_historicas_mongo',
    default_args=default_args,
    description='ETL desde MySQL a MongoDB con transformación',
    schedule='@daily',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['etl', 'mysql', 'mongodb']
) as dag:

    t1 = PythonOperator(
        task_id='extraer_datos',
        python_callable=extraer_datos
    )

    t2 = PythonOperator(
        task_id='transformar_datos',
        python_callable=transformar_datos
    )

    t3 = PythonOperator(
        task_id='cargar_en_mongo',
        python_callable=cargar_en_mongo
    )

    t4 = PythonOperator(
    task_id='registrar_ejecucion',
    python_callable=registrar_ejecucion,
    trigger_rule=TriggerRule.ALL_DONE
)

    t1 >> t2 >> t3 >> t4