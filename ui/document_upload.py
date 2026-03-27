from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import os
from werkzeug.utils import secure_filename

document_upload_bp = Blueprint("document_upload", __name__, template_folder="../templates")

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "uploads")
ALLOWED_EXTENSIONS = {"pdf", "txt", "doc", "docx"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@document_upload_bp.route("/upload", methods=["GET", "POST"])
def upload_document():
    if "user" not in session:
        flash("Please log in first.")
        return redirect("/")

    if request.method == "POST":
        if "file" not in request.files:
            flash("No file part")
            return redirect(request.url)

        file = request.files["file"]

        if file.filename == "":
            flash("No selected file")
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            flash("File uploaded successfully")
            return redirect(url_for("document_upload.upload_document"))

        flash("File type not allowed")
        return redirect(request.url)

    return render_template("document_upload.html")