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
        
        # For MCQs, extract just the letter from both student answer and correct answer
        if q.get('question_type', '').upper() == 'MCQ':
            # Extract letter from student answer (handle "A", "A.", "A)", "A. text", etc.)
            if student_ans and student_ans != "No answer provided":
                student_ans_clean = student_ans.strip()
                # Extract first letter if it's A, B, C, D
                if student_ans_clean and student_ans_clean[0].upper() in ['A', 'B', 'C', 'D']:
                    student_ans_letter = student_ans_clean[0].upper()
                else:
                    student_ans_letter = student_ans_clean
            else:
                student_ans_letter = "No answer"
            
            # Extract letter from correct answer
            correct_ans = q.get('correct_answer', '')
            if correct_ans:
                correct_ans_clean = str(correct_ans).strip()
                # Extract first letter if it's A, B, C, D
                if correct_ans_clean and correct_ans_clean[0].upper() in ['A', 'B', 'C', 'D']:
                    correct_ans_letter = correct_ans_clean[0].upper()
                else:
                    correct_ans_letter = correct_ans_clean
            else:
                correct_ans_letter = "Not specified"
            
            evaluation_details.append(f"""
Question {q_num} ({q['marks']} marks) - MCQ:
Question: {q['question_text']}
Options: {', '.join(q.get('options', []))}
Correct Answer: {correct_ans_letter}
Student's Answer: {student_ans_letter}
""")
        else:
            evaluation_details.append(f"""
Question {q_num} ({q['marks']} marks) - {q['question_type']}:
Question: {q['question_text']}
Correct Answer: {q['correct_answer']}
Student's Answer: {student_ans}
""")
    
    prompt = f"""You are an experienced Oxford curriculum examiner. Evaluate ALL the following student answers carefully and provide COMPREHENSIVE feedback.

IMPORTANT: You MUST evaluate EVERY SINGLE QUESTION listed below. Provide detailed feedback for each question number.

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

DETAILED FEEDBACK REQUIREMENTS FOR EACH QUESTION:
- Explicitly state whether the answer is correct or incorrect
- Explain WHY marks were awarded or deducted
- For incorrect answers: clearly state what was wrong and what the correct approach should be
- Highlight any partial understanding or half-correct attempts
- For correct answers: acknowledge the good understanding or correct approach
- Suggest specific improvements where applicable

COMPREHENSIVE OVERALL FEEDBACK:
Provide a detailed summary that includes:
1. **Strengths**: Specific topics/concepts the student understands well
2. **Weaknesses**: Specific topics/concepts that need improvement
3. **Performance Analysis**: 
   - Which question types performed best (MCQs, Short Answer, etc.)
   - Which topics/concepts were problematic
4. **Improvement Suggestions**: 
   - Specific areas to focus on
   - Study strategies or practice recommendations
   - Concepts to review before next attempt
5. **Overall Assessment**: Brief statement about overall performance level

You MUST return feedback in this EXACT JSON format:
{{
  "question_feedback": [
    {{
      "question_number": 1,
      "marks_obtained": 2.0,
      "marks_total": 2,
      "feedback": "Detailed feedback: Was this correct/incorrect? Why? What should have been done differently?",
      "correct_answer": "The correct/expected answer",
      "explanation": "Brief explanation of the concept"
    }}
  ],
  "overall_feedback": "Comprehensive feedback including: Strengths (specific topics), Weaknesses (specific topics), Performance Analysis, Improvement Suggestions, and Overall Assessment",
  "strengths": ["Specific strength 1", "Specific strength 2", "Specific strength 3"],
  "weaknesses": ["Specific weakness 1", "Specific weakness 2", "Specific weakness 3"],
  "improvement_areas": ["Area to improve 1", "Area to improve 2", "Area to improve 3"]
}}

CRITICAL REQUIREMENTS:
- Include feedback for EVERY question from 1 to {len(questions)} - Do not skip any
- Make feedback SPECIFIC, not generic
- Point out EXACTLY what was wrong or right
- Provide actionable improvement suggestions
- Be honest about performance but constructive"""

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
        
        # Validate the evaluation response has question_feedback
        if "question_feedback" not in evaluation_data:
            raise Exception("Invalid evaluation response: missing 'question_feedback' key")
        
        if not isinstance(evaluation_data["question_feedback"], list):
            raise Exception("Invalid evaluation response: 'question_feedback' must be a list")
        
        # Validate each feedback item has required fields
        for fb in evaluation_data["question_feedback"]:
            if "question_number" not in fb:
                raise Exception(f"Invalid feedback item: missing 'question_number'")
            if "marks_obtained" not in fb:
                raise Exception(f"Invalid feedback for question {fb.get('question_number')}: missing 'marks_obtained'")
            if "marks_total" not in fb:
                raise Exception(f"Invalid feedback for question {fb.get('question_number')}: missing 'marks_total'")
            
            # Ensure marks are numeric
            try:
                fb["marks_obtained"] = float(fb["marks_obtained"])
                fb["marks_total"] = int(fb["marks_total"])
            except (ValueError, TypeError) as e:
                raise Exception(f"Invalid marks format in question {fb.get('question_number')}: {str(e)}")
        
        return evaluation_data
        
    except json.JSONDecodeError as e:
        raise Exception(f"Invalid JSON in evaluation response: {str(e)}")
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


