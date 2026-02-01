import sys
import os
import json
import sqlite3
from sqlalchemy import create_engine, text

# Agregar directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config import settings

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SQLITE_PATH = os.path.join(BASE_DIR, "data", "civilprotect.db")

def migrate_users(sqlite_conn, pg_conn):
    print("--- Migrando Usuarios ---")
    cursor = sqlite_conn.cursor()
    try:
        cursor.execute("SELECT id, email, name, password_hash, role, is_active, created_at FROM users")
        users = cursor.fetchall()
    except Exception as e:
        print(f"Error leyendo usuarios de SQLite: {e}")
        return

    for u in users:
        try:
            # Upsert (ON CONFLICT DO NOTHING)
            # Aseguramos que 'is_active' sea booleano o integer compatible
            is_active = 1 if u[5] else 0
            
            pg_conn.execute(text("""
                INSERT INTO users (id, email, name, password_hash, role, is_active, created_at)
                VALUES (:id, :email, :name, :hash, :role, :active, :created)
                ON CONFLICT (id) DO NOTHING
            """), {
                "id": u[0], 
                "email": u[1], 
                "name": u[2], 
                "hash": u[3], 
                "role": u[4], 
                "active": is_active, 
                "created": u[6]
            })
        except Exception as e:
            print(f"Error migrando usuario {u[1]}: {e}")
            
    print(f"Procesados {len(users)} usuarios.")

def migrate_analyses(sqlite_conn, pg_conn):
    print("--- Migrando Análisis ---")
    cursor = sqlite_conn.cursor()
    try:
        cursor.execute("SELECT * FROM analyses")
        columns = [description[0] for description in cursor.description]
        rows = cursor.fetchall()
    except Exception as e:
        print(f"Error leyendo analisis de SQLite: {e}")
        # Puede que la tabla legacy sea diferente, intentar fallback
        return
    
    count = 0
    skipped = 0
    for row in rows:
        data = dict(zip(columns, row))
        
        # Parsear JSON
        try:
            inp = data.get('input_data')
            if isinstance(inp, str):
                inp = json.loads(inp)
            elif inp is None:
                inp = {}
            
            rep = data.get('report_data')
            if isinstance(rep, str):
                rep = json.loads(rep)
            elif rep is None:
                rep = {}
        except Exception as e:
            print(f"Skipping ID {data.get('id')}: JSON Error {e}")
            skipped += 1
            continue

        # Handle missing user_id (Legacy Data Support)
        user_id = data.get('user_id')
        if user_id is None:
            # Default to Admin (ID 1) if not found
            user_id = 1 
            
        try:
            # Insertar en Postgres
            # Pasamos dumps() porque usando text() raw, Postgres espera string para castear a JSONB
            pg_conn.execute(text("""
                INSERT INTO analyses (
                    id, user_id, tipo_inmueble, m2_construccion, niveles, aforo, 
                    municipio, estado, input_data, report_data, pdf_path, created_at
                ) VALUES (
                    :id, :uid, :tipo, :m2, :niveles, :aforo, 
                    :mun, :est, :inp, :rep, :pdf, :created
                ) ON CONFLICT (id) DO NOTHING
            """), {
                "id": data.get('id'), 
                "uid": user_id, 
                "tipo": data.get('tipo_inmueble'),
                "m2": data.get('m2_construccion'), 
                "niveles": data.get('niveles'), 
                "aforo": data.get('aforo'),
                "mun": data.get('municipio'), 
                "est": data.get('estado'),
                "inp": json.dumps(inp), 
                "rep": json.dumps(rep),
                "pdf": data.get('pdf_path'), 
                "created": data.get('created_at')
            })
            count += 1
        except Exception as e:
            print(f"Error insertando analisis {data.get('id')}: {e}")
            skipped += 1
            
    print(f"Migrados {count} análisis. Saltados {skipped}.")

def main():
    if not os.path.exists(SQLITE_PATH):
        print(f"No se encontró base de datos SQLite en: {SQLITE_PATH}")
        return

    print(f"Origen: {SQLITE_PATH}")
    print(f"Destino: {settings.database_url}")
    
    if "sqlite" in settings.database_url:
        print("ERROR: La configuración actual apunta a SQLite. Cambia DATABASE_URL a Postgres en .env")
        return

    try:
        sqlite_conn = sqlite3.connect(SQLITE_PATH)
        pg_engine = create_engine(settings.database_url)
        
        with pg_engine.connect() as pg_conn:
            with pg_conn.begin(): # Transacción única para todo
                migrate_users(sqlite_conn, pg_conn)
                migrate_analyses(sqlite_conn, pg_conn)
        
        print("\n✅ ETL / Migración Completada Exitosamente.")
        
    except Exception as e:
        print(f"\n❌ Error Fatal en Migración: {e}")

if __name__ == "__main__":
    main()
