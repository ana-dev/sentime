import os

from werkzeug.utils import secure_filename

from models import db, File

filepath = "/home/nastya/ftp_files/{id}{ext}"


def get(file_id):
    file = db.session.query(File).get(file_id)  # type: File
    if file is None:
        raise ValueError("No file found by id {0}".format(file_id))
    return file


def save(file, filestream):
    full_filename = secure_filename(filestream.filename)
    file.name = full_filename
    file.mimetype = filestream.content_type
    db.session.add(file)
    db.session.flush()

    filename, file_extension = os.path.splitext(full_filename)
    full_path = filepath.format(id=file.id, ext=file_extension)
    filestream.save(full_path)
    file.path = full_path

    db.session.commit()
    return file