def generate_paper_from_media_transcript(transcript: str, num_mcqs: int, num_short_questions: int, 
                                          marks_per_mcq: int, marks_per_short: int) -> dict:
    """Generate questions based on audio/video transcript"""
    
    if num_mcqs == 0 and num_short_questions == 0:
        raise Exception("Please specify at least one type of question (MCQs or Short Questions)")
    
    # Build the requirements section with exact counts
    total_questions = num_mcqs + num_short_questions
    requirements_parts = []
    
    if num_mcqs > 0:
        requirements_parts.append(f"- EXACTLY {num_mcqs} Multiple Choice Questions (question numbers 1 to {num_mcqs})")
        requirements_parts.append(f"  * Each MCQ worth {marks_per_mcq} marks")
        requirements_parts.append(f"  * Must have EXACTLY 4 options (A, B, C, D)")
    
    if num_short_questions > 0:
        start_num = num_mcqs + 1
        end_num = num_mcqs + num_short_questions
        requirements_parts.append(f"- EXACTLY {num_short_questions} Short Answer Questions (question numbers {start_num} to {end_num})")
        requirements_parts.append(f"  * Each worth {marks_per_short} marks")
    
    requirements_text = "\n".join(requirements_parts)
    
    prompt = f"""You are an expert examination paper creator. Create examination questions based STRICTLY on the following audio/video transcript content.

========== TRANSCRIPT CONTENT ==========
{transcript[:12000]}
========================================

CRITICAL REQUIREMENTS - YOU MUST FOLLOW EXACTLY:
Generate EXACTLY {total_questions} questions in total:
{requirements_text}

QUESTION GENERATION RULES:
1. ✓ ALL questions MUST be directly based on information present in the transcript above
2. ✓ Extract key facts, concepts, explanations, and details from the transcript
3. ✓ For MCQs: Create 4 unique options where only ONE is correct based on the transcript
4. ✓ For Short Answer: Ask about specific information, concepts, or explanations mentioned in the transcript
5. ✓ Questions should test: comprehension, recall, and understanding of the content
6. ✓ Use question numbers sequentially: 1, 2, 3, ... {total_questions}
7. ✓ Include the correct answer for EVERY question based on transcript content
8. ✓ DO NOT generate more or fewer questions than specified

RETURN FORMAT (STRICT JSON):
{{
  "instructions": "Answer all questions based on the audio/video content.",
  "questions": [
    {{
      "question_number": 1,
      "question_type": "MCQ",
      "question_text": "[Question extracted from transcript]",
      "marks": {marks_per_mcq},
      "options": ["A) [Option 1]", "B) [Option 2]", "C) [Option 3]", "D) [Option 4]"],
      "correct_answer": "A"
    }},
    {{
      "question_number": 2,
      "question_type": "Short Answer",
      "question_text": "[Question extracted from transcript]",
      "marks": {marks_per_short},
      "correct_answer": "[Expected answer based on transcript]"
    }}
  ]
}}

IMPORTANT: 
- Total questions in your response MUST be exactly {total_questions}
- MCQ questions: exactly {num_mcqs}
- Short Answer questions: exactly {num_short_questions}
- All content must come from the transcript provided above
- For MCQ correct_answer: use ONLY the letter (A, B, C, or D)"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert examination paper creator. Generate questions strictly based on the provided audio/video transcript content. You MUST generate the EXACT number of questions requested. Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,  # Lower temperature for more consistent output
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
        
        # Validate that we got the correct number of questions
        generated_questions = paper_data.get("questions", [])
        expected_total = num_mcqs + num_short_questions
        
        if len(generated_questions) != expected_total:
            # Count by type
            mcq_count = sum(1 for q in generated_questions if q.get("question_type", "").upper() == "MCQ")
            short_count = sum(1 for q in generated_questions if q.get("question_type", "").upper() in ["SHORT ANSWER", "SHORT"])
            
            raise Exception(
                f"Question count mismatch. Expected {expected_total} questions ({num_mcqs} MCQs + {num_short_questions} Short), "
                f"but got {len(generated_questions)} questions ({mcq_count} MCQs + {short_count} Short). "
                f"Please try again or adjust the question counts."
            )
        
        # Validate MCQ count
        mcq_count = sum(1 for q in generated_questions if q.get("question_type", "").upper() == "MCQ")
        if num_mcqs > 0 and mcq_count != num_mcqs:
            raise Exception(
                f"MCQ count mismatch. Expected {num_mcqs} MCQs but got {mcq_count}. Please try again."
            )
        
        return paper_data
        
    except json.JSONDecodeError as e:
        raise Exception(f"Invalid JSON response from AI: {str(e)}")
    except Exception as e:
        raise Exception(f"Error generating paper from media transcript with AI: {str(e)}")
