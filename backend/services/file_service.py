import os
import time
from flask import current_app


# check if the uploaded file has an allowed extension
def is_allowed_file(filename):
    allowed = current_app.config.get('ALLOWED_EXTENSIONS', {'pdf', 'doc', 'docx'})
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in allowed


# save the resume file to the uploads folder
def save_resume(file, student_id):
    if not file or file.filename == '':
        return None, 'No file selected'

    if not is_allowed_file(file.filename):
        return None, 'Only PDF, DOC, DOCX files are allowed'

    # get file extension from original filename
    file_ext = file.filename.rsplit('.', 1)[1].lower()

    # use timestamp to make the filename unique for each upload
    timestamp = int(time.time())
    saved_name = 'resume_' + str(student_id) + '_' + str(timestamp) + '.' + file_ext

    upload_folder = current_app.config['UPLOAD_FOLDER']

    # create upload folder if it doesn't exist
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    save_path = os.path.join(upload_folder, saved_name)
    file.save(save_path)

    print('Resume saved:', saved_name)  # debug

    return saved_name, None


# delete old resume when student uploads a new one
def delete_resume(filename):
    if not filename:
        return
    upload_folder = current_app.config['UPLOAD_FOLDER']
    file_path = os.path.join(upload_folder, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
