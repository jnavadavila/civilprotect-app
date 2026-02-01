#!/bin/bash

# Build script for Render

echo "🚀 Starting build process..."

# Install Python dependencies
echo "📦 Installing Python packages..."
pip install -r backend/requirements.txt

# Initialize database
echo "🗄️ Initializing database..."
cd backend && python -c "from database import init_db; init_db(); print('✅ Database initialized')" && cd ..

# Build React frontend
echo "⚛️ Building React frontend..."
cd frontend
npm install
npm run build
cd ..

echo "✅ Build complete!"
