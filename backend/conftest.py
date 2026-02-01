"""
Pytest Configuration and Fixtures
Fixtures comunes para todos los tests
"""
import pytest
import os
import sys
from typing import Generator
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Testing imports
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import responses
from faker import Faker

# App imports
from main import app
from database import Base, get_db
from auth import create_access_token, get_password_hash


# ==================== DATABASE FIXTURES ====================

@pytest.fixture(scope="function")
def test_db() -> Generator[Session, None, None]:
    """
    Fixture de base de datos de testing (in-memory SQLite).
    Crea una nueva BD por cada test para aislamiento completo.
    
    Yields:
        Session: Sesión de SQLAlchemy para el test
    """
    # Crear engine in-memory
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    # Crear todas las tablas
    Base.metadata.create_all(bind=engine)
    
    # Crear sessionmaker
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Crear sesión
    db = TestingSessionLocal()
    
    try:
        yield db
    finally:
        db.close()
        # Drop todas las tablas después del test
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(test_db: Session) -> Generator[TestClient, None, None]:
    """
    Fixture de TestClient de FastAPI con BD de testing.
    
    Args:
        test_db: Fixture de base de datos
        
    Yields:
        TestClient: Cliente de testing de FastAPI
    """
    # Override de dependency de BD
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Limpiar overrides
    app.dependency_overrides.clear()


# ==================== USER FIXTURES ====================

@pytest.fixture
def fake() -> Faker:
    """
    Fixture de Faker para generar datos falsos.
    
    Returns:
        Faker: Instancia de Faker
    """
    return Faker()


@pytest.fixture
def user_data(fake: Faker) -> dict:
    """
    Fixture de datos de usuario para testing.
    
    Args:
        fake: Fixture de Faker
        
    Returns:
        dict: Datos de usuario válidos
    """
    return {
        "email": fake.email(),
        "password": "Test123!",
        "name": fake.name(),
        "role": "user"
    }


@pytest.fixture
def admin_user_data(fake: Faker) -> dict:
    """
    Fixture de datos de usuario admin para testing.
    
    Args:
        fake: Fixture de Faker
        
    Returns:
        dict: Datos de usuario admin válidos
    """
    return {
        "email": fake.email(),
        "password": "Admin123!",
        "name": fake.name(),
        "role": "admin"
    }


@pytest.fixture
def created_user(client: TestClient, user_data: dict) -> dict:
    """
    Fixture de usuario creado en la BD de testing.
    
    Args:
        client: Fixture de TestClient
        user_data: Fixture de datos de usuario
        
    Returns:
        dict: Usuario creado con access_token
    """
    response = client.post("/auth/register", json=user_data)
    assert response.status_code == 201
    data = response.json()
    
    return {
        **user_data,
        "access_token": data["access_token"],
        "user_id": data.get("user_id")
    }


@pytest.fixture
def created_admin(client: TestClient, admin_user_data: dict) -> dict:
    """
    Fixture de usuario admin creado en la BD de testing.
    
    Args:
        client: Fixture de TestClient
        admin_user_data: Fixture de datos de admin
        
    Returns:
        dict: Admin creado con access_token
    """
    response = client.post("/auth/register", json=admin_user_data)
    assert response.status_code == 201
    data = response.json()
    
    return {
        **admin_user_data,
        "access_token": data["access_token"],
        "user_id": data.get("user_id")
    }


@pytest.fixture
def auth_headers(created_user: dict) -> dict:
    """
    Fixture de headers de autenticación para requests.
    
    Args:
        created_user: Fixture de usuario creado
        
    Returns:
        dict: Headers con Authorization Bearer token
    """
    return {
        "Authorization": f"Bearer {created_user['access_token']}"
    }


@pytest.fixture
def admin_auth_headers(created_admin: dict) -> dict:
    """
    Fixture de headers de autenticación de admin.
    
    Args:
        created_admin: Fixture de admin creado
        
    Returns:
        dict: Headers con Authorization Bearer token de admin
    """
    return {
        "Authorization": f"Bearer {created_admin['access_token']}"
    }


# ==================== ANALYSIS DATA FIXTURES ====================

@pytest.fixture
def valid_analysis_data() -> dict:
    """
    Fixture de datos de análisis válidos para testing.
    
    Returns:
        dict: Datos de análisis completos y válidos
    """
    return {
        "municipio": "Guadalajara",
        "estado": "Jalisco",
        "nombre_inmueble": "Centro Comercial Plaza Test",
        "domicilio": "Av. Test 123, Col. Testing",
        "m2_construccion": 1500.0,
        "aforo_autorizado": 250,
        "nivel_riesgo": "ordinario",
        "niveles_edificio": 2,
        "secciones": 1,
        "altura_niveles": 3.5,
        "actividad_preponderante": "Comercio",
        "descripcion_breve": "Centro comercial de prueba"
    }


@pytest.fixture
def invalid_analysis_data() -> dict:
    """
    Fixture de datos de análisis inválidos para testing de validación.
    
    Returns:
        dict: Datos de análisis con valores inválidos
    """
    return {
        "municipio": "<script>alert('xss')</script>",  # XSS attempt
        "estado": "Jalisco",
        "m2_construccion": -100,  # Negativo (inválido)
        "aforo_autorizado": 0,  # Cero (inválido)
        "nivel_riesgo": "invalido"  # Valor no permitido
    }


