"""
Main application file - Home/Landing Page
"""
import streamlit as st
import config
import utils

# Page configuration
st.set_page_config(
    page_title=config.PAGE_TITLE,
    page_icon=config.PAGE_ICON,
    layout="wide",
    initial_sidebar_state=config.SIDEBAR_STATE,
    menu_items=config.MENU_ITEMS
)

# Initialize session state
utils.init_session_state()

# Create sidebar
utils.create_sidebar()


def show_login_page():
    """Display login page"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 40px 0 30px 0;">
            <h1 style="color: #0066cc; font-size: 48px; margin-bottom: 10px;">📚</h1>
            <h1 style="color: #0066cc;">AI Study Coach</h1>
            <p style="color: #666; font-size: 18px;">Generate and evaluate examination papers with AI</p>
        </div>
        """, unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])
        
        # Login Tab
        with tab1:
            st.markdown("### Welcome Back!")
            with st.form("login_form"):
                email = st.text_input("📧 Email", placeholder="Enter your email")
                password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
                submit = st.form_submit_button("Login", use_container_width=True)
                
                if submit:
                    if email and password:
                        with st.spinner("Logging in..."):
                            result = utils.make_api_request(
                                "/api/auth/login",
                                method="POST",
                                data={"email": email, "password": password},
                                use_auth=False
                            )
                            
                            if result["success"]:
                                data = result["data"]
                                st.session_state.token = data["access_token"]
                                st.session_state.user = data["user"]
                                st.session_state.authenticated = True
                                utils.display_success("Login successful!")
                                st.rerun()
                            else:
                                utils.display_error(result["error"])
                    else:
                        utils.display_error("Please enter both email and password")
        
        # Sign Up Tab
        with tab2:
            st.markdown("### Create New Account")
            with st.form("signup_form"):
                full_name = st.text_input("👤 Full Name", placeholder="Enter your full name")
                username = st.text_input("🏷️ Username", placeholder="Choose a username")
                email_signup = st.text_input("📧 Email", placeholder="Enter your email")
                password_signup = st.text_input("🔒 Password", type="password", placeholder="Choose a password (min 6 characters)")
                password_confirm = st.text_input("🔒 Confirm Password", type="password", placeholder="Confirm your password")
                submit_signup = st.form_submit_button("Create Account", use_container_width=True)
                
                if submit_signup:
                    if not all([full_name, username, email_signup, password_signup, password_confirm]):
                        utils.display_error("Please fill in all fields")
                    elif password_signup != password_confirm:
                        utils.display_error("Passwords do not match")
                    elif len(password_signup) < 6:
                        utils.display_error("Password must be at least 6 characters long")
                    else:
                        with st.spinner("Creating account..."):
                            result = utils.make_api_request(
                                "/api/auth/signup",
                                method="POST",
                                data={
                                    "email": email_signup,
                                    "username": username,
                                    "password": password_signup,
                                    "full_name": full_name
                                },
                                use_auth=False
                            )
                            
                            if result["success"]:
                                data = result["data"]
                                st.session_state.token = data["access_token"]
                                st.session_state.user = data["user"]
                                st.session_state.authenticated = True
                                utils.display_success("Account created successfully!")
                                st.rerun()
                            else:
                                utils.display_error(result["error"])


def show_home_page():
    """Display home page for authenticated users"""
    st.markdown(f"""
    <div style="text-align: center; padding: 20px 0 40px 0;">
        <h1 style="color: #0066cc;">Welcome, {st.session_state.user.get('full_name', 'User')}! 👋</h1>
        <p style="color: #666; font-size: 20px;">AI Study Coach Dashboard</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Feature cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 30px;
            border-radius: 15px;
            color: white;
            text-align: center;
            height: 250px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        ">
            <h1 style="font-size: 48px; margin: 0;">📝</h1>
            <h3 style="margin: 15px 0 10px 0;">Generate Papers</h3>
            <p style="font-size: 14px; opacity: 0.9;">Create examination papers based on curriculum or upload documents</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Go to Paper Generation", key="gen_btn", use_container_width=True):
            st.switch_page("pages/1_📝_Generate_Paper.py")
    
    with col2:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
            padding: 30px;
            border-radius: 15px;
            color: white;
            text-align: center;
            height: 250px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        ">
            <h1 style="font-size: 48px; margin: 0;">📚</h1>
            <h3 style="margin: 15px 0 10px 0;">My Papers</h3>
            <p style="font-size: 14px; opacity: 0.9;">View and attempt your saved papers anytime</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("View My Papers", key="papers_btn", use_container_width=True):
            st.switch_page("pages/4_📚_My_Papers.py")
    
    with col3:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            padding: 30px;
            border-radius: 15px;
            color: white;
            text-align: center;
            height: 250px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        ">
            <h1 style="font-size: 48px; margin: 0;">✅</h1>
            <h3 style="margin: 15px 0 10px 0;">Evaluate Answers</h3>
            <p style="font-size: 14px; opacity: 0.9;">Submit answers and get instant AI-powered evaluation</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Go to Evaluation", key="eval_btn", use_container_width=True):
            st.switch_page("pages/2_✅_Evaluate_Paper.py")
    
    with col4:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            padding: 30px;
            border-radius: 15px;
            color: white;
            text-align: center;
            height: 250px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        ">
            <h1 style="font-size: 48px; margin: 0;">📊</h1>
            <h3 style="margin: 15px 0 10px 0;">Dashboard</h3>
            <p style="font-size: 14px; opacity: 0.9;">View your progress, statistics, and history</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Go to Dashboard", key="dash_btn", use_container_width=True):
            st.switch_page("pages/3_📊_Dashboard.py")
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Quick Stats
    with st.spinner("Loading your statistics..."):
        result = utils.make_api_request("/api/dashboard", method="GET")
        
        if result["success"]:
            data = result["data"]
            
            st.markdown("### 📈 Quick Statistics")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Papers Generated", data.get("total_papers", 0))
            with col2:
                st.metric("Total Evaluations", data.get("total_evaluations", 0))
            with col3:
                st.metric("Average Score", f"{data.get('average_score', 0):.1f}%")
            with col4:
                recent_papers = data.get("recent_papers", [])
                st.metric("Recent Papers", len(recent_papers))
            
            # Recent Activity
            if recent_papers:
                st.markdown("### 📋 Recent Papers")
                for paper in recent_papers[:3]:
                    with st.expander(f"{paper['subject']} - {paper['chapter']} ({utils.format_date(paper['created_at'])})"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Grade:** {paper.get('grade', 'N/A')}")
                            st.write(f"**Type:** {paper.get('type', 'N/A')}")
                        with col2:
                            st.write(f"**Total Marks:** {paper.get('total_marks', 'N/A')}")
                            st.write(f"**Paper ID:** {paper.get('id', 'N/A')}")


# Main app logic
if not st.session_state.authenticated:
    show_login_page()
else:
    show_home_page()

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px 0;">
    <p>AI Study Coach © 2026 | Powered by AI</p>
</div>
""", unsafe_allow_html=True)
