MYSQL_HOST = 'localhost'
MYSQL_USER = 'root'
MYSQL_PASSWORD = 'root'
MYSQL_DB = 'gestor_archivos'
MYSQL_PORT = 3306  # Puedes dejarlo así si no cambiaste el puerto de MySQL


import pymysql

def conectar():
    return pymysql.connect(
        host="localhost",
        user="root",        # Tu usuario de MySQL
        password="",        # Deja vacío si no tienes contraseña
        database="gestor_archivos",  # Asegúrate de que la base ya exista
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    
    
    
