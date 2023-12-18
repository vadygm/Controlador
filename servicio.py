from modelo import Usuario, CuentaAhorros
from repositorio import Repositorio
import re

class Servicio:
    def __init__(self, repositorio):
        self.repositorio = repositorio

    def registrar_usuario(self, nombre, apellido, correo, cedula, celular):
        if not nombre or not apellido or not correo or not cedula or not celular:
            print("Por favor ingrese todos sus datos para el registro")
            return None

        if not re.match(r'^[0-9]{10}$', cedula):
            print("La cédula debe contener 10 dígitos numéricos")
            return None

        if not re.match(r'^[0-9]{10}$', celular):
            print("El número de celular debe contener 10 dígitos numéricos")
            return None

        usuario_id = self.repositorio.agregar_usuario(nombre, apellido, correo, cedula, celular)

        if usuario_id:
            print(f"Nuevo usuario agregado con ID: {usuario_id}")

            nueva_cuenta_id = self.repositorio.crear_cuenta_ahorros(usuario_id, saldo_inicial=20)

            if nueva_cuenta_id:
                print(f"Se ha creado una cuenta de ahorros con ID: {nueva_cuenta_id}")

    def realizar_deposito(self, numero_cuenta_destino, monto):
        try:
            cuenta_existente = self.repositorio.depositar_en_cuenta(numero_cuenta_destino, monto)

            if cuenta_existente:
                return {"message": "Depósito realizado exitosamente"}
            else:
                raise ValueError(f"No se encontró una cuenta para el número de cuenta {numero_cuenta_destino}")

        except Exception as e:
            print(f"Error al realizar el depósito: {e}")
            raise

    def realizar_retiro(self, numero_cuenta_origen, monto):
        self.repositorio.retirar_de_cuenta(numero_cuenta_origen, monto)

    def eliminar_cuenta_y_usuario(self, numero_cuenta):
        self.repositorio.eliminar_cuenta_y_usuario(numero_cuenta)


    def solicitar_credito(self, usuario_id, monto, plazo_meses, tasa_interes):
        credito_id = self.repositorio.solicitar_credito(usuario_id, monto, plazo_meses, tasa_interes)
        if credito_id:
            print(f"Crédito solicitado con ID: {credito_id}")
        return credito_id

    def aprobar_credito(self, credito_id):
        self.repositorio.aprobar_credito(credito_id)
        print(f"Crédito con ID {credito_id} aprobado")

    def rechazar_credito(self, credito_id):
        self.repositorio.rechazar_credito(credito_id)
        print(f"Crédito con ID {credito_id} rechazado")

    def generar_reporte_creditos(self, usuario_id):
        creditos_usuario = self.repositorio.obtener_creditos_usuario(usuario_id)

        if creditos_usuario:
            print(f"Reporte de créditos para el usuario con ID {usuario_id}:")
            for credito in creditos_usuario:
                print(credito)
        else:
            print(f"No hay créditos para el usuario con ID {usuario_id}")

    def generar_tabla_amortizacion(self, credito_id):
        self.repositorio.generar_tabla_amortizacion(credito_id)

    def obtener_usuarios(self):
        return self.repositorio.obtener_usuarios()