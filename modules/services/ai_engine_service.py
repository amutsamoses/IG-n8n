import logging
from typing import Dict
import google.generativeai as genai

logger = logging.getLogger(__name__)


class AIEngine:
    NICHE_KEYWORDS: Dict[str, list] = {
        "business": ["founder", "ceo", "startup"],
        "marketing": ["marketing", "branding"],
        "creator": ["content", "creator"],
        "tech": ["developer", "ai"],
    }

    def __init__(self, api_key: str, default_message: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.0-flash")
        self.default_message = default_message

    def analyze_niche(self, bio: str) -> str:
        if not bio:
            return "default"

        bio = bio.lower()

        for niche, keywords in self.NICHE_KEYWORDS.items():
            if any(keyword in bio for keyword in keywords):
                return niche

        return "default"

    def generate_custom_dm(self, bio: str) -> str:
        niche = self.analyze_niche(bio)

        prompt = (
            f"Bio: {bio}\n"
            f"Niche: {niche}\n"
            f"Write a friendly and concise Instagram DM.\n"
            f"Base context: {self.default_message}"
        )

        try:
            response = self.model.generate_content(prompt)

            if not response or not response.text:
                logger.warning("Empty LLM response. Falling back.")
                return self.default_message

            return response.text.strip()

        except Exception:
            logger.exception("LLM generation failed. Using fallback.")
            return self.default_message
