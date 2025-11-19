import os
import tempfile
from typing import Optional, Tuple
import pdfplumber
import pytesseract
from PIL import Image
import io
from fastapi import UploadFile, HTTPException
from ..config import settings


class PDFProcessingService:
    """Service for processing PDF syllabi and extracting text content."""
    
    def __init__(self):
        self.supported_formats = ['.pdf', '.jpg', '.jpeg', '.png']
    
    async def process_uploaded_file(self, file: UploadFile) -> str:
        """
        Process an uploaded file (PDF or image) and extract text content.
        
        Args:
            file: Uploaded file object
            
        Returns:
            Extracted text content from the file
            
        Raises:
            HTTPException: If file format is not supported or processing fails
        """
        # Validate file format
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in self.supported_formats:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format. Supported formats: {', '.join(self.supported_formats)}"
            )
        
        try:
            # Read file content
            file_content = await file.read()
            
            # Process based on file type
            if file_extension == '.pdf':
                return self._extract_text_from_pdf(file_content)
            else:
                return self._extract_text_from_image(file_content)
                
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to process file: {str(e)}"
            )
    
    def _extract_text_from_pdf(self, pdf_content: bytes) -> str:
        """
        Extract text from PDF content using pdfplumber.
        
        Args:
            pdf_content: Raw PDF file content
            
        Returns:
            Extracted text content
        """
        text_content = []
        
        try:
            # Create a temporary file to store the PDF
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                temp_file.write(pdf_content)
                temp_file_path = temp_file.name
            
            # Extract text using pdfplumber
            with pdfplumber.open(temp_file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_content.append(page_text)
            
            # Clean up temporary file
            os.unlink(temp_file_path)
            
            return '\n'.join(text_content)
            
        except Exception as e:
            # Clean up temporary file if it exists
            if 'temp_file_path' in locals():
                try:
                    os.unlink(temp_file_path)
                except:
                    pass
            raise Exception(f"PDF processing failed: {str(e)}")
    
    def _extract_text_from_image(self, image_content: bytes) -> str:
        """
        Extract text from image content using OCR (Tesseract).
        
        Args:
            image_content: Raw image file content
            
        Returns:
            Extracted text content
        """
        try:
            # Open image using PIL
            image = Image.open(io.BytesIO(image_content))
            
            # Convert to RGB if necessary (for PNG with transparency)
            if image.mode in ('RGBA', 'LA', 'P'):
                rgb_image = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                rgb_image.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = rgb_image
            
            # Extract text using Tesseract OCR
            text = pytesseract.image_to_string(image)
            
            return text.strip()
            
        except Exception as e:
            raise Exception(f"Image processing failed: {str(e)}")
    
    def validate_file_size(self, file: UploadFile, max_size_mb: int = 10) -> bool:
        """
        Validate that the file size is within acceptable limits.
        
        Args:
            file: Uploaded file object
            max_size_mb: Maximum file size in megabytes
            
        Returns:
            True if file size is valid
            
        Raises:
            HTTPException: If file size exceeds limit
        """
        # Get file size (this is a rough estimate since we can't get exact size without reading)
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset position
        
        max_size_bytes = max_size_mb * 1024 * 1024
        
        if file_size > max_size_bytes:
            raise HTTPException(
                status_code=413,
                detail=f"File size exceeds maximum limit of {max_size_mb}MB"
            )
        
        return True
    
    def clean_extracted_text(self, text: str) -> str:
        """
        Clean and normalize extracted text content.
        
        Args:
            text: Raw extracted text
            
        Returns:
            Cleaned text content
        """
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = ' '.join(text.split())
        
        # Remove common OCR artifacts
        text = text.replace('|', 'I')  # Common OCR confusion
        text = text.replace('0', 'O', text.count('0'))  # Sometimes 0 is read as O
        
        return text.strip()


# Create a singleton instance
pdf_service = PDFProcessingService()