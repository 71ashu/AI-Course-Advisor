# AI Course Advisor

A full-stack academic planning application that provides intelligent course recommendations based on student profiles, completed courses, and career goals.

## Tech Stack

- **Frontend**: React 18, Vite, Tailwind CSS, Lucide React
- **Backend**: Flask, SQLAlchemy, SQLite
- **Auth**: Session-based (Flask sessions)

## Project Structure

```
AI-Course-Advisor/
├── frontend/          # React + Vite app
│   ├── src/
│   │   ├── App.jsx
│   │   ├── CourseAdvisor.jsx
│   │   ├── api.js
│   │   └── main.jsx
│   └── package.json
├── backend/           # Flask API
│   ├── app.py         # Main application
│   ├── models.py      # Database models
│   ├── services.py    # Recommendation logic
│   ├── seed.py        # Database seeder
│   └── requirements.txt
└── README.md
```

## Setup

### 1. Backend

Requires Python 3.10–3.12 (Python 3.13 may have compatibility issues).

```bash
cd backend
python3.12 -m venv venv   # or python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python seed.py             # Seed courses and demo user
python app.py              # Start server on http://localhost:5000
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev                # Start dev server on http://localhost:5173
```

### 3. Run Both

Open two terminals:
- Terminal 1: `cd backend && python app.py`
- Terminal 2: `cd frontend && npm run dev`

Visit **http://localhost:5173** in your browser.

## Demo Login

- **Email**: alex@demo.edu
- **Password**: demo123

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new student |
| POST | `/api/auth/login` | Login |
| POST | `/api/auth/logout` | Logout |
| GET | `/api/auth/me` | Get current user |
| GET | `/api/profile` | Get profile |
| PUT | `/api/profile` | Update profile |
| GET | `/api/courses` | List all courses |
| POST | `/api/recommend` | Get course recommendations |
| GET | `/api/progress` | Get degree progress |

## Environment Variables

Create `backend/.env` (optional):

```
FLASK_ENV=development
DATABASE_URL=sqlite:///course_advisor.db
SECRET_KEY=your-secret-key
```
