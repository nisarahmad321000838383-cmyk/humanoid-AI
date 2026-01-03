# Quick Start Guide - Humanoid AI Chatbot

## 🚀 Get Started in 3 Steps

### Step 1: Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install setuptools
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_admin
python manage.py runserver
```

### Step 2: Frontend Setup (New Terminal)
```bash
cd frontend
npm install
npm run dev
```

### Step 3: Access the Application
- Open browser: http://localhost:5173
- Login with admin credentials:
  - **Username:** `admin`
  - **Password:** `admin123`

## 📝 What's Included

✅ **Backend (Django REST Framework)**
- JWT Authentication with role validation (Admin/User)
- Hugging Face AI Integration (Qwen model)
- Conversation management API
- Auto-seeded super admin account

✅ **Frontend (React + Vite + TypeScript)**
- Perplexity-like modern UI
- Real-time chat with AI
- Conversation history
- Responsive design

## 🔑 Features

- **No Hallucination AI**: Built with accuracy and reliability in mind
- **Role-Based Access**: All new registrations get "user" role automatically
- **Secure Authentication**: JWT tokens with refresh mechanism
- **Beautiful UI**: Dark theme inspired by Perplexity
- **Markdown Support**: Code syntax highlighting included

## 🔐 Test Accounts

**Super Admin (Pre-seeded):**
- Username: `admin`
- Password: `admin123`

**Create New User:**
- Register through the UI at http://localhost:5173/register
- All new users get "user" role automatically

## 🛠️ Troubleshooting

**Backend Issues:**
- Make sure port 8000 is free
- Check that .env file exists in backend folder
- Verify virtual environment is activated

**Frontend Issues:**
- Make sure port 5173 is free
- Clear node_modules and reinstall: `rm -rf node_modules && npm install`
- Check that backend is running first

## 📚 API Endpoints

- `POST /api/auth/login/` - Login
- `POST /api/auth/register/` - Register
- `GET /api/auth/me/` - Current user
- `POST /api/chat/chat/` - Send message
- `GET /api/chat/conversations/` - List conversations

## 🎨 UI Pages

- `/login` - Login page
- `/register` - Registration page  
- `/chat` - Main chat interface (protected)

Enjoy chatting with Humanoid AI! 🤖
