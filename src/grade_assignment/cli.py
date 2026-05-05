import click
import json
import logging
import time
import sys
from pathlib import Path
from dotenv import load_dotenv
from .extract import CodeExtractor
from .evaluate import EvaluatorLLM

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

@click.command()
@click.option("--coursework-id", required=True, help="google classroom coursework id")
@click.option("--model", default="gemini-2.5-flash", help="ai model version")
@click.option("--delay", default=5, help="seconds to wait between students")
def main(coursework_id, model, delay):
    """runs the grading pipeline for a specific coursework id."""
    
    # dynamically resolving all paths based on coursework_id
    manifest_path = Path(f"./data/manifests/manifest_{coursework_id}.json")
    rubric_path = Path(f"./rules/rubric_{coursework_id}.md")
    prompt_path = Path(f"./instructions/assignment_{coursework_id}.md")
    output_path = Path(f"./grades/grade_report_{coursework_id}.json")
    
    # verifying all required input files exist before starting
    for required_file in [manifest_path, rubric_path, prompt_path]:
        if not required_file.exists():
            logging.error(f"required file missing: {required_file.absolute()}")
            sys.exit(1)
            
    # reading reference files
    rubric_text = rubric_path.read_text(encoding="utf-8")
    prompt_text = prompt_path.read_text(encoding="utf-8")
    
    with open(manifest_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    evaluator = EvaluatorLLM(model_id=model)
    extractor = CodeExtractor()
    results = []
    
    click.echo(f"starting evaluation of {len(data)} submissions for assignment {coursework_id}...")
    
    for i, record in enumerate(data):
        name = record.get("student_name", "unknown")
        file_path = Path(record.get("local_path"))
        
        click.echo(f"processing ({i+1}/{len(data)}): {name}")
        
        code_info = extractor.extract(file_path)
        if "error" not in code_info:
            grade = evaluator.evaluate_submission(code_info, rubric_text, prompt_text)
        else:
            grade = {"suggested_score": 0, "feedback_markdown": code_info["error"]}
            
        record["evaluation"] = grade
        results.append(record)
        
        # waiting to stay under the free tier limits
        if i < len(data) - 1:
            time.sleep(delay)
            
    # ensuring output directory exists and saving with human-readable russian text
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)
        
    click.echo(f"done! results saved to {output_path}")

if __name__ == "__main__":
    main()