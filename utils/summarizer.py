import os
import logging
import re
from typing import Dict, List

logger = logging.getLogger(__name__)

class Summarizer:
    """
    Summarizer tries OpenAI if openai package and API key are available,
    otherwise uses a simple heuristic summarizer.
    """

    def __init__(self, openai_model: str = "gpt-3.5-turbo"):
        self.model = openai_model
        self._openai = None
        try:
            import openai  # type: ignore
            self._openai = openai
            logger.info("openai library found - will attempt to use OpenAI for summarization if API key is configured.")
        except Exception:
            logger.info("openai library not available. Using internal heuristic summarizer.")

    def _heuristic_summary(self, text: str) -> Dict:
        # Split into sentences
        sentences = re.split(r'(?<=[.!?])\s+', text.strip())
        # summary: first 2-4 sentences (or whole text if short)
        summary = " ".join(sentences[:3]).strip()
        if not summary:
            summary = text[:500].strip()

        # key points: choose top 5 longest sentences (naive)
        ss = sorted([s.strip() for s in sentences if s.strip()], key=lambda s: -len(s))
        key_points = ss[:5]

        # action items: sentences containing verbs suggesting tasks
        action_keywords = ["action", "todo", "to do", "will", "should", "assign", "need to", "please", "follow up"]
        action_items = [s for s in sentences if any(k in s.lower() for k in action_keywords)]
        action_items = [a.strip() for a in action_items if a.strip()]

        # deadlines: look for date-like patterns or 'by <date/period>'
        deadlines = []
        # simple date patterns dd/mm/yyyy or yyyy-mm-dd or 'by Friday', 'by June'
        date_pat = re.compile(r'\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}-\d{1,2}-\d{1,2}|by\s+\w+)\b', flags=re.IGNORECASE)
        for s in sentences:
            if date_pat.search(s):
                deadlines.append(s.strip())

        return {
            "summary": summary,
            "key_points": key_points,
            "action_items": action_items,
            "deadlines": deadlines
        }

    def summarize_and_structure(self, text: str) -> Dict:
        if not text or text.strip() == "":
            return {"summary": "", "key_points": [], "action_items": [], "deadlines": []}

        # Attempt OpenAI if available and key present
        if self._openai is not None and os.getenv("OPENAI_API_KEY"):
            try:
                # Use a lightweight prompt to get structured JSON output
                prompt = (
                    "You are given a meeting transcript. Produce a JSON object with keys: "
                    "\"summary\" (short paragraph), \"key_points\" (array of short bullets), "
                    "\"action_items\" (array of tasks), and \"deadlines\" (array). Transcript:\n\n"
                    + text[:30000]  # keep length safe
                )
                resp = self._openai.ChatCompletion.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=800,
                    temperature=0.2,
                )
                content = resp.choices[0].message.get("content", "")
                # try to find JSON inside model output
                import json
                m = re.search(r'(\{[\s\S]*\})', content)
                if m:
                    parsed = json.loads(m.group(1))
                    # normalize structure
                    return {
                        "summary": parsed.get("summary", "") if isinstance(parsed.get("summary", ""), str) else str(parsed.get("summary", "")),
                        "key_points": parsed.get("key_points", []) if isinstance(parsed.get("key_points", []), list) else [],
                        "action_items": parsed.get("action_items", []) if isinstance(parsed.get("action_items", []), list) else [],
                        "deadlines": parsed.get("deadlines", []) if isinstance(parsed.get("deadlines", []), list) else [],
                    }
            except Exception:
                logger.exception("OpenAI summarization failed - falling back to heuristic method.")

        return self._heuristic_summary(text)
