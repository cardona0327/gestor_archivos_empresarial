from config_bd import conectar

def guardar_archivo(id_categoria, carpeta_id, nombre_original, ruta_archivo, descripcion):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("""
        INSERT INTO archivos (id_categoria, carpeta_id, nombre_original, ruta_archivo, descripcion)
        VALUES (%s, %s, %s, %s, %s)
    """, (id_categoria, carpeta_id, nombre_original, ruta_archivo, descripcion))
    conexion.commit()
    conexion.close()

def obtener_archivos_por_ubicacion(id_categoria, carpeta_id=None):
    conexion = conectar()
    cursor = conexion.cursor()
    if carpeta_id is None:
        cursor.execute("""
            SELECT id, nombre_original, fecha_subida
            FROM archivos
            WHERE id_categoria = %s AND carpeta_id IS NULL
            ORDER BY fecha_subida DESC
        """, (id_categoria,))
    else:
        cursor.execute("""
            SELECT id, nombre_original, fecha_subida
            FROM archivos
            WHERE id_categoria = %s AND carpeta_id = %s
            ORDER BY fecha_subida DESC
        """, (id_categoria, carpeta_id))
    archivos = cursor.fetchall()
    conexion.close()
    return archivos

# (para no romper imports antiguos, si los tienes)
def obtener_archivos_por_categoria(id_categoria, carpeta_padre_id=None):
    return obtener_archivos_por_ubicacion(id_categoria, carpeta_padre_id)
