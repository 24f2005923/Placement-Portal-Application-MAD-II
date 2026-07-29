import os
import time
import logging
from flask import current_app

logger = logging.getLogger(__name__)

def is_allowed_file(file_name):
    """Checks if the uploaded file extension is permitted."""
    allowed_extensions = current_app.config.get('ALLOWED_EXTENSIONS', {'pdf', 'doc', 'docx'})
    _, file_extension = os.path.splitext(file_name)
    if not file_extension:
        return False
    return file_extension[1:].lower() in allowed_extensions

def save_resume(upload_file, student_id):
    """
    Saves an uploaded resume file to the configured uploads folder.
    Returns: (saved_filename, error_message)
    """
    if not upload_file or upload_file.filename == '':
        return None, 'No file selected'

    if not is_allowed_file(upload_file.filename):
        return None, 'Only PDF, DOC, and DOCX files are allowed'

    _, original_extension = os.path.splitext(upload_file.filename)
    extension = original_extension[1:].lower()

    timestamp = int(time.time())
    new_filename = f"resume_{student_id}_{timestamp}.{extension}"
    upload_directory = current_app.config['UPLOAD_FOLDER']

    if not os.path.exists(upload_directory):
        os.makedirs(upload_directory)

    save_path = os.path.join(upload_directory, new_filename)
    upload_file.save(save_path)

    logger.info(f"Resume stored successfully: {new_filename}")
    return new_filename, None

def delete_resume(filename):
    """Deletes a resume file if it exists."""
    if not filename:
        return
        
    upload_directory = current_app.config['UPLOAD_FOLDER']
    target_path = os.path.join(upload_directory, filename)
    
    if os.path.exists(target_path):
        try:
            os.remove(target_path)
            logger.info(f"Resume deleted: {filename}")
        except Exception as e:
            logger.error(f"Failed to delete resume {filename}: {e}")
