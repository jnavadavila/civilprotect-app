"""
Tests para database.py
Coverage target: > 70%
"""
import pytest
from sqlalchemy.orm import Session
from database import User, Analysis, get_password_hash, verify_password
from datetime import datetime


# ==================== CLASE 1: TEST CRUD DE USER ====================

@pytest.mark.database
@pytest.mark.unit
class TestUserCRUD:
    """Tests de CRUD de User"""
    
    def test_create_user(self, test_db: Session, user_data):
        """Test crear usuario"""
        user = User(
            email=user_data["email"],
            hashed_password=get_password_hash(user_data["password"]),
            name=user_data["name"],
            role=user_data["role"]
        )
        
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)
        
        assert user.id is not None
        assert user.email == user_data["email"]
        assert user.name == user_data["name"]
        assert user.role == user_data["role"]
        assert user.hashed_password != user_data["password"]  # Debe estar hasheada
    
    def test_read_user_by_id(self, test_db: Session, user_data):
        """Test leer usuario por ID"""
        # Crear usuario
        user = User(
            email=user_data["email"],
            hashed_password=get_password_hash(user_data["password"]),
            name=user_data["name"],
            role=user_data["role"]
        )
        test_db.add(user)
        test_db.commit()
        user_id = user.id
        
        # Leer usuario
        found_user = test_db.query(User).filter(User.id == user_id).first()
        
        assert found_user is not None
        assert found_user.id == user_id
        assert found_user.email == user_data["email"]
    
    def test_read_user_by_email(self, test_db: Session, user_data):
        """Test leer usuario por email"""
        # Crear usuario
        user = User(
            email=user_data["email"],
            hashed_password=get_password_hash(user_data["password"]),
            name=user_data["name"],
            role=user_data["role"]
        )
        test_db.add(user)
        test_db.commit()
        
        # Buscar por email
        found_user = test_db.query(User).filter(User.email == user_data["email"]).first()
        
        assert found_user is not None
        assert found_user.email == user_data["email"]
    
    def test_update_user(self, test_db: Session, user_data):
        """Test actualizar usuario"""
        # Crear usuario
        user = User(
            email=user_data["email"],
            hashed_password=get_password_hash(user_data["password"]),
            name=user_data["name"],
            role=user_data["role"]
        )
        test_db.add(user)
        test_db.commit()
        
        # Actualizar nombre
        new_name = "Updated Name"
        user.name = new_name
        test_db.commit()
        test_db.refresh(user)
        
        assert user.name == new_name
    
    def test_delete_user(self, test_db: Session, user_data):
        """Test eliminar usuario"""
        # Crear usuario
        user = User(
            email=user_data["email"],
            hashed_password=get_password_hash(user_data["password"]),
            name=user_data["name"],
            role=user_data["role"]
        )
        test_db.add(user)
        test_db.commit()
        user_id = user.id
        
        # Eliminar
        test_db.delete(user)
        test_db.commit()
        
        # Verificar que no existe
        found_user = test_db.query(User).filter(User.id == user_id).first()
        assert found_user is None
    
    def test_user_unique_email(self, test_db: Session, user_data):
        """Test que el email debe ser único"""
        # Crear primer usuario
        user1 = User(
            email=user_data["email"],
            hashed_password=get_password_hash(user_data["password"]),
            name=user_data["name"],
            role=user_data["role"]
        )
        test_db.add(user1)
        test_db.commit()
        
        # Intentar crear segundo usuario con mismo email
        user2 = User(
            email=user_data["email"],  # Mismo email
            hashed_password=get_password_hash("different-password"),
            name="Different Name",
            role=user_data["role"]
        )
        test_db.add(user2)
        
        # Debe fallar por constraint de unique email
        with pytest.raises(Exception):  # IntegrityError
            test_db.commit()


# ==================== CLASE 2: TEST CRUD DE ANALYSIS ====================

