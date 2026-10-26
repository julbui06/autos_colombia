from datetime import datetime
from psycopg2.extras import RealDictCursor  # <-- Agrega esta línea
from conexion import obtener_conexion

class ParqueaderoService:

    @staticmethod
    def registrar_ingreso(placa: str, id_celda: int):
        conn = obtener_conexion()
        if not conn:
            return {"exito": False, "mensaje": "Error de conexión con la base de datos."}
            
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # 1. Validar si el vehículo tiene mensualidad activa
        cursor.execute("""
            SELECT u.estado_mensualidad 
            FROM Usuario u 
            JOIN Vehiculo v ON u.id_usuario = v.id_usuario 
            WHERE v.placa = %s
        """, (placa,))
        usuario = cursor.fetchone()

        if not usuario or usuario['estado_mensualidad'] != 'ACTIVO':
            conn.close()
            return {"exito": False, "mensaje": "El vehículo no cuenta con una mensualidad activa."}

        # 2. Validar disponibilidad de la celda
        cursor.execute("SELECT estado FROM Celda WHERE id_celda = %s", (id_celda,))
        celda = cursor.fetchone()

        if not celda or celda['estado'] != 'DISPONIBLE':
            conn.close()
            return {"exito": False, "mensaje": "La celda seleccionada no está disponible."}

        # 3. Registrar la entrada del vehículo y cambiar estado de celda
        cursor.execute("""
            INSERT INTO Registro_Acceso (placa, id_celda, fecha_hora_ingreso, estado_registro)
            VALUES (%s, %s, %s, 'EN_PARQUEADERO')
        """, (placa, id_celda, datetime.now()))

        cursor.execute("UPDATE Celda SET estado = 'OCUPADA' WHERE id_celda = %s", (id_celda,))
        conn.commit()
        conn.close()

        return {"exito": True, "mensaje": f"Ingreso del vehículo {placa} registrado con éxito."}

    @staticmethod
    def registrar_salida(id_registro: int):
        conn = obtener_conexion()
        if not conn:
            return {"exito": False, "mensaje": "Error de conexión con la base de datos."}

        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # 1. Verificar registro activo
        cursor.execute("SELECT id_celda FROM Registro_Acceso WHERE id_registro = %s AND estado_registro = 'EN_PARQUEADERO'", (id_registro,))
        registro = cursor.fetchone()

        if not registro:
            conn.close()
            return {"exito": False, "mensaje": "El registro activo no existe o ya fue finalizado."}

        # 2. Registrar hora de salida y liberar celda
        cursor.execute("""
            UPDATE Registro_Acceso 
            SET fecha_hora_salida = %s, estado_registro = 'FINALIZADO' 
            WHERE id_registro = %s
        """, (datetime.now(), id_registro))

        cursor.execute("UPDATE Celda SET estado = 'DISPONIBLE' WHERE id_celda = %s", (registro['id_celda'],))
        conn.commit()
        conn.close()

        return {"exito": True, "mensaje": "Salida registrada correctamente. Celda liberada."}