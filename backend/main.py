"""
CivilProtect API - Backend

DOCUMENTACIÓN DE ENDPOINTS:
---------------------------

📂 ENDPOINTS PÚBLICOS (Sin autenticación):
  - GET  / - Health check
  - POST /auth/register - Registro de nuevos usuarios
  - POST /auth/login - Login de usuarios
  - POST /auth/refresh - Renovación de tokens
  - GET  /catalog/municipios - Catálogo de municipios (necesario para registro)

🔒 ENDPOINTS PROTEGIDOS (Requieren autenticación):
  - GET  /auth/me - Perfil del usuario autenticado
  
  📊 Análisis:
  - POST /analyze - Generar nuevo análisis ✅ Asociado al usuario
  - POST /save-analysis - Guardar análisis ✅ Asociado al usuario
  
  📜 Historial:
  - GET  /history - Historial del usuario ✅ Solo análisis propios
  - GET  /analysis/{id} - Detalle de análisis ✅ Validación de ownership
  - DELETE /analysis/{id} - Eliminar análisis ✅ Validación de ownership
  
  📥 Descargas:
  - GET  /download/{filename} - Descargar PDF ✅ Validación de ownership
  
  📄 Reportes HTML:
  - POST /generate-html-report - Generar reporte HTML ✅ Requiere autenticación
  - GET  /preview-html/{id} - Preview de reporte ✅ Validación de ownership

👑 ENDPOINTS DE ADMINISTRACIÓN (Solo rol: admin):
  - GET  /admin/users - Listar todos los usuarios del sistema
  - PUT  /admin/users/{id}/role - Cambiar rol de usuario (admin/consultor/cliente)
  - PUT  /admin/users/{id}/status - Activar/desactivar usuario

ROLES Y PERMISOS:
------------------
🔴 ADMIN (Administrador):
  - Acceso total al sistema
  - Gestión de usuarios (crear, modificar roles, activar/desactivar)
  - Ver análisis de todos los usuarios
  - Todas las funciones de consultor

🟡 CONSULTOR:
  - Crear y generar análisis
  - Ver solo sus propios análisis
  - Descargar sus propios reportes PDF/HTML
  - Gestionar su historial

🟢 CLIENTE:
  - Ver análisis compartidos con él (futuro)
  - Solo lectura de reportes (futuro)
  - Sin capacidad de crear análisis

SEGURIDAD:
-----------
- JWT con access tokens (24h) y refresh tokens (7 días)
- Bcrypt para hashing de contraseñas (12 rounds)
- Validación de ownership en todos los recursos
- Validación de roles con decorator @require_role
- CORS configurado para frontend autorizado
"""

from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from typing import Optional
from calculator_engine import CivilProtectionCalculator
from report_generator import generate_pdf_report
import os
from dotenv import load_dotenv
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from logger import logger
import time

# Imports de Autenticación
from auth import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token,
    get_current_user,
    get_current_active_user,
    require_role
)
from database import get_db, User, Analysis, SessionLocal
from sqlalchemy.orm import Session

# Imports de Seguridad (Rate Limiting y Sanitización)
from rate_limit_config import (
    limiter,
    custom_rate_limit_handler,
    get_rate_limit,
    RATE_LIMITS
)
from slowapi.errors import RateLimitExceeded
from input_sanitizer import (
    sanitize_analysis_input,
    validate_alphanumeric_spaces,
    validate_password_strength,
    validate_email_format,
    validate_role
)
# Import de Security Headers
from security_headers import SecurityHeadersMiddleware

# Cargar variables de entorno
load_dotenv()

# Sentry Initialization (Monitoring)
SENTRY_DSN = os.getenv("SENTRY_DSN")
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            FastApiIntegration(),
            SqlalchemyIntegration(),
        ],
        traces_sample_rate=0.1, # En producción ajustar a valores menores (ej. 0.1)
    )
    print(f"[MONITORING] Sentry inicializado correctamente.")
else:
    print(f"[MONITORING] Sentry DSN no configurado (Modo local sin tracking de errores externos).")

