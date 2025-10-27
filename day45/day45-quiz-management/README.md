# Quiz Management Platform - Day 45

A production-ready quiz management system built with React and FastAPI.

## Features

- **CRUD Operations**: Create, read, update, delete quizzes
- **Real-time Search**: Filter quizzes instantly
- **Bulk Actions**: Delete multiple quizzes at once
- **Authentication**: Secure user authentication with JWT
- **Responsive Design**: Mobile-friendly interface
- **Progressive Enhancement**: Optimistic updates for better UX

## Tech Stack

- **Frontend**: React 18, Tailwind CSS, React Query
- **Backend**: FastAPI, SQLAlchemy, PostgreSQL
- **Authentication**: JWT with bcrypt
- **Testing**: Vitest, pytest
- **Deployment**: Docker support

## Quick Start

### Option 1: Local Development
```bash
./build.sh
./start.sh
```

### Option 2: Docker
```bash
./build.sh docker
./start.sh docker
```

## API Endpoints

- `POST /api/auth/register` - Register user
- `POST /api/auth/login` - Login user
- `GET /api/quiz/` - Get quizzes
- `POST /api/quiz/` - Create quiz
- `PUT /api/quiz/{id}` - Update quiz
- `DELETE /api/quiz/{id}` - Delete quiz
- `POST /api/quiz/bulk-delete` - Bulk delete

## Testing

```bash
# Backend tests
cd backend && python -m pytest

# Frontend tests
cd frontend && npm test
```

## Environment Variables

Backend (.env):
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: JWT secret key
- `GEMINI_API_KEY`: Google Gemini API key

Frontend (.env):
- `VITE_API_BASE_URL`: Backend API URL

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── models/
│   │   ├── routes/
│   │   └── services/
│   └── tests/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── context/
│   │   └── services/
│   └── tests/
└── docs/
```