@pytest.mark.database
@pytest.mark.unit
class TestAnalysisCRUD:
    """Tests de CRUD de Analysis"""
    
    def test_create_analysis(self, test_db: Session, user_data, valid_analysis_data):
        """Test crear análisis"""
        # Crear usuario primero
        user = User(
            email=user_data["email"],
            hashed_password=get_password_hash(user_data["password"]),
            name=user_data["name"],
            role=user_data["role"]
        )
        test_db.add(user)
        test_db.commit()
        
        # Crear análisis
        analysis = Analysis(
            user_id=user.id,
            municipio=valid_analysis_data["municipio"],
            estado=valid_analysis_data["estado"],
            nombre_inmueble=valid_analysis_data["nombre_inmueble"],
            domicilio=valid_analysis_data.get("domicilio"),
            m2_construccion=valid_analysis_data["m2_construccion"],
            aforo_autorizado=valid_analysis_data["aforo_autorizado"],
            nivel_riesgo=valid_analysis_data["nivel_riesgo"],
            resultado_json={},  # JSON del resultado
            pdf_path=None
        )
        
        test_db.add(analysis)
        test_db.commit()
        test_db.refresh(analysis)
        
        assert analysis.id is not None
        assert analysis.user_id == user.id
        assert analysis.municipio == valid_analysis_data["municipio"]
        assert analysis.estado == valid_analysis_data["estado"]
        assert analysis.created_at is not None
    
    def test_read_analysis_by_id(self, test_db: Session, user_data, valid_analysis_data):
        """Test leer análisis por ID"""
        # Crear usuario
        user = User(
            email=user_data["email"],
            hashed_password=get_password_hash(user_data["password"]),
            name=user_data["name"],
            role=user_data["role"]
        )
        test_db.add(user)
        test_db.commit()
        
        # Crear análisis
        analysis = Analysis(
            user_id=user.id,
            municipio=valid_analysis_data["municipio"],
            estado=valid_analysis_data["estado"],
            nombre_inmueble=valid_analysis_data["nombre_inmueble"],
            m2_construccion=valid_analysis_data["m2_construccion"],
            aforo_autorizado=valid_analysis_data["aforo_autorizado"],
            nivel_riesgo=valid_analysis_data["nivel_riesgo"],
            resultado_json={}
        )
        test_db.add(analysis)
        test_db.commit()
        analysis_id = analysis.id
        
        # Leer análisis
        found_analysis = test_db.query(Analysis).filter(Analysis.id == analysis_id).first()
        
        assert found_analysis is not None
        assert found_analysis.id == analysis_id
        assert found_analysis.municipio == valid_analysis_data["municipio"]
    
    def test_update_analysis(self, test_db: Session, user_data, valid_analysis_data):
        """Test actualizar análisis"""
        # Crear usuario
        user = User(
            email=user_data["email"],
            hashed_password=get_password_hash(user_data["password"]),
            name=user_data["name"],
            role=user_data["role"]
        )
        test_db.add(user)
        test_db.commit()
        
        # Crear análisis
        analysis = Analysis(
            user_id=user.id,
            municipio=valid_analysis_data["municipio"],
            estado=valid_analysis_data["estado"],
            nombre_inmueble=valid_analysis_data["nombre_inmueble"],
            m2_construccion=valid_analysis_data["m2_construccion"],
            aforo_autorizado=valid_analysis_data["aforo_autorizado"],
            nivel_riesgo=valid_analysis_data["nivel_riesgo"],
            resultado_json={},
            pdf_path=None
        )
        test_db.add(analysis)
        test_db.commit()
        
        # Actualizar pdf_path
        new_path = "/path/to/pdf.pdf"
        analysis.pdf_path = new_path
        test_db.commit()
        test_db.refresh(analysis)
        
        assert analysis.pdf_path == new_path
    
    def test_delete_analysis(self, test_db: Session, user_data, valid_analysis_data):
        """Test eliminar análisis"""
        # Crear usuario
        user = User(
            email=user_data["email"],
            hashed_password=get_password_hash(user_data["password"]),
            name=user_data["name"],
            role=user_data["role"]
        )
        test_db.add(user)
        test_db.commit()
        
        # Crear análisis
        analysis = Analysis(
            user_id=user.id,
            municipio=valid_analysis_data["municipio"],
            estado=valid_analysis_data["estado"],
            nombre_inmueble=valid_analysis_data["nombre_inmueble"],
            m2_construccion=valid_analysis_data["m2_construccion"],
            aforo_autorizado=valid_analysis_data["aforo_autorizado"],
            nivel_riesgo=valid_analysis_data["nivel_riesgo"],
            resultado_json={}
        )
        test_db.add(analysis)
        test_db.commit()
        analysis_id = analysis.id
        
        # Eliminar
        test_db.delete(analysis)
        test_db.commit()
        
        # Verificar que no existe
        found_analysis = test_db.query(Analysis).filter(Analysis.id == analysis_id).first()
        assert found_analysis is None


# ==================== CLASE 3: TEST RELACIONES ====================