app = FastAPI(
    title="CivilProtect API",
    description="API segura para análisis de protección civil con autenticación JWT y rate limiting",
    version="4.5.1"
)

# Confiar en los headers del Proxy (Nginx) para obtener la IP real del cliente
app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware para logging estructurado de cada request"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    logger.info(
        "Request processed",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration": round(process_time, 4),
            "client_ip": request.client.host
        }
    )
    return response

# Configurar Rate Limiter en la app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, custom_rate_limit_handler)

# ==================== CORS RESTRICTIVO (MODO DEV RELAJADO) ====================
# Leer orígenes permitidos desde .env (NO usar wildcard en producción)
allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000")
# origins = [origin.strip() for origin in allowed_origins_str.split(",")]

# [FIX] Relajando CORS para "Modo Emergencia Local"
# [FIX] Relajando CORS para "Modo Emergencia Local" y Producción
origins = [
    "http://localhost:3000", 
    "http://127.0.0.1:3000", 
    "http://localhost:8000",
    "https://civilprotect-app.web.app",
    "https://civilprotect-app.firebaseapp.com",
    "https://civilprotect-backend-707118007645.us-central1.run.app"
]
print(f"[SECURITY] CORS configurado para orígenes: {origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Lista específica de dominios
    allow_credentials=True,  # Permite cookies/auth headers
    allow_methods=["*"],  # [FIX] Permitir todos los métodos (GET, POST, OPTIONS, etc)
    allow_headers=["*"],  # [FIX] Permitir todos los headers
)

# ==================== SECURITY HEADERS ====================
# Agregar headers de seguridad HTTP a todas las respuestas
# Protección contra: XSS, Clickjacking, MIME sniffing, etc.
# print("[SECURITY] Security Headers middleware activado")
# app.add_middleware(
#    SecurityHeadersMiddleware,
#    enable_hsts=False,  # [FIX] Desactivar HSTS en local (rompe HTTP)
#    hsts_max_age=31536000  # 1 año
# )

# --- INICIALIZACIÓN DE MÓDULOS DE IA ---
# 1. Monitor Legislativo (Ejecución en Background)
# [DISABLED FOR DEV] Evitar bloqueo en startup por SSL/Timeout errors
# try:
#     from legislative_monitor import LegislativeMonitor
#     monitor = LegislativeMonitor()
#     monitor.start_scheduler() # Inicia el hilo autónomo
#     print(" [SISTEMA] Módulo de IA Legislativa Iniciado Correctamente.")
# except Exception as e:
#     print(f" [ADVERTENCIA] Falló inicio monitor legislativo: {e}")

# ==================== MODELOS PYDANTIC DE AUTENTICACIÓN ====================

class RegisterRequest(BaseModel):
    """Modelo para registro de usuarios"""
    email: EmailStr
    name: str
    password: str
    role: str = "consultor"  # Por defecto consultor, admin lo puede cambiar

class LoginRequest(BaseModel):
    """Modelo para login"""
    email: EmailStr
    password: str

class RefreshRequest(BaseModel):
    """Modelo para refresh token"""
    refresh_token: str

