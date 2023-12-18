#installamos el paquete psycopg2 para poder realizar conexion a nuestra base de datos en potsgres
import psycopg2
import re
from psycopg2 import sql


#Agregamos la conexion a nuestra base de datos de potsgres
conexion = psycopg2.connect(
    database="usuario",
    user="postgres",
    password="1234",
    host="localhost",
    port="5432"
)
#para poder agregar sentencias SQL en nuestro codigo de pyhton agregamos un cursos el cual 
#permite realizar sentencias SQL
cursor = conexion.cursor()

#Creamos nuestro usuario si en nuestro potsgres aun no lo hemos realizado caso contrario
#lo dejamos comentado.
def crear_tablas():
    crear_usuarios_query = """
    CREATE TABLE IF NOT EXISTS usuarios (
        id SERIAL PRIMARY KEY,
        nombre VARCHAR(50),
        apellido VARCHAR(50),
        correo VARCHAR(100),
        cedula VARCHAR(20),
        celular VARCHAR(15)
    );
    """

    crear_cuentas_query = """
    CREATE TABLE IF NOT EXISTS cuentas_ahorro (
        id SERIAL PRIMARY KEY,
        usuario_id INTEGER UNIQUE REFERENCES usuarios(id),
        saldo DECIMAL(10, 2) DEFAULT 0.0
    );
    """

    cursor.execute(crear_usuarios_query)
    cursor.execute(crear_cuentas_query)
    conexion.commit()
    
#Desarollamos una funcion para poder agregar nuevos usuarios a nuestra base de datos
#llenando los datos creados en nuestra tabla usuarios
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

    insertar_usuario_query = """
    INSERT INTO usuarios (nombre, apellido, correo, cedula, celular)
    VALUES (%s, %s, %s, %s, %s) RETURNING id;
    """
    cursor.execute(insertar_usuario_query, (nombre, apellido, correo, cedula, celular))
    usuario_id = cursor.fetchone()[0]
    conexion.commit()
    return usuario_id

def crear_cuenta_ahorro(usuario_id):
    try:
        crear_cuenta_query = """
        INSERT INTO cuentas_ahorro (usuario_id) VALUES (%s) RETURNING id;
        """
        cursor.execute(crear_cuenta_query, (usuario_id,))
        cuenta_id = cursor.fetchone()[0]
        conexion.commit()
        return cuenta_id
    except psycopg2.IntegrityError:
        # Si hay una violación de la restricción UNIQUE, significa que el usuario ya tiene una cuenta
        print("Este usuario ya tiene una cuenta de ahorro.")
        return None

#Creamos una funcion para poder realizar una sentecia sql a la base de datos
#en este casio una sentencias para obtener los usuarios de una bbdd.
def obtener_usuarios():
    obtener_usuarios_query = "SELECT * FROM usuarios;"
    cursor.execute(obtener_usuarios_query)
    usuarios = cursor.fetchall()
    return usuarios

#Creamos esta funcion para poder visualizar en consola que la conexion sea exitosa
#y la creacion, validacion de datos de un usuario sean correctos
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

#si algun elemento fue eliminado restabl3ecemos los id
def resetear_ids():
    resetear_ids_query = "TRUNCATE TABLE usuarios RESTART IDENTITY;"
    cursor.execute(resetear_ids_query)
    conexion.commit()

#creamos nuestro main donde ejecutaremos nuestras funciones realizadas
#como lo es la creacion de un usuario y visualizacion del mismo en la bbdd si la conexion es exitosa
if __name__ == "__main__":
    #Ingresamos un nuevo usuario por consola validando el mismo
    
    crear_tablas()
    
    datos_usuario = datos_usuario()
    nuevo_usuario_id = agregar_usuario(*datos_usuario)

    if nuevo_usuario_id:
        nuevo_cuenta_id = crear_cuenta_ahorro(nuevo_usuario_id)
        if nuevo_cuenta_id is not None:
            print(f"Nuevo usuario agregado con ID: {nuevo_usuario_id} y cuenta de ahorro creada con ID: {nuevo_cuenta_id}")


    #Imprimimos todo los usuarios ingresados en nuestra bbdd
    usuarios = obtener_usuarios()
    print("\nLista de Usuarios:")
    for usuario in usuarios:
        print(usuario)
    #llamamos la metodo para recetear los ids
    #resetear_ids()
    #Cerramos finalmente nuestra conexion para que sea segura
    cursor.close()
    conexion.close()