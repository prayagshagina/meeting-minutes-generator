import re
import logging

logger = logging.getLogger(__name__)

class Cleaner:
    """
    Minimal text cleaning:
      - remove filler words (uh, um, you know, like)
      - collapse multiple spaces/newlines
      - basic punctuation fixes
    """

    FILLERS = [
        r"\buh\b", r"\bum\b", r"\byou know\b", r"\blike\b", r"\bI mean\b",
        r"\bso\b", r"\bokay\b", r"\bright\b", r"\bmhm\b"
    ]

    def __init__(self):
        self.filler_pattern = re.compile("|".join(self.FILLERS), flags=re.IGNORECASE)

    def clean_text(self, text: str) -> str:
        if not text:
            return ""
        t = text.strip()
        # remove filler words
        t = self.filler_pattern.sub("", t)
        # remove repeated punctuation
        t = re.sub(r"([!.?]){2,}", r"\1", t)
        # collapse whitespace
        t = re.sub(r"\s{2,}", " ", t)
        # normalize newlines to single
        t = re.sub(r"\n{2,}", "\n", t)
        return t.strip()
