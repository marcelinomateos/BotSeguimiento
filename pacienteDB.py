import sqlite3


# Conectar o crear la base de datos y la tabla de pacientes
conn = sqlite3.connect('pacientes.db', check_same_thread=False)
cursor = conn.cursor()

# Crear la tabla si no existe
cursor.execute('''
    CREATE TABLE IF NOT EXISTS pacientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        folio TEXT,
        nombre TEXT,
        apellido_paterno TEXT,
        apellido_materno TEXT,
        edad INTEGER,
        lugar_procedencia TEXT,
        numero INTEGER
    )
''')
conn.commit()


# Crear tabla para seguimientos si no existe
#def crear_tabla_seguimientos():
#    conn = sqlite3.connect('pacientes.db')
#    cursor = conn.cursor()
cursor.execute('''
        CREATE TABLE IF NOT EXISTS seguimientos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            folio TEXT,
            fecha TEXT,
            hora TEXT,
            temperatura TEXT,
            vomitos TEXT,
            frecuencia_vomitos TEXT,
            problemas_respiracion TEXT,
            dolor_corporal TEXT,
            zona_dolor TEXT,
            intensidad_dolor INTEGER
        )
    ''')
conn.commit()
    
conn.close()