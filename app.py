from flask import Flask, render_template, request, redirect, url_for, send_file
from controllers.archivo_controlador import mostrar_inicio, mostrar_categoria
from models.categoria_modelo import crear_categoria as crear_categoria_bd, obtener_categorias
from models.archivo_modelo import guardar_archivo, obtener_archivo_por_id, actualizar_archivo, obtener_archivos_por_ubicacion, buscar_archivos, contar_archivos_por_categoria
from models.carpeta_modelo import crear_carpeta_bd, obtener_subcarpetas, obtener_carpeta_por_id, buscar_carpetas, contar_carpetas_por_categoria
import io, zipfile, os



from models.archivo_modelo import contar_archivos_por_categoria, contar_archivos_por_mes
from models.carpeta_modelo import contar_carpetas_por_categoria, contar_carpetas_por_mes
from models.categoria_modelo import obtener_categorias
from models.categoria_modelo import (
    crear_categoria as crear_categoria_bd,
    obtener_categorias,
    actualizar_categoria,
    eliminar_categoria
)

app = Flask(__name__)
# Carpeta física donde guardas los archivos (ruta absoluta)
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), "archivos")  # p. ej. C:/ruta/proyecto/archivos
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


# -------------------------
# Subir archivo (guarda en estructura: archivos/<categoria>/<carpeta?>/nombre)
# -------------------------
@app.route('/categoria/<int:categoria_id>/subir-archivo', methods=['POST'])
def subir_archivo(categoria_id):
    archivo = request.files.get('archivo')
    descripcion = request.form.get('descripcion', '')
    carpeta_id = request.form.get('carpeta_id')
    carpeta_id = int(carpeta_id) if carpeta_id not in (None, "", "None") else None

    if archivo and archivo.filename.strip():
        # organizar carpeta física por categoría y por carpeta (si aplica)
        carpeta_destino = os.path.join(app.config['UPLOAD_FOLDER'], str(categoria_id))
        if carpeta_id:
            carpeta_destino = os.path.join(carpeta_destino, str(carpeta_id))

        os.makedirs(carpeta_destino, exist_ok=True)

        # guardar archivo en disco
        ruta_guardado = os.path.join(carpeta_destino, archivo.filename)
        archivo.save(ruta_guardado)

        # guardamos en BD la ruta relativa con estructura: archivos/<categoria>/<carpeta?>/nombre
        if carpeta_id:
            ruta_relativa = f"archivos/{categoria_id}/{carpeta_id}/{archivo.filename}"
        else:
            ruta_relativa = f"archivos/{categoria_id}/{archivo.filename}"

        guardar_archivo(categoria_id, carpeta_id, archivo.filename, ruta_relativa, descripcion)

    if carpeta_id is None:
        return redirect(url_for('ver_categoria', categoria_id=categoria_id))
    else:
        return redirect(url_for('ver_categoria', categoria_id=categoria_id, carpeta_id=carpeta_id))


# -------------------------
# Crear carpeta en BD
# -------------------------
@app.route("/crear_carpeta", methods=["POST"])
def crear_carpeta():
    categoria_id = int(request.form["categoria_id"])
    nombre_carpeta = request.form["nombre_carpeta"]
    carpeta_padre_id = request.form.get("carpeta_padre_id")
    carpeta_padre_id = int(carpeta_padre_id) if carpeta_padre_id not in (None, "", "None") else None

    crear_carpeta_bd(categoria_id, nombre_carpeta, carpeta_padre_id)

    if carpeta_padre_id is None:
        return redirect(url_for("ver_categoria", categoria_id=categoria_id))
    else:
        return redirect(url_for("ver_categoria", categoria_id=categoria_id, carpeta_id=carpeta_padre_id))


# -------------------------
# Rutas básicas y plantillas
# -------------------------
@app.route('/')
def inicio():
    return mostrar_inicio()

@app.route("/categoria/<int:categoria_id>")
def ver_categoria(categoria_id):
    carpeta_id = request.args.get("carpeta_id", default=None, type=int)
    return mostrar_categoria(categoria_id, carpeta_id)

