# Humanoid AI Backend

Django REST Framework backend for Humanoid AI chatbot with "No Hallucination" principle.

## Features

- JWT-based authentication
- Role-based access control (Admin/User)
- Hugging Face integration (Qwen/Qwen2.5-72B-Instruct)
- Conversation management
- RESTful API

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your settings
```

4. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

5. Seed super admin account:
```bash
python manage.py seed_admin
```

Default admin credentials:
- Username: `admin`
- Password: `admin123`

6. Run the development server:
```bash
python manage.py runserver
```

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

## Environment Variables

- `DJANGO_SECRET_KEY` - Django secret key
- `DEBUG` - Debug mode (True/False)
- `ALLOWED_HOSTS` - Comma-separated list of allowed hosts
- `CORS_ALLOWED_ORIGINS` - Comma-separated list of CORS origins
- `HUGGINGFACE_API_TOKEN` - Hugging Face API token