@pytest.fixture
def edge_case_analysis_data() -> dict:
    """
    Fixture de datos de análisis con edge cases.
    
    Returns:
        dict: Datos de análisis con valores límite
    """
    return {
        "municipio": "Test",
        "estado": "Test",
        "nombre_inmueble": "Edge Case Building",
        "m2_construccion": 0.1,  # Muy pequeño
        "aforo_autorizado": 1,  # Mínimo
        "nivel_riesgo": "ordinario",
        "niveles_edificio": 1,  # Mínimo
        "secciones": 1
    }


@pytest.fixture
def large_analysis_data() -> dict:
    """
    Fixture de datos de análisis de inmueble grande (>2000m²).
    Debe triggear cálculo de hidrantes.
    
    Returns:
        dict: Datos de análisis de inmueble grande
    """
    return {
        "municipio": "Guadalajara",
        "estado": "Jalisco",
        "nombre_inmueble": "Mega Plaza Test",
        "m2_construccion": 3500.0,  # > 2000m² → hidrantes
        "aforo_autorizado": 800,
        "nivel_riesgo": "alto",
        "niveles_edificio": 4,
        "secciones": 2,
        "altura_niveles": 4.0
    }


# ==================== MOCK FIXTURES ====================

@pytest.fixture
def mock_openai_response():
    """
    Fixture para mockear respuestas de OpenAI API.
    
    Yields:
        responses.RequestsMock: Mock activado
    """
    with responses.RequestsMock() as rsps:
        # Mock de chat completion
        rsps.add(
            responses.POST,
            "https://api.openai.com/v1/chat/completions",
            json={
                "id": "chatcmpl-test",
                "object": "chat.completion",
                "created": 1234567890,
                "model": "gpt-4",
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": "Contenido enriquecido por IA de prueba"
                        },
                        "finish_reason": "stop"
                    }
                ],
                "usage": {
                    "prompt_tokens": 50,
                    "completion_tokens": 100,
                    "total_tokens": 150
                }
            },
            status=200
        )
        
        yield rsps


@pytest.fixture
def disable_rate_limiting(monkeypatch):
    """
    Fixture para deshabilitar rate limiting durante tests.
    
    Args:
        monkeypatch: Fixture de pytest para monkeypatching
    """
    # Mockear limiter para que no limite
    from rate_limit_config import limiter
    
    def mock_limit(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    
    monkeypatch.setattr(limiter, "limit", mock_limit)


# ==================== ENVIRONMENT FIXTURES ====================

@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    """
    Fixture de setup del entorno de testing.
    Se ejecuta una vez por sesión de testing.
    
    Configura variables de entorno necesarias.
    """
    # Setear variables de entorno para testing
    os.environ["ENV"] = "testing"
    os.environ["DEBUG"] = "True"
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    os.environ["OPENAI_API_KEY"] = "sk-test-key-for-testing-only"
    
    # JWT secret de testing
    if "JWT_SECRET_KEY" not in os.environ:
        os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-testing-only-not-for-production"
    
    yield
    
    # Cleanup después de todos los tests
    pass


@pytest.fixture
def temp_pdf_dir(tmp_path):
    """
    Fixture de directorio temporal para PDFs de testing.
    
    Args:
        tmp_path: Fixture de pytest para path temporal
        
    Returns:
        Path: Path al directorio temporal
    """
    pdf_dir = tmp_path / "pdfs"
    pdf_dir.mkdir()
    return pdf_dir


# ==================== HELPER FIXTURES ====================

@pytest.fixture
def capture_logs(caplog):
    """
    Fixture para capturar logs durante tests.
    
    Args:
        caplog: Fixture de pytest para caplog
        
    Returns:
        caplog: Configurado para nivel DEBUG
    """
    import logging
    caplog.set_level(logging.DEBUG)
    return caplog


# ==================== MARKERS ALIASES ====================

def pytest_configure(config):
    """
    Configuración adicional de pytest.
    Registrar markers custom.
    """
    config.addinivalue_line(
        "markers", "smoke: Smoke tests (critical functionality)"
    )
    config.addinivalue_line(
        "markers", "regression: Regression tests"
    )


# ==================== TEST SELECTION HELPERS ====================

def pytest_collection_modifyitems(config, items):
    """
    Modificar items de testing recolectados.
    Agregar markers automáticamente basado en nombre de archivo.
    """
    for item in items:
        # Agregar marker basado en nombre de archivo
        if "calculator" in item.nodeid:
            item.add_marker(pytest.mark.calculator)
        
        if "test_api" in item.nodeid or "endpoints" in item.nodeid:
            item.add_marker(pytest.mark.api)
        
        if "database" in item.nodeid or "test_db" in item.nodeid:
            item.add_marker(pytest.mark.database)
        
        if "report" in item.nodeid:
            item.add_marker(pytest.mark.report)
        
        if "auth" in item.nodeid or "security" in item.nodeid:
            item.add_marker(pytest.mark.security)
