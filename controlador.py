import psycopg2
from psycopg2 import sql
import re
import random

# Conexión a la base de datos
conexion = psycopg2.connect(
    database="usuario",
    user="postgres",
    password="12345",
    host="localhost",
    port="5432"
)

# Cursor para ejecutar consultas SQL
cursor = conexion.cursor()

# Creamos la tabla de usuarios si no existe
crear_tabla_query = """
CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50),
    apellido VARCHAR(50),
    correo VARCHAR(100),
    cedula VARCHAR(20),
    celular VARCHAR(15)
);
"""
cursor.execute(crear_tabla_query)

# Agrega esta parte al código donde defines las tablas
crear_tabla_transacciones_query = """
CREATE TABLE IF NOT EXISTS transacciones (
    id SERIAL PRIMARY KEY,
    tipo VARCHAR(20),
    descripcion TEXT,
    monto DECIMAL(10, 2),
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_id INTEGER REFERENCES usuarios(id),
    cuenta_id INTEGER REFERENCES cuentas_ahorros(id)
);
"""
cursor.execute(crear_tabla_transacciones_query)

crear_tabla_creditos_query = """
CREATE TABLE IF NOT EXISTS creditos (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER,
    cuenta_id INTEGER,
    monto DECIMAL(10, 2),
    plazo_meses INTEGER,
    tasa_interes DECIMAL(5, 4),
    estado VARCHAR(20) DEFAULT 'PENDIENTE'
);
"""
cursor.execute(crear_tabla_creditos_query)

crear_tabla_amortizacion_query = """
CREATE TABLE IF NOT EXISTS amortizacion_creditos (
    id SERIAL PRIMARY KEY,
    credito_id INTEGER,
    mes INTEGER,
    cuota DECIMAL(10, 2),
    interes DECIMAL(10, 2),
    amortizacion DECIMAL(10, 2),
    saldo_pendiente DECIMAL(10, 2)
);
"""
cursor.execute(crear_tabla_amortizacion_query)

conexion.commit()


def agregar_usuario(nombre, apellido, correo, cedula, celular):
    # Validamos que todos los datos estén ingresados
    if not nombre or not apellido or not correo or not cedula or not celular:
        print("Por favor ingrese todos sus datos para el registro")
        return None

    # Validamos el formato de la cédula para Ecuador
    if not re.match(r'^[0-9]{10}$', cedula):
        print("La cédula debe contener 10 dígitos numéricos")
        return None

    # Validamos el formato del número de celular para Ecuador
    if not re.match(r'^[0-9]{10}$', celular):
        print("El número de celular debe contener 10 dígitos numéricos")
        return None

    # Insertamos el usuario en la tabla de usuarios
    insertar_usuario_query = """
    INSERT INTO usuarios (nombre, apellido, correo, cedula, celular)
    VALUES (%s, %s, %s, %s, %s) RETURNING id;
    """
    cursor.execute(insertar_usuario_query, (nombre, apellido, correo, cedula, celular))
    usuario_id = cursor.fetchone()[0]
    conexion.commit()
    return usuario_id

# Agrega estas funciones

def solicitar_credito(usuario_id, monto, plazo_meses, tasa_interes):
    # Se supone que usuario_id y cuenta_id deberían ser diferentes.
    # En este ejemplo, estoy utilizando el mismo usuario_id como cuenta_id.
    cuenta_id = usuario_id

    insertar_credito_query = """
    INSERT INTO creditos (usuario_id, cuenta_id, monto, plazo_meses, tasa_interes)
    VALUES (%s, %s, %s, %s, %s) RETURNING id;
    """
    cursor.execute(insertar_credito_query, (usuario_id, cuenta_id, monto, plazo_meses, tasa_interes))
    credito_id = cursor.fetchone()[0]
    conexion.commit()
    return credito_id

