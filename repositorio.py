import psycopg2
from modelo import Usuario, CuentaAhorros
import random

class Repositorio:
    def __init__(self):
        self.conexion = psycopg2.connect(
            database="usuario",
            user="postgres",
            password="1234",
            host="localhost",
            port="5432"
        )
        self.cursor = self.conexion.cursor()

    def cerrar_conexion(self):
        self.cursor.close()
        self.conexion.close()

    def agregar_usuario(self, nombre, apellido, correo, cedula, celular):
        insertar_usuario_query = """
        INSERT INTO usuarios (nombre, apellido, correo, cedula, celular)
        VALUES (%s, %s, %s, %s, %s) RETURNING id;
        """
        self.cursor.execute(insertar_usuario_query, (nombre, apellido, correo, cedula, celular))
        usuario_id = self.cursor.fetchone()[0]
        self.conexion.commit()
        return usuario_id

    def crear_cuenta_ahorros(self, usuario_id, saldo_inicial=0):
        numero_cuenta = ''.join([str(random.randint(0, 9)) for _ in range(10)])
        insertar_cuenta_query = """
        INSERT INTO cuentas_ahorros (usuario_id, numero_cuenta, saldo)
        VALUES (%s, %s, %s) RETURNING id;
        """
        self.cursor.execute(insertar_cuenta_query, (usuario_id, numero_cuenta, saldo_inicial))
        cuenta_id = self.cursor.fetchone()[0]
        self.conexion.commit()
        return cuenta_id

    def depositar_en_cuenta(self, numero_cuenta_destino, monto):
        verificar_cuenta_query = "SELECT id FROM cuentas_ahorros WHERE numero_cuenta = %s;"
        self.cursor.execute(verificar_cuenta_query, (numero_cuenta_destino,))
        cuenta_existente = self.cursor.fetchone()

        if cuenta_existente:
            depositar_query = """
            UPDATE cuentas_ahorros
            SET saldo = saldo + %s
            WHERE numero_cuenta = %s;
            """
            self.cursor.execute(depositar_query, (monto, numero_cuenta_destino))
            self.conexion.commit()
            print(f"Depósito de {monto} realizado en la cuenta {numero_cuenta_destino}")
        else:
            print(f"No existe una cuenta con el número {numero_cuenta_destino}")

    def retirar_de_cuenta(self, numero_cuenta_origen, monto):
        verificar_cuenta_query = "SELECT id, saldo FROM cuentas_ahorros WHERE numero_cuenta = %s;"
        self.cursor.execute(verificar_cuenta_query, (numero_cuenta_origen,))
        cuenta_existente = self.cursor.fetchone()

        if cuenta_existente:
            cuenta_id, saldo_actual = cuenta_existente
            if saldo_actual >= monto:
                retirar_query = """
                UPDATE cuentas_ahorros
                SET saldo = saldo - %s
                WHERE numero_cuenta = %s;
                """
                self.cursor.execute(retirar_query, (monto, numero_cuenta_origen))
                self.conexion.commit()
                print(f"Retiro de {monto} realizado de la cuenta {numero_cuenta_origen}")
            else:
                print("Saldo insuficiente para realizar el retiro")
        else:
            print(f"No existe una cuenta con el número {numero_cuenta_origen}")



    def eliminar_cuenta_y_usuario(self, numero_cuenta):
        verificar_cuenta_query = "SELECT id, usuario_id FROM cuentas_ahorros WHERE numero_cuenta = %s;"
        self.cursor.execute(verificar_cuenta_query, (numero_cuenta,))
        cuenta_existente = self.cursor.fetchone()

        if cuenta_existente:
            cuenta_id, usuario_id = cuenta_existente
            eliminar_cuenta_query = "DELETE FROM cuentas_ahorros WHERE id = %s;"
            self.cursor.execute(eliminar_cuenta_query, (cuenta_id,))

            eliminar_usuario_query = "DELETE FROM usuarios WHERE id = %s;"
            self.cursor.execute(eliminar_usuario_query, (usuario_id,))

            self.conexion.commit()
            print(f"La cuenta {numero_cuenta} y su usuario asociado han sido eliminados.")
        else:
            print(f"No existe una cuenta con el número {numero_cuenta}")



    def obtener_usuarios(self):
        obtener_usuarios_query = "SELECT * FROM usuarios;"
        self.cursor.execute(obtener_usuarios_query)
        usuarios = self.cursor.fetchall()
        return usuarios

    def obtener_usuario_id_por_cuenta(self, numero_cuenta):
        try:
            # Ejemplo de consulta SQL para obtener usuario_id por número de cuenta
            obtener_usuario_id_query = """
                SELECT usuario_id FROM cuentas_ahorros
                WHERE numero_cuenta = %s;
            """
            self.cursor.execute(obtener_usuario_id_query, (numero_cuenta,))
            usuario_id = self.cursor.fetchone()

            if usuario_id:
                return usuario_id[0]
            else:
                raise ValueError(f"No se encontró un usuario para la cuenta {numero_cuenta}")

        except Exception as e:
            # Manejo de excepciones, puedes personalizar según tus necesidades
            print(f"Error al obtener el usuario por cuenta: {e}")
            raise


    def solicitar_credito(self, usuario_id, monto, plazo_meses, tasa_interes):
        cuenta_id = usuario_id

        insertar_credito_query = """
        INSERT INTO creditos (usuario_id, cuenta_id, monto, plazo_meses, tasa_interes)
        VALUES (%s, %s, %s, %s, %s) RETURNING id;
        """
        self.cursor.execute(insertar_credito_query, (usuario_id, cuenta_id, monto, plazo_meses, tasa_interes))
        credito_id = self.cursor.fetchone()[0]
        self.conexion.commit()
        return credito_id

    def obtener_creditos_usuario(self, usuario_id):
        obtener_creditos_query = """
        SELECT *
        FROM creditos
        WHERE usuario_id = %s;
        """
        self.cursor.execute(obtener_creditos_query, (usuario_id,))
        creditos_usuario = self.cursor.fetchall()
        return creditos_usuario

    def aprobar_credito(self, credito_id):
        aprobar_credito_query = """
        UPDATE creditos
        SET estado = 'APROBADO'
        WHERE id = %s;
        """
        self.cursor.execute(aprobar_credito_query, (credito_id,))
        self.conexion.commit()
        print(f"Crédito con ID {credito_id} aprobado")

    def rechazar_credito(self, credito_id):
        rechazar_query = "UPDATE creditos SET estado = 'Rechazado' WHERE id = %s;"
        self.cursor.execute(rechazar_query, (credito_id,))
        self.conexion.commit()
        print(f"Crédito con ID {credito_id} rechazado")

    def generar_tabla_amortizacion(self, credito_id):
        obtener_credito_query = """
        SELECT monto, plazo_meses, tasa_interes
        FROM creditos
        WHERE id = %s;
        """
        self.cursor.execute(obtener_credito_query, (credito_id,))
        credito_info = self.cursor.fetchone()

        if not credito_info:
            print("No se encontró información del crédito.")
            return

        monto, plazo_meses, tasa_interes = credito_info

        tasa_mensual = tasa_interes / 12
        cuota_mensual = (monto * tasa_mensual) / (1 - (1 + tasa_mensual)**-plazo_meses)

        tabla_amortizacion = []
        saldo_pendiente = monto

        for mes in range(1, plazo_meses + 1):
            interes_mes = saldo_pendiente * tasa_mensual
            amortizacion_mes = cuota_mensual - interes_mes
            saldo_pendiente -= amortizacion_mes

            fila_amortizacion = {
                "Mes": mes,
                "Cuota": cuota_mensual,
                "Interés": interes_mes,
                "Amortización": amortizacion_mes,
                "Saldo Pendiente": saldo_pendiente
            }

            tabla_amortizacion.append(fila_amortizacion)

        guardar_amortizacion_query = """
        INSERT INTO amortizacion_creditos (credito_id, mes, cuota, interes, amortizacion, saldo_pendiente)
        VALUES (%s, %s, %s, %s, %s, %s);
        """
        for fila in tabla_amortizacion:
            self.cursor.execute(
                guardar_amortizacion_query,
                (credito_id, fila["Mes"], fila["Cuota"], fila["Interés"], fila["Amortización"], fila["Saldo Pendiente"])
            )

        self.conexion.commit()
        print("Tabla de amortización generada y guardada.")