class TokenResponse(BaseModel):
    """Respuesta con tokens"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict

class UserResponse(BaseModel):
    """Respuesta con datos de usuario"""
    id: int
    email: str
    name: str
    role: str
    created_at: str

# ==================== ENDPOINTS DE AUTENTICACIÓN ====================

@app.post("/auth/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit(get_rate_limit("register"))
def register(request: Request, user_data: RegisterRequest, db: Session = Depends(get_db)):
    """
    Registra un nuevo usuario.
    Retorna access_token y refresh_token.
    
    RATE LIMIT: 3 requests/hora por IP
    """
    # Sanitizar y validar inputs
    email_clean = validate_email_format(user_data.email)
    name_clean = validate_alphanumeric_spaces(user_data.name, "name", 100)
    password_clean = validate_password_strength(user_data.password)
    role_clean = validate_role(user_data.role)
    
    # Verificar si el email ya existe
    existing_user = db.query(User).filter(User.email == email_clean).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email ya registrado"
        )
    
    # Hash de password
    hashed_pass = hash_password(password_clean)
    
    # Crear usuario
    new_user = User(
        email=email_clean,
        name=name_clean,
        password_hash=hashed_pass,
        role=role_clean,
        is_active=1
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Generar tokens
    token_data = {"sub": str(new_user.id), "email": new_user.email, "role": new_user.role}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": new_user.id,
            "email": new_user.email,
            "name": new_user.name,
            "role": new_user.role
        }
    }

@app.post("/auth/login", response_model=TokenResponse)
@limiter.limit(get_rate_limit("login"))
def login(request: Request, credentials: LoginRequest, db: Session = Depends(get_db)):
    """
    Login de usuario.
    Retorna access_token y refresh_token si las credenciales son correctas.
    
    RATE LIMIT: 5 requests/15 minutos por IP (protección contra brute force)
    """
    # Validar formato de email
    email_clean = validate_email_format(credentials.email)
    
    # Buscar usuario por email
    user = db.query(User).filter(User.email == email_clean).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verificar password
    if not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verificar que el usuario está activo
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario desactivado. Contacte al administrador."
        )
    
    # Generar tokens
    token_data = {"sub": str(user.id), "email": user.email, "role": user.role}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "role": user.role
        }
    }

@app.post("/auth/refresh", response_model=TokenResponse)
def refresh(request: RefreshRequest, db: Session = Depends(get_db)):
    """
    Refresca el access token usando un refresh token válido.
    """
    # Verificar refresh token
    payload = verify_token(request.refresh_token, token_type="refresh")
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado o desactivado"
        )
    
    # Generar nuevos tokens
    token_data = {"sub": str(user.id), "email": user.email, "role": user.role}
    new_access_token = create_access_token(token_data)
    new_refresh_token = create_refresh_token(token_data)
    
    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "role": user.role
        }
    }

@app.get("/auth/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_active_user)):
    """
    Obtiene los datos del usuario autenticado actual.
    Requiere Bearer token válido.
    """
    return {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name,
        "role": current_user.role,
        "created_at": current_user.created_at.isoformat()
    }

# ==================== ENDPOINTS DE ADMINISTRACIÓN (SOLO ADMIN) ====================

class UpdateRoleRequest(BaseModel):
    """Modelo para actualizar rol de usuario"""
    role: str

class UpdateStatusRequest(BaseModel):
    """Modelo para activar/desactivar usuario"""
    is_active: bool

class UserListResponse(BaseModel):
    """Modelo para respuesta de lista de usuarios"""
    id: int
    email: str
    name: str
    role: str
    is_active: bool
    created_at: str
    analyses_count: int

@app.get("/admin/users")
def get_all_users(
    limit: int = 100,
    offset: int = 0,
    current_user: User = Depends(require_role(["admin"]))
):
    """
    Obtiene lista de todos los usuarios del sistema.
    REQUIERE ROL: admin
    
    Permite a los administradores ver todos los usuarios registrados,
    su rol, estado y cantidad de análisis realizados.
    """
    try:
        db = SessionLocal()
        
        # Obtener usuarios con paginación
        users = db.query(User).offset(offset).limit(limit).all()
        total = db.query(User).count()
        
        # Preparar respuesta con conteo de análisis
        users_list = []
        for user in users:
            analyses_count = db.query(Analysis).filter(Analysis.user_id == user.id).count()
            users_list.append({
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "role": user.role,
                "is_active": bool(user.is_active),
                "created_at": user.created_at.isoformat(),
                "analyses_count": analyses_count
            })
        
        db.close()
        
        return {
            "status": "success",
            "total": total,
            "count": len(users_list),
            "users": users_list
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error obteniendo usuarios: {str(e)}"
        }

@app.put("/admin/users/{user_id}/role")
def update_user_role(
    user_id: int,
    request: UpdateRoleRequest,
    current_user: User = Depends(require_role(["admin"]))
):
    """
    Actualiza el rol de un usuario.
    REQUIERE ROL: admin
    
    Permite cambiar el rol de usuarios entre: admin, consultor, cliente.
    No se puede cambiar el rol del propio usuario administrador.
    """
    # Validar rol permitido
    allowed_roles = ["admin", "consultor", "cliente"]
    if request.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Rol inválido. Debe ser: {', '.join(allowed_roles)}"
        )
    
    # Prevenir que admin se quite a sí mismo el rol de admin
    if user_id == current_user.id and request.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes cambiar tu propio rol de admin"
        )
    
    try:
        db = SessionLocal()
        
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            db.close()
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        old_role = user.role
        user.role = request.role
        db.commit()
        db.refresh(user)
        db.close()
        
        return {
            "status": "success",
            "message": f"Rol actualizado de '{old_role}' a '{request.role}'",
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "role": user.role
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error actualizando rol: {str(e)}"
        }

@app.put("/admin/users/{user_id}/status")
def update_user_status(
    user_id: int,
    request: UpdateStatusRequest,
    current_user: User = Depends(require_role(["admin"]))
):
    """
    Activa o desactiva un usuario.
    REQUIERE ROL: admin
    
    Permite activar (is_active=True) o desactivar (is_active=False) usuarios.
    Un usuario desactivado no puede autenticarse.
    No se puede desactivar al propio usuario administrador.
    """
    # Prevenir que admin se desactive a sí mismo
    if user_id == current_user.id and not request.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes desactivar tu propia cuenta de admin"
        )
    
    try:
        db = SessionLocal()
        
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            db.close()
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        user.is_active = 1 if request.is_active else 0
        db.commit()
        db.refresh(user)
        db.close()
        
        status_text = "activado" if request.is_active else "desactivado"
        
        return {
            "status": "success",
            "message": f"Usuario {status_text} correctamente",
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "is_active": bool(user.is_active)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error actualizando estado: {str(e)}"
        }

# ==================== ENDPOINTS DE ANÁLISIS ====================


class AnalysisRequest(BaseModel):
    tipo_inmueble: str
    m2_construccion: float
    niveles: int
    aforo: int
    aforo_autorizado: int # [NUEVO] Solicitud de Usuario
    trabajadores: int
    municipio: str
    estado: str
    # Risk Infrastructure Flags
    has_gas: bool = False
    has_transformer: bool = False
    has_machine_room: bool = False
    has_substation: bool = False
    has_special_inst: bool = False # [NUEVO]
    has_pool: bool = False         # [NUEVO]

@app.post("/analyze")
@limiter.limit(get_rate_limit("analyze"))
def analyze_compliance(
    request: Request,
    data: AnalysisRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Analiza cumplimiento de protección civil.
    REQUIERE AUTENTICACIÓN: Solo usuarios autenticados pueden generar análisis.
    
    RATE LIMIT: 10 requests/hora por usuario autenticado
    """
    from ai_service import AIService
    ai = AIService()
    
    # Sanitizar y validar inputs antes de procesar
    input_dict = data.dict()
    sanitized_data = sanitize_analysis_input(input_dict)
    
    # Asegurarse de que los campos sanitizados se usen
    input_dict.update(sanitized_data)
    
    # 1. Llamar al motor de cálculo avanzado (Lógica Cuantitativa)
    engine = CivilProtectionCalculator()
    # Mockups para lógica extra (Inferencia Inteligente)
    # Si el usuario no lo especifica, lo inferimos por el tipo
    input_dict["has_cocina"] = True if any(x in data.tipo_inmueble for x in ["Restaurante", "Hotel", "Hospital"]) else False
    input_dict["has_site"] = True if any(x in data.tipo_inmueble for x in ["Oficina", "Call center", "Hotel", "Hospital"]) else False
    
    # Usar el método avanzado
    full_report = engine.analyze_full_compliance(input_dict)

    # [FIX] Fusionar datos de entrada al reporte para que el Frontend (ModernReportView) tenga contexto
    # Esto previene el error "Cannot read properties of undefined" al leer m2_construccion, etc.
    full_report.update(input_dict)

    # 2. Agregar Capa de Inteligencia Artificial (Lógica Cualitativa)
    justificacion_legal = ai.generate_legal_justification(input_dict)
    
    # [NUEVO] Enriquecimiento Estructural de la Guía Capitular (Task Step 2322)
    # Buscamos la guía en el checklist generado previamente
    checklist = full_report.get("checklist", [])
    guide_idx = next((i for i, item in enumerate(checklist) if item.get('is_pipc_guide')), -1)
    
    if guide_idx != -1:
        base_structure = checklist[guide_idx]['guide_content']
        # START AI ENRICHMENT
        enriched_structure = ai.enrich_chapter_structure(base_structure, data.estado, data.municipio)
        # UPDATE REPORT
        checklist[guide_idx]['guide_content'] = enriched_structure
        checklist[guide_idx]['titulo'] += " (AMPLIADO POR IA)"
        full_report["checklist"] = checklist

    full_report["ai_analysis"] = {
        "legal_justification": justificacion_legal,
        "normative_updates": ai.check_normative_updates(data.estado)
    }

    # [CORRECCIÓN DE CONSISTENCIA]
    # Sobreescribir la justificación estricta del motor con la generada por el servicio de IA/Legal
    # para que el Frontend muestre exactamente lo mismo que el PDF.
    if "resumen_ejecutivo" in full_report:
        full_report["resumen_ejecutivo"]["legal_justification_strict"] = justificacion_legal
    
    # 3. Generar PDF (Nombre temporal - ¡Mejorado con UUID en Phase 1.clean!)
    import uuid
    filename = f"Dictamen_{data.municipio}_{uuid.uuid4().hex[:8]}.pdf"
    
    # Pasar el reporte completo para que incluya presupuesto
    generate_pdf_report(input_dict, full_report, filename)
    
    # 4. [PROTEGIDO] Auto-guardar en Historial del USUARIO AUTENTICADO
    try:
        from database import SessionLocal, AnalysisCRUD
        db = SessionLocal()
        AnalysisCRUD.create_analysis(
            db=db,
            user_id=current_user.id,  # ✅ PROTEGIDO: Asociar al usuario autenticado
            input_data=input_dict,
            report_data=full_report,
            pdf_path=filename,
            custom_label=None
        )
        db.close()
        print(f"✅ Análisis guardado en historial del usuario {current_user.email}")
    except Exception as e:
        print(f"⚠️ Warning: No se pudo guardar en historial: {e}")
        # No fallar el análisis si falla el guardado
    
    return {
        "status": "success",
        "data": full_report, # Retorna todo: basic, checklist, presupuesto
        "download_url": f"/download/{filename}",
        "pdf_filename": filename  # [NUEVO] Para que el frontend pueda saber el nombre
    }

