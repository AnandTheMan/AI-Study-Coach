"""
Paper Generation Page
"""
import streamlit as st
import sys
sys.path.append('..')
import config
import utils

st.set_page_config(
    page_title=f"{config.PAGE_TITLE} - Generate Paper",
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
    <h1 style="color: #0066cc;">📝 Generate Examination Paper</h1>
    <p style="color: #666; font-size: 18px;">Create custom examination papers using AI</p>
</div>
""", unsafe_allow_html=True)

# Tabs for different generation methods
tab1, tab2 = st.tabs(["📚 From Curriculum", "📄 From Document"])

# Tab 1: Generate from Curriculum
with tab1:
    st.markdown("### Generate Paper from Curriculum")
    st.markdown("Create an examination paper based on specific grade, subject, and chapter.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        grade = st.selectbox(
            "🎓 Grade Level",
            ["9", "10", "11", "12", "A-Level", "O-Level", "AS-Level"],
            help="Select the grade level"
        )
        
        subject = st.selectbox(
            "📖 Subject",
            ["Mathematics", "Physics", "Chemistry", "Biology", "English", "Computer Science", "History", "Geography"],
            help="Select the subject"
        )
    
    with col2:
        chapter = st.text_input(
            "📑 Chapter",
            placeholder="e.g., Algebra, Thermodynamics, etc.",
            help="Enter the chapter name"
        )
        
        topic = st.text_input(
            "📌 Topic (Optional)",
            placeholder="e.g., Quadratic Equations, Heat Transfer, etc.",
            help="Enter a specific topic within the chapter"
        )
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🚀 Generate Paper", use_container_width=True, type="primary"):
            if utils.validate_paper_form(grade, subject, chapter):
                with st.spinner("🤖 Generating your examination paper... This may take a moment."):
                    result = utils.make_api_request(
                        "/api/generate_paper",
                        method="POST",
                        data={
                            "grade": grade,
                            "subject": subject,
                            "chapter": chapter,
                            "topic": topic if topic else None
                        }
                    )
                    
                    if result["success"]:
                        paper_data = result["data"]
                        st.session_state.current_paper = paper_data
                        utils.display_success("Paper generated successfully!")
                        
                        # Display paper details
                        st.markdown("---")
                        st.markdown("## 📋 Generated Paper")
                        
                        # Header
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.markdown(f"**Grade:** {paper_data['grade']}")
                            st.markdown(f"**Subject:** {paper_data['subject']}")
                        with col2:
                            st.markdown(f"**Chapter:** {paper_data['chapter']}")
                            if paper_data.get('topic'):
                                st.markdown(f"**Topic:** {paper_data['topic']}")
                        with col3:
                            st.markdown(f"**Total Marks:** {paper_data['total_marks']}")
                            st.markdown(f"**Paper ID:** {paper_data['paper_id']}")
                        
                        st.markdown("---")
                        st.markdown(f"**Instructions:** {paper_data.get('instructions', 'Answer all questions.')}")
                        st.markdown("---")
                        
                        # Interactive Answer Form
                        st.markdown("### 📝 Solve This Paper")
                        st.info("💡 Enter your answers below and submit for instant evaluation!")
                        
                        with st.form("solve_paper_form"):
                            answers = []
                            for i, question in enumerate(paper_data['questions'], 1):
                                # Display question card
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
                                        key=f"mcq_answer_{question['question_number']}",
                                        help="Select your answer"
                                    )
                                else:
                                    answer = st.text_area(
                                        f"Your Answer for Question {question['question_number']}",
                                        key=f"answer_{question['question_number']}",
                                        height=100,
                                        placeholder="Type your answer here..."
                                    )
                                
                                answers.append({
                                    "question_number": question['question_number'],
                                    "answer": answer
                                })
                                
                                st.markdown("<br>", unsafe_allow_html=True)
                            
                            st.markdown("---")
                            submit_answers = st.form_submit_button("🎯 Submit Answers for Evaluation", use_container_width=True, type="primary")
                        
                        if submit_answers:
                            # Filter out empty answers
                            filled_answers = [ans for ans in answers if ans["answer"] and str(ans["answer"]).strip()]
                            
                            if not filled_answers:
                                utils.display_error("Please provide at least one answer before submitting")
                            else:
                                with st.spinner("🤖 Evaluating your answers... This may take a moment."):
                                    result = utils.make_api_request(
                                        "/api/evaluate_paper",
                                        method="POST",
                                        data={
                                            "paper_id": paper_data['paper_id'],
                                            "answers": filled_answers
                                        }
                                    )
                                    
                                    if result["success"]:
                                        eval_data = result["data"]
                                        utils.display_success("🎉 Evaluation completed successfully!")
                                        
                                        # Display results
                                        st.markdown("---")
                                        st.markdown("## 🎯 Your Results")
                                        
                                        # Overall score with large display
                                        percentage = eval_data.get('percentage', 0)
                                        grade = eval_data.get('grade', 'N/A')
                                        
                                        col1, col2, col3, col4 = st.columns(4)
                                        with col1:
                                            st.metric("Your Score", f"{eval_data.get('score', 0):.1f}")
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
                                        
                                        # Progress bar
                                        st.progress(percentage / 100)
                                        
                                        # Detailed feedback
                                        st.markdown("---")
                                        st.markdown("### 📊 Question-by-Question Feedback")
                                        
                                        feedback_by_question = eval_data.get('feedback_by_question', [])
                                        
                                        if feedback_by_question:
                                            for fb in feedback_by_question:
                                                with st.expander(f"Question {fb['question_number']} - {fb['marks_obtained']}/{fb['marks_available']} marks", expanded=False):
                                                    col1, col2 = st.columns(2)
                                                    with col1:
                                                        st.markdown("**Your Answer:**")
                                                        st.info(fb.get('student_answer', 'No answer provided'))
                                                    with col2:
                                                        if fb.get('correct_answer'):
                                                            st.markdown("**Correct Answer:**")
                                                            st.success(fb['correct_answer'])
                                                    
                                                    st.markdown(f"**Feedback:** {fb.get('feedback', 'No feedback available')}")
                                                    
                                                    # Progress bar for marks
                                                    progress = fb['marks_obtained'] / fb['marks_available'] if fb['marks_available'] > 0 else 0
                                                    st.progress(progress)
                                        
                                        # Overall feedback
                                        if eval_data.get('overall_feedback'):
                                            st.markdown("---")
                                            st.markdown("### 💡 Overall Feedback")
                                            st.info(eval_data['overall_feedback'])
                                        
                                        # Action buttons after evaluation
                                        st.markdown("---")
                                        col1, col2, col3 = st.columns(3)
                                        with col1:
                                            if st.button("📝 Generate New Paper", key="new_paper_after_eval", use_container_width=True):
                                                st.session_state.current_paper = None
                                                st.rerun()
                                        with col2:
                                            if st.button("📊 View Dashboard", key="dash_after_eval", use_container_width=True):
                                                st.switch_page("pages/3_📊_Dashboard.py")
                                        with col3:
                                            if st.button("🏠 Back to Home", key="home_after_eval", use_container_width=True):
                                                st.switch_page("app.py")
                                    else:
                                        utils.display_error(result["error"])
                        
                        # Alternative navigation buttons (shown before submission)
                        if not submit_answers:
                            st.markdown("---")
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.button("🔄 Generate Another Paper", key="gen_another", use_container_width=True):
                                    st.session_state.current_paper = None
                                    st.rerun()
                            with col2:
                                if st.button("🏠 Back to Home", key="home_before", use_container_width=True):
                                    st.switch_page("app.py")
                    else:
                        utils.display_error(result["error"])

# Tab 2: Generate from Document
with tab2:
    st.markdown("### Generate Paper from Document")
    st.markdown("Upload a document (PDF, DOCX, or TXT) and generate questions based on its content.")
    
    uploaded_file = st.file_uploader(
        "📎 Upload Document",
        type=["pdf", "docx", "txt"],
        help="Upload a PDF, DOCX, or TXT file"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        num_mcqs = st.number_input(
            "🔢 Number of MCQs",
            min_value=0,
            max_value=50,
            value=10,
            step=1,
            help="Number of multiple choice questions"
        )
        
        marks_per_mcq = st.number_input(
            "💯 Marks per MCQ",
            min_value=1,
            max_value=10,
            value=2,
            step=1
        )
    
    with col2:
        num_short = st.number_input(
            "📝 Number of Short Questions",
            min_value=0,
            max_value=30,
            value=5,
            step=1,
            help="Number of short answer questions"
        )
        
        marks_per_short = st.number_input(
            "💯 Marks per Short Question",
            min_value=1,
            max_value=20,
            value=5,
            step=1
        )
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("📄 Generate from Document", use_container_width=True, type="primary"):
            if not uploaded_file:
                utils.display_error("Please upload a document first")
            elif num_mcqs == 0 and num_short == 0:
                utils.display_error("Please specify at least one type of question")
            else:
                with st.spinner("🤖 Analyzing document and generating questions... This may take a moment."):
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    data = {
                        "num_mcqs": num_mcqs,
                        "num_short_questions": num_short,
                        "marks_per_mcq": marks_per_mcq,
                        "marks_per_short": marks_per_short
                    }
                    
                    result = utils.make_api_request(
                        "/api/generate_paper_from_document",
                        method="POST",
                        data=data,
                        files=files
                    )
                    
                    if result["success"]:
                        paper_data = result["data"]
                        st.session_state.current_paper = paper_data
                        utils.display_success("Paper generated successfully from document!")
                        
                        st.markdown("---")
                        st.markdown("## 📋 Generated Paper from Document")
                        
                        # Header
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(f"**Document:** {paper_data.get('document_name', 'N/A')}")
                            st.markdown(f"**Total Questions:** {len(paper_data['questions'])}")
                        with col2:
                            st.markdown(f"**Total Marks:** {paper_data['total_marks']}")
                            st.markdown(f"**Paper ID:** {paper_data['paper_id']}")
                        
                        st.markdown("---")
                        
                        # Interactive Answer Form
                        st.markdown("### 📝 Solve This Paper")
                        st.info("💡 Enter your answers below and submit for instant evaluation!")
                        
                        with st.form("solve_doc_paper_form"):
                            answers = []
                            for i, question in enumerate(paper_data['questions'], 1):
                                # Display question card
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
                                        key=f"doc_mcq_answer_{question['question_number']}",
                                        help="Select your answer"
                                    )
                                else:
                                    answer = st.text_area(
                                        f"Your Answer for Question {question['question_number']}",
                                        key=f"doc_answer_{question['question_number']}",
                                        height=100,
                                        placeholder="Type your answer here..."
                                    )
                                
                                answers.append({
                                    "question_number": question['question_number'],
                                    "answer": answer
                                })
                                
                                st.markdown("<br>", unsafe_allow_html=True)
                            
                            st.markdown("---")
                            submit_doc_answers = st.form_submit_button("🎯 Submit Answers for Evaluation", use_container_width=True, type="primary")
                        
                        if submit_doc_answers:
                            # Filter out empty answers
                            filled_answers = [ans for ans in answers if ans["answer"] and str(ans["answer"]).strip()]
                            
                            if not filled_answers:
                                utils.display_error("Please provide at least one answer before submitting")
                            else:
                                with st.spinner("🤖 Evaluating your answers... This may take a moment."):
                                    result = utils.make_api_request(
                                        "/api/evaluate_paper",
                                        method="POST",
                                        data={
                                            "paper_id": paper_data['paper_id'],
                                            "answers": filled_answers
                                        }
                                    )
                                    
                                    if result["success"]:
                                        eval_data = result["data"]
                                        utils.display_success("🎉 Evaluation completed successfully!")
                                        
                                        # Display results
                                        st.markdown("---")
                                        st.markdown("## 🎯 Your Results")
                                        
                                        # Overall score with large display
                                        percentage = eval_data.get('percentage', 0)
                                        grade = eval_data.get('grade', 'N/A')
                                        
                                        col1, col2, col3, col4 = st.columns(4)
                                        with col1:
                                            st.metric("Your Score", f"{eval_data.get('score', 0):.1f}")
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
                                        
                                        # Progress bar
                                        st.progress(percentage / 100)
                                        
                                        # Detailed feedback
                                        st.markdown("---")
                                        st.markdown("### 📊 Question-by-Question Feedback")
                                        
                                        feedback_by_question = eval_data.get('feedback_by_question', [])
                                        
                                        if feedback_by_question:
                                            for fb in feedback_by_question:
                                                with st.expander(f"Question {fb['question_number']} - {fb['marks_obtained']}/{fb['marks_available']} marks", expanded=False):
                                                    col1, col2 = st.columns(2)
                                                    with col1:
                                                        st.markdown("**Your Answer:**")
                                                        st.info(fb.get('student_answer', 'No answer provided'))
                                                    with col2:
                                                        if fb.get('correct_answer'):
                                                            st.markdown("**Correct Answer:**")
                                                            st.success(fb['correct_answer'])
                                                    
                                                    st.markdown(f"**Feedback:** {fb.get('feedback', 'No feedback available')}")
                                                    
                                                    # Progress bar for marks
                                                    progress = fb['marks_obtained'] / fb['marks_available'] if fb['marks_available'] > 0 else 0
                                                    st.progress(progress)
                                        
                                        # Overall feedback
                                        if eval_data.get('overall_feedback'):
                                            st.markdown("---")
                                            st.markdown("### 💡 Overall Feedback")
                                            st.info(eval_data['overall_feedback'])
                                        
                                        # Action buttons
                                        st.markdown("---")
                                        col1, col2, col3 = st.columns(3)
                                        with col1:
                                            if st.button("📝 Generate New Paper", key="new_doc_paper", use_container_width=True):
                                                st.session_state.current_paper = None
                                                st.rerun()
                                        with col2:
                                            if st.button("📊 View Dashboard", key="dash_doc", use_container_width=True):
                                                st.switch_page("pages/3_📊_Dashboard.py")
                                        with col3:
                                            if st.button("🏠 Back to Home", key="home_doc", use_container_width=True):
                                                st.switch_page("app.py")
                                    else:
                                        utils.display_error(result["error"])
                        
                        # Alternative navigation (shown before submission)
                        if not submit_doc_answers:
                            st.markdown("---")
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.button("🔄 Generate Another Paper", key="gen_another_doc", use_container_width=True):
                                    st.session_state.current_paper = None
                                    st.rerun()
                            with col2:
                                if st.button("🏠 Back to Home", key="home_before_doc", use_container_width=True):
                                    st.switch_page("app.py")
                    else:
                        utils.display_error(result["error"])

# Show current paper if exists in session (when navigating back)
if st.session_state.current_paper and not st.session_state.get("_just_generated"):
    paper_data = st.session_state.current_paper
    st.markdown("---")
    st.markdown("## 📋 Your Current Paper")
    st.info("💡 You have a paper ready. Scroll up to answer the questions and submit for evaluation.")
    
    # Quick stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"**Paper ID:** {paper_data.get('paper_id', 'N/A')}")
    with col2:
        st.markdown(f"**Total Questions:** {len(paper_data.get('questions', []))}")
    with col3:
        st.markdown(f"**Total Marks:** {paper_data.get('total_marks', 0)}")
