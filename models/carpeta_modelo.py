from config_bd import conectar

def crear_carpeta_bd(id_categoria, nombre_carpeta, carpeta_padre_id=None):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("""
        INSERT INTO carpetas (id_categoria, nombre_carpeta, carpeta_padre_id)
        VALUES (%s, %s, %s)
    """, (id_categoria, nombre_carpeta, carpeta_padre_id))
    conexion.commit()
    conexion.close()


def obtener_carpetas_por_categoria(id_categoria, carpeta_padre_id=None):
    conexion = conectar()
    cursor = conexion.cursor()
    if carpeta_padre_id is None:
        cursor.execute("""
            SELECT id, nombre_carpeta, fecha_creacion
            FROM carpetas
            WHERE id_categoria = %s AND carpeta_padre_id IS NULL
            ORDER BY nombre_carpeta
        """, (id_categoria,))
    else:
        cursor.execute("""
            SELECT id, nombre_carpeta, fecha_creacion
            FROM carpetas
            WHERE id_categoria = %s AND carpeta_padre_id = %s
            ORDER BY nombre_carpeta
        """, (id_categoria, carpeta_padre_id))

    filas = cursor.fetchall()
    conexion.close()
    return filas


def obtener_carpeta_por_id(carpeta_id):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT id, id_categoria, nombre_carpeta, carpeta_padre_id, fecha_creacion
        FROM carpetas
        WHERE id = %s
    """, (carpeta_id,))
    fila = cursor.fetchone()
    conexion.close()
    return fila  # ya es un dict

def obtener_subcarpetas(id_categoria, carpeta_padre_id=None):
    conexion = conectar()
    cursor = conexion.cursor()

    if carpeta_padre_id is None:
        cursor.execute("""
            SELECT id, id_categoria, nombre_carpeta, carpeta_padre_id, fecha_creacion
            FROM carpetas
            WHERE id_categoria = %s AND carpeta_padre_id IS NULL
        """, (id_categoria,))
    else:
        cursor.execute("""
            SELECT id, id_categoria, nombre_carpeta, carpeta_padre_id, fecha_creacion
            FROM carpetas
            WHERE id_categoria = %s AND carpeta_padre_id = %s
        """, (id_categoria, carpeta_padre_id))

    resultados = cursor.fetchall()  # 👈 ya devuelve lista de diccionarios
    conexion.close()

    print("[DEBUG SUBCARPETAS]", resultados)
    return resultados