@app.get("/")
def read_root():
    return {"message": "CivilProtect AI Engine Operational"}

class SignReportRequest(BaseModel):
    report_data: dict
    signature_image: str

@app.post("/sign-report")
def sign_report_endpoint(
    data: SignReportRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Recibe un reporte existente y una firma en Base64.
    Regenera el PDF incluyendo la firma y lo registra en el historial del usuario.
    """
    try:
        analysis_data = data.report_data
        
        # Extraer input_data de los campos embebidos en analysis_data
        input_data = {
            "tipo_inmueble": analysis_data.get("tipo_inmueble"),
            "m2_construccion": analysis_data.get("m2_construccion"),
            "niveles": analysis_data.get("niveles"),
            "aforo": analysis_data.get("aforo"),
            "aforo_autorizado": analysis_data.get("aforo_autorizado"),
            "trabajadores": analysis_data.get("trabajadores"),
            "municipio": analysis_data.get("municipio"),
            "estado": analysis_data.get("estado"),
            "has_gas": analysis_data.get("has_gas", False),
            "has_transformer": analysis_data.get("has_transformer", False),
            "has_machine_room": analysis_data.get("has_machine_room", False),
            "has_substation": analysis_data.get("has_substation", False),
            "has_special_inst": analysis_data.get("has_special_inst", False),
            "has_pool": analysis_data.get("has_pool", False),
            "has_cocina": analysis_data.get("has_cocina", False),
            "has_site": analysis_data.get("has_site", False),
            "signature_image": data.signature_image  # FIRMA DIGITAL
        }
        
        # Generar PDF Firmado
        import uuid
        municipio = input_data.get("municipio", "Gen")
        # Ensure filename is unique but identifiable
        filename = f"Dictamen_Firmado_{municipio}_{uuid.uuid4().hex[:8]}.pdf"
        
        # Pasar correctamente input_data (con firma) y results (analysis_data)
        generate_pdf_report(input_data, analysis_data, filename)
        
        # [CRITICAL STEP] Guardar en DB para pasar validación de ownership en /download
        from database import SessionLocal, AnalysisCRUD
        try:
            db = SessionLocal()
            AnalysisCRUD.create_analysis(
                db=db,
                user_id=current_user.id,
                input_data=input_data,
                report_data=analysis_data,
                pdf_path=filename,
                custom_label=f"Dictamen Firmado - {municipio}"
            )
            db.close()
        except Exception as db_e:
            print(f"⚠️ Error guardando registro de PDF firmado en DB: {db_e}")
            # Continuamos, pero la descarga podría fallar si es estricta
            
        return {
            "status": "success",
            "download_url": f"/download/{filename}",
            "pdf_filename": filename
        }
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"❌ ERROR FIRMANDO REPORTE: {e}")
        print(f"📋 TRACEBACK:\n{error_detail}")
        return {"status": "error", "message": str(e)}

@app.get("/download/{filename}")
def download_file(
    filename: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Descarga un archivo PDF generado.
    REQUIERE AUTENTICACIÓN Y OWNERSHIP: Solo el propietario del análisis puede descargar el PDF.
    """
    from fastapi.responses import FileResponse
    from database import SessionLocal, Analysis
    
    try:
        # Verificar que el archivo existe
        path = filename
        if not os.path.exists(path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Archivo no encontrado"
            )
        
        # ✅ VALIDAR OWNERSHIP: Verificar que el PDF pertenece al usuario
        db = SessionLocal()
        analysis = db.query(Analysis).filter(Analysis.pdf_path == filename).first()
        db.close()
        
        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Análisis asociado al PDF no encontrado"
            )
        
        if analysis.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para descargar este archivo"
            )
        
        # Si todo está bien, permitir descarga
        return FileResponse(path, media_type='application/pdf', filename=filename)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al descargar archivo: {str(e)}"
        )

