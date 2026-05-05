import io
import json
import logging
import re
from pathlib import Path
from typing import List, Dict, Any, Set
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2.credentials import Credentials

# logging configuration
logger = logging.getLogger(__name__)

class ClassroomExtractor:
    """logic for fetching submissions, downloading files, and generating manifests."""
    
    def __init__(
        self, 
        creds: Credentials, 
        staging_dir: Path, 
        allowed_extensions: Set[str]
    ):
        self.classroom_service = build("classroom", "v1", credentials=creds)
        self.drive_service = build("drive", "v3", credentials=creds)
        self.staging_dir = staging_dir
        self.allowed_extensions = {ext.lower() for ext in allowed_extensions}

    def _get_student_map(self, course_id: str) -> Dict[str, str]:
        """fetches the student roster to map user ids to full names."""
        student_map = {}
        page_token = None
        
        logger.info(f"fetching roster for course {course_id}")
        while True:
            response = self.classroom_service.courses().students().list(
                courseId=course_id, 
                pageToken=page_token
            ).execute()
            
            for student in response.get("students", []):
                user_id = student.get("userId")
                profile = student.get("profile", {})
                full_name = profile.get("name", {}).get("fullName", "unknown_student")
                student_map[user_id] = full_name
                
            page_token = response.get("nextPageToken")
            if not page_token:
                break
        return student_map
        
    def _get_assignment_title(self, course_id: str, coursework_id: str) -> str:
        """fetches the human-readable title of the assignment."""
        try:
            coursework_meta = self.classroom_service.courses().courseWork().get(
                courseId=course_id, 
                id=coursework_id
            ).execute()
            return coursework_meta.get("title", f"assignment_{coursework_id}")
        except Exception as e:
            logger.warning(f"could not fetch assignment title: {e}")
            return f"assignment_{coursework_id}"

    def _slugify(self, text: str) -> str:
        """removes special characters from names for filesystem safety."""
        return re.sub(r"[^\w\s-]", "", text).strip().replace(" ", "_")

    def fetch_submissions(self, course_id: str, coursework_id: str) -> List[Dict[str, Any]]:
        """retrieves all student submissions for a specific coursework item."""
        submissions = []
        page_token = None
        
        while True:
            response = self.classroom_service.courses().courseWork().studentSubmissions().list(
                courseId=course_id,
                courseWorkId=coursework_id,
                pageToken=page_token
            ).execute()
            
            submissions.extend(response.get("studentSubmissions", []))
            page_token = response.get("nextPageToken")
            if not page_token:
                break
                
        return submissions

    def download_attachment(self, file_id: str, file_name: str, target_dir: Path) -> Path:
        """downloads a single file from google drive to the target directory."""
        request = self.drive_service.files().get_media(fileId=file_id)
        file_path = target_dir / file_name
        
        with io.FileIO(str(file_path), "wb") as fh:
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
                
        return file_path

    def process_assignment(self, course_id: str, coursework_id: str, manifest_path: Path) -> Path:
        """orchestrates roster fetching, file downloads, and manifest generation."""
        # fetching the assignment title
        assignment_title = self._get_assignment_title(course_id, coursework_id)
        logger.info(f"processing assignment: {assignment_title}")
        
        # creating dynamic staging directory based on title
        safe_title = self._slugify(assignment_title)
        assignment_staging_dir = self.staging_dir / safe_title
        assignment_staging_dir.mkdir(parents=True, exist_ok=True)
        
        # building the student name cache
        student_map = self._get_student_map(course_id)
        
        # retrieving submissions
        submissions = self.fetch_submissions(course_id, coursework_id)
        manifest = []
        
        for sub in submissions:
            user_id = sub.get("userId")
            student_name = student_map.get(user_id, "unknown")
            submission_state = sub.get("state")
            attachments = sub.get("assignmentSubmission", {}).get("attachments", [])
            
            for attachment in attachments:
                if "driveFile" not in attachment:
                    continue
                    
                drive_file = attachment["driveFile"]
                file_id = drive_file.get("id")
                original_title = drive_file.get("title", "")
                ext = Path(original_title).suffix.lower()
                
                if ext in self.allowed_extensions:
                    # generating a safe and descriptive filename
                    safe_name = self._slugify(student_name)
                    standardized_name = f"{safe_name}_{user_id}_{coursework_id}{ext}"
                    
                    try:
                        local_path = self.download_attachment(file_id, standardized_name, assignment_staging_dir)
                        
                        # building manifest with absolute paths
                        manifest.append({
                            "student_name": student_name,
                            "user_id": user_id,
                            "coursework_id": coursework_id,
                            "assignment_title": assignment_title,
                            "attachment_id": file_id,
                            "submission_state": submission_state,
                            "original_filename": original_title,
                            "local_path": str(local_path.absolute())
                        })
                        logger.info(f"downloaded: {standardized_name}")
                    except Exception as e:
                        logger.error(f"error processing {file_id} for {student_name}: {e}")
        
        # ensuring parent directory for manifest exists
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        
        # ensure_ascii=False guarantees cyrillic names stay readable
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=4, ensure_ascii=False)
            
        return manifest_path