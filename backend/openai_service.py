import json
from openai import OpenAI
import config

client = OpenAI(api_key=config.OPENAI_API_KEY)


def generate_paper_with_ai(grade: str, subject: str, chapter: str, topic: str = None) -> dict:
    """Generate an Oxford curriculum pattern paper using OpenAI"""
    
    topic_info = f" focusing on {topic}" if topic else ""
    
    prompt = f"""Generate an examination paper following the Oxford Curriculum pattern for:
Grade: {grade}
Subject: {subject}
Chapter: {chapter}{topic_info}

IMPORTANT: You MUST generate EXACTLY 20 questions in total as specified below:

1. Section A - Objective Questions (30 marks):
   - Generate EXACTLY 10 Multiple Choice Questions (MCQs), 2 marks each
   - Each MCQ MUST have 4 options (A, B, C, D)
   - Question numbers: 1 to 10

2. Section B - Short Answer Questions (30 marks):
   - Generate EXACTLY 6 Short answer questions, 5 marks each
   - Questions requiring brief explanations or calculations
   - Question numbers: 11 to 16

3. Section C - Long Answer Questions (40 marks):
   - Generate EXACTLY 4 Long answer questions, 10 marks each
   - Questions requiring detailed explanations, problem-solving, or essay-type answers
   - Question numbers: 17 to 20

Total Questions: 20 (10 MCQs + 6 Short + 4 Long)
Total Marks: 100
Time: 3 hours

Return the response in this EXACT JSON format with ALL 20 questions:
{{
  "instructions": "General instructions for the examination",
  "questions": [
    {{
      "question_number": 1,
      "question_type": "MCQ",
      "question_text": "Question text here",
      "marks": 2,
      "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"],
      "correct_answer": "A) Option 1"
    }},
    {{
      "question_number": 11,
      "question_type": "Short Answer",
      "question_text": "Question text here",
      "marks": 5,
      "correct_answer": "Expected answer or key points"
    }},
    {{
      "question_number": 17,
      "question_type": "Long Answer",
      "question_text": "Question text here",
      "marks": 10,
      "correct_answer": "Expected answer structure and key points"
    }}
  ]
}}

Make sure questions are curriculum-appropriate, challenging, and test understanding at multiple cognitive levels."""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Fast and cost-effective
            messages=[
                {"role": "system", "content": "You are an expert Oxford curriculum examination paper creator. Generate well-structured, academically rigorous questions. You MUST generate ALL questions as specified. Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=4096
        )
        
        content = response.choices[0].message.content.strip()
        
        # Clean up the response if it has markdown code blocks
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()
        
        paper_data = json.loads(content)
        return paper_data
        
    except Exception as e:
        raise Exception(f"Error generating paper with AI: {str(e)}")


def evaluate_paper_with_ai(questions: list, student_answers: dict) -> dict:
    """Evaluate student answers using OpenAI"""
    
    # Build detailed question-by-question prompt
    evaluation_details = []
    for q in questions:
        q_num = q["question_number"]
        student_ans = student_answers.get(q_num, "No answer provided")
        
        evaluation_details.append(f"""
Question {q_num} ({q['marks']} marks) - {q['question_type']}:
Question: {q['question_text']}
{f"Options: {', '.join(q.get('options', []))}" if q.get('options') else ""}
Correct Answer: {q['correct_answer']}
Student's Answer: {student_ans}
""")
    
    prompt = f"""You are an experienced Oxford curriculum examiner. Evaluate ALL the following student answers carefully.

IMPORTANT: You MUST evaluate EVERY SINGLE QUESTION listed below. Provide feedback for each question number.

{chr(10).join(evaluation_details)}

EVALUATION CRITERIA:
1. For MCQs: Award full marks if answer matches the correct option letter (A, B, C, or D), otherwise 0 marks
2. For Short Answer questions: Award marks (0 to full) based on:
   - Accuracy of information (40%)
   - Understanding of concept (30%)
   - Clarity of explanation (30%)
3. For Long Answer questions: Award marks (0 to full) based on:
   - Completeness of answer (35%)
   - Depth of understanding (35%)
   - Structure and clarity (30%)

You MUST return feedback for ALL {len(questions)} questions in this EXACT JSON format:
{{
  "question_feedback": [
    {{
      "question_number": 1,
      "marks_obtained": 2.0,
      "marks_total": 2,
      "feedback": "Detailed feedback explaining why marks were awarded or deducted",
      "correct_answer": "The correct/expected answer"
    }}
  ],
  "overall_feedback": "Summary of performance across all questions with specific strengths and improvement areas"
}}

CRITICAL: Include feedback for EVERY question from 1 to {len(questions)}. Do not skip any questions."""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a fair and experienced examination evaluator. You MUST evaluate ALL questions provided. Provide detailed, constructive feedback for every single question. Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,  # Lower temperature for more consistent grading
            max_tokens=4096  # Increased for evaluating all questions
        )
        
        content = response.choices[0].message.content.strip()
        
        # Clean up the response if it has markdown code blocks
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()
        
        evaluation_data = json.loads(content)
        return evaluation_data
        
    except Exception as e:
        raise Exception(f"Error evaluating paper with AI: {str(e)}")


def generate_paper_from_document(document_text: str, num_mcqs: int, num_short_questions: int, 
                                  marks_per_mcq: int, marks_per_short: int) -> dict:
    """Generate questions based on uploaded document content"""
    
    if num_mcqs == 0 and num_short_questions == 0:
        raise Exception("Please specify at least one type of question (MCQs or Short Questions)")
    
    questions_description = []
    question_number = 1
    
    if num_mcqs > 0:
        questions_description.append(f"{num_mcqs} Multiple Choice Questions (MCQs), {marks_per_mcq} marks each, with 4 options (A, B, C, D)")
    
    if num_short_questions > 0:
        questions_description.append(f"{num_short_questions} Short Answer Questions, {marks_per_short} marks each")
    
    prompt = f"""You are an expert examination paper creator. Based on the following document content, generate examination questions.

DOCUMENT CONTENT:
{document_text[:10000]}

REQUIREMENTS:
Generate EXACTLY the following questions based on the document content:
{' and '.join(questions_description)}

IMPORTANT INSTRUCTIONS:
1. All questions MUST be based on the content provided in the document above
2. Questions should test understanding, comprehension, and application of the document content
3. For MCQs: Provide 4 options (A, B, C, D) with only one correct answer
4. For Short Answer: Questions should require brief explanations or summaries from the document
5. Number questions sequentially starting from 1
6. Include the correct answer for each question

Return the response in this EXACT JSON format:
{{
  "instructions": "Answer all questions based on the provided document.",
  "questions": [
    {{
      "question_number": 1,
      "question_type": "MCQ",
      "question_text": "Question text here",
      "marks": {marks_per_mcq},
      "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"],
      "correct_answer": "A) Option 1"
    }},
    {{
      "question_number": 2,
      "question_type": "Short Answer",
      "question_text": "Question text here",
      "marks": {marks_per_short},
      "correct_answer": "Expected answer based on document"
    }}
  ]
}}

Generate questions that are relevant, clear, and directly related to the document content."""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert examination paper creator. Generate questions strictly based on the provided document content. Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=4096
        )
        
        content = response.choices[0].message.content.strip()
        
        # Clean up the response if it has markdown code blocks
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()
        
        paper_data = json.loads(content)
        return paper_data
        
    except Exception as e:
        raise Exception(f"Error generating paper from document with AI: {str(e)}")
