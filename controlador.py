<<<<<<< HEAD
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
=======
# Importamos las bibliotecas necesarias
import psycopg2
import re
import random
from psycopg2 import sql
from flask import Flask
from flask_restful import Api, Resource, reqparse
from flasgger import Swagger

# Conectamos a la base de datos de PostgreSQL
conexion = psycopg2.connect(
    database="usuario",
    user="postgres",
    password="1234",
    host="localhost",
    port="5432"
)

# Creamos un cursor para ejecutar las consultas SQL
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

# Creamos la tabla de cuentas de ahorros si no existe
crear_tabla_cuentas_query = """
CREATE TABLE IF NOT EXISTS cuentas_ahorros (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER REFERENCES usuarios(id),
    numero_cuenta VARCHAR(20) UNIQUE,
    saldo DECIMAL(10, 2) 
);
"""
cursor.execute(crear_tabla_cuentas_query)

# Función para agregar un usuario a la base de datos
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

# Función para crear una cuenta de ahorros
def crear_cuenta_ahorros(usuario_id, saldo_inicial=0):
    # Generamos un número de cuenta aleatorio
    numero_cuenta = ''.join([str(random.randint(0, 9)) for _ in range(10)])

    # Insertamos la cuenta de ahorros en la base de datos
    insertar_cuenta_query = """
    INSERT INTO cuentas_ahorros (usuario_id, numero_cuenta, saldo)
    VALUES (%s, %s, %s) RETURNING id;
    """
    cursor.execute(insertar_cuenta_query, (usuario_id, numero_cuenta, saldo_inicial))
    cuenta_id = cursor.fetchone()[0]
    conexion.commit()
    return cuenta_id


# Función para realizar un depósito en una cuenta de ahorros
def depositar_en_cuenta(numero_cuenta_destino, monto):
    # Verificamos si la cuenta de destino existe
    verificar_cuenta_query = "SELECT id FROM cuentas_ahorros WHERE numero_cuenta = %s;"
    cursor.execute(verificar_cuenta_query, (numero_cuenta_destino,))
    cuenta_existente = cursor.fetchone()

    if cuenta_existente:
        # Realizamos el depósito en la cuenta existente
        depositar_query = """
        UPDATE cuentas_ahorros
        SET saldo = saldo + %s
        WHERE numero_cuenta = %s;
        """
        cursor.execute(depositar_query, (monto, numero_cuenta_destino))
        conexion.commit()
        print(f"Depósito de {monto} realizado en la cuenta {numero_cuenta_destino}")
    else:
        print(f"No existe una cuenta con el número {numero_cuenta_destino}")

# Función para realizar un retiro en una cuenta de ahorros
def retirar_de_cuenta(numero_cuenta_origen, monto):
    # Verificamos si la cuenta de origen existe
    verificar_cuenta_query = "SELECT id, saldo FROM cuentas_ahorros WHERE numero_cuenta = %s;"
    cursor.execute(verificar_cuenta_query, (numero_cuenta_origen,))
    cuenta_existente = cursor.fetchone()

    if cuenta_existente:
        # Verificamos si hay suficiente saldo para el retiro
        cuenta_id, saldo_actual = cuenta_existente
        if saldo_actual >= monto:
            # Realizamos el retiro de la cuenta existente
            retirar_query = """
            UPDATE cuentas_ahorros
            SET saldo = saldo - %s
            WHERE numero_cuenta = %s;
            """
            cursor.execute(retirar_query, (monto, numero_cuenta_origen))
            conexion.commit()
            print(f"Retiro de {monto} realizado de la cuenta {numero_cuenta_origen}")
        else:
            print("Saldo insuficiente para realizar el retiro")
    else:
        print(f"No existe una cuenta con el número {numero_cuenta_origen}")