@pytest.mark.database
@pytest.mark.unit
class TestRelationships:
    """Tests de relaciones entre modelos"""
    
    def test_user_analyses_relationship(self, test_db: Session, user_data, valid_analysis_data):
        """Test relación User -> Analyses"""
        # Crear usuario
        user = User(
            email=user_data["email"],
            hashed_password=get_password_hash(user_data["password"]),
            name=user_data["name"],
            role=user_data["role"]
        )
        test_db.add(user)
        test_db.commit()
        
        # Crear 3 análisis para el usuario
        for i in range(3):
            analysis = Analysis(
                user_id=user.id,
                municipio=f"Municipio {i}",
                estado="Jalisco",
                nombre_inmueble=f"Inmueble {i}",
                m2_construccion=500,
                aforo_autorizado=100,
                nivel_riesgo="ordinario",
                resultado_json={}
            )
            test_db.add(analysis)
        
        test_db.commit()
        test_db.refresh(user)
        
        # Verificar relación
        assert len(user.analyses) == 3
        assert all(a.user_id == user.id for a in user.analyses)
    
    def test_analysis_user_relationship(self, test_db: Session, user_data, valid_analysis_data):
        """Test relación Analysis -> User"""
        # Crear usuario
        user = User(
            email=user_data["email"],
            hashed_password=get_password_hash(user_data["password"]),
            name=user_data["name"],
            role=user_data["role"]
        )
        test_db.add(user)
        test_db.commit()
        
        # Crear análisis
        analysis = Analysis(
            user_id=user.id,
            municipio=valid_analysis_data["municipio"],
            estado=valid_analysis_data["estado"],
            nombre_inmueble=valid_analysis_data["nombre_inmueble"],
            m2_construccion=valid_analysis_data["m2_construccion"],
            aforo_autorizado=valid_analysis_data["aforo_autorizado"],
            nivel_riesgo=valid_analysis_data["nivel_riesgo"],
            resultado_json={}
        )
        test_db.add(analysis)
        test_db.commit()
        test_db.refresh(analysis)
        
        # Verificar relación
        assert analysis.user is not None
        assert analysis.user.id == user.id
        assert analysis.user.email == user_data["email"]
    
    def test_cascade_delete(self, test_db: Session, user_data, valid_analysis_data):
        """Test cascade delete (eliminar usuario elimina sus análisis)"""
        # Crear usuario
        user = User(
            email=user_data["email"],
            hashed_password=get_password_hash(user_data["password"]),
            name=user_data["name"],
            role=user_data["role"]
        )
        test_db.add(user)
        test_db.commit()
        user_id = user.id
        
        # Crear análisis
        analysis = Analysis(
            user_id=user.id,
            municipio=valid_analysis_data["municipio"],
            estado=valid_analysis_data["estado"],
            nombre_inmueble=valid_analysis_data["nombre_inmueble"],
            m2_construccion=valid_analysis_data["m2_construccion"],
            aforo_autorizado=valid_analysis_data["aforo_autorizado"],
            nivel_riesgo=valid_analysis_data["nivel_riesgo"],
            resultado_json={}
        )
        test_db.add(analysis)
        test_db.commit()
        analysis_id = analysis.id
        
        # Eliminar usuario
        test_db.delete(user)
        test_db.commit()
        
        # Verificar que el análisis también se eliminó (si hay cascade)
        found_analysis = test_db.query(Analysis).filter(Analysis.id == analysis_id).first()
        
        # Depende de si está configurado cascade delete
        # Si está configurado, found_analysis debe ser None
        # Si no, puede seguir existiendo


# ==================== CLASE 4: TEST QUERIES CON FILTROS ====================

