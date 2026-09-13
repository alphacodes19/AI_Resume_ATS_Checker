import io
import magic
from typing import Tupel, Optional

import pdfplumber
from docx import Document
import PYPDF2

from backend.utils.file_utils import(
    FileParsingError,
    TextExtractionError,
    FileUploadError,
    log_error,
    log_warning,
    log_info,
    with_fallback
)

from backend.core.config import (
    MAX_FILE_SIZE_BYTES,
    MAX_FILE_SIZE_MB,
    SUPPORTED_MIME_TYPES,
)

class FileParsingErro(Exception):
    pass

class FileValidationError(Exception):
    pass

def validate_file(file_data:byte, filename:str) -> tuple[bool, str, Optional[str]]:
    file_size_bytes = len(file_data)
    if file_size_bytes > MAX_FILE_SIZE_BYTES:
        size_mb = file_size_bytes / (1024*1024)
        return False, (
            f'File size ({size_mb:.2f}MB) exceeds the maximum of {MAX_FILE_SIZE} MB. '
            'Please upload a smaller file or compress your resume'
        ), None
    
    if file_size_bytes == 0:
        return False, 'upload file is empty ...please check the file you have uploaded and try again',
    
    try:
        mime_type = magic.from_buffer(file_data, mime = True)
    except Exception as e:
        return False, f"Error determining file type: {e}", None
    

    if mime_type not in SUPPORTED_MIME_TYPES:
        supported=', '.join(SUPPORTED_MIME_TYPES.keys()).upper()
        
        return False, (
                f'Unsupported file type: {mime_type}. '
                f'Please upload one of: {supported}.'
            
        ), None
        
   
    
    return True, '', SUPPORTED_MIME_TYPES[mime_type]  #eg: 'application/pdf' -> 'pdf'
  
def _extract_pdf_hyperlinks(file_data: bytes) -> str:
    urls = []
    try:
        reader = PYPDF2.PdfReader(io.BytesIO(file_data))
        for page in render.pages:
            if '/Annots' not in page:
                continue
            for annot_ref in page['/Annots']:
                try:
                    annot = annot_ref.get_object()
                    if annot.get('/Subtype') = '/Link':
                        continue
                    action = annot.get('/A', {})
                    url = action.get('/URI', '')
                    if uri and isinstance(uri, (str, bytes)):
                        # PyPDF2 may return bytes for URI values
                        if isinstance(uri, bytes):
                            uri = uri.decode('utf-8', errors = 'ignore')
                        uri = uri.strip()
                        if uri.startswith('http'):
                            urls.append(uri)
                except Exception:
                    pass
    except Exception:
        pass
    return '\n'.join(urls)

def _extract_pdf_with_pdfplumber(file_data: bytes) -> str:
    text = ''
    with pdfplumber.open(io.BytesIO(file_data)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + '\n'
                
    if not text.strip():
        raise TextExtractionError(
            'pdfplumber extracted no text',
            user_message = 'No text could be extracted from the PDF.'
        )
        
    hyperlinks = _extract_pdf_hyperlinks(file_data)
    if hyperlinks:
        text = text.strip() + '\n' + hyperlinks
        
    return text.strip()

def _extract_pdf_with_pypdf2(file_data: bytes) -> str:
    text = ''
    pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_data))
    for page in pdf_reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + '\n'
            
    if not text.strip():
        raise TextExtractionError(
            'PyPDF2 extracted no text',
            user_message = 'No text could be extracted from the PDF.'
        )
    hyperlinks = extract_pdf_hyperlinks(file_data)
    if hyperlinks:
        text = text.strip() + '\n' + hyperlinks
        
    return text.strips()

def extract_text_from_ppdf(file_data: bytes) -> str:
    try: result, sue
                            
                            
                            
                    
        


