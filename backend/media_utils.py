"""
Media Processing Utilities
Handles audio/video file processing and transcription for paper generation
"""
import io
import os
import tempfile
from fastapi import UploadFile, HTTPException
from openai import OpenAI
import config

client = OpenAI(api_key=config.OPENAI_API_KEY)

# Supported media formats
SUPPORTED_AUDIO_FORMATS = ['.mp3', '.wav', '.m4a', '.ogg', '.flac', '.webm']
SUPPORTED_VIDEO_FORMATS = ['.mp4', '.avi', '.mov', '.mkv', '.mpeg', '.mpg', '.wmv']
ALL_SUPPORTED_FORMATS = SUPPORTED_AUDIO_FORMATS + SUPPORTED_VIDEO_FORMATS

# Maximum file size (25MB - Whisper API limit)
MAX_FILE_SIZE = 25 * 1024 * 1024  # 25MB in bytes


async def validate_media_file(file: UploadFile) -> bool:
    """
    Validate that the uploaded file is a supported media format and within size limits
    """
    filename = file.filename.lower()
    
    # Check file extension
    file_ext = os.path.splitext(filename)[1]
    if file_ext not in ALL_SUPPORTED_FORMATS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format. Supported formats: {', '.join(ALL_SUPPORTED_FORMATS)}"
        )
    
    # Read file to check size
    content = await file.read()
    file_size = len(content)
    
    # Reset file pointer for later use
    await file.seek(0)
    
    if file_size > MAX_FILE_SIZE:
        size_mb = file_size / (1024 * 1024)
        raise HTTPException(
            status_code=400,
            detail=f"File too large ({size_mb:.2f}MB). Maximum size is 25MB."
        )
    
    return True


async def transcribe_media_file(file: UploadFile) -> str:
    """
    Transcribe audio/video file to text using OpenAI Whisper API
    """
    try:
        # Validate file first
        await validate_media_file(file)
        
        # Read file content
        content = await file.read()
        filename = file.filename
        
        # Create a temporary file with the correct extension
        file_ext = os.path.splitext(filename)[1]
        
        # For video files, we'll pass directly to Whisper
        # Whisper API can handle video files and extract audio automatically
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Transcribe using OpenAI Whisper API
            with open(temp_file_path, 'rb') as audio_file:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="text"
                )
            
            if not transcript or not transcript.strip():
                raise HTTPException(
                    status_code=400,
                    detail="No speech detected in the media file. Please upload a file with clear audio content."
                )
            
            return transcript.strip()
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error transcribing media file: {str(e)}"
        )


def validate_transcript_length(text: str, max_chars: int = 15000) -> bool:
    """
    Validate that transcript is not too long for processing
    """
    if len(text) > max_chars:
        raise HTTPException(
            status_code=400,
            detail=f"Transcript is too long. Maximum {max_chars} characters allowed. Your transcript has {len(text)} characters. Please upload a shorter media file."
        )
    return True


def get_media_info(filename: str) -> dict:
    """
    Get media file information
    """
    file_ext = os.path.splitext(filename.lower())[1]
    
    if file_ext in SUPPORTED_AUDIO_FORMATS:
        media_type = "audio"
    elif file_ext in SUPPORTED_VIDEO_FORMATS:
        media_type = "video"
    else:
        media_type = "unknown"
    
    return {
        "filename": filename,
        "extension": file_ext,
        "media_type": media_type
    }
