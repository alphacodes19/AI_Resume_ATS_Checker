import io
import magic
from typing import Tupel, Optional

import pdfplumber
from docx import Document
import Pypdf2

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
    ALLOWED_FILE_TYPES
)

class FileParsingErro(Exception):
    pass

class FileValidationError(Exception):
    pass

def validate_file(file_data:byte, filename:str) -> Tuple[bool, str, Optional[str]]:
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
    

    


