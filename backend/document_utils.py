import PyPDF2
from docx import Document
import io
from fastapi import UploadFile, HTTPException


async def extract_text_from_file(file: UploadFile) -> str:
    """
    Extract text content from uploaded file (PDF, DOCX, TXT)
    """
    try:
        content = await file.read()
        filename = file.filename.lower()
        
        if filename.endswith('.pdf'):
            return extract_text_from_pdf(content)
        elif filename.endswith('.docx'):
            return extract_text_from_docx(content)
        elif filename.endswith('.txt'):
            return content.decode('utf-8')
        else:
            raise HTTPException(
                status_code=400, 
                detail="Unsupported file format. Please upload PDF, DOCX, or TXT file."
            )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading file: {str(e)}")


def extract_text_from_pdf(content: bytes) -> str:
    """Extract text from PDF file"""
    try:
        pdf_file = io.BytesIO(content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        
        if not text.strip():
            raise Exception("No text could be extracted from the PDF")
        
        return text.strip()
    except Exception as e:
        raise Exception(f"Error extracting PDF text: {str(e)}")


def extract_text_from_docx(content: bytes) -> str:
    """Extract text from DOCX file"""
    try:
        docx_file = io.BytesIO(content)
        doc = Document(docx_file)
        
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        
        if not text.strip():
            raise Exception("No text could be extracted from the DOCX")
        
        return text.strip()
    except Exception as e:
        raise Exception(f"Error extracting DOCX text: {str(e)}")


def validate_document_length(text: str, max_chars: int = 15000) -> bool:
    """
    Validate that document is not too long for processing
    """
    if len(text) > max_chars:
        raise HTTPException(
            status_code=400,
            detail=f"Document is too long. Maximum {max_chars} characters allowed. Your document has {len(text)} characters."
        )
    return True
