# Importamos las bibliotecas necesarias
import psycopg2
import re
import random
from psycopg2 import sql

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
