import os
import logging
from typing import Dict

logger = logging.getLogger(__name__)

class Transcriber:
    """
    Transcriber tries multiple backends in order:
      1) whisper (if installed)
      2) SpeechRecognition with Sphinx (if installed)
      3) fallback: returns a placeholder message
    """

    def __init__(self, model_name: str = "medium", compute_type: str = "float16", language: str = "en"):
        self.model_name = model_name
        self.compute_type = compute_type
        self.language = language

        # Try to import whisper lazily when needed
        self._whisper = None
        try:
            import whisper  # type: ignore
            self._whisper = whisper
            logger.info("whisper library found - will use for transcription if available.")
        except Exception:
            logger.info("whisper not available. Will try SpeechRecognition/Sphinx or fallback.")

        # SpeechRecognition optional
        self._sr = None
        try:
            import speech_recognition as sr  # type: ignore
            self._sr = sr
            logger.info("SpeechRecognition found.")
        except Exception:
            logger.info("SpeechRecognition not available.")

    def transcribe_file(self, filepath: str, language: str = None) -> Dict:
        language = language or self.language
        logger.info(f"Attempting to transcribe: {filepath} (language={language})")

        # 1) whisper if available
        if self._whisper is not None:
            try:
                model = self._whisper.load_model(self.model_name)
                result = model.transcribe(filepath, language=language)
                transcript = result.get("text", "").strip()
                return {"transcript": transcript, "language": language, "segments": result.get("segments", [])}
            except Exception as e:
                logger.exception("whisper transcription failed -- falling back.")

        # 2) speech_recognition with pocketsphinx (offline) or default recognizer
        if self._sr is not None:
            try:
                r = self._sr.Recognizer()
                with self._sr.AudioFile(filepath) as source:
                    audio = r.record(source)
                # try Sphinx first (offline)
                try:
                    text = r.recognize_sphinx(audio, language=language)
                    return {"transcript": text, "language": language, "segments": []}
                except Exception:
                    # fallback to Google Web Speech (requires internet)
                    text = r.recognize_google(audio, language=language)
                    return {"transcript": text, "language": language, "segments": []}
            except Exception:
                logger.exception("SpeechRecognition transcription failed.")

        # 3) fallback: simple placeholder
        logger.warning("No transcription backend available. Returning placeholder transcript.")
        placeholder = (
            "Transcription not available. Please install 'whisper' (recommended) "
            "or 'SpeechRecognition' with a recognizer (pocketsphinx) to enable transcription."
        )
        return {"transcript": placeholder, "language": language, "segments": []}
