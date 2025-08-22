from config_bd import conectar


def crear_categoria(nombre):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("INSERT INTO categorias (nombre_categoria) VALUES (%s)", (nombre,))
    conexion.commit()
    conexion.close()


def obtener_categorias():
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT id, nombre_categoria FROM categorias")
    categorias = cursor.fetchall()
    print("DEBUG categorias:", categorias)  # 👈 Para ver en la consola
    conexion.close()
    return categorias




def obtener_categoria_por_id(categoria_id):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT id, nombre_categoria FROM categorias WHERE id = %s", (categoria_id,))
    categoria = cursor.fetchone()
    conexion.close()
    return categoria
