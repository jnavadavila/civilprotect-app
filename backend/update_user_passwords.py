"""
Script para Actualizar Passwords de Usuarios Existentes
Permite establecer passwords a usuarios que tienen el hash temporal
"""
from database import SessionLocal, User
from auth import hash_password
import sys

def update_user_password(user_id: int, new_password: str):
    """Actualiza el password de un usuario específico"""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            print(f"❌ Usuario con ID {user_id} no encontrado")
            return False
        
        # Hash del nuevo password
        hashed = hash_password(new_password)
        
        # Actualizar en BD
        user.password_hash = hashed
        db.commit()
        
        print(f"✅ Password actualizado para usuario: {user.email}")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def list_users():
    """Lista todos los usuarios"""
    db = SessionLocal()
    try:
        users = db.query(User).all()
        
        print("\n📋 Usuarios en el sistema:")
        print("-" * 60)
        for user in users:
            status = "🟢 Activo" if user.is_active else "🔴 Inactivo"
            print(f"ID: {user.id} | {user.email} | {user.name} | Rol: {user.role} | {status}")
        print("-" * 60)
        print(f"Total: {len(users)} usuarios\n")
        
    except Exception as e:
        print(f"❌ Error listando usuarios: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("\n🔐 ACTUALIZACIÓN DE PASSWORDS DE USUARIOS")
    print("=" * 60)
    
    # Listar usuarios
    list_users()
    
    # Interactivo
    if len(sys.argv) == 3:
        # Modo: python update_user_passwords.py <user_id> <new_password>
        user_id = int(sys.argv[1])
        new_password = sys.argv[2]
        update_user_password(user_id, new_password)
    else:
        # Modo interactivo
        print("Uso: python update_user_passwords.py <user_id> <new_password>")
        print("Ejemplo: python update_user_passwords.py 1 MiPassword123")
        print("\nO ejecuta sin argumentos para modo interactivo:\n")
        
        try:
            user_id = int(input("Ingresa el ID del usuario: "))
            new_password = input("Ingresa el nuevo password: ")
            update_user_password(user_id, new_password)
        except KeyboardInterrupt:
            print("\n\n❌ Cancelado por el usuario")
        except Exception as e:
            print(f"\n❌ Error: {e}")
