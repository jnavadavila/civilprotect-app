# Guía de Desarrollo - CivilProtect

## 1. Setup del Entorno Local

### Requisitos
- Python 3.9+
- Node.js 16+
- PostgreSQL 15 (opcional, defaults to SQLite local)
- Docker Desktop (Recomendado)

### Backend (FastAPI)
1. `cd backend`
2. `python -m venv venv`
3. `venv\Scripts\activate` (Windows)
4. `pip install -r requirements.txt`
5. Crear archivo `.env` (ver `.env.example`).
6. `uvicorn main:app --reload`
   - API: http://localhost:8000
   - Docs: http://localhost:8000/docs

### Frontend (React)
1. `cd frontend`
2. `npm install`
3. `npm start`
   - App: http://localhost:3000

## 2. Testing
- Backend: `pytest`
- Frontend: `npm test`

## 3. Workflow de Git
- Features branches: `feature/nombre-feature`
- Commits convencionales: `feat: descripción`, `fix: descripción`.

## 4. Estructura de Proyecto
- `backend/`: Lógica de negocio, IA, PDF Gen.
- `frontend/`: UI, Wizard, Auth.
- `docs/`: Documentación del proyecto.
