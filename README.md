# AI Study Coach

AI-powered examination paper generation and evaluation system with automatic grading and feedback.

## Features

- 📝 **Generate Papers**: Create examination papers from curriculum or uploaded documents
- 📚 **My Papers**: Save and attempt papers later
- ✅ **AI Evaluation**: Instant evaluation with detailed feedback and correct answers
- 📊 **Dashboard**: Track progress with statistics and visualizations
- 🔐 **Authentication**: Secure user accounts with JWT tokens

## 🚀 Quick Setup (New System)

### Prerequisites
- Python 3.8 or higher
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

### One-Command Setup

```bash
# Windows
setup.bat

# Or manually:
python setup.py
```

This will:
- ✓ Create virtual environment
- ✓ Install all dependencies
- ✓ Configure environment variables
- ✓ Initialize database
- ✓ Verify setup

### Start the Application

```bash
python start_app.py
```

Access at: **http://localhost:8501**

---

## 📋 Manual Setup (If Needed)

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install requirements
pip install -r requirements.txt
```

### 2. Configure Environment

**Create `backend/.env`:**
```env
OPENAI_API_KEY=your_actual_api_key_here
DATABASE_URL=sqlite:///./oxford_papers.db
SECRET_KEY=your-secret-key-here
```

**Create `frontend/.env`:**
```env
API_BASE_URL=http://localhost:8000
```

### 3. Run Application

**Option 1: Unified Start (Recommended)**
```bash
python start_app.py
```

**Option 2: Manual Start**
```bash
# Terminal 1 - Backend
cd backend
python main.py

# Terminal 2 - Frontend
cd frontend
streamlit run app.py
```

---

## 🔧 Troubleshooting on New System

### Quick Diagnostic Check

Run this first to identify issues:
```bash
# Windows
check_backend.bat

# Or manually:
cd backend
python check_backend.py
```

This checks:
- ✓ Python version
- ✓ Dependencies installed
- ✓ .env configuration
- ✓ OpenAI API key
- ✓ Database setup
- ✓ Port availability

### Common Issues

#### 1. Backend Not Starting (ERR_INVALID_RESPONSE)

**Symptoms:** Can't reach http://localhost:8000, frontend shows connection errors

**Fixes:**
```bash
# Step 1: Check if dependencies are installed
pip install -r requirements.txt

# Step 2: Verify .env file exists
cd backend
# Create .env if missing and add:
# OPENAI_API_KEY=sk-your-actual-key-here
# DATABASE_URL=sqlite:///./oxford_papers.db
# SECRET_KEY=your-secret-key

# Step 3: Run diagnostics
python check_backend.py

# Step 4: Try starting backend
python main.py
```

#### 2. "Extra data: line 1 column 4 (char 3)"

**Cause:** Backend not responding or frontend can't connect

**Fix:**
1. Verify backend is running: Open http://localhost:8000/docs
2. If not accessible, backend isn't running - see issue #1 above
3. Check firewall isn't blocking port 8000

#### 3. Missing OpenAI API Key

**Error:** "OpenAI API Key not configured"

**Fix:**
1. Get key from https://platform.openai.com/api-keys
2. Edit `backend/.env`:
   ```env
   OPENAI_API_KEY=sk-proj-your-actual-key-here
   ```
3. Restart backend

#### 4. Import Errors

**Error:** "ModuleNotFoundError: No module named 'fastapi'"

**Fix:**
```bash
# Make sure you're in the project directory
cd AI-Study-Coach

# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install requirements
pip install -r requirements.txt
```

#### 5. Port Already in Use

**Error:** "Port 8000 is already in use"

**Fix:**
```bash
# Windows: Find and kill process on port 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Or change port in backend/main.py:
# uvicorn.run(app, host="0.0.0.0", port=8001)
```

### Setup on Brand New System

**Complete setup from scratch:**

1. **Clone Repository**
   ```bash
   git clone https://github.com/AnandTheMan/AI-Study-Coach.git
   cd AI-Study-Coach
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment**
   - Copy `backend/.env.example` to `backend/.env`
   - Add your OpenAI API key
   - Copy `frontend/.env.example` to `frontend/.env`

5. **Run Diagnostics**
   ```bash
   cd backend
   python check_backend.py
   ```

6. **Start Application**
   ```bash
   cd ..
   python start_app.py
   ```

---

## 📁 Project Structure

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



