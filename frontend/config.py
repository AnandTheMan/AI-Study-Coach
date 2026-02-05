"""
Configuration file for the frontend application
"""
import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Page Configuration
PAGE_TITLE = "Oxford Examination System"
PAGE_ICON = "📚"

# UI Configuration
SIDEBAR_STATE = "expanded"
MENU_ITEMS = {
    'Get Help': 'https://github.com/yourusername/oxford-exam-system',
    'Report a bug': "https://github.com/yourusername/oxford-exam-system/issues",
    'About': "Oxford Examination System - Generate and evaluate examination papers with AI"
}
