import google.generativeai as genai
from config import GEMINI_API_KEY, DEFAULT_DM_MESSAGE

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

def analyze_niche(bio):
    if not bio: return "default"
    bio = bio.lower()
    niches = {
        "business": ["founder", "ceo", "startup"],
        "marketing": ["marketing", "branding"],
        "creator": ["content", "creator"],
        "tech": ["developer", "ai"]
    }
    for niche, keywords in niches.items():
        if any(word in bio for word in keywords):
            return niche
    return "default"

def generate_custom_dm(bio):
    try:
        niche = analyze_niche(bio)
        prompt = f"Bio: {bio}\nNiche: {niche}\nWrite a friendly DM based on: {DEFAULT_DM_MESSAGE}"
        response = model.generate_content(prompt)
        return response.text.strip()
    except:
        return DEFAULT_DM_MESSAGE