@app.route('/nueva-categoria', methods=['GET'])
def formulario_categoria():
    return render_template('crear_categoria.html')

@app.route('/crear-categoria', methods=['POST'])
def crear_categoria_ruta():
    nombre = request.form['nombre']
    crear_categoria_bd(nombre)
    return redirect(url_for('inicio'))


# -------------------------
# Descargar archivo individual
# -------------------------
@app.route('/download/<int:archivo_id>')
def descargar_archivo(archivo_id):
    archivo = obtener_archivo_por_id(archivo_id)
    if not archivo:
        return f"No se encontró archivo con id={archivo_id}", 404

    nombre = archivo.get('nombre_original')
    ruta_relativa = archivo.get('ruta_archivo')

    if not ruta_relativa:
        return "Error: no hay ruta en la base de datos", 500

    # Resolver ruta absoluta partiendo de UPLOAD_FOLDER
    # ruta_relativa en BD = "archivos/<categoria>/<...>"
    rel = ruta_relativa.replace("\\", "/")
    if rel.startswith("archivos/"):
        rel = rel[len("archivos/"):]
    ruta_absoluta = os.path.join(app.config['UPLOAD_FOLDER'], rel)

    if not os.path.exists(ruta_absoluta):
        return f"El archivo físico no existe en: {ruta_absoluta}", 404

    return send_file(ruta_absoluta, as_attachment=True, download_name=nombre)


# -------------------------
# Editar archivo (si subes nuevo archivo, lo guarda en estructura por categoria)
# -------------------------
@app.route("/archivo/<int:archivo_id>/editar", methods=["GET", "POST"])
def editar_archivo(archivo_id):
    archivo = obtener_archivo_por_id(archivo_id)
    if not archivo:
        return "Archivo no encontrado", 404

    if request.method == "POST":
        nueva_descripcion = request.form.get("descripcion", archivo.get("descripcion",""))

        # Ver si subió un nuevo archivo
        nuevo_archivo = request.files.get("archivo")
        nuevo_nombre = archivo["nombre_original"]
        nueva_ruta = archivo["ruta_archivo"]

        if nuevo_archivo and nuevo_archivo.filename.strip():
            # Guardar el nuevo archivo en la misma categoría y carpeta donde estaba el archivo original
            # Extraer categoria y carpeta del registro actual
            id_categoria = archivo.get("id_categoria")
            carpeta_id = archivo.get("carpeta_id")

            carpeta_destino = os.path.join(app.config['UPLOAD_FOLDER'], str(id_categoria))
            if carpeta_id:
                carpeta_destino = os.path.join(carpeta_destino, str(carpeta_id))
            os.makedirs(carpeta_destino, exist_ok=True)

            ruta_guardado = os.path.join(carpeta_destino, nuevo_archivo.filename)
            nuevo_archivo.save(ruta_guardado)

            nuevo_nombre = nuevo_archivo.filename
            if carpeta_id:
                nueva_ruta = f"archivos/{id_categoria}/{carpeta_id}/{nuevo_archivo.filename}"
            else:
                nueva_ruta = f"archivos/{id_categoria}/{nuevo_archivo.filename}"

        # Actualizamos en BD
        actualizar_archivo(
            archivo_id,
            nuevo_nombre=nuevo_nombre,
            nueva_ruta=nueva_ruta,
            nueva_descripcion=nueva_descripcion
        )

        return redirect(url_for("ver_categoria", categoria_id=archivo["id_categoria"]))

    return render_template("editar_archivo.html", archivo=archivo)


