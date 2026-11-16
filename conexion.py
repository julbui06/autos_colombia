import psycopg2
from psycopg2.extras import RealDictCursor

def obtener_conexion():
    try:
        return psycopg2.connect(
            host="localhost",
            database="autos_colombia_db",
            user="postgres",
            password="Tragojul10",  
            port="5432"
        )
    except Exception as e:
        print(f"Error al conectar con PostgreSQL: {e}")
        return None