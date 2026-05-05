import click
import logging
import sys
from pathlib import Path
from .auth import GoogleAuthManager
from .extract import ClassroomExtractor

# standard logging format
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

@click.command()
@click.option("--course-id", required=True, default="845870833845", help="google classroom course id")
@click.option("--coursework-id", required=True, help="google classroom coursework id")
# file system paths
@click.option(
    "--staging-dir", 
    type=click.Path(path_type=Path),
    default=Path("./data/submissions"), 
    help="base directory for downloads. creates a subfolder based on assignment title."
)
@click.option(
    "--manifest-path", 
    type=click.Path(path_type=Path), 
    default=None, 
    help="path for the generated manifest."
)
@click.option(
    "--credentials", 
    "creds_path",
    type=click.Path(exists=True, path_type=Path), 
    default="secrets/credentials.json", 
    help="path to the google cloud credentials json"
)
@click.option(
    "--token", 
    "token_path",
    type=click.Path(path_type=Path), 
    default="secrets/token.json", 
    help="path to store or read the oauth2 token"
)
@click.option(
    "--ext", 
    "extensions", 
    multiple=True, 
    default=[".py", ".sql", ".txt", ".pdf"], 
    help="allowed extensions, e.g. --ext .pdf"
)
def main(course_id, coursework_id, staging_dir, manifest_path, creds_path, token_path, extensions):
    """cli entry point for the google classroom ingestion pipeline."""
    
    # dynamically resolving manifest path based on coursework_id
    if manifest_path is None:
        manifest_path = Path(f"./data/manifests/manifest_{coursework_id}.json")
    
    # initializing authentication
    auth_manager = GoogleAuthManager(
        credentials_path=creds_path,
        token_path=token_path
    )
    
    try:
        credentials = auth_manager.get_credentials()
        
        # initializing extractor
        extractor = ClassroomExtractor(
            creds=credentials,
            staging_dir=staging_dir,
            allowed_extensions=set(extensions)
        )
        
        click.echo(f"processing ingestion for course {course_id}")
        final_manifest = extractor.process_assignment(course_id, coursework_id, manifest_path)
        click.echo(f"success. manifest generated at {final_manifest}")
        
    except Exception as e:
        logging.error(f"critical failure: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()