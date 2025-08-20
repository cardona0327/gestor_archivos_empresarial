from config_bd import conectar
import pymysql.cursors  

def crear_carpeta_bd(id_categoria, nombre_carpeta, carpeta_padre_id=None):
    conexion = conectar()
    cursor = conexion.cursor()

    if carpeta_padre_id is None:
        cursor.execute("""
            INSERT INTO carpetas (id_categoria, nombre_carpeta, carpeta_padre_id)
            VALUES (%s, %s, NULL)
        """, (id_categoria, nombre_carpeta))
    else:
        cursor.execute("""
            INSERT INTO carpetas (id_categoria, nombre_carpeta, carpeta_padre_id)
            VALUES (%s, %s, %s)
        """, (id_categoria, nombre_carpeta, carpeta_padre_id))

    conexion.commit()
    conexion.close()


def obtener_carpetas_por_categoria(id_categoria, carpeta_padre_id=None):
    conexion = conectar()
    cursor = conexion.cursor(pymysql.cursors.DictCursor)  # 👈 aquí el cambio
    if carpeta_padre_id:
        cursor.execute(
            "SELECT * FROM carpetas WHERE id_categoria = %s AND carpeta_padre_id = %s",
            (id_categoria, carpeta_padre_id),
        )
    else:
        cursor.execute(
            "SELECT * FROM carpetas WHERE id_categoria = %s AND carpeta_padre_id IS NULL",
            (id_categoria,),
        )
    carpetas = cursor.fetchall()
    conexion.close()
    return carpetas

