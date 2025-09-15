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
            SELECT id, nombre_original, ruta_archivo, fecha_subida, descripcion
            FROM archivos
            WHERE id_categoria = %s AND carpeta_id IS NULL
            ORDER BY fecha_subida DESC
        """, (id_categoria,))
    else:
        cursor.execute("""
            SELECT id, nombre_original, ruta_archivo, fecha_subida, descripcion
            FROM archivos
            WHERE id_categoria = %s AND carpeta_id = %s
            ORDER BY fecha_subida DESC
        """, (id_categoria, carpeta_id))

    filas = cursor.fetchall()
    conexion.close()
    return filas


# (para no romper imports antiguos, si los tienes)
def obtener_archivos_por_categoria(id_categoria, carpeta_padre_id=None):
    return obtener_archivos_por_ubicacion(id_categoria, carpeta_padre_id)



def obtener_archivo_por_id(archivo_id):
    conexion = conectar()
    cursor = conexion.cursor()  # 👈 gracias al config_bd ya devuelve diccionarios
    cursor.execute("SELECT * FROM archivos WHERE id = %s", (archivo_id,))
    fila = cursor.fetchone()  # obtenemos solo un archivo
    conexion.close()
    return fila  # puede ser None si no existe

# models/archivo_modelo.py -> corregir eliminar_archivo
def eliminar_archivo(archivo_id):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM archivos WHERE id = %s", (archivo_id,))
    conexion.commit()
    conexion.close()
    
    
def actualizar_archivo(archivo_id, nuevo_nombre=None, nueva_ruta=None, nueva_descripcion=None):
    conexion = conectar()
    cursor = conexion.cursor()

    # Creamos lista dinámica de campos que se van a actualizar
    campos = []
    valores = []

    if nuevo_nombre:
        campos.append("nombre_original = %s")
        valores.append(nuevo_nombre)

    if nueva_ruta:
        campos.append("ruta_archivo = %s")
        valores.append(nueva_ruta)

    if nueva_descripcion is not None:  # puede ser string vacío
        campos.append("descripcion = %s")
        valores.append(nueva_descripcion)

    if not campos:  # nada que actualizar
        conexion.close()
        return

    # Agregar archivo_id al final
    valores.append(archivo_id)

    query = f"""
        UPDATE archivos
        SET {", ".join(campos)}, fecha_actualizacion = NOW()
        WHERE id = %s
    """
    cursor.execute(query, tuple(valores))
    conexion.commit()
    conexion.close()