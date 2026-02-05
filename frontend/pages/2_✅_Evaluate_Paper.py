"""
Paper Evaluation Page
"""
import streamlit as st
import sys
sys.path.append('..')
import config
import utils

st.set_page_config(
    page_title=f"{config.PAGE_TITLE} - Evaluate Paper",
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
    <h1 style="color: #0066cc;">✅ Evaluate Examination Paper</h1>
    <p style="color: #666; font-size: 18px;">Submit your answers for AI-powered evaluation</p>
</div>
""", unsafe_allow_html=True)

# Check if there's a current paper
if not st.session_state.current_paper:
    st.info("ℹ️ No paper selected for evaluation. Please generate a paper first.")
    if st.button("📝 Generate Paper", use_container_width=True):
        st.switch_page("pages/1_📝_Generate_Paper.py")
    st.stop()

paper = st.session_state.current_paper

# Display paper information
st.markdown("### 📋 Paper Information")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"**Paper ID:** {paper['paper_id']}")
    st.markdown(f"**Subject:** {paper.get('subject', 'N/A')}")

with col2:
    st.markdown(f"**Chapter:** {paper.get('chapter', 'N/A')}")
    st.markdown(f"**Total Marks:** {paper['total_marks']}")

with col3:
    st.markdown(f"**Total Questions:** {len(paper['questions'])}")
    if paper.get('grade'):
        st.markdown(f"**Grade:** {paper['grade']}")

st.markdown("---")

# Answer form
st.markdown("### 📝 Submit Your Answers")
st.markdown("Enter your answers for each question below. You can leave questions blank if needed.")

answers = []

with st.form("evaluation_form"):
    for i, question in enumerate(paper['questions'], 1):
        st.markdown(f"""
        <div style="
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid #0066cc;
            margin-bottom: 20px;
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
        answer = st.text_area(
            f"Your Answer for Question {question['question_number']}",
            key=f"answer_{question['question_number']}",
            height=100,
            placeholder="Enter your answer here..."
        )
        
        answers.append({
            "question_number": question['question_number'],
            "answer": answer
        })
        
        st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        submit_button = st.form_submit_button("🎯 Submit for Evaluation", use_container_width=True, type="primary")

if submit_button:
    # Filter out empty answers
    filled_answers = [ans for ans in answers if ans["answer"].strip()]
    
    if not filled_answers:
        utils.display_error("Please provide at least one answer before submitting")
    else:
        with st.spinner("🤖 Evaluating your answers... This may take a moment."):
            result = utils.make_api_request(
                "/api/evaluate_paper",
                method="POST",
                data={
                    "paper_id": paper['paper_id'],
                    "answers": filled_answers
                }
            )
            
            if result["success"]:
                eval_data = result["data"]
                utils.display_success("Evaluation completed successfully!")
                
                # Display results
                st.markdown("---")
                st.markdown("## 🎯 Evaluation Results")
                
                # Overall score
                percentage = eval_data.get('percentage', 0)
                grade = eval_data.get('grade', 'N/A')
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Score", f"{eval_data.get('score', 0):.1f}")
                with col2:
                    st.metric("Total Marks", eval_data.get('total_marks', 0))
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
                
                # Feedback by question
                st.markdown("---")
                st.markdown("### 📊 Detailed Feedback")
                
                feedback_by_question = eval_data.get('feedback_by_question', [])
                
                if feedback_by_question:
                    for fb in feedback_by_question:
                        with st.expander(f"Question {fb['question_number']} - {fb['marks_obtained']}/{fb['marks_available']} marks", expanded=True):
                            st.markdown(f"**Your Answer:** {fb.get('student_answer', 'No answer provided')}")
                            st.markdown(f"**Feedback:** {fb.get('feedback', 'No feedback available')}")
                            
                            # Progress bar for marks
                            progress = fb['marks_obtained'] / fb['marks_available'] if fb['marks_available'] > 0 else 0
                            st.progress(progress)
                else:
                    st.info("Detailed feedback not available")
                
                # Overall feedback
                if eval_data.get('overall_feedback'):
                    st.markdown("---")
                    st.markdown("### 💡 Overall Feedback")
                    st.info(eval_data['overall_feedback'])
                
                # Action buttons
                st.markdown("---")
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("📝 Generate New Paper", use_container_width=True):
                        st.session_state.current_paper = None
                        st.switch_page("pages/1_📝_Generate_Paper.py")
                with col2:
                    if st.button("📊 View Dashboard", use_container_width=True):
                        st.switch_page("pages/3_📊_Dashboard.py")
                with col3:
                    if st.button("🏠 Back to Home", use_container_width=True):
                        st.switch_page("app.py")
            else:
                utils.display_error(result["error"])
