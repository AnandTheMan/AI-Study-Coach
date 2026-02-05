"""
Utility functions for the frontend application
"""
import requests
import streamlit as st
from typing import Dict, Any, Optional, List
import config


def make_api_request(
    endpoint: str,
    method: str = "GET",
    data: Optional[Dict] = None,
    files: Optional[Dict] = None,
    use_auth: bool = True
) -> Dict[str, Any]:
    """
    Make an API request to the backend
    
    Args:
        endpoint: API endpoint (e.g., "/api/auth/login")
        method: HTTP method (GET, POST, etc.)
        data: Request data (for POST, PUT)
        files: Files to upload
        use_auth: Whether to include authentication token
    
    Returns:
        Response data as dictionary
    """
    url = f"{config.API_BASE_URL}{endpoint}"
    headers = {}
    
    if use_auth and "token" in st.session_state:
        headers["Authorization"] = f"Bearer {st.session_state.token}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            if files:
                response = requests.post(url, headers=headers, data=data, files=files)
            else:
                response = requests.post(url, headers=headers, json=data)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        if response.status_code in [200, 201]:
            return {"success": True, "data": response.json()}
        else:
            return {
                "success": False,
                "error": response.json().get("detail", "Unknown error occurred")
            }
    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "error": "Cannot connect to backend server. Please ensure the server is running."
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def init_session_state():
    """Initialize session state variables"""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "token" not in st.session_state:
        st.session_state.token = None
    if "user" not in st.session_state:
        st.session_state.user = None
    if "current_paper" not in st.session_state:
        st.session_state.current_paper = None


def logout():
    """Clear session state and logout user"""
    st.session_state.authenticated = False
    st.session_state.token = None
    st.session_state.user = None
    st.session_state.current_paper = None


def display_error(message: str):
    """Display error message with consistent styling"""
    st.error(f"❌ {message}")


def display_success(message: str):
    """Display success message with consistent styling"""
    st.success(f"✅ {message}")


def display_info(message: str):
    """Display info message with consistent styling"""
    st.info(f"ℹ️ {message}")


def display_warning(message: str):
    """Display warning message with consistent styling"""
    st.warning(f"⚠️ {message}")


def format_date(date_str: str) -> str:
    """Format ISO date string to readable format"""
    from datetime import datetime
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime("%B %d, %Y at %I:%M %p")
    except:
        return date_str


def get_grade_color(percentage: float) -> str:
    """Get color based on grade percentage"""
    if percentage >= 90:
        return "#4CAF50"  # Green
    elif percentage >= 80:
        return "#8BC34A"  # Light Green
    elif percentage >= 70:
        return "#FFC107"  # Amber
    elif percentage >= 60:
        return "#FF9800"  # Orange
    else:
        return "#F44336"  # Red


def display_question_card(question: Dict, index: int):
    """Display a question in a card format"""
    with st.container():
        st.markdown(f"""
        <div style="
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid #0066cc;
            margin-bottom: 20px;
        ">
            <h4 style="color: #0066cc; margin-top: 0;">Question {question['question_number']}</h4>
            <p style="font-size: 16px; color: #333;"><strong>Type:</strong> {question['question_type']}</p>
            <p style="font-size: 16px; color: #333;"><strong>Marks:</strong> {question['marks']}</p>
            <p style="font-size: 18px; margin-top: 15px; color: #000;">{question['question_text']}</p>
        """, unsafe_allow_html=True)
        
        if question.get('options'):
            st.markdown("<p style='font-size: 16px; margin-top: 10px;'><strong>Options:</strong></p>", unsafe_allow_html=True)
            for i, option in enumerate(question['options'], 1):
                st.markdown(f"<p style='margin-left: 20px; font-size: 15px;'>{chr(64+i)}. {option}</p>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)


def create_sidebar():
    """Create sidebar with navigation and user info"""
    with st.sidebar:
        st.markdown(f"""
        <div style="text-align: center; padding: 20px 0;">
            <h1 style="color: #0066cc; margin: 0;">📚</h1>
            <h2 style="color: #0066cc; margin: 10px 0;">Oxford Exam</h2>
            <p style="color: #666; font-size: 14px;">Examination System</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.authenticated and st.session_state.user:
            st.markdown("---")
            st.markdown(f"**👤 {st.session_state.user.get('full_name', 'User')}**")
            st.markdown(f"📧 {st.session_state.user.get('email', '')}")
            st.markdown("---")
            
            if st.button("🚪 Logout", use_container_width=True):
                logout()
                st.rerun()


def validate_paper_form(grade: str, subject: str, chapter: str) -> bool:
    """Validate paper generation form"""
    if not grade or not subject or not chapter:
        display_error("Please fill in all required fields")
        return False
    return True