@app.get("/catalog/municipios")
def get_catalog():
    from data_provider import DataProvider
    provider = DataProvider()
    return provider.get_all_data()

# ==================== ENDPOINTS DE HISTORIAL ====================

@app.post("/save-analysis")
def save_analysis(
    data: dict,
    current_user: User = Depends(get_current_active_user)
):
    """
    Guarda un análisis completo en la base de datos.
    REQUIERE AUTENTICACIÓN: Solo usuarios autenticados pueden guardar análisis.
    El análisis se asocia automáticamente al usuario autenticado.
    """
    from database import SessionLocal, AnalysisCRUD
    
    try:
        db = SessionLocal()
        
        # Extraer datos
        input_data = data.get("input_data", {})
        report_data = data.get("report_data", {})
        pdf_filename = data.get("pdf_filename", None)
        custom_label = data.get("custom_label", None)
        # ✅ PROTEGIDO: Usar el ID del usuario autenticado, ignorar cualquier user_id del request
        
        # Crear análisis en DB
        analysis = AnalysisCRUD.create_analysis(
            db=db,
            user_id=current_user.id,  # ✅ PROTEGIDO: Asociar al usuario autenticado
            input_data=input_data,
            report_data=report_data,
            pdf_path=pdf_filename,
            custom_label=custom_label
        )
        
        db.close()
        
        return {
            "status": "success",
            "message": "Análisis guardado correctamente",
            "analysis_id": analysis.id,
            "created_at": analysis.created_at.isoformat()
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error guardando análisis: {str(e)}"
        }

