from flask import render_template
from models.categoria_modelo import obtener_categorias, obtener_categoria_por_id
from models.carpeta_modelo import obtener_carpetas_por_categoria
from models.archivo_modelo import obtener_archivos_por_categoria
from models.categoria_modelo import obtener_categoria_por_id

def mostrar_inicio():
    categorias = obtener_categorias()
    return render_template("home.html", categorias=categorias)





def mostrar_categoria(categoria_id, carpeta_padre_id=None):
    categoria = obtener_categoria_por_id(categoria_id)
    carpetas = obtener_carpetas_por_categoria(categoria_id, carpeta_padre_id)
    archivos = obtener_archivos_por_categoria(carpeta_padre_id)

    return render_template(
        "categoria_detalle.html",
        categoria=categoria,
        carpetas=carpetas,
        archivos=archivos,
        carpeta_padre_id=carpeta_padre_id
    )