def obtener_creditos_usuario(usuario_id):
    obtener_creditos_query = """
    SELECT *
    FROM creditos
    WHERE usuario_id = %s;
    """
    cursor.execute(obtener_creditos_query, (usuario_id,))
    creditos_usuario = cursor.fetchall()
    return creditos_usuario

def aprobar_credito(credito_id):
    aprobar_credito_query = """
    UPDATE creditos
    SET estado = 'APROBADO'
    WHERE id = %s;
    """
    cursor.execute(aprobar_credito_query, (credito_id,))
    conexion.commit()
    print(f"Crédito con ID {credito_id} aprobado")

def rechazar_credito(credito_id):
    # Actualizamos el estado del crédito a Rechazado
    rechazar_query = "UPDATE creditos SET estado = 'Rechazado' WHERE id = %s;"
    cursor.execute(rechazar_query, (credito_id,))
    conexion.commit()
    print(f"Crédito con ID {credito_id} rechazado")    

def generar_reporte_creditos(usuario_id):
    creditos_usuario = obtener_creditos_usuario(usuario_id)

    if creditos_usuario:
        print(f"Reporte de créditos para el usuario con ID {usuario_id}:")
        for credito in creditos_usuario:
            print(credito)
    else:
        print(f"No hay créditos para el usuario con ID {usuario_id}")

def generar_tabla_amortizacion(credito_id):
    # Obtener información del crédito
    obtener_credito_query = """
    SELECT monto, plazo_meses, tasa_interes
    FROM creditos
    WHERE id = %s;
    """
    cursor.execute(obtener_credito_query, (credito_id,))
    credito_info = cursor.fetchone()

    if not credito_info:
        print("No se encontró información del crédito.")
        return

    monto, plazo_meses, tasa_interes = credito_info

    # Calcular la cuota mensual
    tasa_mensual = tasa_interes / 12
    cuota_mensual = (monto * tasa_mensual) / (1 - (1 + tasa_mensual)**-plazo_meses)

    # Inicializar la tabla de amortización
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

    # Guardar la información en una tabla amortizacion_creditos
    guardar_amortizacion_query = """
    INSERT INTO amortizacion_creditos (credito_id, mes, cuota, interes, amortizacion, saldo_pendiente)
    VALUES (%s, %s, %s, %s, %s, %s);
    """
    for fila in tabla_amortizacion:
        cursor.execute(guardar_amortizacion_query, (credito_id, fila["Mes"], fila["Cuota"], fila["Interés"], fila["Amortización"], fila["Saldo Pendiente"]))

    conexion.commit()
    print("Tabla de amortización generada y guardada.")


# Ejemplo de uso:
# Agregar un usuario
nombre = input("Ingrese el nombre: ")
apellido = input("Ingrese el apellido: ")
correo = input("Ingrese el correo electrónico: ")
cedula = input("Ingrese la cédula (10 dígitos numéricos): ")
celular = input("Ingrese el número de celular (10 dígitos numéricos): ")

usuario_id = agregar_usuario(nombre, apellido, correo, cedula, celular)
print(f"Nuevo usuario agregado con ID: {usuario_id}")

# Solicitar un crédito para el usuario
monto = float(input("Ingrese el monto del crédito: "))
plazo_meses = int(input("Ingrese el plazo del crédito en meses: "))
tasa_interes = float(input("Ingrese la tasa de interés del crédito (porcentaje): "))

credito_id = solicitar_credito(usuario_id, monto, plazo_meses, tasa_interes)
print(f"Crédito solicitado con ID: {credito_id}")

# Aprobar el crédito
aprobar_credito(credito_id)
print(f"Crédito con ID {credito_id} aprobado")

# Obtener la lista de créditos
creditos = obtener_creditos_usuario(usuario_id)
print("\nLista de Créditos:")
for credito in creditos:
    print(credito)

# Generar tabla de amortización
generar_tabla_amortizacion(credito_id)

# Cerramos finalmente nuestra conexión para que sea segura
cursor.close()
conexion.close()