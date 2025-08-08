# API Compresor de imagenes
# Fecha: Agosto 8, 2025
# Especs: Python 3.10.11 (3.10) - instalar dependencias con 'pip install -r requirements.txt' - probar en localhost:8000/img-compressor
# Autor: Francisco Pineda

# Librerias necesarias
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from PIL import Image 
import os 
import io 
import uuid # Genera un codigo único para el guardado de imagen, puede sustituirse por el algoritmo que usa SICAM

app = FastAPI()

FORMATOS_SOPORTADOS = ("image/jpeg", "image/jpg", "image/png")
FOLDER_SALIDA = "imagenes_comprimidas"
os.makedirs(FOLDER_SALIDA, exist_ok=True)

# Especifica la calidad de la imagen comprimida (100 -> sin compresión, 0 -> máxima compresión)
CALIDAD=50

def comprimir_imagen(imagen_archivo, nombre_archivo, formato):
    imagen = Image.open(imagen_archivo)
    imagen_formato = "JPEG" if formato in ["image/jpeg", "image/jpg"] else "PNG"
    
    output_io = io.BytesIO()
    imagen.save(output_io, format=imagen_formato, optimize=True, quality=CALIDAD if imagen_formato == "JPEG" else None)
    output_io.seek(0)
    
    ruta_output = os.path.join(FOLDER_SALIDA, nombre_archivo)
    with open(ruta_output, "wb") as f:
        f.write(output_io.read())
    
    return ruta_output


@app.post("/img-compressor")
async def compresor(archivo: UploadFile = File(...)):
    if archivo.content_type not in FORMATOS_SOPORTADOS:
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "data": None,
                "message": "Los formatos soportados son: [.jpg, .jpeg, .png]"
            }
        )

    try:
        nombre_unico = f"{uuid.uuid4().hex}_{archivo.filename}"
        ruta_archivo_comprimido = comprimir_imagen(archivo.file, nombre_unico, archivo.content_type)
        return FileResponse(
            ruta_archivo_comprimido,
            media_type=archivo.content_type,
            filename=f"compressed_{archivo.filename}",
            headers={
                "X-Success": "true",
                "X-Message": "Imagen comprimida con exito :)"
            }
        )
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "data": None,
                "message": f"Compression failed: {str(e)}"
            }
        )