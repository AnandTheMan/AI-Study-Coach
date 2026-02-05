# Oxford Examination System

AI-powered examination paper generation and evaluation system with automatic grading and feedback.

## Features

- 📝 **Generate Papers**: Create examination papers from curriculum or uploaded documents
- 📚 **My Papers**: Save and attempt papers later
- ✅ **AI Evaluation**: Instant evaluation with detailed feedback and correct answers
- 📊 **Dashboard**: Track progress with statistics and visualizations
- 🔐 **Authentication**: Secure user accounts with JWT tokens

## Quick Start

### Prerequisites
- Python 3.11.9
- OpenAI API key

### Installation

1. **Install Backend Dependencies**
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

2. **Install Frontend Dependencies**
```bash
cd frontend
pip install -r requirements.txt
```

3. **Configure Environment Variables**

Create `backend/.env`:
```env
OPENAI_API_KEY=your_openai_api_key_here
DATABASE_URL=sqlite:///./oxford_papers.db
SECRET_KEY=your-secret-key-here
```

Create `frontend/.env`:
```env
API_BASE_URL=http://localhost:8000
```

### Running the Application

#### Option 1: Unified Launcher (Recommended)

Double-click `start_app.bat` or run:
```bash
python start_app.py
```

This starts both backend and frontend together!

#### Option 2: Manual Start

**Terminal 1 - Backend:**
```bash
cd backend
venv\Scripts\activate
python main.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
streamlit run app.py
```

### Access the Application

- **Frontend**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Usage

1. **Sign Up / Login**: Create an account or login
2. **Generate Paper**: 
   - Choose curriculum-based or document-based generation
   - Fill in subject, chapter, grade details
   - AI generates relevant questions
3. **Solve Paper**: Answer questions directly on the page
4. **Get Evaluation**: Submit for instant AI grading with feedback
5. **View Results**: See your score, grade, correct answers, and detailed feedback
6. **Save Papers**: All papers are automatically saved to "My Papers"
7. **Attempt Later**: Access saved papers anytime from "My Papers" page
8. **Track Progress**: View statistics and history on Dashboard

## Project Structure

```
Study/
├── backend/
│   ├── venv/                 # Python virtual environment
│   ├── main.py              # FastAPI application
│   ├── database.py          # SQLAlchemy models
│   ├── auth.py              # Authentication logic
│   ├── schemas_new.py       # Pydantic schemas
│   ├── openai_service.py    # AI paper generation
│   └── requirements.txt     # Backend dependencies
├── frontend/
│   ├── app.py               # Home page (login/signup)
│   ├── pages/
│   │   ├── 1_📝_Generate_Paper.py    # Paper generation
│   │   ├── 2_✅_Evaluate_Paper.py    # Standalone evaluation
│   │   ├── 3_📊_Dashboard.py         # Statistics
│   │   └── 4_📚_My_Papers.py         # Saved papers
│   ├── utils.py             # API helpers
│   └── requirements.txt     # Frontend dependencies
├── start_app.py             # Unified launcher
└── start_app.bat           # Windows launcher

```

## API Endpoints

### Authentication
- `POST /api/auth/signup` - Create new account
- `POST /api/auth/login` - Login

### Papers
- `GET /api/papers` - List user's papers
- `GET /api/papers/{id}` - Get specific paper with questions
- `POST /api/generate_paper` - Generate from curriculum
- `POST /api/generate_paper_from_document` - Generate from document

### Evaluation
- `POST /api/evaluate_paper` - Evaluate answers

### Dashboard
- `GET /api/dashboard` - Get user statistics

## Technology Stack

### Backend
- **FastAPI** 0.109.0 - Modern Python web framework
- **SQLAlchemy** 2.0.25 - ORM for database
- **SQLite** - Lightweight database
- **OpenAI** 1.54.0 - AI for generation and evaluation
- **JWT** - Secure authentication
- **Bcrypt** 4.0.1 - Password hashing

### Frontend
- **Streamlit** 1.31.0 - Interactive web app framework
- **Plotly** 5.18.0 - Interactive charts
- **Pandas** 2.2.0 - Data manipulation

## Key Features Detail

### Paper Generation
- **Curriculum-based**: Specify subject, chapter, grade, topics
- **Document-based**: Upload PDF/DOCX/TXT files
- AI generates diverse question types (MCQ, Short Answer, Long Answer)
- Appropriate difficulty levels based on grade

### Interactive Solving
- Answer questions directly on the generation page
- MCQ questions use dropdown selection
- Other questions use text areas
- Real-time validation

### AI Evaluation
- Instant feedback on each answer
- Marks allocation per question
- Overall grade (A+ to F)
- Detailed feedback and suggestions
- **Correct answers displayed** for each question
- Progress bars showing performance

### Paper Management
- All papers automatically saved to database
- Access from "My Papers" page
- Search and filter by subject/grade
- Attempt any saved paper anytime
- Full question text and evaluation history

### Dashboard Analytics
- Total papers generated
- Papers evaluated
- Average score tracking
- Grade distribution charts
- Recent papers list
- Performance trends

## Development Notes

- **Pydantic v2**: Uses `model_validate()` instead of `from_orm()`
- **Bcrypt 4.0.1**: Downgraded for passlib compatibility
- **Session State**: Streamlit session management for user data
- **JWT Tokens**: Stored in session state for API authentication

## Troubleshooting

### Backend won't start
- Ensure OpenAI API key is set in `backend/.env`
- Check if port 8000 is available
- Verify virtual environment is activated

### Frontend errors
- Ensure backend is running first
- Check `frontend/.env` has correct API_BASE_URL
- Verify all dependencies installed

### Database issues
- Delete `backend/oxford_papers.db` to reset
- Database auto-creates on first run



