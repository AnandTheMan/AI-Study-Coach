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

# Initialize evaluation results in session state
if 'evaluation_results' not in st.session_state:
    st.session_state.evaluation_results = None

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
tab1, tab2, tab3 = st.tabs(["📚 From Curriculum", "📄 From Document", "🎥 From Audio/Video"])

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
    st.markdown("### ⏱️ Time Limit")
    
    col1, col2 = st.columns(2)
    
    with col1:
        time_hours = st.number_input(
            "⏰ Hours",
            min_value=0,
            max_value=5,
            value=1,
            step=1,
            help="Number of hours allowed to solve the paper"
        )
    
    with col2:
        time_minutes = st.number_input(
            "⏱️ Minutes",
            min_value=0,
            max_value=59,
            value=30,
            step=5,
            help="Number of minutes allowed to solve the paper"
        )
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🚀 Generate Paper", use_container_width=True, type="primary"):
            if utils.validate_paper_form(grade, subject, chapter):
                # Clear previous evaluation results
                st.session_state.evaluation_results = None
                
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
                        st.session_state.paper_source = "curriculum"
                        # Store time limit in seconds
                        st.session_state.paper_time_limit = (time_hours * 3600) + (time_minutes * 60)
                        st.session_state.paper_start_time = None  # Will be set when form starts
                        utils.display_success("Paper generated successfully!")
                        st.rerun()
                    else:
                        utils.display_error(result["error"])

