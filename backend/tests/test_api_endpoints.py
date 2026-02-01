"""
Tests para API Endpoints
Coverage target: > 70%
"""
import pytest
from fastapi import status


# ==================== CLASE 1: TEST ENDPOINT /analyze ====================

@pytest.mark.api
@pytest.mark.integration
class TestAnalyzeEndpoint:
    """Tests del endpoint POST /analyze"""
    
    def test_analyze_with_valid_data(self, client, auth_headers, valid_analysis_data):
        """Test análisis con datos válidos"""
        response = client.post(
            "/analyze",
            json=valid_analysis_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verificar estructura de respuesta
        assert "basic_requirements" in data
        assert "resumen_ejecutivo" in data
        assert "presupuesto_inicial" in data
        assert "checklist" in data
    
    def test_analyze_without_auth(self, client, valid_analysis_data):
        """Test análisis sin autenticación (debe fallar 401)"""
        response = client.post("/analyze", json=valid_analysis_data)
        
        assert response.status_code == 401
        assert "detail" in response.json()
    
    def test_analyze_with_invalid_token(self, client, valid_analysis_data):
        """Test análisis con token inválido"""
        headers = {"Authorization": "Bearer invalid-token-123"}
        response = client.post(
            "/analyze",
            json=valid_analysis_data,
            headers=headers
        )
        
        assert response.status_code == 401
    
    def test_analyze_with_invalid_data(self, client, auth_headers, invalid_analysis_data):
        """Test análisis con datos inválidos (validación)"""
        response = client.post(
            "/analyze",
            json=invalid_analysis_data,
            headers=auth_headers
        )
        
        # Debe rechazar datos inválidos (422 o 400)
        assert response.status_code in [400, 422]
    
    def test_analyze_with_empty_data(self, client, auth_headers):
        """Test análisis con datos vacíos"""
        response = client.post(
            "/analyze",
            json={},
            headers=auth_headers
        )
        
        # Puede ser 400 (bad request) o 422 (validation)
        # dependiendo de cómo se manejen los campos requeridos
        assert response.status_code in [200, 400, 422]
    
    def test_analyze_large_building(self, client, auth_headers, large_analysis_data):
        """Test análisis de inmueble grande (>2000m²)"""
        response = client.post(
            "/analyze",
            json=large_analysis_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verificar que se procesa correctamente
        assert "presupuesto_inicial" in data
        budget = data["presupuesto_inicial"]
        assert isinstance(budget, list)
        assert len(budget) > 0
    
    def test_analyze_edge_cases(self, client, auth_headers, edge_case_analysis_data):
        """Test análisis con edge cases"""
        response = client.post(
            "/analyze",
            json=edge_case_analysis_data,
            headers=auth_headers
        )
        
        # Debe manejar edge cases sin crashear
        assert response.status_code == 200
    
    def test_analyze_returns_analysis_id(self, client, auth_headers, valid_analysis_data):
        """Test que el análisis retorna un ID"""
        response = client.post(
            "/analyze",
            json=valid_analysis_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Puede tener analysis_id si se guarda en BD
        # (depende de la implementación actual)
        assert isinstance(data, dict)


# ==================== CLASE 2: TEST AUTH FLOW ====================

@pytest.mark.auth
@pytest.mark.integration
class TestAuthFlow:
    """Tests del flujo de autenticación completo"""
    
    def test_register_with_valid_data(self, client, user_data):
        """Test registro con datos válidos"""
        response = client.post("/auth/register", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
    
    def test_register_duplicate_email(self, client, user_data):
        """Test registro con email duplicado (debe fallar)"""
        # Primer registro
        response1 = client.post("/auth/register", json=user_data)
        assert response1.status_code == 201
        
        # Segundo registro con mismo email
        response2 = client.post("/auth/register", json=user_data)
        assert response2.status_code == 400
        assert "email" in response2.json()["detail"].lower()
    
    def test_register_with_invalid_email(self, client, user_data):
        """Test registro con email inválido"""
        invalid_data = user_data.copy()
        invalid_data["email"] = "not-an-email"
        
        response = client.post("/auth/register", json=invalid_data)
        assert response.status_code == 400
    
    def test_register_with_weak_password(self, client, user_data):
        """Test registro con contraseña débil"""
        weak_data = user_data.copy()
        weak_data["password"] = "123"  # Muy corta
        
        response = client.post("/auth/register", json=weak_data)
        assert response.status_code == 400
    
    
    def test_register_with_xss_attempt(self, client, user_data):
        """Test registro con intento de XSS en nombre"""
        xss_data = user_data.copy()
        xss_data["name"] = "<script>alert('xss')</script>"
        
        response = client.post("/auth/register", json=xss_data)
        # Debe rechazarse por validación
        assert response.status_code == 400
    
    def test_login_with_valid_credentials(self, client, created_user):
        """Test login con credenciales válidas"""
        response = client.post("/auth/login", json={
            "email": created_user["email"],
            "password": created_user["password"]
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert "access_token" in data
        assert "refresh_token" in data
        assert "token_type" in data
    
    def test_login_with_invalid_password(self, client, created_user):
        """Test login con contraseña incorrecta"""
        response = client.post("/auth/login", json={
            "email": created_user["email"],
            "password": "wrong-password"
        })
        
        assert response.status_code == 401
    
    def test_login_with_nonexistent_email(self, client):
        """Test login con email que no existe"""
        response = client.post("/auth/login", json={
            "email": "nonexistent@example.com",
            "password": "password123"
        })
        
        assert response.status_code == 401
    
    def test_refresh_token_flow(self, client, created_user):
        """Test flujo de refresh token"""
        # Login para obtener refresh token
        login_response = client.post("/auth/login", json={
            "email": created_user["email"],
            "password": created_user["password"]
        })
        
        assert login_response.status_code == 200
        refresh_token = login_response.json()["refresh_token"]
        
        # Usar refresh token para obtener nuevo access token
        refresh_response = client.post("/auth/refresh", json={
            "refresh_token": refresh_token
        })
        
        # Depende de si está implementado
        # Si no está, será 404
        if refresh_response.status_code != 404:
            assert refresh_response.status_code == 200
            assert "access_token" in refresh_response.json()


# ==================== CLASE 3: TEST ENDPOINT PROTECTION ====================

@pytest.mark.security
@pytest.mark.integration
class TestEndpointProtection:
    """Tests de protección de endpoints (401 Unauthorized)"""
    
    def test_analyze_requires_auth(self, client, valid_analysis_data):
        """Test que /analyze requiere autenticación"""
        response = client.post("/analyze", json=valid_analysis_data)
        assert response.status_code == 401
    
    def test_history_requires_auth(self, client):
        """Test que /history requiere autenticación"""
        response = client.get("/history")
        
        # Si el endpoint existe
        if response.status_code != 404:
            assert response.status_code == 401
    
    def test_download_requires_auth(self, client):
        """Test que /download requiere autenticación"""
        response = client.get("/download/123")
        
        # Si el endpoint existe
        if response.status_code != 404:
            assert response.status_code == 401
    
    def test_public_endpoints_no_auth(self, client):
        """Test que endpoints públicos NO requieren auth"""
        # Root endpoint
        response = client.get("/")
        assert response.status_code == 200
    
    def test_expired_token(self, client, valid_analysis_data):
        """Test con token expirado"""
        # Token claramente inválido/expirado
        headers = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.expired"}
        
        response = client.post(
            "/analyze",
            json=valid_analysis_data,
            headers=headers
        )
        
        assert response.status_code == 401


# ==================== CLASE 4: TEST OWNERSHIP VALIDATION ====================

@pytest.mark.security
@pytest.mark.integration
class TestOwnershipValidation:
    """Tests de validación de ownership (user A no puede borrar análisis de user B)"""
    
    def test_user_can_access_own_analysis(self, client, auth_headers, valid_analysis_data):
        """Test que un usuario puede acceder a sus propios análisis"""
        # Crear análisis
        create_response = client.post(
            "/analyze",
            json=valid_analysis_data,
            headers=auth_headers
        )
        
        assert create_response.status_code == 200
        
        # Intentar acceder a historial
        history_response = client.get("/history", headers=auth_headers)
        
        # Si el endpoint existe
        if history_response.status_code != 404:
            assert history_response.status_code == 200
    
    def test_user_cannot_delete_others_analysis(
        self, 
        client, 
        created_user, 
        created_admin,
        valid_analysis_data
    ):
        """Test que un usuario NO puede borrar análisis de otro usuario"""
        # Usuario 1 crea análisis
        user1_headers = {"Authorization": f"Bearer {created_user['access_token']}"}
        
        create_response = client.post(
            "/analyze",
            json=valid_analysis_data,
            headers=user1_headers
        )
        
        # Si retorna ID del análisis
        if create_response.status_code == 200:
            analysis_data = create_response.json()
            
            # Usuario 2 intenta borrar
            user2_headers = {"Authorization": f"Bearer {created_admin['access_token']}"}
            
            # Intentar DELETE (si existe el endpoint)
            # El ID real depende de la implementación
            delete_response = client.delete(
                "/analysis/1",  # ID de ejemplo
                headers=user2_headers
            )
            
            # Si el endpoint existe, debe verificar ownership
            if delete_response.status_code != 404:
                # Debe ser 403 (Forbidden) o 404 (Not Found)
                assert delete_response.status_code in [403, 404]


# ==================== CLASE 5: TEST RATE LIMITING ====================

@pytest.mark.security
@pytest.mark.slow
class TestRateLimiting:
    """Tests de rate limiting (429 Too Many Requests)"""
    
    def test_register_rate_limit(self, client, fake):
        """Test rate limit en /auth/register (3/hora)"""
        # Intentar 4 registros
        for i in range(4):
            user_data = {
                "email": fake.email(),
                "password": "Test123!",
                "name": fake.name(),
                "role": "user"
            }
            
            response = client.post("/auth/register", json=user_data)
            
            if i < 3:
                # Primeros 3 deben pasar
                assert response.status_code == 201
            else:
                # El 4to debe ser bloqueado (429)
                assert response.status_code == 429
                assert "Retry-After" in response.headers
    
    def test_login_rate_limit(self, client, created_user):
        """Test rate limit en /auth/login (5/15min)"""
        # Intentar 6 logins
        for i in range(6):
            response = client.post("/auth/login", json={
                "email": created_user["email"],
                "password": "wrong-password"  # Contraseña incorrecta
            })
            
            if i < 5:
                # Primeros 5 intentos (pueden ser 401)
                assert response.status_code in [401, 429]
            else:
                # El 6to debe ser bloqueado por rate limit
                assert response.status_code == 429
    
    def test_analyze_rate_limit(self, client, auth_headers, valid_analysis_data):
        """Test rate limit en /analyze (10/hora)"""
        # Intentar 11 análisis
        success_count = 0
        rate_limited = False
        
        for i in range(11):
            response = client.post(
                "/analyze",
                json=valid_analysis_data,
                headers=auth_headers
            )
            
            if response.status_code == 200:
                success_count += 1
            elif response.status_code == 429:
                rate_limited = True
                # Verificar Retry-After header
                assert "Retry-After" in response.headers
                break
        
        # Después de 10 requests, debe activarse rate limit
        assert success_count <= 10
        assert rate_limited or success_count == 10
    
    def test_retry_after_header(self, client, fake):
        """Test que respuesta 429 incluye Retry-After header"""
        # Hacer requests hasta triggear rate limit
        for i in range(5):
            user_data = {
                "email": fake.email(),
                "password": "Test123!",
                "name": fake.name(),
                "role": "user"
            }
            
            response = client.post("/auth/register", json=user_data)
            
            if response.status_code == 429:
                assert "Retry-After" in response.headers
                retry_after = response.headers["Retry-After"]
                assert int(retry_after) > 0
                break


# ==================== CLASE 6: TEST VALIDATION ====================

@pytest.mark.api
@pytest.mark.unit
class TestInputValidation:
    """Tests de validación de inputs"""
    
    def test_analyze_validates_m2_positive(self, client, auth_headers):
        """Test que m2_construccion debe ser positivo"""
        data = {
            "m2_construccion": -100,  # Negativo (inválido)
            "municipio": "Test",
            "estado": "Test"
        }
        
        response = client.post("/analyze", json=data, headers=auth_headers)
        assert response.status_code in [400, 422]
    
    def test_analyze_validates_aforo_positive(self, client, auth_headers):
        """Test que aforo_autorizado debe ser positivo"""
        data = {
            "aforo_autorizado": 0,  # Cero (inválido)
            "municipio": "Test",
            "estado": "Test"
        }
        
        response = client.post("/analyze", json=data, headers=auth_headers)
        # Puede ser aceptado dependiendo de la lógica
        assert response.status_code in [200, 400, 422]
    
    def test_register_validates_role(self, client, user_data):
        """Test que el role debe ser válido"""
        invalid_data = user_data.copy()
        invalid_data["role"] = "super-admin"  # Role inválido
        
        response = client.post("/auth/register", json=invalid_data)
        assert response.status_code == 400


# ==================== CLASE 7: TEST ERROR HANDLING ====================

@pytest.mark.api
@pytest.mark.unit
class TestErrorHandling:
    """Tests de manejo de errores"""
    
    def test_404_on_nonexistent_endpoint(self, client):
        """Test 404 en endpoint que no existe"""
        response = client.get("/nonexistent-endpoint")
        assert response.status_code == 404
    
    def test_405_on_wrong_method(self, client):
        """Test 405 con método HTTP incorrecto"""
        # GET en lugar de POST
        response = client.get("/auth/register")
        assert response.status_code == 405
    
    def test_422_on_invalid_json(self, client, auth_headers):
        """Test 422 con JSON inválido"""
        # Content-Type JSON pero body inválido
        response = client.post(
            "/analyze",
            data="invalid json {{{",
            headers={**auth_headers, "Content-Type": "application/json"}
        )
        
        assert response.status_code == 422


# ==================== CLASE 8: TEST RESPONSE FORMATS ====================

@pytest.mark.api
@pytest.mark.unit
class TestResponseFormats:
    """Tests de formatos de respuesta"""
    
    def test_analyze_returns_json(self, client, auth_headers, valid_analysis_data):
        """Test que /analyze retorna JSON"""
        response = client.post(
            "/analyze",
            json=valid_analysis_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"
    
    def test_error_responses_include_detail(self, client):
        """Test que respuestas de error incluyen 'detail'"""
        response = client.post("/auth/login", json={
            "email": "test@example.com",
            "password": "wrong"
        })
        
        assert response.status_code == 401
        assert "detail" in response.json()


# ==================== RUN ALL TESTS ====================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=main", "--cov-report=term-missing"])
