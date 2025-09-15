from flask import render_template
from models.categoria_modelo import obtener_categorias, obtener_categoria_por_id
from models.carpeta_modelo import obtener_carpetas_por_categoria, obtener_carpeta_por_id
from models.archivo_modelo import obtener_archivos_por_ubicacion

def mostrar_inicio():
    categorias = obtener_categorias()
    return render_template("home.html", categorias=categorias)

def mostrar_categoria(categoria_id, carpeta_id=None):
    categoria = obtener_categoria_por_id(categoria_id)
    carpetas  = obtener_carpetas_por_categoria(categoria_id, carpeta_id)
    archivos  = obtener_archivos_por_ubicacion(categoria_id, carpeta_id)
    carpeta_actual = obtener_carpeta_por_id(carpeta_id) if carpeta_id else None

    return render_template(
        "categoria_detalle.html",
        categoria=categoria,
        carpetas=carpetas,
        archivos=archivos,
        carpeta_padre_id=carpeta_id,   # para los formularios
        carpeta_actual=carpeta_actual  # para breadcrumb / volver
    )
