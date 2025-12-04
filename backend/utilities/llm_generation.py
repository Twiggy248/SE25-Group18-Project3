import re

def clean_llm_json(json_str: str) -> str:
    """Clean JSON from LLM output"""

    json_str = re.sub(r"^```json\s*", "", json_str.strip())
    json_str = re.sub(r"^```\s*", "", json_str.strip())
    json_str = re.sub(r"\s*```$", "", json_str.strip())

    first_bracket = json_str.find("[")
    if first_bracket > 0:
        json_str = json_str[first_bracket:]

    last_bracket = json_str.rfind("]")
    if last_bracket != -1:
        json_str = json_str[: last_bracket + 1]

    json_str = json_str.replace(r"\"", '"')
    json_str = json_str.replace(r'\\"', '"')
    json_str = json_str.replace("None", "null")
    json_str = json_str.replace("True", "true")
    json_str = json_str.replace("False", "false")
    json_str = re.sub(r",(\s*[}\]])", r"\1", json_str)

    open_braces = json_str.count("{")
    close_braces = json_str.count("}")
    if open_braces > close_braces:
        json_str += "}" * (open_braces - close_braces)

    open_brackets = json_str.count("[")
    close_brackets = json_str.count("]")
    if open_brackets > close_brackets:
        json_str += "]" * (open_brackets - close_brackets)

    return json_str
