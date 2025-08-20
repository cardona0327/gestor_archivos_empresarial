from config_bd import conectar

try:
    conexion = conectar()
    print("✅ Conexión exitosa a la base de datos.")
    conexion.close()
except Exception as e:
    print("❌ Error de conexión:", e)
