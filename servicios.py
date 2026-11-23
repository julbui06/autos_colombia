from datetime import date, timedelta
from conexion import obtener_conexion

class ParqueaderoService:

    # =========================================================================
    # MÓDULO 0: AUTENTICACIÓN, CUENTAS DE ACCESO Y ROLES
    # =========================================================================

    def autenticar_usuario(self, correo: str, password: str):
        conn = obtener_conexion()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT id_cuenta, nombre_completo, correo, rol, estado FROM cuenta_sistema WHERE correo = %s AND password = %s",
                (correo.strip().lower(), password.strip())
            )
            cuenta = cursor.fetchone()
            if not cuenta:
                return {"exito": False, "mensaje": "Credenciales incorrectas. Verifica correo y contraseña."}
            if cuenta[4] != "ACTIVO":
                return {"exito": False, "mensaje": "Esta cuenta de acceso se encuentra INACTIVA."}

            return {
                "exito": True,
                "mensaje": f"Bienvenido(a) {cuenta[1]} ({cuenta[3]})",
                "usuario": {
                    "id_cuenta": cuenta[0],
                    "nombre": cuenta[1],
                    "correo": cuenta[2],
                    "rol": cuenta[3]
                }
            }
        except Exception as e:
            return {"exito": False, "mensaje": f"Error de conexión: {str(e)}"}
        finally:
            cursor.close()
            conn.close()

    def crear_cuenta_sistema(self, nombre_completo: str, correo: str, password: str, rol: str, rol_solicitante: str = "ADMINISTRADOR"):
        if rol_solicitante != "ADMINISTRADOR":
            return {"exito": False, "mensaje": "Acceso denegado: Solo un ADMINISTRADOR puede crear cuentas del sistema."}
        conn = obtener_conexion()
        cursor = conn.cursor()
        try:
            correo = correo.strip().lower()
            rol = rol.strip().upper()
            if rol not in ("ADMINISTRADOR", "OPERADOR"):
                return {"exito": False, "mensaje": "Rol inválido. Debe ser ADMINISTRADOR u OPERADOR."}
            if len(password.strip()) < 4:
                return {"exito": False, "mensaje": "La contraseña debe tener al menos 4 caracteres."}

            cursor.execute("SELECT id_cuenta FROM cuenta_sistema WHERE correo = %s", (correo,))
            if cursor.fetchone():
                return {"exito": False, "mensaje": f"El correo {correo} ya está registrado en el sistema."}

            cursor.execute(
                "INSERT INTO cuenta_sistema (nombre_completo, correo, password, rol, estado) VALUES (%s, %s, %s, %s, 'ACTIVO') RETURNING id_cuenta",
                (nombre_completo.strip(), correo, password.strip(), rol)
            )
            id_cuenta = cursor.fetchone()[0]
            conn.commit()
            return {"exito": True, "mensaje": f"Cuenta {rol} creada para {nombre_completo}.", "id_cuenta": id_cuenta}
        except Exception as e:
            conn.rollback()
            return {"exito": False, "mensaje": f"Error al crear cuenta: {str(e)}"}
        finally:
            cursor.close()
            conn.close()

    def listar_cuentas_sistema(self):
        conn = obtener_conexion()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id_cuenta, nombre_completo, correo, rol, estado FROM cuenta_sistema ORDER BY id_cuenta")
            filas = cursor.fetchall()
            cuentas = [{"id_cuenta": f[0], "nombre": f[1], "correo": f[2], "rol": f[3], "estado": f[4]} for f in filas]
            return {"total": len(cuentas), "cuentas": cuentas}
        finally:
            cursor.close()
            conn.close()

    def cambiar_estado_cuenta(self, id_cuenta: int, nuevo_estado: str, rol_solicitante: str = "ADMINISTRADOR"):
        if rol_solicitante != "ADMINISTRADOR":
            return {"exito": False, "mensaje": "Acceso denegado: Solo un ADMINISTRADOR puede modificar cuentas."}
        conn = obtener_conexion()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE cuenta_sistema SET estado = %s WHERE id_cuenta = %s", (nuevo_estado.upper(), id_cuenta))
            conn.commit()
            return {"exito": True, "mensaje": f"Estado de cuenta actualizado a {nuevo_estado.upper()}."}
        except Exception as e:
            conn.rollback()
            return {"exito": False, "mensaje": f"Error: {str(e)}"}
        finally:
            cursor.close()
            conn.close()

    # =========================================================================
    # MÓDULO 1: GESTIÓN DE PROPIETARIOS, VEHÍCULOS Y MENSUALIDADES
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

            cursor.execute("SELECT placa FROM vehiculo WHERE placa = %s", (placa,))
            if cursor.fetchone():
                return {"exito": False, "mensaje": f"La placa {placa} ya se encuentra registrada."}

            if id_celda_inicial:
                hoy = date.today()
                if estado_mensualidad != "ACTIVO" or fecha_fin_mensualidad < hoy or fecha_inicio_mensualidad > hoy:
                    return {"exito": False, "mensaje": "Para asignar una celda al crear, la mensualidad debe estar ACTIVA y vigente hoy."}

                cursor.execute("SELECT numero_celda, tipo_vehiculo, estado FROM celda WHERE id_celda = %s", (id_celda_inicial,))
                celda = cursor.fetchone()
                if not celda:
                    return {"exito": False, "mensaje": "La celda seleccionada no existe."}
                if celda[2] != "DISPONIBLE":
                    return {"exito": False, "mensaje": f"La celda {celda[0]} ya está ocupada."}
                if celda[1] != tipo_vehiculo:
                    return {"exito": False, "mensaje": f"Incompatibilidad: la celda {celda[0]} es para {celda[1]} y el vehículo es {tipo_vehiculo}."}

            cursor.execute("SELECT id_usuario FROM usuario WHERE documento = %s", (documento,))
            usuario_existente = cursor.fetchone()

            if usuario_existente:
                id_usuario = usuario_existente[0]
            else:
                cursor.execute(
                    "INSERT INTO usuario (nombre, documento, telefono) VALUES (%s, %s, %s) RETURNING id_usuario",
                    (nombre, documento, telefono)
                )
                id_usuario = cursor.fetchone()[0]

            cursor.execute(
                """
                INSERT INTO vehiculo (
                    placa, id_usuario, tipo_vehiculo, estado_mensualidad,
                    fecha_inicio_mensualidad, fecha_fin_mensualidad
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (placa, id_usuario, tipo_vehiculo, estado_mensualidad, fecha_inicio_mensualidad, fecha_fin_mensualidad)
            )

            mensaje_extra = ""
            if id_celda_inicial:
                cursor.execute("INSERT INTO registro_acceso (placa, id_celda) VALUES (%s, %s)", (placa, id_celda_inicial))
                cursor.execute("UPDATE celda SET estado = 'OCUPADA' WHERE id_celda = %s", (id_celda_inicial,))
                mensaje_extra = f" y celda {celda[0]} asignada"

            conn.commit()
            return {
                "exito": True,
                "mensaje": f"Propietario {nombre} y vehículo {placa} guardados{mensaje_extra}.",
                "id_usuario": id_usuario
            }
        except Exception as e:
            conn.rollback()
            return {"exito": False, "mensaje": f"Error al registrar: {str(e)}"}
        finally:
            cursor.close()
            conn.close()

    def eliminar_usuario(self, id_usuario: int, rol_solicitante: str = "ADMINISTRADOR"):
        if rol_solicitante != "ADMINISTRADOR":
            return {"exito": False, "mensaje": "Acceso denegado: Solo un ADMINISTRADOR puede eliminar propietarios."}
        conn = obtener_conexion()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT nombre FROM usuario WHERE id_usuario = %s", (id_usuario,))
            usuario = cursor.fetchone()
            if not usuario:
                return {"exito": False, "mensaje": "El propietario no existe."}

            cursor.execute(
                """
                SELECT r.placa FROM registro_acceso r
                JOIN vehiculo v ON r.placa = v.placa
                WHERE v.id_usuario = %s AND r.estado_registro = 'EN_PARQUEADERO'
                """,
                (id_usuario,)
            )
            activo = cursor.fetchone()
            if activo:
                return {"exito": False, "mensaje": f"No se puede eliminar porque su vehículo ({activo[0]}) está dentro del parqueadero."}

            cursor.execute("DELETE FROM registro_acceso WHERE placa IN (SELECT placa FROM vehiculo WHERE id_usuario = %s)", (id_usuario,))
            cursor.execute("DELETE FROM pago WHERE placa IN (SELECT placa FROM vehiculo WHERE id_usuario = %s)", (id_usuario,))
            cursor.execute("DELETE FROM vehiculo WHERE id_usuario = %s", (id_usuario,))
            cursor.execute("DELETE FROM usuario WHERE id_usuario = %s", (id_usuario,))
            conn.commit()
            return {"exito": True, "mensaje": f"Propietario {usuario[0]} eliminado correctamente."}
        except Exception as e:
            conn.rollback()
            return {"exito": False, "mensaje": f"Error al eliminar: {str(e)}"}
        finally:
            cursor.close()
            conn.close()

    def cambiar_estado_mensualidad(self, placa: str, nuevo_estado: str, fecha_inicio: date = None, fecha_fin: date = None):
        conn = obtener_conexion()
        cursor = conn.cursor()
        try:
            placa = placa.strip().upper()
            nuevo_estado = nuevo_estado.strip().upper()
            cursor.execute("SELECT placa FROM vehiculo WHERE placa = %s", (placa,))
            if not cursor.fetchone():
                return {"exito": False, "mensaje": f"No se encontró el vehículo {placa}."}

            if nuevo_estado == "ACTIVO":
                f_ini = fecha_inicio or date.today()
                f_fin = fecha_fin or (date.today() + timedelta(days=30))
                cursor.execute(
                    "UPDATE vehiculo SET estado_mensualidad = 'ACTIVO', fecha_inicio_mensualidad = %s, fecha_fin_mensualidad = %s WHERE placa = %s",
                    (f_ini, f_fin, placa)
                )
                conn.commit()
                return {"exito": True, "mensaje": f"Mensualidad de {placa} ACTIVADA ({f_ini} a {f_fin})."}
            else:
                cursor.execute("UPDATE vehiculo SET estado_mensualidad = 'INACTIVO' WHERE placa = %s", (placa,))
                conn.commit()
                return {"exito": True, "mensaje": f"Mensualidad de {placa} DESACTIVADA."}
        except Exception as e:
            conn.rollback()
            return {"exito": False, "mensaje": f"Error: {str(e)}"}
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
                    FROM usuario u
                    LEFT JOIN vehiculo v ON u.id_usuario = v.id_usuario
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
                    FROM usuario u
                    LEFT JOIN vehiculo v ON u.id_usuario = v.id_usuario
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
            return {"total_usuarios": f"{len(registros)} propietarios", "registros": registros}
        finally:
            cursor.close()
            conn.close()

    # =========================================================================
    # MÓDULO 2: GESTIÓN DE CELDAS Y OCUPACIÓN
    # =========================================================================

    def crear_celda(self, numero_celda: str, tipo_vehiculo: str, rol_solicitante: str = "ADMINISTRADOR"):
        if rol_solicitante != "ADMINISTRADOR":
            return {"exito": False, "mensaje": "Acceso denegado: Solo un ADMINISTRADOR puede crear celdas."}
        conn = obtener_conexion()
        cursor = conn.cursor()
        try:
            numero_celda = numero_celda.strip().upper()
            tipo_vehiculo = tipo_vehiculo.strip().upper()
            cursor.execute("SELECT id_celda FROM celda WHERE numero_celda = %s", (numero_celda,))
            if cursor.fetchone():
                return {"exito": False, "mensaje": f"La celda {numero_celda} ya existe."}

            cursor.execute(
                "INSERT INTO celda (numero_celda, tipo_vehiculo, estado) VALUES (%s, %s, 'DISPONIBLE') RETURNING id_celda",
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

    def eliminar_celda(self, id_celda: int, rol_solicitante: str = "ADMINISTRADOR"):
        if rol_solicitante != "ADMINISTRADOR":
            return {"exito": False, "mensaje": "Acceso denegado: Solo un ADMINISTRADOR puede eliminar celdas."}
        conn = obtener_conexion()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT numero_celda, estado FROM celda WHERE id_celda = %s", (id_celda,))
            celda = cursor.fetchone()
            if not celda:
                return {"exito": False, "mensaje": "La celda no existe."}
            if celda[1] == "OCUPADA":
                return {"exito": False, "mensaje": f"No se puede eliminar la celda {celda[0]} porque está ocupada."}

            cursor.execute("DELETE FROM celda WHERE id_celda = %s", (id_celda,))
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
            cursor.execute("SELECT id_celda, numero_celda, tipo_vehiculo, estado FROM celda ORDER BY id_celda")
            filas = cursor.fetchall()
            celdas = [{"id_celda": f[0], "numero_celda": f[1], "tipo_vehiculo": f[2], "estado": f[3]} for f in filas]
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
    # MÓDULO 3: CONTROL DE ACCESO (ENTRADA Y SALIDA)
    # =========================================================================

    def listar_ingresos_activos(self):
        conn = obtener_conexion()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                SELECT r.id_registro, r.placa, v.tipo_vehiculo, u.nombre,
                       c.numero_celda, r.fecha_hora_ingreso, r.estado_registro
                FROM registro_acceso r
                JOIN vehiculo v ON r.placa = v.placa
                JOIN usuario u ON v.id_usuario = u.id_usuario
                JOIN celda c ON r.id_celda = c.id_celda
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
            cursor.execute("SELECT id_registro FROM registro_acceso WHERE placa = %s AND estado_registro = 'EN_PARQUEADERO'", (placa,))
            if cursor.fetchone():
                return {"exito": False, "mensaje": f"Rechazado: El vehículo {placa} ya tiene un ingreso activo en el parqueadero."}

            cursor.execute(
                "SELECT tipo_vehiculo, estado_mensualidad, fecha_inicio_mensualidad, fecha_fin_mensualidad FROM vehiculo WHERE placa = %s",
                (placa,)
            )
            vehiculo = cursor.fetchone()
            if not vehiculo:
                return {"exito": False, "mensaje": f"Rechazado: El vehículo {placa} no está registrado."}

            tipo_vehiculo, estado_mensualidad, fecha_inicio, fecha_fin = vehiculo
            hoy = date.today()

            if estado_mensualidad != "ACTIVO":
                return {"exito": False, "mensaje": f"Rechazado: El vehículo {placa} tiene su mensualidad INACTIVA."}
            if not fecha_fin or fecha_fin < hoy or (fecha_inicio and fecha_inicio > hoy):
                return {"exito": False, "mensaje": f"Rechazado: La mensualidad de {placa} está vencida ({fecha_inicio} a {fecha_fin})."}

            cursor.execute("SELECT numero_celda, tipo_vehiculo, estado FROM celda WHERE id_celda = %s", (id_celda,))
            celda = cursor.fetchone()
            if not celda:
                return {"exito": False, "mensaje": "Rechazado: La celda seleccionada no existe."}
            if celda[2] != "DISPONIBLE":
                return {"exito": False, "mensaje": f"Rechazado: La celda {celda[0]} ya está ocupada."}
            if celda[1] != tipo_vehiculo:
                return {"exito": False, "mensaje": f"Rechazado: La celda {celda[0]} es para {celda[1]} y el vehículo {placa} es {tipo_vehiculo}."}

            cursor.execute("INSERT INTO registro_acceso (placa, id_celda) VALUES (%s, %s) RETURNING id_registro", (placa, id_celda))
            id_registro = cursor.fetchone()[0]
            cursor.execute("UPDATE celda SET estado = 'OCUPADA' WHERE id_celda = %s", (id_celda,))
            conn.commit()
            return {"exito": True, "mensaje": f"Ingreso autorizado para {placa} en celda {celda[0]}.", "id_registro": id_registro}
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
            cursor.execute("SELECT id_celda, placa, estado_registro FROM registro_acceso WHERE id_registro = %s", (id_registro,))
            registro = cursor.fetchone()
            if not registro:
                return {"exito": False, "mensaje": "Rechazado: El registro de ingreso no existe."}
            if registro[2] == "FINALIZADO":
                return {"exito": False, "mensaje": "Rechazado: Este registro ya fue finalizado."}

            cursor.execute(
                "UPDATE registro_acceso SET fecha_hora_salida = CURRENT_TIMESTAMP, estado_registro = 'FINALIZADO' WHERE id_registro = %s",
                (id_registro,)
            )
            cursor.execute("UPDATE celda SET estado = 'DISPONIBLE' WHERE id_celda = %s", (registro[0],))
            conn.commit()
            return {"exito": True, "mensaje": f"Salida registrada para {registro[1]}. La celda quedó DISPONIBLE."}
        except Exception as e:
            conn.rollback()
            return {"exito": False, "mensaje": f"Error al registrar salida: {str(e)}"}
        finally:
            cursor.close()
            conn.close()

    # =========================================================================
    # MÓDULO 4: GESTIÓN DE PAGOS Y MENSUALIDADES
    # =========================================================================

    def registrar_pago(self, placa: str, monto: float, metodo_pago: str, periodo_inicio: date, periodo_fin: date):
        conn = obtener_conexion()
        cursor = conn.cursor()
        try:
            placa = placa.strip().upper()
            if monto <= 0:
                return {"exito": False, "mensaje": "Rechazado: El monto del pago debe ser mayor a $0."}
            if periodo_fin < periodo_inicio:
                return {"exito": False, "mensaje": "Rechazado: La fecha fin no puede ser menor a la fecha inicio."}

            cursor.execute("SELECT placa FROM vehiculo WHERE placa = %s", (placa,))
            if not cursor.fetchone():
                return {"exito": False, "mensaje": f"Rechazado: El vehículo {placa} no está registrado."}

            cursor.execute("SELECT COALESCE(MAX(id_pago), 0) + 1 FROM pago")
            siguiente_id = cursor.fetchone()[0]
            numero_recibo = f"REC-{siguiente_id:04d}"

            cursor.execute(
                """
                INSERT INTO pago (numero_recibo, placa, monto, metodo_pago, periodo_inicio, periodo_fin, estado_pago)
                VALUES (%s, %s, %s, %s, %s, %s, 'PAGADO') RETURNING id_pago
                """,
                (numero_recibo, placa, monto, metodo_pago, periodo_inicio, periodo_fin)
            )
            id_pago = cursor.fetchone()[0]

            cursor.execute(
                """
                UPDATE vehiculo
                SET estado_mensualidad = 'ACTIVO',
                    fecha_inicio_mensualidad = %s,
                    fecha_fin_mensualidad = %s
                WHERE placa = %s
                """,
                (periodo_inicio, periodo_fin, placa)
            )

            conn.commit()
            return {
                "exito": True,
                "mensaje": f"Pago {numero_recibo} registrado por ${monto:,.0f}. Mensualidad de {placa} ACTIVADA hasta {periodo_fin}.",
                "id_pago": id_pago,
                "numero_recibo": numero_recibo
            }
        except Exception as e:
            conn.rollback()
            return {"exito": False, "mensaje": f"Error al registrar pago: {str(e)}"}
        finally:
            cursor.close()
            conn.close()

    def listar_pagos(self, buscar: str = None):
        conn = obtener_conexion()
        cursor = conn.cursor()
        try:
            base_query = """
                SELECT p.id_pago, p.numero_recibo, u.nombre, u.documento, p.placa,
                       v.tipo_vehiculo, p.monto, p.metodo_pago, p.fecha_pago,
                       p.periodo_inicio, p.periodo_fin, p.estado_pago
                FROM pago p
                JOIN vehiculo v ON p.placa = v.placa
                JOIN usuario u ON v.id_usuario = u.id_usuario
            """
            if buscar:
                filtro = f"%{buscar.strip()}%"
                cursor.execute(
                    base_query + " WHERE p.numero_recibo ILIKE %s OR p.placa ILIKE %s OR u.documento ILIKE %s OR u.nombre ILIKE %s ORDER BY p.id_pago DESC",
                    (filtro, filtro, filtro, filtro)
                )
            else:
                cursor.execute(base_query + " ORDER BY p.id_pago DESC")

            filas = cursor.fetchall()
            pagos = [
                {
                    "id_pago": f[0],
                    "numero_recibo": f[1],
                    "propietario": f[2],
                    "documento": f[3],
                    "placa": f[4],
                    "tipo_vehiculo": f[5],
                    "monto": float(f[6]),
                    "metodo_pago": f[7],
                    "fecha_pago": f[8].strftime("%Y-%m-%d %H:%M") if f[8] else "",
                    "vigencia": f"{f[9]} a {f[10]}",
                    "estado_pago": f[11]
                }
                for f in filas
            ]
            total_recaudado = sum(p["monto"] for p in pagos if p["estado_pago"] == "PAGADO")
            pagos_validos = sum(1 for p in pagos if p["estado_pago"] == "PAGADO")
            return {"total_recaudado": total_recaudado, "total_transacciones": pagos_validos, "registros": pagos}
        finally:
            cursor.close()
            conn.close()

    def anular_pago(self, id_pago: int, rol_solicitante: str = "ADMINISTRADOR"):
        if rol_solicitante != "ADMINISTRADOR":
            return {"exito": False, "mensaje": "Acceso denegado: Solo un ADMINISTRADOR puede anular pagos."}
        conn = obtener_conexion()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT numero_recibo, estado_pago FROM pago WHERE id_pago = %s", (id_pago,))
            pago = cursor.fetchone()
            if not pago:
                return {"exito": False, "mensaje": "El pago no existe."}
            if pago[1] == "ANULADO":
                return {"exito": False, "mensaje": "Este pago ya se encuentra anulado."}

            cursor.execute("UPDATE pago SET estado_pago = 'ANULADO' WHERE id_pago = %s", (id_pago,))
            conn.commit()
            return {"exito": True, "mensaje": f"Comprobante {pago[0]} anulado correctamente."}
        except Exception as e:
            conn.rollback()
            return {"exito": False, "mensaje": f"Error al anular pago: {str(e)}"}
        finally:
            cursor.close()
            conn.close()