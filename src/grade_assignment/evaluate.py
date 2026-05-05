import json
import logging
from typing import Dict, Any
from google import genai
from google.genai import types

# logging setup for api calls
logger = logging.getLogger(__name__)

class EvaluatorLLM:
    """sends code to gemini and retrieves structured feedback."""
    
    def __init__(self, model_id: str = "gemini-2.5-flash"):
        # the client automatically looks for the api key in the environment
        self.client = genai.Client()
        self.model_id = model_id
        
    def evaluate_submission(
        self, 
        code_data: Dict[str, Any], 
        rubric: str, 
        assignment_prompt: str
    ) -> Dict[str, Any]:
        """formats the prompt and parses the json response."""
        
        instructions = f"""
        evaluate the following submission.
        
        context: {assignment_prompt}
        rubric: {rubric}
        code: {code_data.get('source_code')}
        
        return a json object with:
        {{
            "suggested_score": integer (0-100),
            "feedback_markdown": string (feedback in russian)
        }}
        """
        
        try:
            # calling the model
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=instructions,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            return json.loads(response.text)
        except Exception as e:
            logger.error(f"api call failed: {e}")
            return {
                "suggested_score": 0,
                "feedback_markdown": "ошибка при вызове api."
            }