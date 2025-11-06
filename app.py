import os
import uuid
import datetime
import logging
from flask import Flask, request, render_template, send_from_directory

from werkzeug.utils import secure_filename

# local utilities
from utils.transcription import Transcriber
from utils.cleaning import Cleaner
from utils.summarizer import Summarizer
from utils.export_utils import Exporter

# Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
EXPORTS_DIR = os.path.join(BASE_DIR, "outputs", "exports")
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(EXPORTS_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {"wav", "mp3", "m4a", "ogg", "flac", "aac"}

# Flask app
app = Flask(__name__, template_folder="templates", static_folder="static")

# Initialize components
transcriber = Transcriber()            # tries whisper -> speech_recognition -> placeholder
cleaner = Cleaner()
summarizer = Summarizer()              # tries OpenAI -> basic heuristic
exporter = Exporter(EXPORTS_DIR)       # always creates TXT; PDF/DOCX optional

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    if "audio" not in request.files:
        return render_template("error.html", message="No audio file in request.")
    file = request.files["audio"]
    if file.filename == "":
        return render_template("error.html", message="No file selected.")
    if not allowed_file(file.filename):
        return render_template("error.html", message="Unsupported file type.")

    filename = secure_filename(file.filename)
    uid = uuid.uuid4().hex
    saved_name = f"{uid}_{filename}"
    saved_path = os.path.join(UPLOAD_DIR, saved_name)
    file.save(saved_path)
    logger.info(f"Saved uploaded file to {saved_path}")

    try:
        # 1) Transcribe
        trans_result = transcriber.transcribe_file(saved_path)
        raw_transcript = trans_result.get("transcript", "")
        language = trans_result.get("language", "unknown")

        # 2) Clean
        cleaned = cleaner.clean_text(raw_transcript)

        # 3) Summarize / Structure
        structured = summarizer.summarize_and_structure(cleaned)

        # 4) Export (TXT always; PDF/DOCX if libs are available)
        title = request.form.get("title", f"Meeting-{datetime.date.today().isoformat()}")
        date_str = request.form.get("date", datetime.date.today().isoformat())
        export_base = f"{uid}_minutes"
        txt_file = exporter.export_txt(export_base, title, date_str, structured, cleaned)
        pdf_file = exporter.export_pdf(export_base, title, date_str, structured, cleaned)  # may return None
        docx_file = exporter.export_docx(export_base, title, date_str, structured, cleaned)  # may return None

        return render_template(
            "result.html",
            title=title,
            summary=structured.get("summary", ""),
            key_points=structured.get("key_points", []),
            action_items=structured.get("action_items", []),
            deadlines=structured.get("deadlines", []),
            transcript=cleaned,
            txt_file=os.path.basename(txt_file) if txt_file else None,
            pdf_file=os.path.basename(pdf_file) if pdf_file else None,
            docx_file=os.path.basename(docx_file) if docx_file else None,
            language=language
        )
    except Exception as e:
        logger.exception("Error during processing")
        return render_template("error.html", message=str(e))

@app.route("/export")
def export():
    filename = request.args.get("file")
    if not filename:
        return "Missing file parameter", 400
    path = os.path.join(EXPORTS_DIR, filename)
    if not os.path.exists(path):
        return "File not found", 404
    return send_from_directory(EXPORTS_DIR, filename, as_attachment=True)

if __name__ == "__main__":
    # Use debug=False in production. For development set debug=True
    app.run(host="0.0.0.0", port=5000, debug=True)