# -------------------------
# Construcción recursiva del ZIP 
# -------------------------
def agregar_archivos_recursivos(zipf, id_categoria, carpeta_id=None, ruta_relativa_zip=""):
    # Obtener subcarpetas reales de la BD
    filas = obtener_subcarpetas(id_categoria, carpeta_id)
    print("[DEBUG SUBCARPETAS]", filas)

    for fila in filas:
        try:
            carpeta_nombre = fila["nombre_carpeta"]
            carpeta_id_actual = fila["id"]
        except Exception as e:
            print("[ERROR] fila malformada:", fila, e)
            continue

        # Crear directorio dentro del ZIP
        nueva_ruta_zip = os.path.join(ruta_relativa_zip, carpeta_nombre) + "/"
        print(f"[ZIP] Creando carpeta en zip: '{nueva_ruta_zip}' (id={carpeta_id_actual})")
        zipf.writestr(nueva_ruta_zip, "")

        # Obtener archivos de esta carpeta
        archivos = obtener_archivos_por_ubicacion(id_categoria, carpeta_id_actual)
        for archivo in archivos:
            archivo_nombre = archivo["nombre_original"]
            ruta_rel_bd = archivo["ruta_archivo"].replace("\\", "/")

            if ruta_rel_bd.startswith("archivos/"):
                rel = ruta_rel_bd[len("archivos/"):]
            else:
                rel = ruta_rel_bd

            ruta_fisica = os.path.join(app.config['UPLOAD_FOLDER'], rel)
            ruta_en_zip = os.path.join(nueva_ruta_zip, archivo_nombre)

            print(f"[ZIP] Añadiendo archivo: físico='{ruta_fisica}' -> zip='{ruta_en_zip}'")
            if os.path.exists(ruta_fisica):
                zipf.write(ruta_fisica, ruta_en_zip)
            else:
                print(f"[WARN] Archivo no encontrado: {ruta_fisica}")

        # Recursión para procesar subcarpetas
        agregar_archivos_recursivos(zipf, id_categoria, carpeta_id_actual, nueva_ruta_zip)
# -------------------------
# Endpoint para descargar carpeta (zip)
# -------------------------