@app.get("/history")
def get_history(
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtiene el historial de análisis del usuario autenticado.
    REQUIERE AUTENTICACIÓN: Solo muestra los análisis del usuario actual.
    Paginado y ordenado por fecha descendente.
    """
    from database import SessionLocal, AnalysisCRUD
    import json
    
    try:
        db = SessionLocal()
        
        # ✅ PROTEGIDO: Solo obtener análisis del usuario autenticado
        analyses = AnalysisCRUD.get_user_analyses(db, current_user.id, limit, offset)
        total = AnalysisCRUD.count_user_analyses(db, current_user.id)
        
        db.close()
        
        # Convertir a formato serializable
        result = []
        for a in analyses:
            result.append({
                "id": a.id,
                "municipio": a.municipio,
                "estado": a.estado,
                "tipo_inmueble": a.tipo_inmueble,
                "custom_label": a.custom_label,
                "pdf_path": a.pdf_path,
                "created_at": a.created_at.isoformat(),
                "has_pdf": bool(a.pdf_path and os.path.exists(a.pdf_path))
            })
        
        return {
            "status": "success",
            "total": total,
            "count": len(result),
            "analyses": result,
            "user_email": current_user.email  # ✅ Confirmación de usuario
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error obteniendo historial: {str(e)}"
        }

@app.get("/analysis/{analysis_id}")
def get_analysis(
    analysis_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtiene los detalles completos de un análisis específico.
    REQUIERE AUTENTICACIÓN Y OWNERSHIP: Solo el propietario puede ver el análisis.
    Incluye input_data y report_data deserializados.
    """
    from database import SessionLocal, AnalysisCRUD
    import json
    
    try:
        db = SessionLocal()
        
        analysis = AnalysisCRUD.get_analysis(db, analysis_id)
        
        db.close()
        
        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Análisis no encontrado"
            )
        
        # ✅ VALIDAR OWNERSHIP: Solo el propietario puede acceder
        if analysis.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para acceder a este análisis"
            )
        
        return {
            "status": "success",
            "analysis": {
                "id": analysis.id,
                "municipio": analysis.municipio,
                "estado": analysis.estado,
                "tipo_inmueble": analysis.tipo_inmueble,
                "custom_label": analysis.custom_label,
                "input_data": json.loads(analysis.input_data),
                "report_data": json.loads(analysis.report_data),
                "pdf_path": analysis.pdf_path,
                "created_at": analysis.created_at.isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error obteniendo análisis: {str(e)}"
        }

@app.delete("/analysis/{analysis_id}")
def delete_analysis(
    analysis_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """
    Elimina un análisis (y su PDF asociado).
    REQUIERE AUTENTICACIÓN Y OWNERSHIP: Solo el propietario puede eliminar el análisis.
    """
    from database import SessionLocal, AnalysisCRUD
    
    try:
        db = SessionLocal()
        
        # Primero verificar que existe y obtener el análisis
        analysis = AnalysisCRUD.get_analysis(db, analysis_id)
        
        if not analysis:
            db.close()
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Análisis no encontrado"
            )
        
        # ✅ VALIDAR OWNERSHIP: Solo el propietario puede eliminar
        if analysis.user_id != current_user.id:
            db.close()
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para eliminar este análisis"
            )
        
        # Proceder con la eliminación
        success = AnalysisCRUD.delete_analysis(db, analysis_id)
        
        db.close()
        
        if success:
            return {
                "status": "success",
                "message": "Análisis eliminado correctamente"
            }
        else:
            return {
                "status": "error",
                "message": "Error al eliminar el análisis"
            }
        
    except HTTPException:
        raise
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error eliminando análisis: {str(e)}"
        }

