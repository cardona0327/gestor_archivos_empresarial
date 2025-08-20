from flask import Flask, render_template, request, redirect, url_for
from controllers.archivo_controlador import mostrar_inicio, mostrar_categoria
from models.categoria_modelo import crear_categoria as crear_categoria_bd, obtener_categorias
from models.archivo_modelo import guardar_archivo
from models.carpeta_modelo import crear_carpeta_bd
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'archivos'

# Subir archivo
@app.route('/categoria/<int:categoria_id>/subir-archivo', methods=['POST'])
def subir_archivo(categoria_id):
    archivo = request.files['archivo']
    descripcion = request.form.get('descripcion', '')

    if archivo:
        ruta_guardado = os.path.join(app.config['UPLOAD_FOLDER'], archivo.filename)
        archivo.save(ruta_guardado)
        guardar_archivo(categoria_id, archivo.filename, ruta_guardado, descripcion)
    return redirect(url_for('ver_categoria', categoria_id=categoria_id))

# Crear carpeta
@app.route("/crear_carpeta", methods=["POST"])
def crear_carpeta():
    categoria_id = request.form["categoria_id"]
    nombre_carpeta = request.form["nombre_carpeta"]
    carpeta_padre_id = request.form.get("carpeta_padre_id")

    # Convertir "" o "None" en None real de Python
    if not carpeta_padre_id or carpeta_padre_id == "None":
        carpeta_padre_id = None
    else:
        carpeta_padre_id = int(carpeta_padre_id)  # lo convertimos a entero

    crear_carpeta_bd(categoria_id, nombre_carpeta, carpeta_padre_id)
    return redirect(url_for("ver_categoria", categoria_id=categoria_id))


# Vista de inicio
@app.route('/')
def inicio():
    return mostrar_inicio()

# Vista detalle categoría (corregida)
@app.route("/categoria/<int:categoria_id>")
def ver_categoria(categoria_id):
    carpeta_padre_id = request.args.get("carpeta_id")
    return mostrar_categoria(categoria_id, carpeta_padre_id)

@app.route('/nueva-categoria', methods=['GET'])
def formulario_categoria():
    return render_template('crear_categoria.html')

@app.route('/crear-categoria', methods=['POST'])
def crear_categoria_ruta():
    nombre = request.form['nombre']
    crear_categoria_bd(nombre)
    return redirect(url_for('inicio'))



# Esto inyecta las categorías a TODAS las plantillas
@app.context_processor
def inject_categorias():
    categorias = obtener_categorias()
    return dict(categorias=categorias)

if __name__ == '__main__':
    app.run(debug=True)
