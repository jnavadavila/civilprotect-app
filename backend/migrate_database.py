"""
Script de Migración de Base de Datos
Actualiza el modelo User para agregar campos de autenticación
"""
from sqlalchemy import create_engine, text
import os
import sys

# Fix encoding for Windows console
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Obtener ruta de la BD
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "civilprotect.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

print(f"[BD] Migrando base de datos: {DB_PATH}")

engine = create_engine(DATABASE_URL, echo=True)

with engine.connect() as conn:
    try:
        # Verificar si la columna password_hash ya existe
        result = conn.execute(text("PRAGMA table_info(users)"))
        columns = [row[1] for row in result]
        
        if "password_hash" in columns:
            print("[OK] La base de datos ya tiene los campos de autenticacion.")
            print("[INFO] No se requiere migracion.")
        else:
            print("[WARN] Agregando campos de autenticacion al modelo User...")
            
            # SQLite no soporta ALTER TABLE ADD COLUMN con NOT NULL directamente
            # Debemos usar valores por defecto temporales
            
            # Agregar password_hash (temporal con valor por defecto)
            conn.execute(text(
                "ALTER TABLE users ADD COLUMN password_hash VARCHAR(255) DEFAULT 'temp_hash'"
            ))
            conn.commit()
            print("[OK] Agregada columna password_hash")
            
            # Agregar role
            conn.execute(text(
                "ALTER TABLE users ADD COLUMN role VARCHAR(50) DEFAULT 'consultor'"
            ))
            conn.commit()
            print("[OK] Agregada columna role")
            
            # Agregar is_active
            conn.execute(text(
                "ALTER TABLE users ADD COLUMN is_active INTEGER DEFAULT 1"
            ))
            conn.commit()
            print("[OK] Agregada columna is_active")
            
            # Hacer que email sea NOT NULL (si ya hay datos, esto podría fallar)
            # En SQLite, cambiar constraints requiere recrear la tabla
            # Por ahora, solo aseguramos que los nuevos registros lo cumplan
            
            print("\n[OK] Migracion completada exitosamente!")
            print("\n[WARN] IMPORTANTE: Los usuarios existentes tienen password temporal.")
            print("   Debes usar el script update_user_passwords.py para establecer passwords reales.\n")
            
    except Exception as e:
        print(f"\n[ERROR] Error durante la migracion: {e}")
        print("\n[INFO] Si la base de datos es nueva, esto es normal.")
        print("   Ejecuta database.py para inicializar la BD correctamente.\n")
