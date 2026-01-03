@echo off
echo ==========================================
echo Humanoid AI Chatbot Setup
echo ==========================================
echo.

REM Backend Setup
echo Setting up Backend...
cd backend

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing Python dependencies...
pip install -r requirements.txt

REM Run migrations
echo Running database migrations...
python manage.py makemigrations
python manage.py migrate

REM Seed admin user
echo Creating super admin account...
python manage.py seed_admin

echo Backend setup complete!
echo.

REM Frontend Setup
echo Setting up Frontend...
cd ..\frontend

REM Install dependencies
echo Installing Node dependencies...
call npm install

echo Frontend setup complete!
echo.

REM Instructions
echo ==========================================
echo Setup Complete!
echo ==========================================
echo.
echo To start the application:
echo.
echo 1. Start the Backend (in terminal 1):
echo    cd backend
echo    venv\Scripts\activate.bat
echo    python manage.py runserver
echo.
echo 2. Start the Frontend (in terminal 2):
echo    cd frontend
echo    npm run dev
echo.
echo Default Admin Credentials:
echo    Username: admin
echo    Password: admin123
echo.
echo Access the app at: http://localhost:5173
echo ==========================================
pause
