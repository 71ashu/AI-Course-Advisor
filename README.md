# AI Course Advisor

A full-stack academic planning application that provides intelligent course recommendations based on student profiles, completed courses, and career goals. Features a multi-signal recommendation engine with explainability, collaborative filtering, GPA prediction, job market alignment, and cold start handling.

## Features

- **Explainable Recommendations** -- Each course recommendation includes structured explanation factors (prerequisite status, interest match, peer patterns, career fit, GPA prediction) with color-coded UI pills
- **Collaborative Filtering** -- Item-based collaborative filtering using co-enrollment patterns from synthetic student data to surface courses taken by students with similar backgrounds
- **GPA / Grade Prediction** -- Predicts likely grades using historical grade distributions, flags courses that may lower a student's GPA
- **Job Market Alignment** -- Optional target job title input; uses LLM-based skill extraction to align course recommendations with career goals
- **Prerequisite Knowledge Graph** -- NetworkX-powered DAG that computes reachable courses, prerequisite paths, and course depth
- **Cold Start Handling** -- 4-step onboarding quiz for new users (interests, experience level, career path, course load) to bootstrap personalized recommendations before any history exists
- **Evaluation Metrics** -- Leave-one-out evaluation script computing Precision@k, Recall@k, and Hit Rate across 30 synthetic students

## Tech Stack

- **Frontend**: React 18, Vite, Tailwind CSS, Lucide React
- **Backend**: Flask, SQLAlchemy, PostgreSQL
- **ML/Graph**: NetworkX (prerequisite DAG), NumPy, item-based collaborative filtering
- **LLM**: OpenAI GPT-4o-mini (advisory messages, job skill extraction)
- **Auth**: Session-based (Flask sessions)

## Project Structure

```
AI-Course-Advisor/
├── frontend/                    # React + Vite app
│   ├── src/
│   │   ├── App.jsx
│   │   ├── CourseAdvisor.jsx    # Main shell with cold start detection
│   │   ├── api.js               # API client
│   │   └── components/
│   │       ├── course-advisor/
│   │       │   ├── AdvisorTab.jsx       # Chat + job title input
│   │       │   ├── CourseCard.jsx       # Explainability pills + grade prediction
│   │       │   ├── OnboardingQuiz.jsx   # Cold start 4-step wizard
│   │       │   ├── ProgressPanel.jsx
│   │       │   ├── ProfilePanel.jsx
│   │       │   └── DifficultyBadge.jsx
│   │       └── auth/
│   └── package.json
├── backend/                     # Flask API
│   ├── app.py                   # Routes (recommend, onboarding, prerequisite-path)
│   ├── models.py                # DB models (Course.skills, Student.target_job_title)
│   ├── services.py              # Multi-signal scoring engine
│   ├── llm.py                   # GPT-4o-mini: advisory messages + job skill extraction
│   ├── knowledge_graph.py       # NetworkX prerequisite DAG
│   ├── collaborative.py         # Item-based collaborative filtering
│   ├── grade_predictor.py       # Historical grade-based prediction
│   ├── evaluate.py              # Leave-one-out evaluation metrics
│   ├── seed.py                  # Courses, demo user, 30 synthetic students
│   ├── config.py
│   └── requirements.txt
└── README.md
```

## Setup

### 1. Backend

Requires Python 3.10-3.12 (Python 3.13 may have compatibility issues).

```bash
cd backend
python3.12 -m venv venv   # or python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python seed.py             # Seed courses, demo user, and 30 synthetic students
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

New user registration triggers the onboarding quiz for cold start handling.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new student |
| POST | `/api/auth/login` | Login |
| POST | `/api/auth/logout` | Logout |
| GET | `/api/auth/me` | Get current user |
| GET | `/api/profile` | Get profile |
| PUT | `/api/profile` | Update profile (supports `targetJobTitle`) |
| GET | `/api/courses` | List all courses (with skills) |
| POST | `/api/recommend` | Get recommendations (accepts `targetJobTitle`) |
| GET | `/api/progress` | Get degree progress |
| POST | `/api/onboarding` | Submit onboarding quiz answers |
| GET | `/api/prerequisite-path?target=CS301` | Get prerequisite path to a course |
| GET | `/api/prerequisite-graph` | Get full prerequisite graph |
| GET | `/api/programs` | List programs |
| GET | `/api/programs/:id` | Get program details |
| GET | `/api/health` | Health check |

## Recommendation Scoring Engine

Each candidate course is scored using multiple signals:

| Signal | Points | Description |
|--------|--------|-------------|
| Prerequisite eligibility | +50 | All prerequisites completed (via knowledge graph) |
| Interest/topic match | +30 | Course topics align with student interests |
| Query keywords | +10..40 | Matches to ML/AI/web keywords in the query |
| Collaborative filtering | +25 * ratio | Fraction of similar students who took this course |
| Job market alignment | +15 per skill | Skills matching target job title |
| GPA protection | -10 | Penalty if predicted grade would lower overall GPA |

The top 6 courses by total score are returned, each with structured `explanationFactors` for transparency.

## Evaluation

The system is evaluated using a **leave-one-out** protocol on 30 synthetic students:

1. For each student, each completed course is held out one at a time
2. The recommender runs on the reduced profile
3. A "hit" is recorded if the held-out course appears in the top-k recommendations

Run the evaluation:

```bash
cd backend
python evaluate.py
```

### Metrics

| Metric | k=3 | k=6 |
|--------|-----|-----|
| Hit Rate@k | Fraction of holdouts found in top-k |
| Precision@k | Hits / k, averaged across evaluations |
| Recall@k | Hits / 1 (one relevant item), averaged |

These metrics validate that the multi-signal scoring engine can recover courses that students actually took, demonstrating the system's predictive quality beyond random ranking.

## Environment Variables

Create `backend/.env` (optional):

```
FLASK_ENV=development
DATABASE_URL=postgresql://localhost/course_advisor
SECRET_KEY=your-secret-key
OPENAI_API_KEY=your-openai-api-key-here
```

The `OPENAI_API_KEY` enables GPT-4o-mini for:
- Personalized advisory messages with explainability-aware prompting
- Job skill extraction from target job titles

Without it, the system falls back to template-based messages and keyword-based skill matching.