# Función para eliminar una cuenta de ahorros y su usuario asociado
def eliminar_cuenta_y_usuario(numero_cuenta):
    # Verificamos si la cuenta de destino existe
    verificar_cuenta_query = "SELECT id, usuario_id FROM cuentas_ahorros WHERE numero_cuenta = %s;"
    cursor.execute(verificar_cuenta_query, (numero_cuenta,))
    cuenta_existente = cursor.fetchone()

    if cuenta_existente:
        # Obtenemos el id de la cuenta y el id del usuario asociado
        cuenta_id, usuario_id = cuenta_existente

        # Eliminamos la cuenta de ahorros
        eliminar_cuenta_query = "DELETE FROM cuentas_ahorros WHERE id = %s;"
        cursor.execute(eliminar_cuenta_query, (cuenta_id,))

        # Eliminamos al usuario asociado
        eliminar_usuario_query = "DELETE FROM usuarios WHERE id = %s;"
        cursor.execute(eliminar_usuario_query, (usuario_id,))

        conexion.commit()
        print(f"La cuenta {numero_cuenta} y su usuario asociado han sido eliminados.")
    else:
        print(f"No existe una cuenta con el número {numero_cuenta}")



# Función para obtener todos los usuarios de la base de datos
def obtener_usuarios():
    obtener_usuarios_query = "SELECT * FROM usuarios;"
    cursor.execute(obtener_usuarios_query)
    usuarios = cursor.fetchall()
    return usuarios

# Función para mostrar datos de un usuario
def datos_usuario():
    while True:
        nombre = input("Ingrese el nombre: ")
        apellido = input("Ingrese el apellido: ")
        correo = input("Ingrese el correo electrónico: ")
        cedula = input("Ingrese la cédula (10 dígitos numéricos): ")
        celular = input("Ingrese el número de celular (10 dígitos numéricos): ")

        # Validamos los datos del usuario
        if nombre and apellido and correo and re.match(r'^[0-9]{10}$', cedula) and re.match(r'^[0-9]{10}$', celular):
            return nombre, apellido, correo, cedula, celular
        else:
            print("Por favor ingrese todos sus datos correctamente")

if __name__ == "__main__":
    # Ingresamos un nuevo usuario por consola validando el mismo
    datos_usuario = datos_usuario()
    nuevo_usuario_id = agregar_usuario(*datos_usuario)

    if nuevo_usuario_id:
        # Traemos el id del usuario
        print(f"Nuevo usuario agregado con ID: {nuevo_usuario_id}")

        # Creamos una cuenta de ahorros asociada al nuevo usuario
        nueva_cuenta_id = crear_cuenta_ahorros(nuevo_usuario_id, saldo_inicial=20)  # Puedes ajustar el saldo inicial

        if nueva_cuenta_id:
            print(f"Se ha creado una cuenta de ahorros con ID: {nueva_cuenta_id}")
    
    # Realizamos un depósito y un retiro de ejemplo
    deposito_numero_cuenta = "1081464755"  # Reemplaza con un número de cuenta existente
    deposito_monto = 500
    depositar_en_cuenta(deposito_numero_cuenta, deposito_monto)

    retiro_numero_cuenta = "2713939291"  # Reemplaza con un número de cuenta existente
    retiro_monto = 700
    retirar_de_cuenta(retiro_numero_cuenta, retiro_monto)

    # Eliminamos una cuenta de ahorros y su usuario asociado de ejemplo
    cuenta_a_eliminar = "3365158619"  # Reemplaza con un número de cuenta existente
    eliminar_cuenta_y_usuario(cuenta_a_eliminar)
    
    # Imprimimos todas las cuentas de ahorros
    cuentas_ahorros_query = "SELECT * FROM cuentas_ahorros;"
    cursor.execute(cuentas_ahorros_query)
    cuentas_ahorros = cursor.fetchall()
    print("\nLista de Cuentas de Ahorros:")
    for cuenta in cuentas_ahorros:
        print(cuenta)

    
    
    # Cerramos finalmente nuestra conexión para que sea segura
    cursor.close()
    conexion.close()
>>>>>>> 8e9c11f589de18096b57fbedd78e0e6c02947a10
