from fastapi import FastAPI
from pymongo import MongoClient
from bson.objectid import ObjectId
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Permitir el acceso desde cualquier frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Conexión a MongoDB
cliente = MongoClient("mongodb://localhost:27017/")
db = cliente["etl_resultados"]
coleccion = db["ejecuciones_etl"]

@app.get("/ejecuciones")
def listar_ejecuciones():
    ejecuciones = list(coleccion.find().sort("fecha_ejecucion", -1))
    for e in ejecuciones:
        e["_id"] = str(e["_id"])
    return ejecuciones

@app.get("/ejecuciones/{id}")
def obtener_ejecucion(id: str):
    ejecucion = coleccion.find_one({"_id": ObjectId(id)})
    if ejecucion:
        ejecucion["_id"] = str(ejecucion["_id"])
        return ejecucion
    return JSONResponse(status_code=404, content={"mensaje": "Ejecución no encontrada"})

@app.get("/estadisticas")
def estadisticas():
    total = coleccion.count_documents({})
    exitosas = coleccion.count_documents({"estado": "éxito"})
    fallidas = coleccion.count_documents({"estado": "fallo"})
    return {
        "total": total,
        "exitosas": exitosas,
        "fallidas": fallidas
    }