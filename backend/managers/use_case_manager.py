import json
import re
import time
from typing import List
from backend.utilities.llm.hf_llm_util import getTokenizer, getPipe

from use_case.use_case_enrichment import enrich_use_case
from utilities.use_case_utilities import get_smart_max_use_cases, get_smart_token_budget
from utilities.llm_generation import clean_llm_json
from utilities.misc import ensure_string_list
from utilities.key_values import ACTION_VERBS, ACTORS
from utilities.query_generation import uc_batch_extract_queryGen, uc_single_stage_extract_queryGen

tokenizer = getTokenizer()
pipe = getPipe()

"""
use_case_manager.py
Handles any operations (outside of API or Database) that deal with Use Cases
"""

def extract_use_cases_single_stage(text: str, memory_context: str, max_use_cases: int = None) -> List[dict]:
    """
    ROBUST SINGLE-STAGE EXTRACTION
    - Better prompting
    - Robust JSON parsing
    - Quality validation
    """

    # Smart estimation
    if max_use_cases is None:
        max_use_cases = get_smart_max_use_cases(text)

    # Dynamic token budget
    max_new_tokens = get_smart_token_budget(text, max_use_cases)

    # ✅ IMPROVED PROMPT - Clearer, more explicit
    prompt = uc_single_stage_extract_queryGen(max_use_cases, memory_context, text)

    try:

        # Generate with conservative settings
        outputs = pipe(
            prompt,
            max_new_tokens=max_new_tokens,
            temperature=0.3,  # Increase from 0.1 - less rigid
            top_p=0.85,  # Increase from 0.7 - more diverse
            repetition_penalty=1.1,  # Reduce from 1.15 - less restrictive
            do_sample=True,
            return_full_text=False,
            eos_token_id=tokenizer.eos_token_id,
            pad_token_id=tokenizer.eos_token_id,
        )

        response = "[" + outputs[0]["generated_text"].strip()

        # Extract JSON array
        start_idx = response.find("[")
        end_idx = response.rfind("]")

        if start_idx == -1 or end_idx == -1:
            return extract_with_smart_fallback(text)

        json_str = response[start_idx : end_idx + 1]

        # ✅ ROBUST CLEANING
        json_str = clean_llm_json(json_str)

        # Attempt to parse
        try:
            use_cases_raw = json.loads(json_str)

            if not isinstance(use_cases_raw, list):
                return extract_with_smart_fallback(text)

            use_cases = []

            for idx, uc in enumerate(use_cases_raw, 1):
                if not isinstance(uc, dict):
                    continue

                # Validate and structure
                validated_uc = {
                    "title": str(uc.get("title", f"Use Case {idx}")).strip(),
                    "preconditions": ensure_string_list(uc.get("preconditions", [])),
                    "main_flow": ensure_string_list(uc.get("main_flow", [])),
                    "sub_flows": ensure_string_list(uc.get("sub_flows", [])),
                    "alternate_flows": ensure_string_list(
                        uc.get("alternate_flows", [])
                    ),
                    "outcomes": ensure_string_list(uc.get("outcomes", [])),
                    "stakeholders": ensure_string_list(uc.get("stakeholders", [])),
                }

                # Quality check
                title_len = len(validated_uc["title"])
                flow_len = len(validated_uc["main_flow"])

                if title_len < 10:
                    continue

                if flow_len < 3:
                    # Enrich it instead of skipping
                    validated_uc = enrich_use_case(validated_uc, text)

                # Enrich to improve quality
                validated_uc = enrich_use_case(validated_uc, text)
                use_cases.append(validated_uc)

            # Hard limit check
            if len(use_cases) > max_use_cases + 2:
                use_cases = use_cases[:max_use_cases]

            return use_cases

        except json.JSONDecodeError as e:
            return extract_with_smart_fallback(text)

    except Exception as e:
        import traceback

        traceback.print_exc()
        return extract_with_smart_fallback(text)

