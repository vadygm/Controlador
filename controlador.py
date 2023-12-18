from repositorio import Repositorio
from servicio import Servicio
import re
import random


class Controlador:
    def __init__(self):
        self.repositorio = Repositorio()
        self.servicio = Servicio(self.repositorio)

    def registrar_usuario_desde_consola(self):
        nombre = input("Ingrese el nombre: ")
        apellido = input("Ingrese el apellido: ")
        correo = input("Ingrese el correo electrónico: ")
        cedula = input("Ingrese la cédula (10 dígitos numéricos): ")
        celular = input("Ingrese el número de celular (10 dígitos numéricos): ")

        self.servicio.registrar_usuario(nombre, apellido, correo, cedula, celular)

    def realizar_deposito_desde_consola(self):
        numero_cuenta_destino = input("Ingrese el número de cuenta de destino: ")
        monto = float(input("Ingrese el monto a depositar: "))

        self.servicio.realizar_deposito(numero_cuenta_destino, monto)

    def realizar_retiro_desde_consola(self):
        numero_cuenta_origen = input("Ingrese el número de cuenta de origen: ")
        monto = float(input("Ingrese el monto a retirar: "))

        self.servicio.realizar_retiro(numero_cuenta_origen, monto)

    def eliminar_cuenta_y_usuario_desde_consola(self):
        numero_cuenta = input("Ingrese el número de cuenta a eliminar: ")

        self.servicio.eliminar_cuenta_y_usuario(numero_cuenta)

    def solicitar_credito_desde_consola(self):
        numero_cuenta = input("Ingrese el número de cuenta del usuario: ")
        monto = float(input("Ingrese el monto del crédito: "))
        plazo_meses = int(input("Ingrese el plazo del crédito en meses: "))
        tasa_interes = float(input("Ingrese la tasa de interés del crédito (porcentaje): "))

        credito_id = self.servicio.solicitar_credito(numero_cuenta, monto, plazo_meses, tasa_interes)
        print(f"Crédito solicitado con ID: {credito_id}")

    def aprobar_credito_desde_consola(self):
        numero_cuenta = input("Ingrese el número de cuenta del crédito a aprobar: ")
        self.servicio.aprobar_credito(numero_cuenta)
        print(f"Crédito para la cuenta {numero_cuenta} aprobado")

    def rechazar_credito_desde_consola(self):
        numero_cuenta = input("Ingrese el número de cuenta del crédito a rechazar: ")
        self.servicio.rechazar_credito(numero_cuenta)
        print(f"Crédito para la cuenta {numero_cuenta} rechazado")

    def generar_tabla_amortizacion_desde_consola(self):
        numero_cuenta = input("Ingrese el número de cuenta del crédito para generar la tabla de amortización: ")
        self.servicio.generar_tabla_amortizacion(numero_cuenta)
    def generar_reporte_creditos_desde_consola(self):
        numero_cuenta = input("Ingrese el número de cuenta del usuario para generar el reporte: ")
        self.servicio.generar_reporte_creditos(numero_cuenta)


    def obtener_usuarios_desde_consola(self):
        usuarios = self.repositorio.obtener_usuarios()
        if usuarios:
            print("Lista de Usuarios:")
            for usuario in usuarios:
                print(usuario)
        else:
            print("No hay usuarios registrados.")




if __name__ == "__main__":
    controlador = Controlador()
    #DESCOMENTAR PARA REALIZAR LAS RESPECTIVAS FUNCIONES
    
    #controlador.registrar_usuario_desde_consola()
    #controlador.realizar_deposito_desde_consola()
    #controlador.eliminar_cuenta_y_usuario_desde_consola()
    #controlador.realizar_deposito_desde_consola()
    #controlador.realizar_retiro_desde_consola()
    controlador.solicitar_credito_desde_consola()
    controlador.generar_reporte_creditos_desde_consola()

    # Cerrar la conexión al finalizar
    controlador.repositorio.cerrar_conexion()
