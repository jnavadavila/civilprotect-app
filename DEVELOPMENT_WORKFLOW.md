# Workflow de Desarrollo CivilProtect

Este documento describe el flujo de trabajo estándar para garantizar la calidad del código, la seguridad y la estabilidad de la aplicación CivilProtect v2.0.

## 1. Configuración del Entorno (Pre-commit)

Utilizamos `pre-commit` para ejecutar verificaciones automáticas de calidad antes de cada commit. Esto asegura que el código esté formateado y libre de errores básicos.

### Instalación

1.  Asegúrate de tener Python instalado.
2.  Instala el framework `pre-commit`:
    ```bash
    pip install pre-commit
    ```
3.  Instala los hooks en el repositorio:
    ```bash
    pre-commit install
    ```

### Hooks Activos
*   **black**: Formateo automático de código Python (Backend).
*   **flake8**: Linting de código Python para seguir PEP8.
*   **prettier**: Formateo de JavaScript, CSS, JSON y Markdown (Frontend).
*   **Trailing Whitespace / End of File**: Limpieza general de archivos.

Si un hook falla, `pre-commit` intentará arreglar el archivo (en caso de formateo) o te mostrará el error. Corrige y vuelve a hacer `git add` y `git commit`.

## 2. CI/CD Pipeline (GitHub Actions)

Cada vez que haces push a `main` o `develop`, o abres un Pull Request, se ejecuta automáticamente nuestro pipeline de Integración Continua.

### Jobs del Pipeline
1.  **Backend Quality**:
    *   Instala dependencias Python.
    *   Ejecuta `flake8` para linting.
    *   Ejecuta `bandit` para escaneo de seguridad.
    *   Ejecuta `safety` para verificar dependencias vulnerables.
    *   Ejecuta `pytest` para pruebas unitarias.
2.  **Frontend Quality**:
    *   Instala dependencias Node.js.
    *   Ejecuta `lint` (ESLint).
    *   Ejecuta `npm test` (Jest).
3.  **Build Verification**:
    *   Intenta construir las imágenes Docker de Backend y Frontend para asegurar que los Dockerfiles son válidos.

### Badges de Estado
Agrega estos badges a tu README para visibilidad del estado del build:

```markdown
[![CivilProtect CI/CD Pipeline](https://github.com/TU_USUARIO/TU_REPO/actions/workflows/ci.yml/badge.svg)](https://github.com/TU_USUARIO/TU_REPO/actions/workflows/ci.yml)
```

## 3. Comandos Útiles

*   **Ejecutar Tests Backend Localmente**:
    ```bash
    cd backend
    pytest
    ```
*   **Ejecutar Tests Frontend Localmente**:
    ```bash
    cd frontend
    npm test
    ```
*   **Ejecutar Hooks Manualmente en todos los archivos**:
    ```bash
    pre-commit run --all-files
    ```

## 4. Política de Ramas
*   **main**: Producción estable.
*   **develop**: Desarrollo activo. PRs deben apuntar aquí.
*   **feature/**: Nuevas funcionalidades.

---
**Recuerda**: "Sin retroceder, sin eliminar, sin dañar". El CI está ahí para proteger este principio.
