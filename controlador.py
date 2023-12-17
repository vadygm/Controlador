#installamos el paquete psycopg2 para poder realizar conexion a nuestra base de datos en potsgres
import psycopg2
from psycopg2 import sql

#Agregamos la conexion a nuestra base de datos de potsgres
conexion = psycopg2.connect(
    database="usuario",
    user="postgres",
    password="12345",
    host="localhost",
    port="5432"
)
#para poder agregar sentencias SQL en nuestro codigo de pyhton agregamos un cursos el cual 
#permite realizar sentencias SQL
cursor = conexion.cursor()

#Creamos nuestro usuario si en nuestro potsgres aun no lo hemos realizado caso contrario
#lo dejamos comentado.
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

#Desarollamos una funcion para poder agregar nuevos usuarios a nuestra base de datos
#llenando los datos creados en nuestra tabla usuarios
def agregar_usuario(nombre, apellido, correo, cedula, celular):
    #Validamos que los campos esten llenos caso contrario no se ingresaran los datos
    if not nombre or not apellido or not correo or not cedula or not celular:
        print("Por favor ingrese todos sus datos para el registro")
        return None

    insertar_usuario_query = """
    INSERT INTO usuarios (nombre, apellido, correo, cedula, celular)
    VALUES (%s, %s, %s, %s, %s) RETURNING id;
    """
    cursor.execute(insertar_usuario_query, (nombre, apellido, correo, cedula, celular))
    usuario_id = cursor.fetchone()[0]
    conexion.commit()
    return usuario_id

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
        cedula = input("Ingrese la cédula: ")
        celular = input("Ingrese el número de celular: ")
        #Aqui tambien validamos los campos se encuentren llenos
        if nombre and apellido and correo and cedula and celular:
            return nombre, apellido, correo, cedula, celular
        else:
            print("Por favor ingrese todos sus datos para el registro")

#creamos nuestro main donde ejecutaremos nuestras funciones realizadas
#como lo es la creacion de un usuario y visualizacion del mismo en la bbdd si la conexion es exitosa
if __name__ == "__main__":
    #Ingresamos un nuevo usuario por consola validando el mismo
    datos_usuario = datos_usuario()
    nuevo_usuario_id = agregar_usuario(*datos_usuario)

    if nuevo_usuario_id:
        #Traemos el Id de creacion del usuario
        print(f"Nuevo usuario agregado con ID: {nuevo_usuario_id}")

    #Imprimimos todo los usuarios ingresados en nuestra bbdd
    usuarios = obtener_usuarios()
    print("\nLista de Usuarios:")
    for usuario in usuarios:
        print(usuario)

    #Cerramos finalmente nuestra conexion para que sea segura
    cursor.close()
    conexion.close()
