# Humanoid AI Chatbot

A modern, full-stack chatbot application with **"No Hallucination"** principle using Django REST Framework and React + Vite + TypeScript.

![Humanoid AI](https://img.shields.io/badge/AI-No%20Hallucination-blue)
![Django](https://img.shields.io/badge/Django-4.2.7-green)
![React](https://img.shields.io/badge/React-18.2-blue)
![TypeScript](https://img.shields.io/badge/TypeScript-5.2-blue)

## Features

### Backend (Django REST Framework)
- 🔐 JWT-based authentication with role validation
- 👥 User management with roles (Admin/User)
- 💬 Chat API with conversation management
- 🤖 Hugging Face integration (Qwen/Qwen2.5-72B-Instruct)
- 🌱 Database seeder for super admin account
- 📝 RESTful API design

### Frontend (React + Vite + TypeScript)
- 🎨 Perplexity-like modern UI design
- 💬 Real-time chat interface
- 📱 Fully responsive design
- 🔒 Protected routes with authentication
- 💾 Conversation history management
- ✨ Markdown rendering with syntax highlighting
- 🎯 State management with Zustand

## Tech Stack

### Backend
- Django 4.2.7
- Django REST Framework 3.14.0
- Simple JWT for authentication
- Hugging Face Hub API
- SQLite database (can be switched to PostgreSQL)

### Frontend
- React 18
- TypeScript
- Vite
- React Router DOM
- Zustand (State Management)
- Axios (HTTP Client)
- React Markdown
- Lucide React (Icons)

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Automated Setup (Recommended)

**For Linux/Mac:**
```bash
chmod +x setup.sh
./setup.sh
```

**For Windows:**
```bash
setup.bat
```

### Manual Setup

#### Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows: venv\Scripts\activate
# On Linux/Mac: source venv/bin/activate
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create super admin
python manage.py seed_admin

# Start server
python manage.py runserver
```

#### Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

## Default Credentials

**Super Admin Account:**
- Username: `admin`
- Password: `admin123`

⚠️ **Important:** Change the admin password in production!

## Environment Variables

The `.env` file in the backend directory contains:
- `DJANGO_SECRET_KEY`: Django secret key
- `DEBUG`: Debug mode (True/False)
- `ALLOWED_HOSTS`: Comma-separated allowed hosts
- `CORS_ALLOWED_ORIGINS`: Comma-separated CORS origins
- `HUGGINGFACE_API_TOKEN`: Your Hugging Face API token (pre-configured)

## API Endpoints

### Authentication
- `POST /api/auth/register/` - Register new user
- `POST /api/auth/login/` - Login
- `POST /api/auth/logout/` - Logout
- `GET /api/auth/me/` - Get current user
- `POST /api/auth/token/refresh/` - Refresh JWT token

### Chat
- `GET /api/chat/conversations/` - List all conversations
- `POST /api/chat/conversations/` - Create new conversation
- `GET /api/chat/conversations/<id>/` - Get conversation details
- `PUT /api/chat/conversations/<id>/` - Update conversation
- `DELETE /api/chat/conversations/<id>/` - Delete conversation
- `POST /api/chat/chat/` - Send message and get AI response

## Project Structure

```
.
├── backend/
│   ├── config/              # Django project settings
│   ├── accounts/            # User authentication app
│   │   ├── models.py       # Custom User model with roles
│   │   ├── views.py        # Auth endpoints
│   │   ├── serializers.py  # User serializers
│   │   └── permissions.py  # Role-based permissions
│   ├── chat/               # Chat functionality app
│   │   ├── models.py       # Conversation & Message models
│   │   ├── views.py        # Chat endpoints
│   │   ├── services.py     # Hugging Face integration
│   │   └── serializers.py  # Chat serializers
│   ├── manage.py
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── components/     # React components
│   │   │   ├── Sidebar.tsx
│   │   │   ├── ChatArea.tsx
│   │   │   └── ProtectedRoute.tsx
│   │   ├── pages/          # Page components
│   │   │   ├── Login.tsx
│   │   │   ├── Register.tsx
│   │   │   └── Chat.tsx
│   │   ├── services/       # API services
│   │   │   └── api.ts
│   │   ├── store/          # State management
│   │   │   ├── authStore.ts
│   │   │   └── chatStore.ts
│   │   ├── types/          # TypeScript types
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   └── vite.config.ts
├── setup.sh               # Linux/Mac setup script
├── setup.bat              # Windows setup script
└── README.md
```

## Features Walkthrough

### Role-Based Access Control
- All registered users automatically get the "user" role
- Only the seeded admin account has "admin" role
- Role validation is enforced on the backend
- Frontend adjusts UI based on user role

### No Hallucination Principle
The AI is configured with a system prompt that emphasizes:
- Accurate, fact-based responses
- Honesty about limitations and uncertainties
- Clear communication when information is unknown
- No fabricated information or false claims

### Perplexity-Like Interface
- Clean, modern dark theme
- Smooth animations and transitions
- Collapsible sidebar for better space utilization
- Markdown rendering with code syntax highlighting
- Responsive design for mobile and desktop

## Development

### Backend Development
```bash
cd backend
source venv/bin/activate
python manage.py runserver
```

### Frontend Development
```bash
cd frontend
npm run dev
```

### Creating Migrations
```bash
cd backend
python manage.py makemigrations
python manage.py migrate
```

## Production Deployment

### Backend
1. Set `DEBUG=False` in `.env`
2. Update `ALLOWED_HOSTS` and `CORS_ALLOWED_ORIGINS`
3. Use a production database (PostgreSQL recommended)
4. Set a strong `DJANGO_SECRET_KEY`
5. Use a WSGI server like Gunicorn
6. Set up HTTPS

### Frontend
1. Build the production bundle:
   ```bash
   npm run build
   ```
2. Serve the `dist` folder using a web server (Nginx, Apache, etc.)

## License

This project is created for educational and development purposes.

## Support

For issues and questions, please create an issue in the repository.

---

**Built with ❤️ using Django REST Framework and React**
