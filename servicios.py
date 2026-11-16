from datetime import date, timedelta
from conexion import obtener_conexion

class ParqueaderoService:

    # =========================================================================
    # MÓDULO 1: GESTIÓN DE USUARIOS, VEHÍCULOS Y MENSUALIDADES (ITERACIÓN 2)
    # =========================================================================

    def registrar_usuario_y_vehiculo(
        self,
        nombre: str,
        documento: str,
        telefono: str,
        placa: str,
        tipo_vehiculo: str,
        estado_mensualidad: str,
        fecha_inicio_mensualidad: date,
        fecha_fin_mensualidad: date,
        id_celda_inicial: int = None
    ):
        conn = obtener_conexion()
        cursor = conn.cursor()
        try:
            placa = placa.strip().upper()
            tipo_vehiculo = tipo_vehiculo.strip().upper()
            estado_mensualidad = estado_mensualidad.strip().upper()

            if fecha_fin_mensualidad < fecha_inicio_mensualidad:
                return {"exito": False, "mensaje": "La fecha fin no puede ser menor a la fecha inicio."}

            cursor.execute("SELECT placa FROM Vehiculo WHERE placa = %s", (placa,))
            if cursor.fetchone():
                return {"exito": False, "mensaje": f"La placa {placa} ya se encuentra registrada."}

            # Si eligió asignar una celda de una vez, validar compatibilidad y vigencia antes de guardar
            if id_celda_inicial:
                hoy = date.today()
                if estado_mensualidad != "ACTIVO" or fecha_fin_mensualidad < hoy or fecha_inicio_mensualidad > hoy:
                    return {"exito": False, "mensaje": "Para asignar una celda al crear el usuario, la mensualidad debe estar ACTIVA y vigente hoy."}

                cursor.execute("SELECT numero_celda, tipo_vehiculo, estado FROM Celda WHERE id_celda = %s", (id_celda_inicial,))
                celda = cursor.fetchone()
                if not celda:
                    return {"exito": False, "mensaje": "La celda seleccionada no existe."}
                if celda[2] != "DISPONIBLE":
                    return {"exito": False, "mensaje": f"La celda {celda[0]} ya está ocupada."}
                if celda[1] != tipo_vehiculo:
                    return {"exito": False, "mensaje": f"Incompatibilidad: la celda {celda[0]} es para {celda[1]} y el vehículo es {tipo_vehiculo}."}

            cursor.execute("SELECT id_usuario FROM Usuario WHERE documento = %s", (documento,))
            usuario_existente = cursor.fetchone()

            if usuario_existente:
                id_usuario = usuario_existente[0]
            else:
                cursor.execute(
                    "INSERT INTO Usuario (nombre, documento, telefono) VALUES (%s, %s, %s) RETURNING id_usuario",
                    (nombre, documento, telefono)
                )
                id_usuario = cursor.fetchone()[0]

            cursor.execute(
                """
                INSERT INTO Vehiculo (
                    placa, id_usuario, tipo_vehiculo, estado_mensualidad,
                    fecha_inicio_mensualidad, fecha_fin_mensualidad
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (placa, id_usuario, tipo_vehiculo, estado_mensualidad, fecha_inicio_mensualidad, fecha_fin_mensualidad)
            )

            mensaje_extra = ""
            if id_celda_inicial:
                cursor.execute(
                    "INSERT INTO Registro_Acceso (placa, id_celda) VALUES (%s, %s)",
                    (placa, id_celda_inicial)
                )
                cursor.execute("UPDATE Celda SET estado = 'OCUPADA' WHERE id_celda = %s", (id_celda_inicial,))
                mensaje_extra = f" y celda {celda[0]} asignada"

            conn.commit()
            return {
                "exito": True,
                "mensaje": f"Usuario {nombre} y vehículo {placa} guardados{mensaje_extra}.",
                "id_usuario": id_usuario
            }
        except Exception as e:
            conn.rollback()
            return {"exito": False, "mensaje": f"Error al registrar: {str(e)}"}
        finally:
            cursor.close()
            conn.close()

    def eliminar_usuario(self, id_usuario: int):
        conn = obtener_conexion()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT nombre FROM Usuario WHERE id_usuario = %s", (id_usuario,))
            usuario = cursor.fetchone()
            if not usuario:
                return {"exito": False, "mensaje": "El usuario no existe."}

            # Validar que no tenga vehículos actualmente estacionados dentro del parqueadero
            cursor.execute(
                """
                SELECT r.placa FROM Registro_Acceso r
                JOIN Vehiculo v ON r.placa = v.placa
                WHERE v.id_usuario = %s AND r.estado_registro = 'EN_PARQUEADERO'
                """,
                (id_usuario,)
            )
            activo = cursor.fetchone()
            if activo:
                return {
                    "exito": False,
                    "mensaje": f"No se puede eliminar a {usuario[0]} porque su vehículo ({activo[0]}) está actualmente dentro del parqueadero. Registra primero su salida."
                }

            # Eliminar historial de registros finalizados, vehículos asociados y finalmente el usuario
            cursor.execute(
                """
                DELETE FROM Registro_Acceso
                WHERE placa IN (SELECT placa FROM Vehiculo WHERE id_usuario = %s)
                """,
                (id_usuario,)
            )
            cursor.execute("DELETE FROM Vehiculo WHERE id_usuario = %s", (id_usuario,))
            cursor.execute("DELETE FROM Usuario WHERE id_usuario = %s", (id_usuario,))
            conn.commit()
            return {"exito": True, "mensaje": f"Usuario {usuario[0]} y sus datos asociados eliminados correctamente."}
        except Exception as e:
            conn.rollback()
            return {"exito": False, "mensaje": f"Error al eliminar usuario: {str(e)}"}
        finally:
            cursor.close()
            conn.close()

    def cambiar_estado_mensualidad(
        self,
        placa: str,
        nuevo_estado: str,
        fecha_inicio: date = None,
        fecha_fin: date = None
    ):
        conn = obtener_conexion()
        cursor = conn.cursor()
        try:
            placa = placa.strip().upper()
            nuevo_estado = nuevo_estado.strip().upper()

            cursor.execute("SELECT placa FROM Vehiculo WHERE placa = %s", (placa,))
            if not cursor.fetchone():
                return {"exito": False, "mensaje": f"No se encontró el vehículo {placa}."}

            if nuevo_estado == "ACTIVO":
                f_ini = fecha_inicio or date.today()
                f_fin = fecha_fin or (date.today() + timedelta(days=30))
                cursor.execute(
                    """
                    UPDATE Vehiculo
                    SET estado_mensualidad = 'ACTIVO',
                        fecha_inicio_mensualidad = %s,
                        fecha_fin_mensualidad = %s
                    WHERE placa = %s
                    """,
                    (f_ini, f_fin, placa)
                )
                conn.commit()
                return {
                    "exito": True,
                    "mensaje": f"Mensualidad de {placa} ACTIVADA (vigente del {f_ini} al {f_fin})."
                }
            else:
                cursor.execute(
                    "UPDATE Vehiculo SET estado_mensualidad = 'INACTIVO' WHERE placa = %s",
                    (placa,)
                )
                conn.commit()
                return {
                    "exito": True,
                    "mensaje": f"Mensualidad de {placa} DESACTIVADA."
                }
        except Exception as e:
            conn.rollback()
            return {"exito": False, "mensaje": f"Error al actualizar mensualidad: {str(e)}"}
        finally:
            cursor.close()
            conn.close()

    def listar_usuarios_y_vehiculos(self, buscar: str = None):
        conn = obtener_conexion()
        cursor = conn.cursor()
        try:
            if buscar:
                filtro = f"%{buscar.strip()}%"
                cursor.execute(
                    """
                    SELECT u.id_usuario, u.nombre, u.documento, v.placa, v.tipo_vehiculo,
                           v.fecha_inicio_mensualidad, v.fecha_fin_mensualidad, v.estado_mensualidad
                    FROM Usuario u
                    LEFT JOIN Vehiculo v ON u.id_usuario = v.id_usuario
                    WHERE u.documento ILIKE %s OR v.placa ILIKE %s OR u.nombre ILIKE %s
                    ORDER BY u.id_usuario
                    """,
                    (filtro, filtro, filtro)
                )
            else:
                cursor.execute(
                    """
                    SELECT u.id_usuario, u.nombre, u.documento, v.placa, v.tipo_vehiculo,
                           v.fecha_inicio_mensualidad, v.fecha_fin_mensualidad, v.estado_mensualidad
                    FROM Usuario u
                    LEFT JOIN Vehiculo v ON u.id_usuario = v.id_usuario
                    ORDER BY u.id_usuario
                    """
                )
            filas = cursor.fetchall()
            registros = [
                {
                    "id_usuario": f[0],
                    "Propietario": f[1],
                    "Documento": f[2],
                    "Placa": f[3],
                    "Tipo": f[4],
                    "Vigencia": f"{f[5]} a {f[6]}" if f[5] and f[6] else "Sin vigencia",
                    "Estado": f[7]
                }
                for f in filas
            ]
            return {"total_usuarios": f"{len(registros)} usuarios", "registros": registros}
        finally:
            cursor.close()
            conn.close()

    # =========================================================================
    # MÓDULO 2: GESTIÓN DE CELDAS Y OCUPACIÓN (ITERACIÓN 2)
    # =========================================================================

    def crear_celda(self, numero_celda: str, tipo_vehiculo: str):
        conn = obtener_conexion()
        cursor = conn.cursor()
        try:
            numero_celda = numero_celda.strip().upper()
            tipo_vehiculo = tipo_vehiculo.strip().upper()

            cursor.execute("SELECT id_celda FROM Celda WHERE numero_celda = %s", (numero_celda,))
            if cursor.fetchone():
                return {"exito": False, "mensaje": f"La celda {numero_celda} ya existe."}

            cursor.execute(
                "INSERT INTO Celda (numero_celda, tipo_vehiculo, estado) VALUES (%s, %s, 'DISPONIBLE') RETURNING id_celda",
                (numero_celda, tipo_vehiculo)
            )
            id_celda = cursor.fetchone()[0]
            conn.commit()
            return {"exito": True, "mensaje": f"Celda {numero_celda} creada con éxito.", "id_celda": id_celda}
        except Exception as e:
            conn.rollback()
            return {"exito": False, "mensaje": f"Error al crear celda: {str(e)}"}
        finally:
            cursor.close()
            conn.close()

    def eliminar_celda(self, id_celda: int):
        conn = obtener_conexion()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT numero_celda, estado FROM Celda WHERE id_celda = %s", (id_celda,))
            celda = cursor.fetchone()
            if not celda:
                return {"exito": False, "mensaje": "La celda no existe."}
            if celda[1] == "OCUPADA":
                return {"exito": False, "mensaje": f"No se puede eliminar la celda {celda[0]} porque está ocupada."}

            cursor.execute("DELETE FROM Celda WHERE id_celda = %s", (id_celda,))
            conn.commit()
            return {"exito": True, "mensaje": f"Celda {celda[0]} eliminada correctamente."}
        except Exception:
            conn.rollback()
            return {"exito": False, "mensaje": "No se puede eliminar la celda porque tiene historial de accesos."}
        finally:
            cursor.close()
            conn.close()

    def consultar_ocupacion(self):
        conn = obtener_conexion()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id_celda, numero_celda, tipo_vehiculo, estado FROM Celda ORDER BY id_celda")
            filas = cursor.fetchall()
            celdas = [
                {"id_celda": f[0], "numero_celda": f[1], "tipo_vehiculo": f[2], "estado": f[3]}
                for f in filas
            ]
            return {
                "total_celdas": len(celdas),
                "disponibles": sum(1 for c in celdas if c["estado"] == "DISPONIBLE"),
                "ocupadas": sum(1 for c in celdas if c["estado"] == "OCUPADA"),
                "celdas": celdas
            }
        finally:
            cursor.close()
            conn.close()

    # =========================================================================
    # MÓDULO 3: CONTROL DE ACCESO - ENTRADA Y SALIDA (ITERACIÓN 1 CORREGIDA)
    # =========================================================================

    def listar_ingresos_activos(self):
        conn = obtener_conexion()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                SELECT r.id_registro, r.placa, v.tipo_vehiculo, u.nombre,
                       c.numero_celda, r.fecha_hora_ingreso, r.estado_registro
                FROM Registro_Acceso r
                JOIN Vehiculo v ON r.placa = v.placa
                JOIN Usuario u ON v.id_usuario = u.id_usuario
                JOIN Celda c ON r.id_celda = c.id_celda
                WHERE r.estado_registro = 'EN_PARQUEADERO'
                ORDER BY r.fecha_hora_ingreso DESC
                """
            )
            filas = cursor.fetchall()
            activos = [
                {
                    "id_registro": f[0],
                    "placa": f[1],
                    "tipo_vehiculo": f[2],
                    "propietario": f[3],
                    "numero_celda": f[4],
                    "fecha_hora_ingreso": f[5].strftime("%Y-%m-%d %H:%M") if f[5] else "",
                    "estado": f[6]
                }
                for f in filas
            ]
            return {"total_activos": len(activos), "registros": activos}
        finally:
            cursor.close()
            conn.close()

    def registrar_ingreso(self, placa: str, id_celda: int):
        conn = obtener_conexion()
        cursor = conn.cursor()
        try:
            placa = placa.strip().upper()

            cursor.execute(
                "SELECT id_registro FROM Registro_Acceso WHERE placa = %s AND estado_registro = 'EN_PARQUEADERO'",
                (placa,)
            )
            if cursor.fetchone():
                return {"exito": False, "mensaje": f"El vehículo {placa} ya tiene un ingreso activo en el parqueadero."}

            cursor.execute(
                """
                SELECT tipo_vehiculo, estado_mensualidad, fecha_inicio_mensualidad, fecha_fin_mensualidad
                FROM Vehiculo WHERE placa = %s
                """,
                (placa,)
            )
            vehiculo = cursor.fetchone()
            if not vehiculo:
                return {"exito": False, "mensaje": f"El vehículo {placa} no está registrado."}

            tipo_vehiculo, estado_mensualidad, fecha_inicio, fecha_fin = vehiculo
            hoy = date.today()

            if estado_mensualidad != "ACTIVO":
                return {"exito": False, "mensaje": f"El vehículo {placa} tiene su mensualidad INACTIVA. Actívala en 'Usuarios y vehículos'."}

            if not fecha_fin or fecha_fin < hoy or (fecha_inicio and fecha_inicio > hoy):
                return {"exito": False, "mensaje": f"La mensualidad de {placa} está vencida ({fecha_inicio} a {fecha_fin}). Renuévala en 'Usuarios y vehículos'."}

            cursor.execute("SELECT numero_celda, tipo_vehiculo, estado FROM Celda WHERE id_celda = %s", (id_celda,))
            celda = cursor.fetchone()
            if not celda:
                return {"exito": False, "mensaje": "La celda seleccionada no existe."}

            numero_celda, tipo_celda, estado_celda = celda
            if estado_celda != "DISPONIBLE":
                return {"exito": False, "mensaje": f"La celda {numero_celda} ya está ocupada."}

            if tipo_celda != tipo_vehiculo:
                return {"exito": False, "mensaje": f"Incompatibilidad: la celda {numero_celda} es para {tipo_celda} y el vehículo {placa} es {tipo_vehiculo}."}

            cursor.execute(
                "INSERT INTO Registro_Acceso (placa, id_celda) VALUES (%s, %s) RETURNING id_registro",
                (placa, id_celda)
            )
            id_registro = cursor.fetchone()[0]
            cursor.execute("UPDATE Celda SET estado = 'OCUPADA' WHERE id_celda = %s", (id_celda,))
            conn.commit()
            return {"exito": True, "mensaje": f"Ingreso registrado para {placa} en celda {numero_celda}.", "id_registro": id_registro}
        except Exception as e:
            conn.rollback()
            return {"exito": False, "mensaje": f"Error al registrar ingreso: {str(e)}"}
        finally:
            cursor.close()
            conn.close()

    def registrar_salida(self, id_registro: int):
        conn = obtener_conexion()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT id_celda, placa, estado_registro FROM Registro_Acceso WHERE id_registro = %s",
                (id_registro,)
            )
            registro = cursor.fetchone()
            if not registro:
                return {"exito": False, "mensaje": "El registro no existe."}

            id_celda, placa, estado_registro = registro
            if estado_registro == "FINALIZADO":
                return {"exito": False, "mensaje": "Este registro ya fue finalizado."}

            cursor.execute(
                """
                UPDATE Registro_Acceso
                SET fecha_hora_salida = CURRENT_TIMESTAMP, estado_registro = 'FINALIZADO'
                WHERE id_registro = %s
                """,
                (id_registro,)
            )
            cursor.execute("UPDATE Celda SET estado = 'DISPONIBLE' WHERE id_celda = %s", (id_celda,))
            conn.commit()
            return {"exito": True, "mensaje": f"Salida registrada para {placa}. La celda quedó DISPONIBLE."}
        except Exception as e:
            conn.rollback()
            return {"exito": False, "mensaje": f"Error al registrar salida: {str(e)}"}
        finally:
            cursor.close()
            conn.close()