def extract_use_cases_batch(text: str, memory_context: str, max_use_cases: int) -> List[dict]:
    """
    BATCH EXTRACTION - Extract use cases in small batches for speed
    Optimized for RTX 3050: 3-5x faster than single-stage
    """

    all_use_cases = []
    batch_size = 3  # Extract 3 use cases per batch
    total_batches = (max_use_cases + batch_size - 1) // batch_size

    for batch_num in range(total_batches):
        start_idx = batch_num * batch_size
        remaining = max_use_cases - start_idx
        batch_count = min(batch_size, remaining)

        # Create focused prompt for this batch
        prompt = uc_batch_extract_queryGen(batch_count, memory_context, text)

        # Calculate token budget for this batch
        batch_tokens = batch_count * 150 + 100  # 150 tokens per use case + overhead

        start_time = time.time()

        try:
            # Generate with reduced tokens
            outputs = pipe(
                prompt,
                max_new_tokens=batch_tokens,
                temperature=0.3,
                top_p=0.85,
                repetition_penalty=1.1,
                do_sample=True,
                return_full_text=False,
                eos_token_id=tokenizer.eos_token_id,
                pad_token_id=tokenizer.eos_token_id,
            )

            response = "[" + outputs[0]["generated_text"].strip()

            # Extract JSON
            start_idx = response.find("[")
            end_idx = response.rfind("]")

            if start_idx == -1 or end_idx == -1:
                continue

            json_str = response[start_idx : end_idx + 1]
            json_str = clean_llm_json(json_str)

            # Parse JSON
            try:
                batch_use_cases = json.loads(json_str)

                if not isinstance(batch_use_cases, list):
                    continue

                # Validate and add to results
                for idx, uc in enumerate(batch_use_cases, 1):
                    if not isinstance(uc, dict):
                        continue

                    validated_uc = {
                        "title": str(
                            uc.get("title", f"Use Case {len(all_use_cases) + 1}")
                        ).strip(),
                        "preconditions": ensure_string_list(
                            uc.get("preconditions", [])
                        ),
                        "main_flow": ensure_string_list(uc.get("main_flow", [])),
                        "sub_flows": ensure_string_list(uc.get("sub_flows", [])),
                        "alternate_flows": ensure_string_list(
                            uc.get("alternate_flows", [])
                        ),
                        "outcomes": ensure_string_list(uc.get("outcomes", [])),
                        "stakeholders": ensure_string_list(uc.get("stakeholders", [])),
                    }

                    # Enrich for quality
                    validated_uc = enrich_use_case(validated_uc, text)
                    all_use_cases.append(validated_uc)

            except json.JSONDecodeError as e:
                continue

        except Exception as e:
            import traceback
            traceback.print_exc()
            continue

    return all_use_cases

def extract_with_smart_fallback(text: str) -> List[dict]:
    """
    IMPROVED FALLBACK with better pattern recognition
    """

    use_cases = []
    seen_titles = set()

    # Split into sentences
    sentences = [s.strip() for s in re.split(r"[.!?]+", text) if len(s.strip()) > 20]

    for sentence in sentences:
        sentence_lower = sentence.lower()

        # Pattern 1: "Actor should/can/must verb object"
        # Pattern 2: "Platform/System should let/allow actors verb object"
        # Pattern 3: "Actor verb object" (direct statement)

        for actor in ACTORS:
            # Try multiple patterns
            patterns = [
                # "Users should be able to track"
                rf"\b{actor}\s+(?:should|can|must|may|will|shall|need to|able to)\s+([a-z]+)\s+([^,\.]+)",
                # "Platform should let users find"
                rf"platform\s+should\s+(?:let|allow)\s+{actor}\s+([a-z]+)\s+([^,\.]+)",
                # "Users track their order"
                rf"\b{actor}\s+([a-z]+)\s+(?:the|their|a|an)\s+([^,\.]+)",
            ]

            for pattern in patterns:
                matches = re.findall(pattern, sentence_lower, re.IGNORECASE)

                for match in matches:
                    if len(match) == 2:
                        verb, obj = match
                    else:
                        continue

                    verb = verb.strip()
                    obj = obj.strip()[:80]

                    # Clean object
                    obj = re.sub(
                        r"\s+(and|or|but|if|when|after|before|to|that|which|for now).*$",
                        "",
                        obj,
                    )
                    obj = obj.strip()

                    if len(obj) < 5 or len(obj) > 100:
                        continue

                    # Skip if verb not in our list
                    if verb not in ACTION_VERBS:
                        continue

                    conjugated = ACTION_VERBS[ACTION_VERBS.index(verb)]

                    # Build title
                    title = f"{actor.capitalize()} {conjugated} {obj}"
                    title_key = title.lower().strip()

                    if title_key in seen_titles or len(title) < 15:
                        continue

                    seen_titles.add(title_key)

                    # Build quality use case
                    use_case = {
                        "title": title,
                        "preconditions": [
                            f"{actor.capitalize()} is authenticated and authorized",
                            "System is operational and responsive",
                        ],
                        "main_flow": [
                            f"{actor.capitalize()} navigates to relevant section",
                            f"{actor.capitalize()} initiates {verb} action",
                            "System validates request",
                            f"System processes {obj}",
                            f"System confirms completion to {actor}",
                            f"{actor.capitalize()} receives confirmation",
                        ],
                        "sub_flows": [
                            f"{actor.capitalize()} can view additional details",
                            f"{actor.capitalize()} can customize preferences",
                        ],
                        "alternate_flows": [
                            f"If validation fails: System displays error and prompts correction",
                            f"If system timeout: System retries and notifies {actor}",
                        ],
                        "outcomes": [
                            f"{title} completed successfully",
                            "System state is updated",
                        ],
                        "stakeholders": [actor.capitalize(), "System"],
                    }

                    use_cases.append(use_case)

                    if len(use_cases) >= 15:
                        break

            if len(use_cases) >= 15:
                break

        if len(use_cases) >= 15:
            break
        
    return use_cases

