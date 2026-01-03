#!/bin/bash

echo "=========================================="
echo "Humanoid AI Chatbot Setup"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Backend Setup
echo -e "${BLUE}Setting up Backend...${NC}"
cd backend

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Run migrations
echo "Running database migrations..."
python manage.py makemigrations
python manage.py migrate

# Seed admin user
echo "Creating super admin account..."
python manage.py seed_admin

echo -e "${GREEN}✓ Backend setup complete!${NC}"
echo ""

# Frontend Setup
echo -e "${BLUE}Setting up Frontend...${NC}"
cd ../frontend

# Install dependencies
echo "Installing Node dependencies..."
npm install

echo -e "${GREEN}✓ Frontend setup complete!${NC}"
echo ""

# Instructions
echo "=========================================="
echo -e "${GREEN}Setup Complete!${NC}"
echo "=========================================="
echo ""
echo "To start the application:"
echo ""
echo "1. Start the Backend (in terminal 1):"
echo "   cd backend"
echo "   source venv/bin/activate"
echo "   python manage.py runserver"
echo ""
echo "2. Start the Frontend (in terminal 2):"
echo "   cd frontend"
echo "   npm run dev"
echo ""
echo "Default Admin Credentials:"
echo "   Username: admin"
echo "   Password: admin123"
echo ""
echo "Access the app at: http://localhost:5173"
echo "=========================================="