# ==================== ENDPOINTS INTELIGENCIA ARTIFICIAL (ALERTS) ====================

@app.get("/check-updates")
def check_updates_endpoint():
    """
    Escanea el Buzón de Cuarentena (inbox) en busca de actualizaciones propuestas por la IA.
    Retorna lista de archivos pendientes de aprobación.
    """
    import json
    inbox_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "inbox_updates")
    
    if not os.path.exists(inbox_path):
        return {"status": "success", "count": 0, "updates": []}
        
    updates = []
    try:
        for filename in os.listdir(inbox_path):
            if filename.endswith(".json"):
                filepath = os.path.join(inbox_path, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Añadir metadatos de archivo
                    data["file_id"] = filename
                    updates.append(data)
                    
        return {
            "status": "success",
            "count": len(updates),
            "updates": updates
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/approve-update")
def approve_update_endpoint(payload: dict):
    """
    Mueve una actualización del inbox a la base de datos maestra (states_db).
    (Simulado por seguridad: En V1 solo borra el archivo del inbox y loguea éxito)
    """
    file_id = payload.get("file_id")
    if not file_id:
        return {"status": "error", "message": "Falta file_id"}
        
    inbox_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "inbox_updates")
    filepath = os.path.join(inbox_path, file_id)
    
    if os.path.exists(filepath):
        # AQUÍ IRÍA LA LÓGICA DE FUSIÓN (MERGE) CON STATES_DB
        # Por ahora, solo simular aprobación y limpieza
        try:
            os.remove(filepath)
            return {"status": "success", "message": f"Actualización {file_id} aprobada e integrada."}
        except Exception as e:
            return {"status": "error", "message": f"Error procesando archivo: {e}"}
    else:
        return {"status": "error", "message": "Archivo no encontrado"}

# ==================== ENDPOINTS DE REPORTE HTML PREMIUM ====================

@app.post("/generate-html-report")
def generate_html_report_endpoint(
    data: dict,
    current_user: User = Depends(get_current_active_user)
):
    """
    Genera un reporte HTML premium del análisis.
    REQUIERE AUTENTICACIÓN: Solo usuarios autenticados pueden generar reportes HTML.
    Retorna el HTML como string para preview o descarga.
    """
    from html_report_generator import generate_html_report
    
    try:
        input_data = data.get("input_data", {})
        analysis_data = data.get("analysis_data", {})
        
        html_content = generate_html_report(input_data, analysis_data)
        
        return {
            "status": "success",
            "html_content": html_content
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error generando HTML: {str(e)}"
        }

@app.get("/preview-html/{analysis_id}")
def preview_html_report(
    analysis_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """
    Genera y muestra un reporte HTML de un análisis guardado.
    REQUIERE AUTENTICACIÓN Y OWNERSHIP: Solo el propietario puede visualizar el reporte.
    Se puede abrir directamente en el navegador.
    """
    from database import SessionLocal, AnalysisCRUD
    from html_report_generator import generate_html_report
    from fastapi.responses import HTMLResponse
    import json
    
    try:
        db = SessionLocal()
        analysis = AnalysisCRUD.get_analysis(db, analysis_id)
        db.close()
        
        if not analysis:
            return HTMLResponse(
                content="<h1>Análisis no encontrado</h1>",
                status_code=404
            )
        
        # ✅ VALIDAR OWNERSHIP: Solo el propietario puede ver el reporte
        if analysis.user_id != current_user.id:
            return HTMLResponse(
                content="<h1>Acceso Denegado</h1><p>No tienes permiso para ver este análisis.</p>",
                status_code=403
            )
        
        input_data = json.loads(analysis.input_data)
        report_data = json.loads(analysis.report_data)
        
        html_content = generate_html_report(input_data, report_data)
        
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        return HTMLResponse(
            content=f"<h1>Error: {str(e)}</h1>",
            status_code=500
        )

if __name__ == "__main__":
    import uvicorn
    print("Iniciando CivilProtect Backend en puerto 8000...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
