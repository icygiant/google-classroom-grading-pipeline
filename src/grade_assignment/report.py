import json
import click
import re
from pathlib import Path

def strip_markdown(text: str) -> str:
    """removes basic markdown formatting like headers and bold text."""
    text = re.sub(r'#+\s*', '', text)
    text = re.sub(r'\*+', '', text)
    text = re.sub(r'^\s*[\*\-]\s+', '- ', text, flags=re.MULTILINE)
    return text.strip()

@click.command()
@click.option("--coursework-id", required=True, help="google classroom coursework id")
def main(coursework_id):
    """parses results, prints to terminal, and exports a clean txt file."""
    
    input_path = Path(f"./grades/grade_report_{coursework_id}.json")
    export_path = Path(f"./grades/feedback_export_{coursework_id}.txt")
    
    try:
        if not input_path.exists():
            click.echo(f"error: result file not found at {input_path}")
            click.echo("please run the grader pipeline first.")
            return
            
        with open(input_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        if not data:
            click.echo("the json file is empty.")
            return

        # grabbing the title from the first record, defaulting to the id if missing
        main_title = data[0].get("assignment_title", f"задание {coursework_id}")
        
        report_buffer = []
        separator = "=" * 40
        
        # adding a master header to the top of the text file
        report_buffer.append(f"Отчет по заданию: {main_title}")
        report_buffer.append(f"Количество работ: {len(data)}")
        report_buffer.append(separator + "\n")

        for record in data:
            name = record.get("student_name", "неизвестно")
            score = record.get("evaluation", {}).get("suggested_score", 0)
            raw_feedback = record.get("evaluation", {}).get("feedback_markdown", "")
            assignment_title = record.get("assignment_title", main_title)
            
            clean_feedback = strip_markdown(raw_feedback)
            
            # formatting the student entry with the assignment title included
            entry = (
                f"задание: {assignment_title}\n"
                f"студент: {name}\n"
                f"балл: {score}/100\n"
                f"комментарий:\n{clean_feedback}\n"
                f"{separator}\n"
            )
            report_buffer.append(entry)

            # terminal output update
            click.secho(f"\nстудент: {name}", fg="cyan", bold=True)
            click.echo(f"задание: {assignment_title}")
            click.echo(f"балл: {score}")
            click.echo(clean_feedback)

        export_path.parent.mkdir(parents=True, exist_ok=True)
        with open(export_path, "w", encoding="utf-8") as f:
            f.write("\n".join(report_buffer))
            
        click.echo(f"\nsuccess. clean export saved to: {export_path}")

    except Exception as e:
        click.echo(f"ошибка: {e}")

if __name__ == "__main__":
    main()