@app.route("/download/carpeta/<int:categoria_id>")
def descargar_carpeta(categoria_id):
    carpeta_id = request.args.get("carpeta_id", default=None, type=int)

    mem_zip = io.BytesIO()
    with zipfile.ZipFile(mem_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        if carpeta_id:
            carpeta = obtener_carpeta_por_id(carpeta_id)
            nombre_carpeta = carpeta["nombre_carpeta"] if carpeta and carpeta.get("nombre_carpeta") else f"carpeta_{carpeta_id}"

            # Crear entrada raíz con nombre de carpeta seleccionada
            zf.writestr(f"{nombre_carpeta}/", "")

            # 👉 Archivos dentro de esta carpeta
            archivos = obtener_archivos_por_ubicacion(categoria_id, carpeta_id)
            for archivo in archivos:
                ruta_archivo = archivo["ruta_archivo"]
                if os.path.exists(ruta_archivo):
                    zf.write(ruta_archivo, f"{nombre_carpeta}/{archivo['nombre_original']}")

            # 👉 Subcarpetas y sus archivos
            agregar_archivos_recursivos(zf, categoria_id, carpeta_id, ruta_relativa_zip=nombre_carpeta)

        else:
            raiz_nombre = f"categoria_{categoria_id}_raiz"
            zf.writestr(f"{raiz_nombre}/", "")

            # 👉 Archivos que están en la raíz de la categoría (sin carpeta_id)
            archivos_sueltos = obtener_archivos_por_ubicacion(categoria_id, carpeta_id=None)
            for archivo in archivos_sueltos:
                ruta_archivo = archivo["ruta_archivo"]
                if os.path.exists(ruta_archivo):
                    zf.write(ruta_archivo, f"{raiz_nombre}/{archivo['nombre_original']}")

            # 👉 Carpetas con sus archivos
            agregar_archivos_recursivos(zf, categoria_id, None, ruta_relativa_zip=raiz_nombre)

    mem_zip.seek(0)
    nombre_zip = f"carpeta_{carpeta_id or 'raiz'}_categoria_{categoria_id}.zip"
    return send_file(mem_zip, as_attachment=True, download_name=nombre_zip, mimetype="application/zip")






@app.route("/buscar", methods=["GET", "POST"])
def buscar():
    # Si es GET mostramos el formulario vacío
    if request.method == "GET":
        return render_template(
            "buscar.html",
            resultados_archivos=[],
            resultados_carpetas=[],
            filtros={}
        )

    # POST -> procesamos filtros
    nombre = request.form.get("q_nombre") or None
    descripcion = request.form.get("q_descripcion") or None
    fecha_desde = request.form.get("q_fecha_desde") or None
    fecha_hasta = request.form.get("q_fecha_hasta") or None

    # checkboxes para decidir si buscamos archivos/carpetas
    buscar_en_archivos = bool(request.form.get("filtrar_archivos"))
    buscar_en_carpetas = bool(request.form.get("filtrar_carpetas"))

    # 👇 ajuste: si no se marcó ninguno, activamos ambos por defecto
    if not buscar_en_archivos and not buscar_en_carpetas:
        buscar_en_archivos = True
        buscar_en_carpetas = True

    categoria_id = request.form.get("q_categoria")
    categoria_id = int(categoria_id) if categoria_id not in (None, "", "None") else None

    carpeta_id_raw = request.form.get("q_carpeta")
    # opcional: filtrar por carpeta específica
    if carpeta_id_raw in (None, "", "None"):
        carpeta_filter = "__ANY__"  # no limitamos por carpeta
    elif carpeta_id_raw == "NULL":
        carpeta_filter = None  # solo archivos en raíz
    else:
        carpeta_filter = int(carpeta_id_raw)

    resultados_archivos = []
    resultados_carpetas = []

    if buscar_en_archivos:
        resultados_archivos = buscar_archivos(
            nombre=nombre,
            descripcion=descripcion,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            categoria_id=categoria_id,
            carpeta_id=carpeta_filter
        )

    if buscar_en_carpetas:
        resultados_carpetas = buscar_carpetas(
            nombre=nombre,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            categoria_id=categoria_id
        )

    filtros = {
        "nombre": nombre,
        "descripcion": descripcion,
        "fecha_desde": fecha_desde,
        "fecha_hasta": fecha_hasta,
        "buscar_en_archivos": buscar_en_archivos,
        "buscar_en_carpetas": buscar_en_carpetas,
        "categoria_id": categoria_id,
        "carpeta_filter": carpeta_filter,
    }

    return render_template(
        "buscar.html",
        resultados_archivos=resultados_archivos,
        resultados_carpetas=resultados_carpetas,
        filtros=filtros
    )



@app.route("/estadisticas")
def estadisticas():
    datos_carpetas = contar_carpetas_por_categoria()  # devuelve lista
    datos_archivos  = contar_archivos_por_categoria() # devuelve lista
    return render_template("estadisticas.html",
    datos_carpetas=contar_carpetas_por_categoria(),
    datos_archivos=contar_archivos_por_categoria(),
    evol_carpetas=contar_carpetas_por_mes(),
    evol_archivos=contar_archivos_por_mes(),
    total_categorias=len(obtener_categorias()),
    total_carpetas=sum([c["total_carpetas"] for c in contar_carpetas_por_categoria()]),
    total_archivos=sum([a["total_archivos"] for a in contar_archivos_por_categoria()])
)




# ---- Editar categoría ----
@app.route("/categoria/<int:categoria_id>/editar", methods=["GET", "POST"])
def editar_categoria(categoria_id):
    from models.categoria_modelo import obtener_categoria_por_id
    categoria = obtener_categoria_por_id(categoria_id)
    if not categoria:
        return "Categoría no encontrada", 404

    if request.method == "POST":
        nuevo_nombre = request.form.get("nombre_categoria")
        if nuevo_nombre:
            actualizar_categoria(categoria_id, nuevo_nombre)
        return redirect(url_for("inicio"))

    return render_template("editar_categoria.html", categoria=categoria)


# ---- Eliminar categoría ----
@app.route("/categoria/<int:categoria_id>/eliminar", methods=["POST"])
def eliminar_categoria_ruta(categoria_id):
    eliminar_categoria(categoria_id)
    return redirect(url_for("inicio"))



# -------------------------
# Inyectar categorias en templates
# -------------------------
@app.context_processor
def inject_categorias():
    categorias = obtener_categorias()
    return dict(categorias=categorias)


if __name__ == '__main__':
    app.run(debug=True)