# Display current paper if exists (outside button clicks)
if st.session_state.current_paper and st.session_state.get('paper_source') == 'curriculum':
    paper_data = st.session_state.current_paper
    
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
    
    # Show evaluation results if they exist
    if st.session_state.evaluation_results:
        eval_data = st.session_state.evaluation_results
        
        # Display results
        st.markdown("## 🎯 Your Results")
        
        # Overall score with large display
        percentage = eval_data.get('percentage', 0)
        grade_letter = eval_data.get('grade_letter', eval_data.get('grade', 'N/A'))
        total_score = eval_data.get('total_score', eval_data.get('score', 0))
        total_marks = eval_data.get('total_marks', 0)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Your Score", f"{total_score:.1f}")
        with col2:
            st.metric("Total Marks", total_marks)
        with col3:
            st.metric("Percentage", f"{percentage:.1f}%")
        with col4:
            color = utils.get_grade_color(percentage)
            st.markdown(f"""
            <div style="text-align: center; padding: 10px;">
                <p style="margin: 0; color: #666; font-size: 14px;">Grade</p>
                <p style="margin: 5px 0 0 0; color: {color}; font-size: 32px; font-weight: bold;">{grade_letter}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Progress bar
        st.progress(percentage / 100)
        
        # Comprehensive Feedback Section
        st.markdown("---")
        st.markdown("### 📋 Comprehensive Analysis")
        
        # Strengths
        if eval_data.get('strengths'):
            strengths = eval_data.get('strengths', [])
            if isinstance(strengths, str):
                strengths = [strengths]
            
            with st.expander("💪 Your Strengths", expanded=True):
                if isinstance(strengths, list):
                    for strength in strengths:
                        st.success(f"✓ {strength}")
                else:
                    st.success(f"✓ {strengths}")
        
        # Weaknesses
        if eval_data.get('weaknesses'):
            weaknesses = eval_data.get('weaknesses', [])
            if isinstance(weaknesses, str):
                weaknesses = [weaknesses]
            
            with st.expander("⚠️ Areas for Improvement", expanded=True):
                if isinstance(weaknesses, list):
                    for weakness in weaknesses:
                        st.warning(f"• {weakness}")
                else:
                    st.warning(f"• {weaknesses}")
        
        # Improvement Areas
        if eval_data.get('improvement_areas'):
            improvements = eval_data.get('improvement_areas', [])
            if isinstance(improvements, str):
                improvements = [improvements]
            
            with st.expander("🎯 Recommended Actions", expanded=True):
                if isinstance(improvements, list):
                    for i, improvement in enumerate(improvements, 1):
                        st.info(f"{i}. {improvement}")
                else:
                    st.info(f"1. {improvements}")
        
        # Detailed feedback
        st.markdown("---")
        st.markdown("### 📊 Question-by-Question Feedback")
        
        feedback_list = eval_data.get('feedback', [])
        
        if feedback_list:
            for fb in feedback_list:
                with st.expander(f"Question {fb['question_number']} - {fb['marks_obtained']}/{fb['marks_total']} marks", expanded=False):
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
                    progress = fb['marks_obtained'] / fb['marks_total'] if fb['marks_total'] > 0 else 0
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
                st.session_state.evaluation_results = None
                st.session_state.paper_source = None
                st.rerun()
        with col2:
            if st.button("📊 View Dashboard", key="dash_after_eval", use_container_width=True):
                st.switch_page("pages/3_📊_Dashboard.py")
        with col3:
            if st.button("🏠 Back to Home", key="home_after_eval", use_container_width=True):
                st.switch_page("app.py")
    else:
        # Interactive Answer Form (only show if no evaluation results yet)
        st.markdown("### 📝 Solve This Paper")
        st.info("💡 Enter your answers below and submit for instant evaluation!")
        
        # Initialize timer on first visit to this section
        if st.session_state.paper_start_time is None:
            st.session_state.paper_start_time = __import__('time').time()
        
        # Timer display
        time_limit = st.session_state.get('paper_time_limit', 3600)
        elapsed_time = int(__import__('time').time() - st.session_state.paper_start_time)
        remaining_time = max(0, time_limit - elapsed_time)
        remaining_minutes = remaining_time // 60
        remaining_seconds = remaining_time % 60
        
        # Create timer display
        timer_col1, timer_col2, timer_col3 = st.columns([2, 2, 1])
        with timer_col1:
            st.markdown(f"### ⏱️ Time Remaining: **{remaining_minutes:02d}:{remaining_seconds:02d}**")
        with timer_col2:
            progress = min(elapsed_time / time_limit, 1.0)
            st.progress(progress)
        
        # Auto-submit if time is up
        auto_submit_curr = False
        if remaining_time <= 0:
            st.error("⏰ **Time's up!** Your paper is being automatically submitted for evaluation...")
            auto_submit_curr = True
        
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
            submit_curr_answers = st.form_submit_button("🎯 Submit Answers for Evaluation", use_container_width=True, type="primary")
        
        # Handle auto-submit or manual submit
        if auto_submit_curr or submit_curr_answers:
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
                        st.session_state.evaluation_results = result["data"]
                        st.rerun()
                    else:
                        utils.display_error(result["error"])
        
        # Alternative navigation buttons (shown before submission)
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Generate Another Paper", key="gen_another", use_container_width=True):
                st.session_state.current_paper = None
                st.session_state.evaluation_results = None
                st.session_state.paper_source = None
                st.rerun()
        with col2:
            if st.button("🏠 Back to Home", key="home_before", use_container_width=True):
                st.switch_page("app.py")

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
    st.markdown("### ⏱️ Time Limit")
    
    col1, col2 = st.columns(2)
    
    with col1:
        time_hours_doc = st.number_input(
            "⏰ Hours",
            min_value=0,
            max_value=5,
            value=1,
            step=1,
            help="Number of hours allowed to solve the paper",
            key="doc_hours"
        )
    
    with col2:
        time_minutes_doc = st.number_input(
            "⏱️ Minutes",
            min_value=0,
            max_value=59,
            value=30,
            step=5,
            help="Number of minutes allowed to solve the paper",
            key="doc_minutes"
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
                # Clear previous evaluation results
                st.session_state.evaluation_results = None
                
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
                        st.session_state.paper_source = "document"
                        utils.display_success("Paper generated successfully from document!")
                        st.rerun()
                    else:
                        utils.display_error(result["error"])

# Display document paper if exists (outside button clicks)
if st.session_state.current_paper and st.session_state.get('paper_source') == 'document':
    paper_data = st.session_state.current_paper
    
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
    
    # Show evaluation results if they exist
    if st.session_state.evaluation_results:
        eval_data = st.session_state.evaluation_results
        
        # Display results
        st.markdown("## 🎯 Your Results")
        
        # Overall score with large display
        percentage = eval_data.get('percentage', 0)
        grade_letter = eval_data.get('grade_letter', eval_data.get('grade', 'N/A'))
        total_score = eval_data.get('total_score', eval_data.get('score', 0))
        total_marks = eval_data.get('total_marks', 0)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Your Score", f"{total_score:.1f}")
        with col2:
            st.metric("Total Marks", total_marks)
        with col3:
            st.metric("Percentage", f"{percentage:.1f}%")
        with col4:
            color = utils.get_grade_color(percentage)
            st.markdown(f"""
            <div style="text-align: center; padding: 10px;">
                <p style="margin: 0; color: #666; font-size: 14px;">Grade</p>
                <p style="margin: 5px 0 0 0; color: {color}; font-size: 32px; font-weight: bold;">{grade_letter}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Progress bar
        st.progress(percentage / 100)
        
        # Comprehensive Feedback Section
        st.markdown("---")
        st.markdown("### 📋 Comprehensive Analysis")
        
        # Strengths
        if eval_data.get('strengths'):
            strengths = eval_data.get('strengths', [])
            if isinstance(strengths, str):
                strengths = [strengths]
            
            with st.expander("💪 Your Strengths", expanded=True):
                if isinstance(strengths, list):
                    for strength in strengths:
                        st.success(f"✓ {strength}")
                else:
                    st.success(f"✓ {strengths}")
        
        # Weaknesses
        if eval_data.get('weaknesses'):
            weaknesses = eval_data.get('weaknesses', [])
            if isinstance(weaknesses, str):
                weaknesses = [weaknesses]
            
            with st.expander("⚠️ Areas for Improvement", expanded=True):
                if isinstance(weaknesses, list):
                    for weakness in weaknesses:
                        st.warning(f"• {weakness}")
                else:
                    st.warning(f"• {weaknesses}")
        
        # Improvement Areas
        if eval_data.get('improvement_areas'):
            improvements = eval_data.get('improvement_areas', [])
            if isinstance(improvements, str):
                improvements = [improvements]
            
            with st.expander("🎯 Recommended Actions", expanded=True):
                if isinstance(improvements, list):
                    for i, improvement in enumerate(improvements, 1):
                        st.info(f"{i}. {improvement}")
                else:
                    st.info(f"1. {improvements}")
        
        # Detailed feedback
        st.markdown("---")
        st.markdown("### 📊 Question-by-Question Feedback")
        
        feedback_list = eval_data.get('feedback', [])
        
        if feedback_list:
            for fb in feedback_list:
                with st.expander(f"Question {fb['question_number']} - {fb['marks_obtained']}/{fb['marks_total']} marks", expanded=False):
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
                    progress = fb['marks_obtained'] / fb['marks_total'] if fb['marks_total'] > 0 else 0
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
                st.session_state.evaluation_results = None
                st.session_state.paper_source = None
                st.rerun()
        with col2:
            if st.button("📊 View Dashboard", key="dash_doc", use_container_width=True):
                st.switch_page("pages/3_📊_Dashboard.py")
        with col3:
            if st.button("🏠 Back to Home", key="home_doc", use_container_width=True):
                st.switch_page("app.py")
    else:
        # Interactive Answer Form (only show if no evaluation results yet)
        st.markdown("### 📝 Solve This Paper")
        st.info("💡 Enter your answers below and submit for instant evaluation!")
        
        # Store time limit in session state
        if 'doc_paper_time_limit' not in st.session_state:
            st.session_state.doc_paper_time_limit = (time_hours_doc * 3600) + (time_minutes_doc * 60)
        
        if 'doc_paper_start_time' not in st.session_state:
            st.session_state.doc_paper_start_time = __import__('time').time()
        
        # Display timer
        time_limit = st.session_state.doc_paper_time_limit
        start_time = st.session_state.doc_paper_start_time
        elapsed_time = int(__import__('time').time() - start_time)
        remaining_time = max(0, time_limit - elapsed_time)
        
        remaining_minutes = remaining_time // 60
        remaining_seconds = remaining_time % 60
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            if remaining_time > 300:  # More than 5 minutes
                st.markdown(f"### ⏱️ Time Remaining: **{remaining_minutes:02d}:{remaining_seconds:02d}**")
            elif remaining_time > 0:  # Less than 5 minutes
                st.markdown(f"### ⏱️ Time Remaining: **{remaining_minutes:02d}:{remaining_seconds:02d}**")
                st.warning(f"⚠️ Only {remaining_minutes} minute(s) left!")
            else:
                st.error("⏰ **Time's up!** Your paper is being automatically submitted...")
        
        with col2:
            progress_percentage = (elapsed_time / time_limit) if time_limit > 0 else 1.0
            st.progress(min(progress_percentage, 1.0))
        
        with col3:
            st.metric("Progress", f"{min(int(progress_percentage * 100), 100)}%")
        
        st.markdown("---")
        
        # Auto-submit if time is up
        auto_submit_doc = False
        if remaining_time <= 0:
            auto_submit_doc = True
        
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
        
        # Handle auto-submit or manual submit
        if auto_submit_doc or submit_doc_answers:
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
                        st.session_state.evaluation_results = result["data"]
                        st.rerun()
                    else:
                        utils.display_error(result["error"])
        
        # Alternative navigation (shown before submission)
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Generate Another Paper", key="gen_another_doc", use_container_width=True):
                st.session_state.current_paper = None
                st.session_state.evaluation_results = None
                st.session_state.paper_source = None
                st.rerun()
        with col2:
            if st.button("🏠 Back to Home", key="home_before_doc", use_container_width=True):
                st.switch_page("app.py")


# Tab 3: Generate from Audio/Video
with tab3:
    st.markdown("### Generate Paper from Audio/Video")
    st.markdown("Upload audio or video files and generate questions based on their content.")
    
    st.info("💡 **Supported Formats:** Audio (MP3, WAV, M4A, OGG, FLAC) | Video (MP4, AVI, MOV, MKV, MPEG) | Max Size: 25MB")
    
    uploaded_file_media = st.file_uploader(
        "🎬 Upload Media File",
        type=["mp3", "wav", "m4a", "ogg", "flac", "webm", "mp4", "avi", "mov", "mkv", "mpeg", "mpg", "wmv"],
        help="Upload an audio or video file. The system will transcribe the content and generate questions.",
        key="media_upload"
    )
    
    if uploaded_file_media:
        # Display file info
        file_size = len(uploaded_file_media.getvalue()) / (1024 * 1024)  # Convert to MB
        st.success(f"✅ File uploaded: **{uploaded_file_media.name}** ({file_size:.2f} MB)")
        
        # Warning if file is large
        if file_size > 20:
            st.warning("⚠️ Large file detected. Transcription may take longer.")
    
    st.markdown("---")
    st.markdown("### ⚙️ Configure Questions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        num_mcqs_media = st.number_input(
            "🔢 Number of MCQs",
            min_value=0,
            max_value=50,
            value=10,
            step=1,
            help="Number of multiple choice questions based on the media content",
            key="media_mcqs"
        )
        
        marks_per_mcq_media = st.number_input(
            "💯 Marks per MCQ",
            min_value=1,
            max_value=10,
            value=2,
            step=1,
            key="media_mcq_marks"
        )
    
    with col2:
        num_short_media = st.number_input(
            "📝 Number of Short Questions",
            min_value=0,
            max_value=30,
            value=5,
            step=1,
            help="Number of short answer questions based on the media content",
            key="media_short"
        )
        
        marks_per_short_media = st.number_input(
            "💯 Marks per Short Question",
            min_value=1,
            max_value=20,
            value=5,
            step=1,
            key="media_short_marks"
        )
    
    st.markdown("---")
    
    st.markdown("### ⏱️ Time Limit")
    
    col1, col2 = st.columns(2)
    
    with col1:
        time_hours_media = st.number_input(
            "⏰ Hours",
            min_value=0,
            max_value=5,
            value=1,
            step=1,
            help="Number of hours allowed to solve the paper",
            key="media_hours"
        )
    
    with col2:
        time_minutes_media = st.number_input(
            "⏱️ Minutes",
            min_value=0,
            max_value=59,
            value=1,
            step=5,
            help="Number of minutes allowed to solve the paper",
            key="media_minutes"
        )
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🚀 Generate from Media", use_container_width=True, type="primary", key="gen_media_btn"):
            if not uploaded_file_media:
                utils.display_error("Please upload a media file first")
            elif num_mcqs_media == 0 and num_short_media == 0:
                utils.display_error("Please specify at least one type of question")
            else:
                # Clear previous evaluation results
                st.session_state.evaluation_results = None
                
                with st.spinner("🎙️ Transcribing media and generating questions... This may take a few moments."):
                    files = {"file": (uploaded_file_media.name, uploaded_file_media.getvalue(), uploaded_file_media.type)}
                    data = {
                        "num_mcqs": num_mcqs_media,
                        "num_short_questions": num_short_media,
                        "marks_per_mcq": marks_per_mcq_media,
                        "marks_per_short": marks_per_short_media
                    }
                    
                    result = utils.make_api_request(
                        "/api/generate_paper_from_media",
                        method="POST",
                        data=data,
                        files=files
                    )
                    
                    if result["success"]:
                        paper_data = result["data"]
                        st.session_state.current_paper = paper_data
                        st.session_state.paper_source = "media"
                        utils.display_success("Paper generated successfully from media!")
                        st.rerun()
                    else:
                        utils.display_error(result["error"])

# Display media paper if exists (outside button clicks)
if st.session_state.current_paper and st.session_state.get('paper_source') == 'media':
    paper_data = st.session_state.current_paper
    
    st.markdown("---")
    st.markdown("## 📋 Generated Paper from Audio/Video")
    
    # Header with media info
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"**Media File:** {paper_data.get('media_name', 'N/A')}")
        st.markdown(f"**Media Type:** {paper_data.get('media_type', 'N/A').title()}")
    with col2:
        st.markdown(f"**Total Questions:** {len(paper_data['questions'])}")
        st.markdown(f"**Total Marks:** {paper_data['total_marks']}")
    with col3:
        st.markdown(f"**Paper ID:** {paper_data['paper_id']}")
    
    # Show transcript preview if available
    if paper_data.get('transcript_preview'):
        with st.expander("📝 View Transcript Preview"):
            st.text_area("Transcript Preview", paper_data['transcript_preview'], height=100, disabled=True)
    
    st.markdown("---")
    st.markdown(f"**Instructions:** {paper_data.get('instructions', 'Answer all questions based on the media content.')}")
    st.markdown("---")
    
    # Show evaluation results if they exist
    if st.session_state.evaluation_results:
        eval_data = st.session_state.evaluation_results
        
        # Display results
        st.markdown("## 🎯 Your Results")
        
        # Overall score with large display
        percentage = eval_data.get('percentage', 0)
        grade_letter = eval_data.get('grade_letter', eval_data.get('grade', 'N/A'))
        total_score = eval_data.get('total_score', eval_data.get('score', 0))
        total_marks = eval_data.get('total_marks', 0)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Your Score", f"{total_score:.1f}")
        with col2:
            st.metric("Total Marks", total_marks)
        with col3:
            st.metric("Percentage", f"{percentage:.1f}%")
        with col4:
            color = utils.get_grade_color(percentage)
            st.markdown(f"""
            <div style="text-align: center; padding: 10px;">
                <p style="margin: 0; color: #666; font-size: 14px;">Grade</p>
                <p style="margin: 5px 0 0 0; color: {color}; font-size: 32px; font-weight: bold;">{grade_letter}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Progress bar
        st.progress(percentage / 100)
        
        # Comprehensive Feedback Section
        st.markdown("---")
        st.markdown("### 📋 Comprehensive Analysis")
        
        # Strengths
        if eval_data.get('strengths'):
            strengths = eval_data.get('strengths', [])
            if isinstance(strengths, str):
                strengths = [strengths]
            
            with st.expander("💪 Your Strengths", expanded=True):
                if isinstance(strengths, list):
                    for strength in strengths:
                        st.success(f"✓ {strength}")
                else:
                    st.success(f"✓ {strengths}")
        
        # Weaknesses
        if eval_data.get('weaknesses'):
            weaknesses = eval_data.get('weaknesses', [])
            if isinstance(weaknesses, str):
                weaknesses = [weaknesses]
            
            with st.expander("⚠️ Areas for Improvement", expanded=True):
                if isinstance(weaknesses, list):
                    for weakness in weaknesses:
                        st.warning(f"• {weakness}")
                else:
                    st.warning(f"• {weaknesses}")
        
        # Improvement Areas
        if eval_data.get('improvement_areas'):
            improvements = eval_data.get('improvement_areas', [])
            if isinstance(improvements, str):
                improvements = [improvements]
            
            with st.expander("🎯 Recommended Actions", expanded=True):
                if isinstance(improvements, list):
                    for i, improvement in enumerate(improvements, 1):
                        st.info(f"{i}. {improvement}")
                else:
                    st.info(f"1. {improvements}")
        
        # Detailed feedback
        st.markdown("---")
        st.markdown("### 📊 Question-by-Question Feedback")
        
        feedback_list = eval_data.get('feedback', [])
        
        if feedback_list:
            for fb in feedback_list:
                with st.expander(f"Question {fb['question_number']} - {fb['marks_obtained']}/{fb['marks_total']} marks", expanded=False):
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
                    progress = fb['marks_obtained'] / fb['marks_total'] if fb['marks_total'] > 0 else 0
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
            if st.button("📝 Generate New Paper", key="new_paper_after_eval_media", use_container_width=True):
                st.session_state.current_paper = None
                st.session_state.evaluation_results = None
                st.session_state.paper_source = None
                st.rerun()
        with col2:
            if st.button("📊 View Dashboard", key="dash_after_eval_media", use_container_width=True):
                st.switch_page("pages/3_📊_Dashboard.py")
        with col3:
            if st.button("🏠 Back to Home", key="home_after_eval_media", use_container_width=True):
                st.switch_page("app.py")
    else:
        # Interactive Answer Form (only show if no evaluation results yet)
        st.markdown("### 📝 Solve This Paper")
        st.info("💡 Enter your answers below and submit for instant evaluation!")
        
        # Store time limit in session state
        if 'media_paper_time_limit' not in st.session_state:
            st.session_state.media_paper_time_limit = (time_hours_media * 3600) + (time_minutes_media * 60)
        
        if 'media_paper_start_time' not in st.session_state:
            st.session_state.media_paper_start_time = __import__('time').time()
        
        # Display timer
        time_limit = st.session_state.media_paper_time_limit
        start_time = st.session_state.media_paper_start_time
        elapsed_time = int(__import__('time').time() - start_time)
        remaining_time = max(0, time_limit - elapsed_time)
        
        remaining_minutes = remaining_time // 60
        remaining_seconds = remaining_time % 60
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            if remaining_time > 300:  # More than 5 minutes
                st.markdown(f"### ⏱️ Time Remaining: **{remaining_minutes:02d}:{remaining_seconds:02d}**")
            elif remaining_time > 0:  # Less than 5 minutes
                st.markdown(f"### ⏱️ Time Remaining: **{remaining_minutes:02d}:{remaining_seconds:02d}**")
                st.warning(f"⚠️ Only {remaining_minutes} minute(s) left!")
            else:
                st.error("⏰ **Time's up!** Your paper is being automatically submitted...")
        
        with col2:
            progress_percentage = (elapsed_time / time_limit) if time_limit > 0 else 1.0
            st.progress(min(progress_percentage, 1.0))
        
        with col3:
            st.metric("Progress", f"{min(int(progress_percentage * 100), 100)}%")
        
        st.markdown("---")
        
        # Auto-submit if time is up
        auto_submit_media = False
        if remaining_time <= 0:
            auto_submit_media = True
        
        with st.form("solve_media_paper_form_main"):
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
                        st.markdown(f"<p style='margin-left: 20px; font-size: 15px;'>{option}</p>", unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Answer input
                if question['question_type'].upper() == 'MCQ' and question.get('options'):
                    answer = st.selectbox(
                        f"Your Answer for Question {question['question_number']}",
                        [""] + [f"{chr(65+j)}" for j in range(len(question['options']))],
                        key=f"mcq_media_answer_main_{question['question_number']}",
                        help="Select your answer (A, B, C, D)"
                    )
                else:
                    answer = st.text_area(
                        f"Your Answer for Question {question['question_number']}",
                        key=f"media_answer_main_{question['question_number']}",
                        height=100,
                        placeholder="Type your answer here..."
                    )
                
                answers.append({
                    "question_number": question['question_number'],
                    "answer": answer
                })
                
                st.markdown("<br>", unsafe_allow_html=True)
            
            st.markdown("---")
            submit_media_answers = st.form_submit_button("🎯 Submit Answers for Evaluation", use_container_width=True, type="primary")
        
        # Handle auto-submit or manual submit
        if auto_submit_media or submit_media_answers:
            # Filter out empty answers
            filled_answers = []
            for ans in answers:
                if ans["answer"] and str(ans["answer"]).strip():
                    filled_answers.append({
                        "question_number": ans["question_number"],
                        "answer": str(ans["answer"]).strip()
                    })
            
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
                        st.session_state.evaluation_results = result["data"]
                        st.rerun()
                    else:
                        utils.display_error(result["error"])
        
        # Alternative navigation buttons (shown before submission)
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Generate Another Paper", key="gen_another_media", use_container_width=True):
                st.session_state.current_paper = None
                st.session_state.evaluation_results = None
                st.session_state.paper_source = None
                st.rerun()
        with col2:
            if st.button("🏠 Back to Home", key="home_before_media", use_container_width=True):
                st.switch_page("app.py")
