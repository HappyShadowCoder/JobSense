# JobSense — AI-Powered Job Application Tracker

> Track every application. Analyse every opportunity. Land the right role.

![Status](https://img.shields.io/badge/status-active-brightgreen)
![Stack](https://img.shields.io/badge/stack-Next.js%20%7C%20Flask%20%7C%20PostgreSQL-blue)
![Auth](https://img.shields.io/badge/auth-Clerk-purple)
![Database](https://img.shields.io/badge/database-Neon%20PostgreSQL-teal)

---

## What is JobSense?

JobSense is a full-stack web application built for students and developers actively applying for jobs and internships. It combines a clean job application tracker with AI-powered resume analysis — giving you a match score, skill gap breakdown, and personalised suggestions every time you paste a job description.

Built as a real product, not a tutorial. Every feature solves a problem that job seekers face every day.

---

## Features

### ✅ Job Application Tracker
- Add every job you've applied to with company, role, status, date, and notes
- Kanban-style board organised by application status
- Move applications across stages — Saved → Applied → Screening → Interview → Offer → Rejected
- Full CRUD — add, edit, update status, delete

### ✅ Authentication
- Sign up and sign in with Email, Google, or GitHub
- Powered by Clerk — production-grade auth with zero configuration
- Every user's data is fully isolated and private

### ✅ Dashboard
- Personalised greeting with your name
- Live stats showing count of applications per status
- Quick navigation to all features

### 🔜 AI Resume Analyser *(Week 2)*
- Upload your resume as PDF or DOCX
- Paste any job description
- Get an AI-powered match score (0–100%)
- See exactly which skills match and which are missing
- Receive personalised suggestions on what to add or improve
- Powered by LangChain + Google Gemini Pro

### 🔜 ML Skill Scoring *(Week 3)*
- Machine learning model trained on real job description data
- Cosine similarity scoring using sentence-transformers embeddings
- Gets smarter as more users submit job descriptions

### 🔜 Skill Trends Dashboard *(Week 3)*
- Weekly aggregation of the most in-demand skills across all submitted JDs
- Visual charts showing which skills are rising in demand
- Helps you decide what to learn next

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 14, TypeScript, Tailwind CSS |
| Backend | Flask (Python) |
| Authentication | Clerk (Email, Google, GitHub OAuth) |
| Database | PostgreSQL hosted on Neon |
| AI / LLM | LangChain + Google Gemini Pro *(Week 2)* |
| ML Model | scikit-learn + sentence-transformers *(Week 3)* |
| File Storage | Cloudinary *(Week 2)* |
| Deploy | Vercel (frontend) + Render (backend) *(Week 4)* |

---

## Project Structure

```
jobsense/
├── frontend/                  # Next.js 14 App
│   ├── app/
│   │   ├── dashboard/         # Stats overview
│   │   ├── tracker/           # Kanban board
│   │   ├── analyze/           # Resume + JD analysis (Week 2)
│   │   ├── trends/            # Skill trends (Week 3)
│   │   └── sign-in / sign-up  # Clerk auth pages
│   ├── components/            # Reusable UI components
│   ├── lib/api.ts             # Axios API client
│   └── types/index.ts         # Shared TypeScript types
│
├── backend/                   # Flask REST API
│   ├── routes/                # HTTP route handlers
│   │   ├── applications.py    # Full CRUD ✅
│   │   ├── resumes.py         # Week 2
│   │   ├── analyses.py        # Week 2
│   │   └── trends.py          # Week 3
│   ├── services/              # Business logic
│   ├── ml/                    # ML model training & serving
│   └── utils/
│       ├── db.py              # PostgreSQL connection pool
│       └── clerk.py           # Auth middleware
│
└── database/
    └── schema.sql             # Full PostgreSQL schema
```

---

## Database Schema

| Table | Purpose |
|---|---|
| `users` | User accounts (synced with Clerk) |
| `applications` | Job applications with status tracking |
| `resumes` | Uploaded resumes + extracted skills |
| `analyses` | AI analysis results — match score, gaps, suggestions |
| `skill_trends` | Weekly aggregated skill demand data |
| `refresh_tokens` | JWT refresh token management |

---

## API Endpoints

| Method | Endpoint | Description | Status |
|---|---|---|---|
| GET | `/api/health` | Health check | ✅ |
| GET | `/api/applications/` | List all applications | ✅ |
| POST | `/api/applications/` | Add new application | ✅ |
| PATCH | `/api/applications/:id` | Update status / notes | ✅ |
| DELETE | `/api/applications/:id` | Delete application | ✅ |
| GET | `/api/applications/stats` | Count per status | ✅ |
| POST | `/api/resumes/` | Upload resume | Week 2 |
| POST | `/api/analyses/` | Run AI analysis | Week 2 |
| GET | `/api/trends/` | Get skill trends | Week 3 |

---

## Getting Started

### Prerequisites
- Node.js 18+
- Python 3.11+
- A [Neon](https://neon.tech) account (free)
- A [Clerk](https://clerk.com) account (free)

### 1. Clone the repository
```bash
git clone https://github.com/your-username/jobsense.git
cd jobsense
```

### 2. Set up the database
1. Create a free project at [neon.tech](https://neon.tech)
2. Copy your connection string
3. Run the schema in the Neon SQL editor:
```sql
-- paste contents of database/schema.sql
```

### 3. Set up the backend
```bash
cd backend
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env          # fill in your values
python app.py
# → Running on http://localhost:8000
```

### 4. Set up the frontend
```bash
cd frontend
npm install
cp .env.example .env.local    # fill in your values
npm run dev
# → Running on http://localhost:3000
```

### Environment Variables

**`backend/.env`**
```
FLASK_DEBUG=1
SECRET_KEY=your-secret
DATABASE_URL=postgresql://...
CLERK_SECRET_KEY=sk_test_...
```

**`frontend/.env.local`**
```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...
NEXTAUTH_SECRET=your-secret
```

---

## Build Roadmap

- [x] **Week 1** — Auth, PostgreSQL schema, Job application tracker, Dashboard
- [x] **Week 2** — Resume upload, LangChain AI analysis, Skill gap feature
- [x] **Week 3** — ML scoring model, Skill trends dashboard
- [ ] **Week 4** — Deploy to Vercel + Render, real user testing

---

## Why I Built This

Every student applying for internships faces the same problem — no visibility into their job search, no feedback on why they're not getting calls, and no idea which skills are actually in demand right now.

JobSense solves all three. It started as a personal tool and became a full product built with the same stack used in industry.

---

*If this helped you, leave a ⭐ on the repo.*
