import logging
from pathlib import Path
from typing import Dict, Any

# logging setup to track file reading
logger = logging.getLogger(__name__)

class CodeExtractor:
    """reads student code files to prepare them for grading."""
    
    @staticmethod
    def extract(file_path: Path) -> Dict[str, Any]:
        """opens a file and returns its content as a dictionary."""
        try:
            if not file_path.exists():
                return {"error": f"file not found at {file_path}"}
            
            # read the text content of the submission
            content = file_path.read_text(encoding="utf-8")
            
            return {
                "file_name": file_path.name,
                "extension": file_path.suffix.lower(),
                "source_code": content
            }
        except Exception as e:
            logger.error(f"failed to read file {file_path}: {e}")
            return {"error": str(e)}