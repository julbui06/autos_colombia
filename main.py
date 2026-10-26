from fastapi import FastAPI
from servicios import ParqueaderoService

app = FastAPI(
    title="API Autos Colombia",
    description="Backend para la gestión de entrada y salida de vehículos en parqueadero",
    version="1.0"
)

@app.post("/ingreso")
def registrar_ingreso(placa: str, id_celda: int):
    return ParqueaderoService.registrar_ingreso(placa, id_celda)

@app.put("/salida/{id_registro}")
def registrar_salida(id_registro: int):
    return ParqueaderoService.registrar_salida(id_registro)