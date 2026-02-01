# Tarea de Intervención: Resolución de Regresiones (QA)

Se han detectado fallos en las pruebas automatizadas que deben ser resueltos para garantizar la estabilidad del código "Gold".

## 1. Regresiones de Backend (Prioridad Alta)
*   **Problema:** `ImportError: attempted relative import...` al ejecutar `pytest`.
*   **Causa:** El refactoring de `database.py` introdujo imports relativos (`from .config`) que rompen la ejecución cuando el módulo se importa como top-level en tests.
*   **Plan de Acción:**
    - [ ] Modificar `backend/database.py`: Cambiar `from .config import settings` a `from config import settings`.
    - [ ] Verificar `backend/auth/dependencies.py` por problemas similares.
    - [ ] Ejecutar `pytest` para validar corrección.

## 2. Regresiones de Frontend (Prioridad Media)
*   **Problema:** `npm test` falla en 5 suites (`FormWizard`).
*   **Causa:** La implementación de `Lazy Loading` (React.lazy + Suspense) en `App.js` hace que los componentes se carguen asíncronamente, pero los tests actuales esperan renderizado síncrono.
*   **Plan de Acción:**
    - [ ] Actualizar `App.test.js` usando `waitFor` para la carga de rutas.
    - [ ] Revisar `FormWizard.test.js`: Asegurar que los Mocks de contexto (`AnalysisContext`) coinciden con la nueva estructura de datos (`aforo_autorizado`, etc.).
    - [ ] Ejecutar `npm test` para validar.

## 3. Entregables
*   ✅ Backend Tests pasando (100%).
*   ✅ Frontend Tests pasando (>80%).
