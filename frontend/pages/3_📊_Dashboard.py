"""
Dashboard Page - Statistics and History
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import sys
sys.path.append('..')
import config
import utils

st.set_page_config(
    page_title=f"{config.PAGE_TITLE} - Dashboard",
    page_icon=config.PAGE_ICON,
    layout="wide"
)

utils.init_session_state()
utils.create_sidebar()

# Check authentication
if not st.session_state.authenticated:
    st.warning("⚠️ Please login first")
    if st.button("Go to Login"):
        st.switch_page("app.py")
    st.stop()

st.markdown("""
<div style="text-align: center; padding: 20px 0;">
    <h1 style="color: #0066cc;">📊 Your Dashboard</h1>
    <p style="color: #666; font-size: 18px;">Track your progress and performance</p>
</div>
""", unsafe_allow_html=True)

# Fetch dashboard data
with st.spinner("Loading dashboard data..."):
    result = utils.make_api_request("/api/dashboard", method="GET")
    
    if not result["success"]:
        utils.display_error(result["error"])
        st.stop()
    
    data = result["data"]

# Key Metrics
st.markdown("### 📈 Overview")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 25px;
        border-radius: 15px;
        color: white;
        text-align: center;
    ">
        <h1 style="font-size: 40px; margin: 0;">{}</h1>
        <p style="font-size: 16px; margin: 10px 0 0 0; opacity: 0.9;">Papers Generated</p>
    </div>
    """.format(data.get('total_papers', 0)), unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 25px;
        border-radius: 15px;
        color: white;
        text-align: center;
    ">
        <h1 style="font-size: 40px; margin: 0;">{}</h1>
        <p style="font-size: 16px; margin: 10px 0 0 0; opacity: 0.9;">Evaluations Done</p>
    </div>
    """.format(data.get('total_evaluations', 0)), unsafe_allow_html=True)

with col3:
    avg_score = data.get('average_score', 0)
    color = utils.get_grade_color(avg_score)
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 25px;
        border-radius: 15px;
        color: white;
        text-align: center;
    ">
        <h1 style="font-size: 40px; margin: 0;">{:.1f}%</h1>
        <p style="font-size: 16px; margin: 10px 0 0 0; opacity: 0.9;">Average Score</p>
    </div>
    """.format(avg_score), unsafe_allow_html=True)

with col4:
    recent_papers = data.get('recent_papers', [])
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        padding: 25px;
        border-radius: 15px;
        color: white;
        text-align: center;
    ">
        <h1 style="font-size: 40px; margin: 0;">{}</h1>
        <p style="font-size: 16px; margin: 10px 0 0 0; opacity: 0.9;">Recent Papers</p>
    </div>
    """.format(len(recent_papers)), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Charts
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📊 Grade Distribution")
    grade_dist = data.get('grade_distribution', {})
    
    if grade_dist:
        df_grades = pd.DataFrame(list(grade_dist.items()), columns=['Grade', 'Count'])
        
        fig = px.pie(
            df_grades,
            values='Count',
            names='Grade',
            title='',
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(
            showlegend=True,
            height=350,
            margin=dict(t=0, b=0, l=0, r=0)
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No grade data available yet. Complete evaluations to see grade distribution.")

with col2:
    st.markdown("### 📈 Subject Performance")
    subject_perf = data.get('subject_performance', [])
    
    if subject_perf:
        df_subjects = pd.DataFrame(subject_perf)
        
        fig = px.bar(
            df_subjects,
            x='subject',
            y='average_score',
            title='',
            color='average_score',
            color_continuous_scale='Blues',
            labels={'subject': 'Subject', 'average_score': 'Average Score (%)'}
        )
        fig.update_layout(
            showlegend=False,
            height=350,
            xaxis_title="Subject",
            yaxis_title="Average Score (%)",
            margin=dict(t=0, b=0, l=0, r=0)
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No subject performance data available yet. Generate papers to see subject-wise performance.")

st.markdown("---")

# Recent Papers
st.markdown("### 📋 Recent Papers")
if recent_papers:
    for paper in recent_papers:
        # Determine paper type display
        paper_type = paper.get('type', 'curriculum')
        
        if paper_type == 'media':
            icon = "🎥"
            title = f"{icon} Media Paper: {paper.get('document_name', 'N/A')}"
        elif paper_type == 'document':
            icon = "📄"
            title = f"{icon} Document Paper: {paper.get('document_name', 'N/A')}"
        else:
            icon = "📚"
            title = f"{icon} {paper.get('subject', 'N/A')} - {paper.get('chapter', 'N/A')} | Grade: {paper.get('grade', 'N/A')}"
        
        with st.expander(f"{title} | {utils.format_date(paper['created_at'])}"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"**Paper ID:** {paper['id']}")
                st.markdown(f"**Type:** {paper_type.title()}")
            with col2:
                if paper_type == 'curriculum':
                    st.markdown(f"**Subject:** {paper.get('subject', 'N/A')}")
                    st.markdown(f"**Chapter:** {paper.get('chapter', 'N/A')}")
                    if paper.get('grade'):
                        st.markdown(f"**Grade:** {paper.get('grade', 'N/A')}")
                else:
                    st.markdown(f"**File:** {paper.get('document_name', 'N/A')}")
                    if paper_type == 'media':
                        st.markdown("**Source:** Audio/Video")
                    else:
                        st.markdown("**Source:** Document")
            with col3:
                st.markdown(f"**Total Marks:** {paper.get('total_marks', 'N/A')}")
                st.markdown(f"**Created:** {utils.format_date(paper['created_at'])}")
else:
    st.info("No papers generated yet. Start by generating your first paper!")

st.markdown("---")

# Recent Evaluations
st.markdown("### ✅ Recent Evaluations")
recent_evals = data.get('recent_evaluations', [])

if recent_evals:
    for evaluation in recent_evals:
        percentage = evaluation.get('percentage', 0)
        color = utils.get_grade_color(percentage)
        
        with st.expander(
            f"Paper #{evaluation.get('paper_id')} - Score: {evaluation.get('score')}/{evaluation.get('total_marks')} ({percentage:.1f}%) | {utils.format_date(evaluation['evaluated_at'])}"
        ):
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f"**Evaluation ID:** {evaluation['id']}")
            with col2:
                st.markdown(f"**Score:** {evaluation['score']}/{evaluation['total_marks']}")
            with col3:
                st.markdown(f"**Percentage:** {percentage:.1f}%")
            with col4:
                st.markdown(f"**Grade:** <span style='color: {color}; font-weight: bold; font-size: 20px;'>{evaluation.get('grade', 'N/A')}</span>", unsafe_allow_html=True)
            
            # Progress bar
            st.progress(percentage / 100)
else:
    st.info("No evaluations yet. Submit answers to your generated papers to see evaluation history!")

st.markdown("---")

# Action buttons
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📝 Generate Paper", use_container_width=True, type="primary"):
        st.switch_page("pages/1_📝_Generate_Paper.py")

with col2:
    if st.button("🎥 Audio/Video Paper", use_container_width=True, type="primary"):
        st.switch_page("pages/2_🎥_Audio_Video_Paper.py")

with col3:
    if st.button("📚 My Papers", use_container_width=True):
        st.switch_page("pages/4_📚_My_Papers.py")

# Refresh button
st.markdown("<br>", unsafe_allow_html=True)
if st.button("🔄 Refresh Dashboard", use_container_width=True):
    st.rerun()
