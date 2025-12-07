import json
from typing import List

def ensure_string_list(value) -> List[str]:
    """Safely convert any value to list of strings"""
    if isinstance(value, list):
        result = []
        for item in value:
            if isinstance(item, str):
                result.append(item)
            elif isinstance(item, (list, tuple)):
                result.extend([str(x) for x in item])
            elif isinstance(item, dict):
                result.append(json.dumps(item))
            elif item:
                result.append(str(item))
        return result
    elif isinstance(value, str):
        return [value] if value.strip() else []
    elif value:
        return [str(value)]
    return []
