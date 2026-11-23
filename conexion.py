import psycopg

def obtener_conexion():
    return psycopg.connect(
        host="127.0.0.1",
        dbname="autos_colombia_db",
        user="postgres",
        password="Tragojul10",
        port=5432
    )