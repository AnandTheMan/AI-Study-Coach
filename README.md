# AI Study Coach

The AI Study Coach is a cloud-deployed adaptive study support system that generates exam-style papers, evaluates answers automatically using AI, and tracks user performance over time.

The system follows a client–server architecture:

- **Frontend:** Streamlit web application for user interaction
- **Backend:** FastAPI REST API deployed on Render
- **Database:** SQLite with SQLAlchemy ORM
- **AI Services:** OpenAI API used for question generation and automated grading

Frontend and backend communicate through authenticated HTTP requests using JWT tokens.

## Features

-  **Generate Papers**: Create examination papers from curriculum or uploaded documents
-  **My Papers**: Save and attempt papers later
-  **AI Evaluation**: Instant evaluation with detailed feedback and correct answers
-  **Dashboard**: Track progress with statistics and visualizations
-  **Authentication**: Secure user accounts with JWT tokens

##  How to Start Application
Simply open this link:
https://anand-ai-study-coach.streamlit.app/

Then put in this email and password:
Email: testerman123@gmail.com

Password: testerman123

Note: This is a demonstration account provided for project evaluation purposes. If for whatever reason, just sign up a fresh account with the above credentials, and it will work.

The backend of the AI Study Coach is deployed as a FastAPI REST service on the Render cloud platform:

https://ai-study-coach-backend.onrender.com/

When accessed directly, the API returns a JSON response listing the available endpoints for the system, including authentication, paper generation, automated evaluation, and dashboard analytics.

The Streamlit frontend communicates with this backend using HTTP requests secured by JWT authentication tokens. The backend handles the core application logic such as generating examination papers using AI, evaluating submitted answers, storing papers in the database, and returning user performance statistics. Users do not need to interact with the backend API directly. To run and use the application, simply access the Streamlit frontend link provided above. The backend endpoint is included here for completeness and transparency regarding the system’s deployed architecture.

##  Project Structure

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
- `GET /api/auth/me` - Get current authenticated user details

### Papers
- `POST /api/generate_paper` - Generate examination paper from curriculum parameters
- `POST /api/generate_paper_from_document` - Generate examination paper from uploaded document
- `POST /api/generate_paper_from_media` - Generate examination paper from media input
- `GET /api/papers/{paper_id}` - Get specific paper with questions

### Evaluation
- `POST /api/evaluate_paper` - Evaluate submitted answers for a paper

### Dashboard
- `GET /api/dashboard` - Get user statistics and performance analytics
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




