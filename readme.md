import os
import uuid
import json
from flask import Flask, request, render_template, jsonify, send_file, abort
from werkzeug.utils import secure_filename
from utils.transcribe import transcribe_file
from utils.cleanup import clean_transcript
from utils.summarize import summarize_transcript, build_structured_minutes
from utils.export_utils import export_pdf, export_docx, export_txt

UPLOAD_FOLDER = "uploads"
GENERATED_FOLDER = "generated"
ALLOWED_EXT = {"wav", "mp3", "m4a", "flac"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(GENERATED_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["GENERATED_FOLDER"] = GENERATED_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 200 * 1024 * 1024  # 200MB

# in-memory store for results (simple; for production use DB)
RESULT_STORE = {}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".",1)[1].lower() in ALLOWED_EXT

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return render_template("index.html", error="No file uploaded.")
    file = request.files["file"]
    style = request.form.get("style", "Concise")
    title = request.form.get("title", "")
    date_str = request.form.get("date", "")
    attendees = request.form.get("attendees", "")

    if file.filename == "":
        return render_template("index.html", error="No file selected.")
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        uid = str(uuid.uuid4())
        saved_path = os.path.join(app.config["UPLOAD_FOLDER"], f"{uid}_{filename}")
        file.save(saved_path)

        raw_transcript = transcribe_file(saved_path)
        cleaned = clean_transcript(raw_transcript)
        summary_text = summarize_transcript(cleaned, style=style)
        minutes = build_structured_minutes(cleaned, summary_text,
                                           title=title, date=date_str, attendees=attendees)

        RESULT_STORE[uid] = {
            "transcript": raw_transcript,
            "cleaned": cleaned,
            "summary": summary_text,
            "minutes": minutes
        }

        return render_template("index.html", minutes=minutes, uid=uid)
    return render_template("index.html", error="Invalid file type.")


@app.route("/export/pdf", methods=["GET"])
def export_pdf_route():
    uid = request.args.get("id")
    if not uid or uid not in RESULT_STORE:
        return abort(404, "Result not found")
    minutes = RESULT_STORE[uid]["minutes"]
    out_path = os.path.join(app.config["GENERATED_FOLDER"], f"{uid}.pdf")
    export_pdf(minutes, out_path)
    return send_file(out_path, as_attachment=True, download_name=f"minutes_{uid}.pdf")

@app.route("/export/docx", methods=["GET"])
def export_docx_route():
    uid = request.args.get("id")
    if not uid or uid not in RESULT_STORE:
        return abort(404, "Result not found")
    minutes = RESULT_STORE[uid]["minutes"]
    out_path = os.path.join(app.config["GENERATED_FOLDER"], f"{uid}.docx")
    export_docx(minutes, out_path)
    return send_file(out_path, as_attachment=True, download_name=f"minutes_{uid}.docx")

@app.route("/export/txt", methods=["GET"])
def export_txt_route():
    uid = request.args.get("id")
    if not uid or uid not in RESULT_STORE:
        return abort(404, "Result not found")
    minutes = RESULT_STORE[uid]["minutes"]
    out_path = os.path.join(app.config["GENERATED_FOLDER"], f"{uid}.txt")
    export_txt(minutes, out_path)
    return send_file(out_path, as_attachment=True, download_name=f"minutes_{uid}.txt")

if __name__ == "__main__":
    app.run(debug=True)
