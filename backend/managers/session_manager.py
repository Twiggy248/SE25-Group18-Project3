from backend.utilities.llm.hf_llm_util import getPipe
import re
from utilities.key_values import ACTION_VERBS, ACTORS
from utilities.query_generation import session_title_queryGen

pipe = getPipe()

# NOTE: Why is max_length a parameter if it is never passed in?
# NOTE: Why is the use_llm being passed if it is always passed as true by outside functions?
def generate_session_title(first_user_message: str, max_length: int = 50, use_llm: bool = False) -> str:
    """
    Generate a concise, meaningful session title from the first user message.

    Strategy:
    1. Quick extraction for initial loads (use_llm=False)
    2. LLM-based title generation for important views (use_llm=True)
    """
    if not first_user_message:
        return "New Session"

    text = first_user_message.strip()

    # Handle file uploads specially
    if text.startswith("Uploaded document:"):
        filename = text.replace("Uploaded document:", "").strip()
        base_name = filename.rsplit(".", 1)[0] if "." in filename else filename
        clean_name = base_name.replace("_", " ").replace("-", " ").title()
        return (
            clean_name[:max_length]
            if len(clean_name) <= max_length
            else clean_name[: max_length - 3] + "..."
        )

    # For initial loads, use quick keyword extraction
    if not use_llm:
        return generate_fallback_title(text, max_length)

    # For important views, use LLM
    try:
        prompt = session_title_queryGen(text[:300])
        
        outputs = pipe(
            prompt,
            max_new_tokens=30,
            temperature=0.3,
            top_p=0.85,
            do_sample=True,
            return_full_text=False,
        )

        title = outputs[0]["generated_text"].strip()
        title = title.replace("\n", " ").strip().strip("\"'.,;:")

        word_count = len(title.split())
        if 3 <= word_count <= 10 and len(title) <= max_length:
            return title

    except Exception as e:
        print(f"LLM title generation failed: {e}")

    return generate_fallback_title(text, max_length)

def generate_fallback_title(text: str, max_length: int = 50) -> str:
    """
    Fallback method: Extract key concepts and build a title
    Uses simple NLP techniques without LLM
    """

    text_lower = text.lower()

    # Find mentioned verbs and nouns
    found_verbs = [v for v in ACTION_VERBS if v in text_lower]
    found_nouns = [n for n in ACTORS if n in text_lower]

    # Build title from found keywords
    if found_verbs and found_nouns:
        # Format: "User Login And Product Search"
        verb_part = " And ".join([v.title() for v in found_verbs[:2]])
        noun_part = found_nouns[0].title()
        title = f"{noun_part} {verb_part}"

        if len(title) <= max_length:
            return title

    # If keywords don't work, use first meaningful sentence
    sentences = [s.strip() for s in re.split(r"[.!?]+", text) if len(s.strip()) > 10]

    if sentences:
        first_sentence = sentences[0]

        # Remove common prefixes
        prefixes = ["the system should", "the user can", "user can", "system should"]
        for prefix in prefixes:
            if first_sentence.lower().startswith(prefix):
                first_sentence = first_sentence[len(prefix) :].strip()

        # Capitalize and truncate
        first_sentence = first_sentence.capitalize()

        if len(first_sentence) <= max_length:
            return first_sentence

        # Truncate at last complete word
        truncated = first_sentence[:max_length]
        last_space = truncated.rfind(" ")
        if last_space > max_length * 0.6:
            return truncated[:last_space] + "..."
        return truncated + "..."

    # Ultimate fallback
    return "Requirements Session"
