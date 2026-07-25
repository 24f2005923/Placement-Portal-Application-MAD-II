import os
import time
from flask import current_app

def is_allowed_file(file_name):
    # Retrieve permitted list
    extensions = current_app.config.get('ALLOWED_EXTENSIONS', {'pdf', 'doc', 'docx'})
    
    # Split out the file extension
    base, ext = os.path.splitext(file_name)
    if not ext:
        return False
        
    cleaned_ext = ext[1:].lower()
    return cleaned_ext in extensions

def save_resume(upload_file, std_id):
    if upload_file is None or upload_file.filename == '':
        return None, 'No file selected'

    if not is_allowed_file(upload_file.filename):
        return None, 'Only PDF, DOC, DOCX files are allowed'

    # Extract extension
    _, original_ext = os.path.splitext(upload_file.filename)
    extension_str = original_ext[1:].lower()

    # Generate custom timestamp-based filename
    curr_time_sec = int(time.time())
    final_filename = f"resume_{std_id}_{curr_time_sec}.{extension_str}"

    upload_dir_path = current_app.config['UPLOAD_FOLDER']

    # Create folder if missing
    if not os.path.exists(upload_dir_path):
        os.makedirs(upload_dir_path)

    full_save_path = os.path.join(upload_dir_path, final_filename)
    upload_file.save(full_save_path)

    print(f"File stored: {final_filename}")

    return final_filename, None

def delete_resume(file_name):
    if not file_name:
        return
        
    upload_dir_path = current_app.config['UPLOAD_FOLDER']
    target_path = os.path.join(upload_dir_path, file_name)
    
    if os.path.exists(target_path):
        os.remove(target_path)

