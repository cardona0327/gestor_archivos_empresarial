import pymysql

MYSQL_HOST = 'localhost'
MYSQL_USER = 'root'
MYSQL_PASSWORD = 'root'
MYSQL_DB = 'gestor_archivos'
MYSQL_PORT = 3306  # Puedes dejarlo así si no cambiaste el puerto de MySQL


def conectar():
    return pymysql.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB,
        port=MYSQL_PORT,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
