import os
import zipfile
import datetime
import sys

# Configuración de exclusiones (Directorios pesados o generados)
IGNORE_DIRS = {
    'node_modules', 'venv', 'env', '__pycache__', '.git', '.idea', '.vscode',
    'postgres_data', 'postgres_data_prod', 'logs', 'reports', 'build', 'dist',
    'coverage', 'backups'
}
IGNORE_FILES = {
    '.DS_Store', 'Thumbs.db'
}
IGNORE_EXTENSIONS = {'.pyc', '.log', '.tmp', '.zip', '.gz'}

def get_project_root():
    # Asumimos que este script está en /tools, así que root es ../
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_version(root_dir):
    v_file = os.path.join(root_dir, "VERSION.txt")
    if os.path.exists(v_file):
        try:
            with open(v_file, 'r', encoding='utf-8') as f:
                line = f.readline()
                if "VERSION:" in line:
                    # Extract 4.5.2
                    return line.split(":")[1].strip().split(" ")[0]
        except:
            pass
    return "Snapshot"

def create_backup():
    root_dir = get_project_root()
    version = get_version(root_dir)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Nombre del archivo ZIP
    zip_name = f"CivilProtect_Source_metrics_{version}_{timestamp}.zip"
    
    # Destino: Carpeta "SystemBackups" al mismo nivel que el proyecto (fuera del repo)
    # o dentro del proyecto en una carpeta ignorada.
    # Para seguridad, lo pondremos en root/backups_shield (añadir a ignore manual)
    backup_dir = os.path.join(root_dir, "civilprotect_shield_backups")
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
        
    zip_path = os.path.join(backup_dir, zip_name)
    
    print(f"🔄 Iniciando respaldo de código fuente...")
    print(f"📍 Origen: {root_dir}")
    print(f"📦 Destino: {zip_path}")
    print("⏳ Comprimiendo archivos (esto puede tardar unos segundos)...")
    
    file_count = 0
    
    try:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(root_dir):
                # Filtrar directorios ignorados
                dirs[:] = [d for d in dirs if d not in IGNORE_DIRS and d != "civilprotect_shield_backups"]
                
                for file in files:
                    if file in IGNORE_FILES:
                        continue
                    if any(file.endswith(ext) for ext in IGNORE_EXTENSIONS):
                        continue
                        
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, root_dir)
                    
                    # Evitar recursividad si el zip se crea dentro (aunque filtramos el dir)
                    if file_path == zip_path:
                        continue

                    zipf.write(file_path, arcname)
                    file_count += 1
        
        print(f"✅ Respaldo COMPLETADO. {file_count} archivos comprimidos.")
        print(f"🛡️  Tu versión {version} está blindada en: {zip_path}")
        
    except Exception as e:
        print(f"❌ Error creando respaldo: {e}")

if __name__ == "__main__":
    create_backup()
