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


# --- carpeta_modelo.py (añadir esto) ---
def buscar_carpetas(nombre=None, fecha_desde=None, fecha_hasta=None, categoria_id=None):
    """
    Busca carpetas por nombre y/o rango de fecha (fecha_creacion).
    - nombre: LIKE sobre nombre_carpeta
    - fecha_desde / fecha_hasta: filtra por fecha_creacion
    - categoria_id: limitar por categoría
    """
    conexion = conectar()
    cursor = conexion.cursor()

    condiciones = []
    params = []

    if nombre:
        condiciones.append("nombre_carpeta LIKE %s")
        params.append(f"%{nombre}%")

    if fecha_desde:
        condiciones.append("fecha_creacion >= %s")
        params.append(fecha_desde)

    if fecha_hasta:
        condiciones.append("fecha_creacion <= %s")
        params.append(fecha_hasta)

    if categoria_id is not None:
        condiciones.append("id_categoria = %s")
        params.append(categoria_id)

    where_clause = ("WHERE " + " AND ".join(condiciones)) if condiciones else ""

    consulta = f"""
        SELECT id, id_categoria, nombre_carpeta, carpeta_padre_id, fecha_creacion
        FROM carpetas
        {where_clause}
        ORDER BY fecha_creacion DESC
    """
    cursor.execute(consulta, tuple(params))
    resultados = cursor.fetchall()
    conexion.close()
    return resultados


def contar_carpetas_por_categoria():
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT c.id_categoria, cat.nombre_categoria, COUNT(*) as total_carpetas
        FROM carpetas c
        JOIN categorias cat ON c.id_categoria = cat.id
        GROUP BY c.id_categoria, cat.nombre_categoria
    """)
    filas = cursor.fetchall()
    conexion.close()
    return filas

# carpeta_modelo.py
def contar_carpetas_por_mes():
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT DATE_FORMAT(fecha_creacion, '%Y-%m') as mes, COUNT(*) as total
        FROM carpetas
        GROUP BY mes
        ORDER BY mes
    """)
    filas = cursor.fetchall()
    conexion.close()
    return filas
