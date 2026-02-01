"""
Configuración Centralizada con Pydantic Settings
Valida y carga todas las variables de entorno al inicio
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, validator
from typing import List, Optional
import os
from pathlib import Path
import logging

# Configurar logging básico
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """
    Configuración centralizada de la aplicación.
    Todas las variables de entorno se validan aquí.
    """
    
    # ==================== DATABASE ====================
    database_url: str = Field(
        default="sqlite:///./data/civilprotect.db",
        description="URL de conexión a la base de datos"
    )
    
    # ==================== OPENAI API ====================
    openai_api_key: str = Field(
        ...,  # Requerido
        min_length=20,
        description="API Key de OpenAI"
    )
    
    # ==================== JWT ====================
    jwt_secret_key: str = Field(
        ...,  # Requerido
        min_length=32,
        description="Secret key para firmar JWT tokens"
    )
    
    jwt_algorithm: str = Field(
        default="HS256",
        description="Algoritmo de firma JWT"
    )
    
    access_token_expire_minutes: int = Field(
        default=30,
        gt=0,
        le=10080,  # Máx 7 días
        description="Minutos de expiración del access token"
    )
    
    refresh_token_expire_days: int = Field(
        default=7,
        gt=0,
        le=90,  # Máx 90 días
        description="Días de expiración del refresh token"
    )
    
    # ==================== CORS ====================
    allowed_origins: str = Field(
        default="http://localhost:3000",
        description="Orígenes permitidos para CORS (separados por coma)"
    )
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """Convertir string de orígenes a lista"""
        return [origin.strip() for origin in self.allowed_origins.split(",")]
    
    # ==================== RATE LIMITING ====================
    rate_limit_analyze: str = Field(
        default="10/hour",
        description="Rate limit para endpoint /analyze"
    )
    
    rate_limit_login: str = Field(
        default="5/15minute",
        description="Rate limit para endpoint /auth/login"
    )
    
    rate_limit_register: str = Field(
        default="3/hour",
        description="Rate limit para endpoint /auth/register"
    )
    
    rate_limit_global_auth: str = Field(
        default="100/hour",
        description="Rate limit global para usuarios autenticados"
    )
    
    rate_limit_global_public: str = Field(
        default="50/hour",
        description="Rate limit global para requests públicos"
    )
    
    # ==================== SEGURIDAD ====================
    debug: bool = Field(
        default=False,
        description="Habilitar modo debug"
    )
    
    security_logging: bool = Field(
        default=True,
        description="Habilitar logging de seguridad"
    )
    
    log_level: str = Field(
        default="INFO",
        description="Nivel de logging"
    )
    
    @validator('log_level')
    def validate_log_level(cls, v):
        """Validar que el nivel de logging sea válido"""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f"LOG_LEVEL debe ser uno de: {', '.join(valid_levels)}")
        return v.upper()
    
    # ==================== SERVIDOR ====================
    server_host: str = Field(
        default="0.0.0.0",
        description="Host del servidor"
    )
    
    server_port: int = Field(
        default=8000,
        gt=0,
        le=65535,
        description="Puerto del servidor"
    )
    
    workers: int = Field(
        default=4,
        gt=0,
        le=32,
        description="Número de workers de Uvicorn"
    )
    
    # ==================== ENTORNO ====================
    env: str = Field(
        default="production",
        description="Entorno de ejecución"
    )
    
    @validator('env')
    def validate_env(cls, v):
        """Validar que el entorno sea válido"""
        valid_envs = ['development', 'staging', 'production']
        if v.lower() not in valid_envs:
            raise ValueError(f"ENV debe ser uno de: {', '.join(valid_envs)}")
        return v.lower()
    
    app_name: str = Field(
        default="CivilProtect API",
        description="Nombre de la aplicación"
    )
    
    app_version: str = Field(
        default="4.5.0",
        description="Versión de la aplicación"
    )
    
    # ==================== FEATURE FLAGS ====================
    enable_ai_enrichment: bool = Field(
        default=True,
        description="Habilitar enriquecimiento con IA"
    )
    
    enable_legislative_monitor: bool = Field(
        default=True,
        description="Habilitar monitor legislativo"
    )
    
    enable_pdf_generation: bool = Field(
        default=True,
        description="Habilitar generación de PDFs"
    )
    
    enable_html_reports: bool = Field(
        default=True,
        description="Habilitar reportes HTML"
    )
    
    # ==================== PATHS ====================
    pdf_output_dir: str = Field(
        default="./pdfs",
        description="Directorio para PDFs generados"
    )
    
    data_dir: str = Field(
        default="./data",
        description="Directorio para datos"
    )
    
    log_dir: str = Field(
        default="./logs",
        description="Directorio para logs"
    )
    
    # Configuración de Pydantic Settings
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"  # Ignorar variables extra en .env
    )
    
    def __init__(self, **kwargs):
        """Inicializar y validar configuración"""
        super().__init__(**kwargs)
        self._validate_security()
        self._create_directories()
    
    def _validate_security(self):
        """Validaciones adicionales de seguridad"""
        # Validar JWT_SECRET_KEY no sea el placeholder
        if "your-super-secret" in self.jwt_secret_key.lower() or \
           "change-this" in self.jwt_secret_key.lower() or \
           "placeholder" in self.jwt_secret_key.lower():
            raise ValueError(
                "JWT_SECRET_KEY contiene un placeholder. "
                "Genera una clave segura con: python -c \"import secrets; print(secrets.token_hex(32))\""
            )
        
        # Validar OPENAI_API_KEY no sea el placeholder
        if "placeholder" in self.openai_api_key.lower() or \
           "your-" in self.openai_api_key.lower():
            logger.warning(
                "⚠️  OPENAI_API_KEY parece ser un placeholder. "
                "Las funcionalidades de IA no funcionarán correctamente."
            )
        
        # Advertir si DEBUG está activado en producción
        if self.env == "production" and self.debug:
            logger.warning(
                "⚠️  DEBUG=True en entorno de producción. "
                "Esto puede exponer información sensible. Cambia DEBUG=False"
            )
        
        # Advertir si CORS permite cualquier origen
        if "*" in self.allowed_origins:
            logger.warning(
                "⚠️  CORS está configurado con '*' (cualquier origen). "
                "Esto es inseguro en producción. Configura dominios específicos."
            )
        
        # Validar que ACCESS_TOKEN_EXPIRE sea razonable
        if self.env == "production" and self.access_token_expire_minutes > 60:
            logger.warning(
                f"⚠️  ACCESS_TOKEN_EXPIRE_MINUTES={self.access_token_expire_minutes} "
                f"es muy alto para producción. Recomendado: 30 minutos"
            )
    
    def _create_directories(self):
        """Crear directorios necesarios si no existen"""
        directories = [
            self.pdf_output_dir,
            self.data_dir,
            self.log_dir
        ]
        
        for directory in directories:
            path = Path(directory)
            if not path.exists():
                path.mkdir(parents=True, exist_ok=True)
                logger.info(f"✅ Directorio creado: {directory}")
    
    def log_config(self, mask_secrets: bool = True):
        """
        Logear configuración actual (sin exponer secretos)
        
        Args:
            mask_secrets: Si True, enmascara valores sensibles
        """
        logger.info("="*70)
        logger.info("CONFIGURACIÓN DE LA APLICACIÓN")
        logger.info("="*70)
        
        # Información general
        logger.info(f"App: {self.app_name} v{self.app_version}")
        logger.info(f"Entorno: {self.env.upper()}")
        logger.info(f"Debug: {self.debug}")
        logger.info(f"Log Level: {self.log_level}")
        
        # Base de datos
        if mask_secrets:
            # Ocultar path completo
            db_display = self.database_url.split("/")[-1] if "/" in self.database_url else self.database_url
            logger.info(f"Database: {db_display}")
        else:
            logger.info(f"Database: {self.database_url}")
        
        # JWT
        if mask_secrets:
            logger.info(f"JWT Algorithm: {self.jwt_algorithm}")
            logger.info(f"JWT Secret: {'*' * 32}...")
        else:
            logger.info(f"JWT Secret Key: {self.jwt_secret_key}")
        
        logger.info(f"Access Token Expiry: {self.access_token_expire_minutes} min")
        logger.info(f"Refresh Token Expiry: {self.refresh_token_expire_days} days")
        
        # CORS
        logger.info(f"CORS Origins: {self.allowed_origins}")
        
        # Rate Limiting
        logger.info("Rate Limits:")
        logger.info(f"  - Login: {self.rate_limit_login}")
        logger.info(f"  - Register: {self.rate_limit_register}")
        logger.info(f"  - Analyze: {self.rate_limit_analyze}")
        
        # Features
        logger.info("Features:")
        logger.info(f"  - AI Enrichment: {self.enable_ai_enrichment}")
        logger.info(f"  - Legislative Monitor: {self.enable_legislative_monitor}")
        logger.info(f"  - PDF Generation: {self.enable_pdf_generation}")
        logger.info(f"  - HTML Reports: {self.enable_html_reports}")
        
        # Server
        logger.info(f"Server: {self.server_host}:{self.server_port}")
        logger.info(f"Workers: {self.workers}")
        
        logger.info("="*70)
    
    @property
    def is_production(self) -> bool:
        """Determinar si estamos en producción"""
        return self.env == "production"
    
    @property
    def is_development(self) -> bool:
        """Determinar si estamos en desarrollo"""
        return self.env == "development"


# Instancia global de configuración
# Se carga automáticamente al importar este módulo
try:
    settings = Settings()
    settings.log_config(mask_secrets=True)
except Exception as e:
    logger.error(f"❌ Error cargando configuración: {e}")
    logger.error("Verifica que el archivo .env existe y tiene todas las variables requeridas")
    logger.error("Ejecuta: python check_env.py para validar la configuración")
    raise


# Función helper para obtener configuración
def get_settings() -> Settings:
    """
    Obtener instancia de configuración.
    Usar en dependency injection de FastAPI.
    """
    return settings


# Exportar lo necesario
__all__ = ['Settings', 'settings', 'get_settings']
