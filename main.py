"""
INTEGRANTES:
JOEL CORRALES
VADY MORA
JORDAN CABRERA
ALEXANDER PADILLA
ROMULO TORRES
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from repositorio import Repositorio
from servicio import Servicio

app = FastAPI()

repositorio = Repositorio()
servicio = Servicio(repositorio)

class UsuarioIn(BaseModel):
    nombre: str
    apellido: str
    correo: str
    cedula: str
    celular: str

class CreditoIn(BaseModel):
    monto: float
    plazo_meses: int
    tasa_interes: float

class TransaccionIn(BaseModel):
    monto: float

@app.post("/usuarios", response_model=dict)
async def registrar_usuario(usuario: UsuarioIn):
    """
    Registra un usuario.

    Examples:
        >>> registrar_usuario(UsuarioIn(nombre="John", apellido="Doe", correo="john@example.com", cedula="1234567890", celular="987654321"))
        {'usuario_id': 1}
    """
    usuario_id = servicio.registrar_usuario(usuario.nombre, usuario.apellido, usuario.correo, usuario.cedula, usuario.celular)
    return {"usuario_id": usuario_id}

@app.post("/creditos/{numero_cuenta}", response_model=dict)
async def solicitar_credito(numero_cuenta: str, credito: CreditoIn):
    """
    Solicita un crédito.

    Examples:
        >>> solicitar_credito("1234567890", CreditoIn(monto=1000.0, plazo_meses=12, tasa_interes=5.0))
        {'credito_id': 1}
    """
    try:
        usuario_id = repositorio.obtener_usuario_id_por_cuenta(numero_cuenta)
        credito_id = servicio.solicitar_credito(usuario_id, credito.monto, credito.plazo_meses, credito.tasa_interes)
        return {"credito_id": credito_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/creditos/{credito_id}/aprobar", response_model=dict)
async def aprobar_credito(credito_id: int):
    """
    Aprueba un crédito.

    Examples:
        >>> aprobar_credito(1)
        {'message': 'Crédito con ID 1 aprobado'}
    """
    servicio.aprobar_credito(credito_id)
    return {"message": f"Crédito con ID {credito_id} aprobado"}

@app.put("/creditos/{credito_id}/rechazar", response_model=dict)
async def rechazar_credito(credito_id: int):
    """
    Rechaza un crédito.

    Examples:
        >>> rechazar_credito(1)
        {'message': 'Crédito con ID 1 rechazado'}
    """
    servicio.rechazar_credito(credito_id)
    return {"message": f"Crédito con ID {credito_id} rechazado"}

@app.get("/creditos/{usuario_id}/reporte", response_class=HTMLResponse)
async def generar_reporte_creditos(usuario_id: int):
    """
    Genera un reporte de créditos.

    Examples:
        >>> generar_reporte_creditos(1)
        <HTMLResponse>
    """
    reporte = servicio.generar_reporte_creditos(usuario_id)
    return HTMLResponse(content=reporte)

@app.get("/creditos/{credito_id}/amortizacion", response_model=dict)
async def generar_tabla_amortizacion(credito_id: int):
    """
    Genera una tabla de amortización.

    Examples:
        >>> generar_tabla_amortizacion(1)
        {'message': 'Tabla de amortización generada y guardada.'}
    """
    servicio.generar_tabla_amortizacion(credito_id)
    return {"message": "Tabla de amortización generada y guardada."}

@app.post("/cuentas/{numero_cuenta}/deposito", response_model=dict)
async def realizar_deposito(numero_cuenta: str, transaccion: TransaccionIn):
    """
    Realiza un depósito en una cuenta.

    Examples:
        >>> realizar_deposito("1234567890", TransaccionIn(monto=500.0))
        {'message': 'Depósito de 500.0 realizado en la cuenta 1234567890'}
    """
    try:
        usuario_id = repositorio.obtener_usuario_id_por_cuenta(numero_cuenta)
        servicio.realizar_deposito(usuario_id, numero_cuenta, transaccion.monto)
        return {"message": f"Depósito de {transaccion.monto} realizado en la cuenta {numero_cuenta}"}
    except Exception as e:
        print(f"Error en la función realizar_deposito: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/cuentas/{numero_cuenta}/retiro", response_model=dict)
async def realizar_retiro(numero_cuenta: str, transaccion: TransaccionIn):
    """
    Realiza un retiro en una cuenta.

    Examples:
        >>> realizar_retiro("1234567890", TransaccionIn(monto=200.0))
        {'message': 'Retiro de 200.0 realizado en la cuenta 1234567890'}
    """
    try:
        usuario_id = repositorio.obtener_usuario_id_por_cuenta(numero_cuenta)
        servicio.realizar_retiro(usuario_id, numero_cuenta, transaccion.monto)
        return {"message": f"Retiro de {transaccion.monto} realizado en la cuenta {numero_cuenta}"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/usuarios", response_model=dict)
async def obtener_usuarios():
    """
    Obtiene la lista de usuarios.

    Examples:
        >>> obtener_usuarios()
        {'usuarios': []}
    """
    usuarios = repositorio.obtener_usuarios()
    return {"usuarios": usuarios}
