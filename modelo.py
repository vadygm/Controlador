"""
INTEGRANTES:
JOEL CORRALES
VADY MORA
JORDAN CABRERA
ALEXANDER PADILLA
ROMULO TORRES
"""

class Usuario:
    """
    Clase que representa a un usuario.

    Examples:
        >>> usuario = Usuario(id=1, nombre="John", apellido="Doe", correo="john@example.com", cedula="1234567890", celular="987654321")
        >>> usuario.id
        1
        >>> usuario.nombre
        'John'
        >>> usuario.correo
        'john@example.com'
    """
    def __init__(self, id, nombre, apellido, correo, cedula, celular):
        self.id = id
        self.nombre = nombre
        self.apellido = apellido
        self.correo = correo
        self.cedula = cedula
        self.celular = celular

class CuentaAhorros:
    """
    Clase que representa una cuenta de ahorros.

    Examples:
        >>> usuario = Usuario(id=1, nombre="John", apellido="Doe", correo="john@example.com", cedula="1234567890", celular="987654321")
        >>> cuenta = CuentaAhorros(id=1, usuario=usuario, numero_cuenta="1234567890", saldo=1000.0)
        >>> cuenta.id
        1
        >>> cuenta.numero_cuenta
        '1234567890'
        >>> cuenta.saldo
        1000.0
    """
    def __init__(self, id, usuario, numero_cuenta, saldo):
        self.id = id
        self.usuario = usuario
        self.numero_cuenta = numero_cuenta
        self.saldo = saldo

# Ejecuta los doctests
if __name__ == "__main__":
    import doctest
    doctest.testmod()
