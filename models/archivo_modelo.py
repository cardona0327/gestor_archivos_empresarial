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
    
    
    
# --- archivo_modelo.py (añadir esto) ---
def buscar_archivos(nombre=None, descripcion=None, fecha_desde=None, fecha_hasta=None, categoria_id=None, carpeta_id=None):
    """
    Busca archivos con filtros opcionales:
    - nombre: buscado con LIKE en nombre_original
    - descripcion: buscado con LIKE en descripcion
    - fecha_desde / fecha_hasta: filtra por fecha_subida (YYYY-MM-DD o YYYY-MM-DD HH:MM:SS)
    - categoria_id: si se quiere limitar a una categoría concreta (opcional)
    - carpeta_id: si se quiere limitar a una carpeta concreta (opcional; puede ser None para archivos en raíz)
    Devuelve lista de diccionarios.
    """
    conexion = conectar()
    cursor = conexion.cursor()

    condiciones = []
    params = []

    if nombre:
        condiciones.append("nombre_original LIKE %s")
        params.append(f"%{nombre}%")

    if descripcion:
        condiciones.append("descripcion LIKE %s")
        params.append(f"%{descripcion}%")

    if fecha_desde:
        condiciones.append("fecha_subida >= %s")
        params.append(fecha_desde)

    if fecha_hasta:
        condiciones.append("fecha_subida <= %s")
        params.append(fecha_hasta)

    if categoria_id is not None:
        condiciones.append("id_categoria = %s")
        params.append(categoria_id)

    # carpeta_id puede ser None (archivos en raíz) o un entero (archivos dentro de carpeta)
    if carpeta_id is None:
        # si el usuario indicó explicitamente carpeta_id=None queremos archivos en la raíz:
        condiciones.append("carpeta_id IS NULL")
    elif carpeta_id != "__ANY__":  # si el caller pasa "__ANY__" quiere todas las carpetas (no filtrar)
        condiciones.append("carpeta_id = %s")
        params.append(carpeta_id)

    where_clause = ("WHERE " + " AND ".join(condiciones)) if condiciones else ""

    consulta = f"""
        SELECT id, id_categoria, carpeta_id, nombre_original, ruta_archivo, descripcion, fecha_subida
        FROM archivos
        {where_clause}
        ORDER BY fecha_subida DESC
    """
    cursor.execute(consulta, tuple(params))
    resultados = cursor.fetchall()
    conexion.close()
    return resultados


def contar_archivos_por_categoria():
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT a.id_categoria, cat.nombre_categoria, COUNT(*) as total_archivos
        FROM archivos a
        JOIN categorias cat ON a.id_categoria = cat.id
        GROUP BY a.id_categoria, cat.nombre_categoria
    """)
    filas = cursor.fetchall()
    conexion.close()
    return filas

# archivo_modelo.py
def contar_archivos_por_mes():
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT DATE_FORMAT(fecha_subida, '%Y-%m') as mes, COUNT(*) as total
        FROM archivos
        GROUP BY mes
        ORDER BY mes
    """)
    filas = cursor.fetchall()
    conexion.close()
    return filas
