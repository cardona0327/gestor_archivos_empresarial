from config_bd import conectar


def guardar_archivo(id_categoria, nombre_original, ruta_archivo, descripcion):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("""
        INSERT INTO archivos (id_categoria, nombre_original, ruta_archivo, descripcion)
        VALUES (%s, %s, %s, %s)
    """, (id_categoria, nombre_original, ruta_archivo, descripcion))
    conexion.commit()
    conexion.close()

def obtener_archivos_por_categoria(categoria_id, carpeta_padre_id=None):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT id, nombre_original, fecha_subida
        FROM archivos
        WHERE id_categoria = %s
        ORDER BY fecha_subida DESC
    """, (categoria_id,))
    archivos = cursor.fetchall()
    conexion.close()
    return archivos
