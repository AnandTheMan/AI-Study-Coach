"""
My Papers Page - View and attempt saved papers
"""
import streamlit as st
import json
import sys
sys.path.append('..')
import config
import utils

st.set_page_config(
    page_title=f"{config.PAGE_TITLE} - My Papers",
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
    <h1 style="color: #0066cc;">📚 My Papers</h1>
    <p style="color: #666; font-size: 18px;">View and attempt your saved papers</p>
</div>
""", unsafe_allow_html=True)

# Fetch dashboard to get papers
with st.spinner("Loading your papers..."):
    result = utils.make_api_request("/api/dashboard", method="GET")
    
    if not result["success"]:
        utils.display_error(result["error"])
        st.stop()
    
    data = result["data"]
    papers = data.get("recent_papers", [])

if not papers:
    st.info("📝 No papers generated yet. Generate your first paper to get started!")
    if st.button("Generate New Paper", use_container_width=True, type="primary"):
        st.switch_page("pages/1_📝_Generate_Paper.py")
    st.stop()

# Filter and search
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    search = st.text_input("🔍 Search papers", placeholder="Search by subject, chapter, or grade...")
with col2:
    filter_subject = st.selectbox("Filter by Subject", ["All"] + list(set([p.get('subject', 'N/A') for p in papers if p.get('subject')])))
with col3:
    filter_grade = st.selectbox("Filter by Grade", ["All"] + list(set([p.get('grade', 'N/A') for p in papers if p.get('grade')])))

# Apply filters
filtered_papers = papers
if search:
    filtered_papers = [p for p in filtered_papers if 
                      search.lower() in str(p.get('subject', '')).lower() or
                      search.lower() in str(p.get('chapter', '')).lower() or
                      search.lower() in str(p.get('grade', '')).lower()]
if filter_subject != "All":
    filtered_papers = [p for p in filtered_papers if p.get('subject') == filter_subject]
if filter_grade != "All":
    filtered_papers = [p for p in filtered_papers if p.get('grade') == filter_grade]

st.markdown(f"### 📋 {len(filtered_papers)} Paper(s) Found")
st.markdown("---")

# Display papers as cards
for i, paper in enumerate(filtered_papers):
    with st.container():
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 20px;
                border-radius: 15px;
                color: white;
                margin-bottom: 20px;
            ">
                <h3 style="margin: 0 0 10px 0;">{paper.get('subject', 'N/A')} - {paper.get('chapter', 'N/A')}</h3>
                <p style="margin: 5px 0; opacity: 0.9;"><strong>Grade:</strong> {paper.get('grade', 'N/A')} | <strong>Type:</strong> {paper.get('type', 'N/A')}</p>
                <p style="margin: 5px 0; opacity: 0.9;"><strong>Total Marks:</strong> {paper.get('total_marks', 'N/A')}</p>
                <p style="margin: 5px 0; opacity: 0.9; font-size: 14px;">Created: {utils.format_date(paper['created_at'])}</p>
                {f"<p style='margin: 5px 0; opacity: 0.9; font-size: 14px;'>Document: {paper.get('document_name', '')}</p>" if paper.get('document_name') else ""}
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button(f"📝 Attempt Paper", key=f"attempt_{paper['id']}", use_container_width=True, type="primary"):
                # Fetch full paper details
                with st.spinner("Loading paper..."):
                    # Get paper from API by reconstructing it
                    st.session_state.selected_paper_id = paper['id']
                    st.session_state.view_paper = True
                    st.rerun()

# If a paper is selected, show it
if st.session_state.get('view_paper') and st.session_state.get('selected_paper_id'):
    paper_id = st.session_state.selected_paper_id
    
    # Fetch full paper with questions
    with st.spinner("Loading paper..."):
        result = utils.make_api_request(f"/api/papers/{paper_id}", method="GET")
        
        if not result["success"]:
            utils.display_error(result["error"])
            st.session_state.view_paper = False
            st.session_state.selected_paper_id = None
        else:
            paper_data = result["data"]
            
            st.markdown("---")
            st.markdown("## 📝 Solve This Paper")
            
            # Display paper info
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"**Subject:** {paper_data.get('subject', 'N/A')}")
                st.markdown(f"**Chapter:** {paper_data.get('chapter', 'N/A')}")
            with col2:
                st.markdown(f"**Grade:** {paper_data.get('grade', 'N/A')}")
                st.markdown(f"**Total Marks:** {paper_data.get('total_marks', 'N/A')}")
            with col3:
                st.markdown(f"**Paper ID:** {paper_data['paper_id']}")
                if paper_data.get('document_name'):
                    st.markdown(f"**Document:** {paper_data['document_name']}")
            
            st.markdown("---")
            st.info("💡 Enter your answers below and submit for instant AI evaluation!")
            
            # Answer form
            with st.form("solve_saved_paper"):
                answers = []
                for question in paper_data['questions']:
                    st.markdown(f"""
                    <div style="
                        background-color: #f8f9fa;
                        padding: 20px;
                        border-radius: 10px;
                        border-left: 4px solid #0066cc;
                        margin-bottom: 15px;
                    ">
                        <h4 style="color: #0066cc; margin-top: 0;">Question {question['question_number']}</h4>
                        <p style="font-size: 16px; color: #333;"><strong>Type:</strong> {question['question_type']} | <strong>Marks:</strong> {question['marks']}</p>
                        <p style="font-size: 18px; margin-top: 15px; color: #000;">{question['question_text']}</p>
                    """, unsafe_allow_html=True)
                    
                    if question.get('options'):
                        st.markdown("<p style='font-size: 16px; margin-top: 10px;'><strong>Options:</strong></p>", unsafe_allow_html=True)
                        for j, option in enumerate(question['options'], 1):
                            st.markdown(f"<p style='margin-left: 20px; font-size: 15px;'>{chr(64+j)}. {option}</p>", unsafe_allow_html=True)
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Answer input
                    if question['question_type'].upper() == 'MCQ' and question.get('options'):
                        answer = st.selectbox(
                            f"Your Answer for Question {question['question_number']}",
                            [""] + [f"{chr(64+j)}. {opt}" for j, opt in enumerate(question['options'], 1)],
                            key=f"saved_mcq_{question['question_number']}",
                            help="Select your answer"
                        )
                    else:
                        answer = st.text_area(
                            f"Your Answer for Question {question['question_number']}",
                            key=f"saved_answer_{question['question_number']}",
                            height=100,
                            placeholder="Type your answer here..."
                        )
                    
                    answers.append({
                        "question_number": question['question_number'],
                        "answer": answer
                    })
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                
                st.markdown("---")
                col1, col2 = st.columns(2)
                with col1:
                    submit_btn = st.form_submit_button("🎯 Submit for Evaluation", use_container_width=True, type="primary")
                with col2:
                    back_btn = st.form_submit_button("🔙 Back to Papers", use_container_width=True)
            
            if back_btn:
                st.session_state.view_paper = False
                st.session_state.selected_paper_id = None
                st.rerun()
            
            if submit_btn:
                # Filter out empty answers and process MCQ answers
                filled_answers = []
                for ans in answers:
                    if ans["answer"] and str(ans["answer"]).strip():
                        answer_text = str(ans["answer"]).strip()
                        # Extract just the letter for MCQ answers (e.g., "B. Option" -> "B")
                        if answer_text and answer_text[0] in ['A', 'B', 'C', 'D', 'E', 'F']:
                            # Get just the first letter if it's an MCQ
                            answer_text = answer_text[0]
                        filled_answers.append({
                            "question_number": ans["question_number"],
                            "answer": answer_text
                        })
                
                if not filled_answers:
                    utils.display_error("Please provide at least one answer before submitting")
                else:
                    with st.spinner("🤖 Evaluating your answers..."):
                        eval_result = utils.make_api_request(
                            "/api/evaluate_paper",
                            method="POST",
                            data={
                                "paper_id": paper_data['paper_id'],
                                "answers": filled_answers
                            }
                        )
                        
                        if eval_result["success"]:
                            eval_data = eval_result["data"]
                            utils.display_success("🎉 Evaluation completed!")
                            
                            st.markdown("---")
                            st.markdown("## 🎯 Your Results")
                            
                            # Score display
                            percentage = eval_data.get('percentage', 0)
                            grade = eval_data.get('grade_letter', 'N/A')
                            
                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                st.metric("Score", f"{eval_data.get('total_score', 0):.1f}")
                            with col2:
                                st.metric("Total", eval_data.get('total_marks', 0))
                            with col3:
                                st.metric("Percentage", f"{percentage:.1f}%")
                            with col4:
                                color = utils.get_grade_color(percentage)
                                st.markdown(f"""
                                <div style="text-align: center; padding: 10px;">
                                    <p style="margin: 0; color: #666; font-size: 14px;">Grade</p>
                                    <p style="margin: 5px 0 0 0; color: {color}; font-size: 32px; font-weight: bold;">{grade}</p>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            st.progress(percentage / 100)
                            
                            # Question feedback
                            st.markdown("---")
                            st.markdown("### 📊 Detailed Feedback")
                            
                            for fb in eval_data.get('feedback', []):
                                with st.expander(f"Question {fb['question_number']} - {fb['marks_obtained']}/{fb['marks_total']} marks"):
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        st.markdown(f"**Your Answer:**")
                                        st.info(fb.get('student_answer', 'No answer'))
                                    with col2:
                                        if fb.get('correct_answer'):
                                            st.markdown(f"**Correct Answer:**")
                                            st.success(fb['correct_answer'])
                                    
                                    st.markdown(f"**Feedback:** {fb.get('feedback', 'No feedback')}")
                                    st.progress(fb['marks_obtained'] / fb['marks_total'] if fb['marks_total'] > 0 else 0)
                            
                            # Overall feedback
                            if eval_data.get('overall_feedback'):
                                st.markdown("---")
                                st.markdown("### 💡 Overall Feedback")
                                st.info(eval_data['overall_feedback'])
                            
                            st.markdown("---")
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                if st.button("📝 Try Another Paper", use_container_width=True):
                                    st.session_state.view_paper = False
                                    st.session_state.selected_paper_id = None
                                    st.rerun()
                            with col2:
                                if st.button("📊 View Dashboard", use_container_width=True):
                                    st.switch_page("pages/3_📊_Dashboard.py")
                            with col3:
                                if st.button("🏠 Home", use_container_width=True):
                                    st.switch_page("app.py")
                        else:
                            utils.display_error(eval_result["error"])

# Action buttons at bottom
st.markdown("---")
col1, col2 = st.columns(2)
with col1:
    if st.button("📝 Generate New Paper", use_container_width=True, type="primary"):
        st.switch_page("pages/1_📝_Generate_Paper.py")
with col2:
    if st.button("🏠 Back to Home", use_container_width=True):
        st.switch_page("app.py")
