# INTEGRANTES:
# JOEL CORRALES
# VADY MORA
# JORDAN CABRERA
# ALEXANDER PADILLA
# ROMULO TORRES

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from repositorio import Repositorio
from servicio import Servicio
from fastapi import Path

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


from pydantic import BaseModel

class TransaccionIn(BaseModel):
    monto: float

@app.post("/usuarios", response_model=dict)
async def registrar_usuario(usuario: UsuarioIn):
    usuario_id = servicio.registrar_usuario(usuario.nombre, usuario.apellido, usuario.correo, usuario.cedula, usuario.celular)
    return {"usuario_id": usuario_id}

@app.post("/creditos/{numero_cuenta}", response_model=dict)
async def solicitar_credito(numero_cuenta: str, credito: CreditoIn):
    try:
        usuario_id = repositorio.obtener_usuario_id_por_cuenta(numero_cuenta)
        credito_id = servicio.solicitar_credito(usuario_id, credito.monto, credito.plazo_meses, credito.tasa_interes)
        return {"credito_id": credito_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/creditos/{credito_id}/aprobar", response_model=dict)
async def aprobar_credito(credito_id: int):
    servicio.aprobar_credito(credito_id)
    return {"message": f"Crédito con ID {credito_id} aprobado"}

@app.put("/creditos/{credito_id}/rechazar", response_model=dict)
async def rechazar_credito(credito_id: int):
    servicio.rechazar_credito(credito_id)
    return {"message": f"Crédito con ID {credito_id} rechazado"}

@app.get("/creditos/{usuario_id}/reporte", response_class=HTMLResponse)
async def generar_reporte_creditos(usuario_id: int):
    reporte = servicio.generar_reporte_creditos(usuario_id)
    return HTMLResponse(content=reporte)

@app.get("/creditos/{credito_id}/amortizacion", response_model=dict)
async def generar_tabla_amortizacion(credito_id: int):
    servicio.generar_tabla_amortizacion(credito_id)
    return {"message": "Tabla de amortización generada y guardada."}


@app.post("/cuentas/{numero_cuenta}/deposito", response_model=dict)
async def realizar_deposito(numero_cuenta: str, transaccion: TransaccionIn):
    try:
        usuario_id = repositorio.obtener_usuario_id_por_cuenta(numero_cuenta)
        servicio.realizar_deposito(usuario_id, numero_cuenta, transaccion.monto)
        return {"message": f"Depósito de {transaccion.monto} realizado en la cuenta {numero_cuenta}"}
    except Exception as e:
        print(f"Error en la función realizar_deposito: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/cuentas/{numero_cuenta}/retiro", response_model=dict)
async def realizar_retiro(numero_cuenta: str, transaccion: TransaccionIn):
    try:
        usuario_id = repositorio.obtener_usuario_id_por_cuenta(numero_cuenta)
        servicio.realizar_retiro(usuario_id, numero_cuenta, transaccion.monto)
        return {"message": f"Retiro de {transaccion.monto} realizado en la cuenta {numero_cuenta}"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
@app.get("/usuarios", response_model=dict)
async def obtener_usuarios():
    usuarios = repositorio.obtener_usuarios()
    return {"usuarios": usuarios}
