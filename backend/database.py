"""
Sistema de Base de Datos para Historial de Análisis
Usando SQLAlchemy ORM con PostgreSQL (adaptado desde SQLite)
"""
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.types import JSON
from datetime import datetime
import json
import os
from config import settings

# Configuración de SQLAlchemy
DATABASE_URL = settings.database_url

# Determinar tipo de JSON según motor
# Si es postgres, usar JSONB, si es sqlite (test/fallback), usar JSON genérico
is_postgres = 'postgresql' in DATABASE_URL
JSON_TYPE = JSONB if is_postgres else JSON

# Argumentos de conexión
connect_args = {}
pool_args = {}

if is_postgres:
    # Configuración de Connection Pooling para PostgreSQL
    pool_args = {
        "pool_size": 20,
        "max_overflow": 10,
        "pool_timeout": 30,
        "pool_recycle": 1800
    }
else:
    # SQLite specific
    connect_args = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL, 
    echo=False, 
    connect_args=connect_args,
    **pool_args
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ==================== MODELOS ====================

class User(Base):
    """Modelo de Usuario con Autenticación"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)  # Hash bcrypt del password
    role = Column(String(50), default="consultor", nullable=False)  # admin, consultor, cliente
    is_active = Column(Integer, default=1, nullable=False)  # 1=activo, 0=desactivado
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relación con análisis
    analyses = relationship("Analysis", back_populates="user", cascade="all, delete-orphan")

class Analysis(Base):
    """Modelo de Análisis de Protección Civil"""
    __tablename__ = "analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Datos principales (indexados para búsqueda)
    # Índices compuestos definidos abajo
    municipio = Column(String(255), index=True)
    estado = Column(String(255), index=True)
    tipo_inmueble = Column(String(255))
    
    # Etiqueta personalizada del usuario
    custom_label = Column(String(255), nullable=True)
    
    # Datos completos del análisis (JSON/JSONB)
    input_data = Column(JSON_TYPE, nullable=False)  # JSON del formulario
    report_data = Column(JSON_TYPE, nullable=False)  # JSON del reporte completo
    
    # Ruta del PDF generado
    pdf_path = Column(String(500), nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    user = relationship("User", back_populates="analyses")

    # Índices Compuestos para Optimización (Fase 4.3.1)
    __table_args__ = (
        Index('idx_analysis_user_created', user_id, created_at.desc()),
        Index('idx_analysis_location', estado, municipio),
    )

# ==================== UTILIDADES ====================

def get_db():
    """Dependency para obtener sesión de DB"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Inicializa la base de datos creando todas las tablas"""
    Base.metadata.create_all(bind=engine)
    print("[OK] Base de datos inicializada correctamente")
    
    # Crear usuario por defecto si no existe
    db = SessionLocal()
    try:
        default_user = db.query(User).filter(User.id == 1).first()
        if not default_user:
            # Importar aquí para evitar ciclo
            from auth.hash_handler import hash_password
            
            # Password default seguro y VÁLIDO (Debe ser un hash bcrypt)
            hashed_pw = hash_password("admin123")
            
            default_user = User(
                id=1,
                email="default@civilprotect.local",
                name="Usuario Sistema",
                password_hash=hashed_pw,
                role="admin",
                is_active=1
            )
            db.add(default_user)
            db.commit()
            print("[OK] Usuario por defecto creado (Email: default@civilprotect.local / Pass: admin123)")
    except Exception as e:
        print(f"[WARN] Error creando usuario por defecto: {e}")
    finally:
        db.close()

def reset_db():
    """Elimina y recrea todas las tablas (⚠️ USAR CON CUIDADO)"""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("[WARN] Base de datos reseteada")

# ==================== FUNCIONES CRUD ====================

class AnalysisCRUD:
    """Operaciones CRUD para análisis"""
    
    @staticmethod
    def create_analysis(db, user_id: int, input_data: dict, report_data: dict, pdf_path: str = None, custom_label: str = None):
        """Crea un nuevo análisis en la DB"""
        # Nota: input_data y report_data se pasan como dicts, SQLAlchemy maneja la serialización a JSON/JSONB
        analysis = Analysis(
            user_id=user_id,
            municipio=input_data.get("municipio", ""),
            estado=input_data.get("estado", ""),
            tipo_inmueble=input_data.get("tipo_inmueble", ""),
            custom_label=custom_label,
            input_data=input_data,  # No usar json.dumps() con JSONB/JSON type
            report_data=report_data, # No usar json.dumps() con JSONB/JSON type
            pdf_path=pdf_path
        )
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
        return analysis
    
    @staticmethod
    def get_analysis(db, analysis_id: int):
        """Obtiene un análisis por ID"""
        return db.query(Analysis).filter(Analysis.id == analysis_id).first()
    
    @staticmethod
    def get_user_analyses(db, user_id: int, limit: int = 50, offset: int = 0):
        """Obtiene análisis de un usuario con paginación"""
        return db.query(Analysis)\
            .filter(Analysis.user_id == user_id)\
            .order_by(Analysis.created_at.desc())\
            .limit(limit)\
            .offset(offset)\
            .all()
    
    @staticmethod
    def search_analyses(db, user_id: int, municipio: str = None, estado: str = None):
        """Busca análisis por criterios"""
        query = db.query(Analysis).filter(Analysis.user_id == user_id)
        
        if municipio:
            query = query.filter(Analysis.municipio.ilike(f"%{municipio}%"))
        if estado:
            query = query.filter(Analysis.estado.ilike(f"%{estado}%"))
        
        return query.order_by(Analysis.created_at.desc()).all()
    
    @staticmethod
    def delete_analysis(db, analysis_id: int):
        """Elimina un análisis por ID"""
        analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
        if analysis:
            # Eliminar archivo PDF si existe
            if analysis.pdf_path and os.path.exists(analysis.pdf_path):
                try:
                    os.remove(analysis.pdf_path)
                except Exception as e:
                    print(f"[WARN] Error eliminando PDF: {e}")
            
            db.delete(analysis)
            db.commit()
            return True
        return False
    
    @staticmethod
    def count_user_analyses(db, user_id: int):
        """Cuenta total de análisis de un usuario"""
        return db.query(Analysis).filter(Analysis.user_id == user_id).count()

# Inicializar DB al importar el módulo (Solo si no es importado por alembic o test runner de manera especial)
if __name__ != "__main__":
    pass 
