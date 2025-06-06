from pathlib import Path
import os
from typing import List
from ..core.exceptions import FileValidationError

def sanitize_path(user_path: str) -> Path:
    base_path = Path("/approved/docs").resolve()
    requested_path = (base_path / user_path).resolve()
    
    if not requested_path.is_relative_to(base_path):
        raise ValueError("Attempted directory traversal")
    
    if not requested_path.exists():
        raise FileNotFoundError(f"Path {requested_path} does not exist")
    
    return requested_path

def ensure_directory(path: str) -> Path:
    dir_path = Path(path)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path

def validate_file_path(file_path: str) -> bool:
    """
    Validate if the file exists and is accessible.
    
    Args:
        file_path: Path to the file
        
    Returns:
        bool: True if file is valid
        
    Raises:
        FileValidationError: If file validation fails
    """
    try:
        path = Path(file_path)
        if not path.exists():
            raise FileValidationError(f"File not found: {file_path}")
        if not os.access(path, os.R_OK):
            raise FileValidationError(f"File not readable: {file_path}")
        return True
    except Exception as e:
        raise FileValidationError(f"Error validating file: {str(e)}")

def get_supported_formats() -> List[str]:
    """Return list of supported file formats."""
    return ['pdf']
