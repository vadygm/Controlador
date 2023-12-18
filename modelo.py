class Usuario:
    def __init__(self, id, nombre, apellido, correo, cedula, celular):
        self.id = id
        self.nombre = nombre
        self.apellido = apellido
        self.correo = correo
        self.cedula = cedula
        self.celular = celular

class CuentaAhorros:
    def __init__(self, id, usuario, numero_cuenta, saldo):
        self.id = id
        self.usuario = usuario
        self.numero_cuenta = numero_cuenta
        self.saldo = saldo