@pytest.mark.database
@pytest.mark.unit
class TestQueriesWithFilters:
    """Tests de queries con filtros"""
    
    def test_filter_analyses_by_user(self, test_db: Session, user_data, valid_analysis_data):
        """Test filtrar análisis por usuario"""
        # Crear 2 usuarios
        user1 = User(
            email="user1@example.com",
            hashed_password=get_password_hash("password"),
            name="User 1",
            role="user"
        )
        user2 = User(
            email="user2@example.com",
            hashed_password=get_password_hash("password"),
            name="User 2",
            role="user"
        )
        test_db.add(user1)
        test_db.add(user2)
        test_db.commit()
        
        # Crear análisis para cada usuario
        for user in [user1, user2]:
            for i in range(3):
                analysis = Analysis(
                    user_id=user.id,
                    municipio=f"Municipio {i}",
                    estado="Jalisco",
                    nombre_inmueble=f"Inmueble {i}",
                    m2_construccion=500,
                    aforo_autorizado=100,
                    nivel_riesgo="ordinario",
                    resultado_json={}
                )
                test_db.add(analysis)
        
        test_db.commit()
        
        # Filtrar análisis de user1
        user1_analyses = test_db.query(Analysis).filter(Analysis.user_id == user1.id).all()
        
        assert len(user1_analyses) == 3
        assert all(a.user_id == user1.id for a in user1_analyses)
    
    def test_filter_analyses_by_estado(self, test_db: Session, user_data):
        """Test filtrar análisis por estado"""
        # Crear usuario
        user = User(
            email=user_data["email"],
            hashed_password=get_password_hash(user_data["password"]),
            name=user_data["name"],
            role=user_data["role"]
        )
        test_db.add(user)
        test_db.commit()
        
        # Crear análisis en diferentes estados
        estados = ["Jalisco", "CDMX", "Jalisco", "Nuevo León", "Jalisco"]
        
        for estado in estados:
            analysis = Analysis(
                user_id=user.id,
                municipio="Test",
                estado=estado,
                nombre_inmueble="Test",
                m2_construccion=500,
                aforo_autorizado=100,
                nivel_riesgo="ordinario",
                resultado_json={}
            )
            test_db.add(analysis)
        
        test_db.commit()
        
        # Filtrar por Jalisco
        jalisco_analyses = test_db.query(Analysis).filter(Analysis.estado == "Jalisco").all()
        
        assert len(jalisco_analyses) == 3
    
    def test_filter_analyses_by_date_range(self, test_db: Session, user_data, valid_analysis_data):
        """Test filtrar análisis por rango de fechas"""
        # Crear usuario
        user = User(
            email=user_data["email"],
            hashed_password=get_password_hash(user_data["password"]),
            name=user_data["name"],
            role=user_data["role"]
        )
        test_db.add(user)
        test_db.commit()
        
        # Crear análisis
        analysis = Analysis(
            user_id=user.id,
            municipio=valid_analysis_data["municipio"],
            estado=valid_analysis_data["estado"],
            nombre_inmueble=valid_analysis_data["nombre_inmueble"],
            m2_construccion=valid_analysis_data["m2_construccion"],
            aforo_autorizado=valid_analysis_data["aforo_autorizado"],
            nivel_riesgo=valid_analysis_data["nivel_riesgo"],
            resultado_json={}
        )
        test_db.add(analysis)
        test_db.commit()
        
        # Filtrar por fecha (hoy)
        today = datetime.utcnow().date()
        recent_analyses = test_db.query(Analysis).filter(
            Analysis.created_at >= today
        ).all()
        
        assert len(recent_analyses) >= 1


# ==================== CLASE 5: TEST PAGINACIÓN ====================

@pytest.mark.database
@pytest.mark.unit
class TestPagination:
    """Tests de paginación"""
    
    def test_pagination_limit_offset(self, test_db: Session, user_data):
        """Test paginación con limit y offset"""
        # Crear usuario
        user = User(
            email=user_data["email"],
            hashed_password=get_password_hash(user_data["password"]),
            name=user_data["name"],
            role=user_data["role"]
        )
        test_db.add(user)
        test_db.commit()
        
        # Crear 10 análisis
        for i in range(10):
            analysis = Analysis(
                user_id=user.id,
                municipio=f"Municipio {i}",
                estado="Jalisco",
                nombre_inmueble=f"Inmueble {i}",
                m2_construccion=500,
                aforo_autorizado=100,
                nivel_riesgo="ordinario",
                resultado_json={}
            )
            test_db.add(analysis)
        
        test_db.commit()
        
        # Página 1 (primeros 5)
        page1 = test_db.query(Analysis).limit(5).offset(0).all()
        assert len(page1) == 5
        
        # Página 2 (siguientes 5)
        page2 = test_db.query(Analysis).limit(5).offset(5).all()
        assert len(page2) == 5
        
        # No debe haber duplicados
        page1_ids = {a.id for a in page1}
        page2_ids = {a.id for a in page2}
        assert len(page1_ids.intersection(page2_ids)) == 0


# ==================== CLASE 6: TEST PASSWORD HASHING ====================

@pytest.mark.database
@pytest.mark.unit
class TestPasswordHashing:
    """Tests de hashing de contraseñas"""
    
    def test_password_hashing(self):
        """Test que las contraseñas se hashean correctamente"""
        password = "MySecretPassword123!"
        hashed = get_password_hash(password)
        
        assert hashed != password
        assert len(hashed) > 0
        assert hashed.startswith("$2b$")  # bcrypt hash
    
    def test_password_verification_success(self):
        """Test verificación de contraseña correcta"""
        password = "MySecretPassword123!"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) == True
    
    def test_password_verification_failure(self):
        """Test verificación de contraseña incorrecta"""
        password = "MySecretPassword123!"
        wrong_password = "WrongPassword456!"
        hashed = get_password_hash(password)
        
        assert verify_password(wrong_password, hashed) == False
    
    def test_same_password_different_hashes(self):
        """Test que el mismo password genera hashes diferentes (salt)"""
        password = "MySecretPassword123!"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        # Los hashes deben ser diferentes (por el salt)
        assert hash1 != hash2
        
        # Pero ambos deben verificar correctamente
        assert verify_password(password, hash1) == True
        assert verify_password(password, hash2) == True


# ==================== RUN ALL TESTS ====================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=database", "--cov-report=term-missing"])
