"""
Script de Migración de Análisis Existentes
Migra análisis del user_id=1 genérico a usuarios reales basándose en metadata
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
import sys
from datetime import datetime
import json

# Fix encoding for Windows console
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Obtener ruta de la BD
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "civilprotect.db")
BACKUP_PATH = os.path.join(BASE_DIR, "data", f"civilprotect_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

print("="*80)
print("SCRIPT DE MIGRACIÓN DE ANÁLISIS EXISTENTES")
print("="*80)
print(f"\n[INFO] Base de datos: {DB_PATH}")
print(f"[INFO] Backup será creado en: {BACKUP_PATH}\n")

# Crear backup antes de migrar
print("[PASO 1/5] Creando backup de seguridad...")
try:
    import shutil
    shutil.copy2(DB_PATH, BACKUP_PATH)
    print(f"✅ Backup creado exitosamente: {BACKUP_PATH}\n")
except Exception as e:
    print(f"❌ ERROR al crear backup: {e}")
    print("[ABORT] No se puede continuar sin backup.\n")
    sys.exit(1)

# Conectar a la BD
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

try:
    # PASO 2: Verificar estructura de tablas
    print("[PASO 2/5] Verificando estructura de tablas...")
    
    # Verificar tabla users
    result = db.execute(text("PRAGMA table_info(users)"))
    user_columns = [row[1] for row in result]
    
    if "password_hash" not in user_columns:
        print("❌ ERROR: La tabla 'users' no tiene el campo 'password_hash'")
        print("[INFO] Primero ejecuta: python migrate_database.py\n")
        sys.exit(1)
    
    print("✅ Tabla 'users' con estructura correcta")
    
    # Verificar tabla analysis
    result = db.execute(text("PRAGMA table_info(analysis)"))
    analysis_columns = [row[1] for row in result]
    
    if "user_id" not in analysis_columns:
        print("❌ ERROR: La tabla 'analysis' no tiene el campo 'user_id'")
        print("[INFO] La base de datos necesita ser actualizada.\n")
        sys.exit(1)
    
    print("✅ Tabla 'analysis' con estructura correcta\n")
    
    # PASO 3: Contar análisis existentes
    print("[PASO 3/5] Analizando datos existentes...")
    
    result = db.execute(text("SELECT COUNT(*) FROM analysis"))
    total_analyses = result.scalar()
    print(f"[INFO] Total de análisis en DB: {total_analyses}")
    
    result = db.execute(text("SELECT COUNT(*) FROM analysis WHERE user_id = 1"))
    analyses_user1 = result.scalar()
    print(f"[INFO] Análisis con user_id=1 (genérico): {analyses_user1}")
    
    result = db.execute(text("SELECT COUNT(*) FROM users"))
    total_users = result.scalar()
    print(f"[INFO] Total de usuarios: {total_users}")
    
    if analyses_user1 == 0:
        print("\n✅ No hay análisis con user_id=1. No se requiere migración.\n")
        sys.exit(0)
    
    if total_users == 0:
        print("\n❌ ERROR: No hay usuarios en la base de datos.")
        print("[INFO] Primero crea un usuario admin:\n")
        print("   python -c \"from auth.handlers import create_user; create_user('admin@civilprotect.com', 'Admin User', 'Admin123', 'admin')\"")
        print()
        sys.exit(1)
    
    print()
    
    # PASO 4: Estrategia de migración
    print("[PASO 4/5] Estrategia de migración...")
    print(f"\n[OPCIÓN 1] Asignar todos los análisis ({analyses_user1}) al primer usuario admin")
    print("[OPCIÓN 2] Distribuir análisis entre usuarios consultores existentes")
    print("[OPCIÓN 3] Crear usuario 'Legacy' y asignarle todos los análisis antiguos")
    print()
    
    # Obtener primer admin
    result = db.execute(text("SELECT id, email, name FROM users WHERE role = 'admin' LIMIT 1"))
    admin_user = result.fetchone()
    
    if admin_user:
        print(f"[INFO] Usuario admin disponible: {admin_user[1]} (ID: {admin_user[0]})")
    
    # Obtener consultores
    result = db.execute(text("SELECT COUNT(*) FROM users WHERE role = 'consultor'"))
    consultores_count = result.scalar()
    print(f"[INFO] Consultores disponibles: {consultores_count}")
    
    print("\n" + "="*80)
    print("EJECUTANDO MIGRACIÓN CON ESTRATEGIA POR DEFECTO:")
    print("Todos los análisis de user_id=1 serán asignados al primer admin")
    print("="*80 + "\n")
    
    if not admin_user:
        # No hay admin, crear usuario Legacy
        print("[WARN] No hay usuario admin. Creando usuario 'Legacy'...")
        
        from auth.handlers import hash_password
        hashed_password = hash_password("Legacy123")
        
        db.execute(text("""
            INSERT INTO users (email, name, password_hash, role, is_active, created_at)
            VALUES (:email, :name, :password_hash, :role, :is_active, :created_at)
        """), {
            "email": "legacy@civilprotect.com",
            "name": "Usuario Legacy (Migración)",
            "password_hash": hashed_password,
            "role": "consultor",
            "is_active": True,
            "created_at": datetime.now()
        })
        db.commit()
        
        result = db.execute(text("SELECT id FROM users WHERE email = 'legacy@civilprotect.com'"))
        new_user_id = result.scalar()
        
        print(f"✅ Usuario Legacy creado con ID: {new_user_id}")
        print(f"   Email: legacy@civilprotect.com")
        print(f"   Password: Legacy123")
        
        target_user_id = new_user_id
    else:
        target_user_id = admin_user[0]
    
    print()
    
    # PASO 5: Ejecutar migración
    print(f"[PASO 5/5] Migrando análisis de user_id=1 → user_id={target_user_id}...")
    
    result = db.execute(text("""
        UPDATE analysis 
        SET user_id = :new_user_id 
        WHERE user_id = 1
    """), {"new_user_id": target_user_id})
    
    db.commit()
    
    rows_affected = result.rowcount
    print(f"✅ Migrados {rows_affected} análisis exitosamente\n")
    
    # Verificación final
    print("[VERIFICACIÓN] Comprobando migración...")
    result = db.execute(text("SELECT COUNT(*) FROM analysis WHERE user_id = 1"))
    remaining = result.scalar()
    
    if remaining == 0:
        print("✅ Todos los análisis fueron migrados correctamente")
    else:
        print(f"⚠️ Aún quedan {remaining} análisis con user_id=1")
    
    result = db.execute(text("""
        SELECT COUNT(*) FROM analysis WHERE user_id = :user_id
    """), {"user_id": target_user_id})
    migrated_count = result.scalar()
    
    print(f"✅ Usuario {target_user_id} ahora tiene {migrated_count} análisis")
    
    print("\n" + "="*80)
    print("MIGRACIÓN COMPLETADA EXITOSAMENTE")
    print("="*80)
    print(f"\n[RESUMEN]")
    print(f"  - Análisis migrados: {rows_affected}")
    print(f"  - Usuario destino: ID {target_user_id}")
    print(f"  - Backup disponible en: {BACKUP_PATH}")
    
    if not admin_user:
        print(f"\n[IMPORTANTE] Se creó usuario Legacy:")
        print(f"  Email: legacy@civilprotect.com")
        print(f"  Password: Legacy123")
        print(f"  Cambia la contraseña después del primer login.\n")
    
    print("\n[PRÓXIMOS PASOS]")
    print("  1. Verifica que todos los análisis sean accesibles")
    print("  2. Si todo está bien, puedes eliminar el backup")
    print("  3. Los usuarios pueden ahora gestionar sus propios análisis\n")

except Exception as e:
    print(f"\n❌ ERROR durante la migración: {e}")
    print(f"\n[ROLLBACK] Para restaurar el backup:")
    print(f"  1. Detén el servidor")
    print(f"  2. Copia: {BACKUP_PATH}")
    print(f"  3. A: {DB_PATH}")
    print()
    db.rollback()
    sys.exit(1)

finally:
    db.close()
    engine.dispose()
