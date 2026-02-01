# 🧪 TESTING GUIDE - CIVILPROTECT BACKEND

**Versión:** V4.5  
**Tests Framework:** pytest  
**Coverage Target:** > 60% global

---

## 📋 TABLA DE CONTENIDOS

1. [Requisitos](#requisitos)
2. [Instalación](#instalación)
3. [Estructura de Tests](#estructura-de-tests)
4. [Ejecutar Tests](#ejecutar-tests)
5. [Coverage Reports](#coverage-reports)
6. [Markers y Categorías](#markers-y-categorías)
7. [Testing en CI/CD](#testing-en-cicd)
8. [Troubleshooting](#troubleshooting)

---

## ⚙️ REQUISITOS

- **Python:** 3.9+
- **pytest:** >= 9.0.0
- **pytest-cov:** >= 7.0.0
- **pytest-asyncio:** >= 1.3.0

---

## 📦 INSTALACIÓN

### **1. Instalar Dependencias**

```bash
cd backend
pip install -r requirements.txt
```

### **2. Verificar Instalación**

```bash
pytest --version
# pytest 9.0.2
```

---

## 📂 ESTRUCTURA DE TESTS

```
backend/
├── tests/
│   ├── __init__.py
│   ├── test_calculator_engine.py      # Tests del motor de cálculo
│   ├── test_api_endpoints.py           # Tests de endpoints de API
│   ├── test_database.py                 # Tests de modelos y BD
│   └── test_report_generator.py         # Tests de generación de PDFs
├── conftest.py                          # Fixtures compartidas
├── pytest.ini                           # Configuración de pytest
└── ...
```

### **Archivos de Configuración:**

- **`pytest.ini`**: Configuración general de pytest, markers, coverage
- **`conftest.py`**: Fixtures comunes (BD, usuarios, datos de prueba)

---

## 🚀 EJECUTAR TESTS

### **1. Ejecutar Todos los Tests**

```bash
cd backend
pytest
```

**Output esperado:**
```
============================= test session starts ==============================
collected 150 items

tests/test_calculator_engine.py ........... tests/test_api_endpoints.py ........................
tests/test_database.py ................
tests/test_report_generator.py ............

============================== 150 passed in 15.23s =============================
```

### **2. Ejecutar Tests de un Módulo Específico**

```bash
# Tests del calculator
pytest tests/test_calculator_engine.py

# Tests de API
pytest tests/test_api_endpoints.py

# Tests de database
pytest tests/test_database.py

# Tests de reportes
pytest tests/test_report_generator.py
```

### **3. Ejecutar un Test Específico**

```bash
# Por clase
pytest tests/test_calculator_engine.py::TestExtintoresCalculation

# Por método
pytest tests/test_calculator_engine.py::TestExtintoresCalculation::test_extintores_basic_calculation
```

### **4. Ejecutar con Verbose**

```bash
pytest -v
# Muestra cada test individualmente

pytest -vv
# Muestra detalles completos de asserts
```

---

## 📊 COVERAGE REPORTS

### **1. Generar Reporte de Coverage**

```bash
# Terminal (resumen)
pytest --cov=. --cov-report=term-missing

# HTML (interactivo)
pytest --cov=. --cov-report=html

# Ambos
pytest --cov=. --cov-report=term-missing --cov-report=html
```

### **2. Ver Reporte HTML**

```bash
# Generar reporte
pytest --cov=. --cov-report=html

# Abrir en browser
start htmlcov/index.html  # Windows
# o
open htmlcov/index.html   # Mac/Linux
```

### **3. Coverage por Módulo**

```bash
# Solo calculator_engine
pytest tests/test_calculator_engine.py --cov=calculator_engine --cov-report=term-missing

# Solo API
pytest tests/test_api_endpoints.py --cov=main --cov-report=term-missing

# Solo database
pytest tests/test_database.py --cov=database --cov-report=term-missing

# Solo reports
pytest tests/test_report_generator.py --cov=report_generator --cov-report=term-missing
```

### **4. Targets de Coverage**

| Módulo | Target | Actual |
|--------|--------|--------|
| `calculator_engine.py` | > 80% | ✅ |
| `main.py` (API endpoints) | > 70% | ✅ |
| `database.py` | > 70% | ✅ |
| `report_generator.py` | > 70% | ✅ |
| **GLOBAL** | **> 60%** | **✅** |

---

## 🏷️ MARKERS Y CATEGORÍAS

Los tests están organizados con markers para facilitar su ejecución selectiva:

### **Markers Disponibles:**

- **`unit`**: Tests unitarios (rápidos, aislados)
- **`integration`**: Tests de integración (BD, API)
- **`slow`**: Tests lentos (> 1s)
- **`auth`**: Tests de autenticación
- **`calculator`**: Tests del motor de cálculo
- **`api`**: Tests de API endpoints
- **`database`**: Tests de base de datos
- **`report`**: Tests de generación de reportes
- **`security`**: Tests de seguridad

### **Ejecutar por Marker:**

```bash
# Solo tests unitarios
pytest -m unit

# Solo tests de integración
pytest -m integration

# Solo tests de seguridad
pytest -m security

# Excluir tests lentos
pytest -m "not slow"

# Combinar markers
pytest -m "unit and calculator"
```

### **Listar Todos los Markers:**

```bash
pytest --markers
```

---

## 🔄 TESTING EN CI/CD

### **1. GitHub Actions Example**

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        cd backend
        pip install -r requirements.txt
    
    - name: Run tests with coverage
      run: |
        cd backend
        pytest --cov=. --cov-report=xml --cov-report=term-missing
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v2
      with:
        file: ./backend/coverage.xml
        fail_ci_if_error: true
```

### **2. Coverage Badge**

Agregar al README.md:

```markdown
![Coverage](https://img.shields.io/codecov/c/github/tu-usuario/civilprotect-app)
![Tests](https://img.shields.io/github/workflow/status/tu-usuario/civilprotect-app/Tests)
```

---

## 🔍 OPCIONES ÚTILES

### **1. Modo Verbose**

```bash
pytest -v          # Verbose
pytest -vv         # Extra verbose
pytest -q          # Quiet (solo errores)
```

### **2. Stop on First Failure**

```bash
pytest -x          # Detener en primer fallo
pytest --maxfail=3 # Detener después de 3 fallos
```

### **3. Solo Fallos Previos**

```bash
pytest --lf        # Last failed
pytest --ff        # Failed first, luego el resto
```

### **4. Output de Print Statements**

```bash
pytest -s          # Mostrar prints
pytest --capture=no # Sin captura de output
```

### **5. Duración de Tests**

```bash
pytest --durations=10  # Mostrar 10 tests más lentos
pytest --durations=0   # Mostrar todos
```

### **6. Parallel Execution**

```bash
# Instalar pytest-xdist
pip install pytest-xdist

# Ejecutar en paralelo
pytest -n 4  # 4 workers
pytest -n auto  # Auto-detect CPUs
```

---

## 🐛 TROUBLESHOOTING

### **Problema 1: ModuleNotFoundError**

```bash
# Error
ModuleNotFoundError: No module named 'module_name'

# Solución
cd backend
pip install -r requirements.txt
```

### **Problema 2: Fixtures not found**

```bash
# Error
fixture 'test_db' not found

# Solución
# Verificar que conftest.py está en el directorio correcto
backend/conftest.py  # ✅ Correcto
backend/tests/conftest.py  # ❌ Incorrecto
```

### **Problema 3: Database errors in tests**

```bash
# Error
sqlalchemy.exc.OperationalError

# Solución
# Los tests usan BD in-memory, no debe haber errores de BD
# Verificar que el fixture test_db esté configurado correctamente
```

### **Problema 4: Coverage muy bajo**

```bash
# Verificar que los paths son correctos
pytest --cov=. --cov-report=term-missing

# Excluir archivos de test
# Ya configurado en pytest.ini sección [coverage:run]
```

### **Problema 5: Tests lentos**

```bash
# Identificar tests lentos
pytest --durations=20

# Ejecutar solo tests rápidos
pytest -m "not slow"

# Usar parallel execution
pytest -n auto
```

---

## 📝 EJEMPLOS DE USO

### **Desarrollo Diario:**

```bash
# 1. Durante desarrollo: tests rápidos
pytest -m unit

# 2. Antes de commit: todos los tests
pytest

# 3. Verificar coverage
pytest --cov=. --cov-report=term-missing

# 4. Si hay fallos, ejecutar solo los que fallaron
pytest --lf
```

### **Pre-Deploy:**

```bash
# 1. Todos los tests con coverage
pytest --cov=. --cov-report=html --cov-report=term-missing

# 2. Verificar coverage > 60%
# Ver reporte HTML

# 3. Verificar tests de seguridad
pytest -m security -v

# 4. Verificar tests de integración
pytest -m integration -v
```

---

## ✅ CHECKLIST DE TESTING

Antes de hacer merge/deploy:

- [ ] Todos los tests pasan (`pytest`)
- [ ] Coverage global > 60%
- [ ] Coverage por módulo alcanza targets
- [ ] Tests de seguridad pasan
- [ ] Tests de integración pasan
- [ ] No hay warnings de pytest
- [ ] Documentación actualizada

---

## 📚 RECURSOS ADICIONALES

- **Pytest Documentation:** https://docs.pytest.org/
- **Coverage.py:** https://coverage.readthedocs.io/
- **pytest-cov:** https://pytest-cov.readthedocs.io/
- **FastAPI Testing:** https://fastapi.tiangolo.com/tutorial/testing/

---

## 🎯 COVERAGE TARGETS

### **Actual:**

| Módulo | Líneas | Cobertura |
|--------|--------|-----------|
| `calculator_engine.py` | ~155 | > 80% |
| `main.py` | ~1100 | > 70% |
| `database.py` | ~300 | > 70% |
| `report_generator.py` | ~440 | > 70% |
| **TOTAL** | **~2000** | **> 60%** |

---

**Última actualización:** 30 de Enero 2026  
**Versión:** CivilProtect V4.5  
**Autor:** CivilProtect DevOps Team
