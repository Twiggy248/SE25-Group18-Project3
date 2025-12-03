import re
from typing import Tuple
from utilities.key_values import ACTION_VERBS, ACTORS
from database.models import UseCaseSchema
from backend.utilities.llm.hf_llm_util import getEmbedder
class UseCaseEstimator:
    """Intelligently estimate number of use cases in requirements text"""

    @staticmethod
    def count_conjunction_actions(text: str) -> int:
        """
        🔥 NEW: Detect compound actions split by 'and'
        Example: "proceeds to checkout and selects payment" = 2 actions
        """
        text_lower = text.lower()
        compound_action_count = 0

        # Split by 'and' and check if both sides have verbs
        and_splits = re.split(r"\band\b", text_lower)

        if len(and_splits) >= 2:
            for split in and_splits:
                # Check if this split contains an action verb
                has_action = any(
                    verb in split for verb in ACTION_VERBS
                )
                if has_action:
                    compound_action_count += 1

        return max(1, compound_action_count)

    @staticmethod
    def estimate_use_cases(text: str) -> Tuple[int, int, dict]:
        """
        Estimate number of use cases in text

        Returns:
            (min_estimate, max_estimate, analysis_details)
        """

        text_lower = text.lower()
        char_count = len(text)

        # Count sentences
        sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]
        sentence_count = len(sentences)

        # FIXED: Count action verbs (each UNIQUE verb = potential use case)
        action_count = 0
        found_actions = set()

        for verb in ACTION_VERBS:
            # Look for verb patterns
            patterns = [
                rf"\b(?:can|should|must|may|will|shall)\s+{verb}\b",
                rf"\b{verb}(?:s|ed|ing)?\b",  # matches: cancel, cancels, cancelled, canceling
            ]

            # Check if ANY pattern matches (don't count duplicates!)
            verb_found = False
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    verb_found = True
                    break

            if verb_found:
                found_actions.add(verb)
                action_count += 1  # Count only ONCE per unique verb

        unique_actions = len(found_actions)
        conjunction_action_count = UseCaseEstimator.count_conjunction_actions(text)
        # Count actors mentioned
        actor_count = sum(1 for actor in ACTORS if actor in text_lower)

        # Count conjunctions that separate actions ("and", "or")
        conjunction_splits = len(re.findall(r"\b(?:and|or)\b", text_lower))

        # Count bullet points or numbered lists (each = potential use case)
        bullet_patterns = [
            r"^\s*[-*•]\s+",
            r"^\s*\d+\.\s+",
        ]
        list_items = 0
        for line in text.split("\n"):
            for pattern in bullet_patterns:
                if re.match(pattern, line):
                    list_items += 1
                    break

        # Analysis details
        details = {
            "char_count": char_count,
            "sentence_count": sentence_count,
            "action_verb_count": action_count,
            "unique_actions": unique_actions,
            "found_actions": list(found_actions),
            "conjunction_action_count": conjunction_action_count,
            "actor_count": actor_count,
            "conjunction_splits": conjunction_splits,
            "list_items": list_items,
        }

        # Calculate estimates using multiple heuristics
        estimates = []

        # Heuristic 1: Based on action verbs (most reliable)
        if action_count > 0:
            # FIXED: For very short text, use EXACT unique action count
            if char_count < 150 and conjunction_action_count > unique_actions:
                verb_estimate = conjunction_action_count
            elif char_count < 100:
                verb_estimate = unique_actions
            else:
                # For longer text, use dampened approach
                verb_estimate = min(unique_actions * 1.5, action_count * 0.8)
            estimates.append(int(verb_estimate))

        # Heuristic 2: Based on list items (if structured)
        if list_items > 0:
            estimates.append(list_items)

        # Heuristic 3: Based on sentences (conservative)
        sentences_with_actions = 0
        for sentence in sentences:
            sentence_lower = sentence.lower()
            has_action = any(
                verb in sentence_lower for verb in ACTION_VERBS
            )
            has_actor = any(
                actor in sentence_lower for actor in ACTORS
            )
            if has_action or has_actor:
                sentences_with_actions += 1

        if sentences_with_actions > 0:
            estimates.append(int(sentences_with_actions * 0.6))

        # Heuristic 4: Based on character count (fallback)
        char_based = max(1, char_count // 150)
        estimates.append(char_based)

        # Calculate min and max
        if estimates:
            min_estimate = min(estimates)
            max_estimate = max(estimates)
        else:
            min_estimate = 1
            max_estimate = 3

        # Apply sensible bounds
        min_estimate = max(1, min_estimate)  # FIXED: At least 1 (not 2)
        max_estimate = min(20, max_estimate)

        # Adjust based on text size
        if char_count < 100:
            max_estimate = min(max_estimate, 2)
        elif char_count < 500:
            max_estimate = min(max_estimate, 5)

        details["estimates"] = estimates
        details["sentences_with_actions"] = sentences_with_actions

        return min_estimate, max_estimate, details

def get_smart_max_use_cases(text: str) -> int:
    """
    Get intelligent estimate for max_use_cases parameter
    FIXED: Adaptive minimum based on text size
    """

    min_est, max_est, details = UseCaseEstimator.estimate_use_cases(text)

    print(f"\n{'='*80}")
    print(f"🧠 SMART USE CASE ESTIMATION")
    print(f"{'='*80}")
    print(
        f"Input: {details['char_count']} chars, {details['sentence_count']} sentences"
    )
    print(f"\nAnalysis:")
    print(f"  • Action verbs found: {details['action_verb_count']}")
    if details["found_actions"]:
        actions_preview = ", ".join(list(details["found_actions"])[:8])
        if len(details["found_actions"]) > 8:
            actions_preview += f", +{len(details['found_actions']) - 8} more"
        print(f"    Actions: {actions_preview}")
    print(f"  • Unique actions: {details['unique_actions']}")
    if details["conjunction_action_count"] > 1:
        print(
            f"  • Compound actions detected: {details['conjunction_action_count']} (split by 'and')"
        )
    print(f"  • Actors mentioned: {details['actor_count']}")
    if details["list_items"] > 0:
        print(f"  • List items: {details['list_items']}")
    if "sentences_with_actions" in details:
        print(f"  • Sentences with actions: {details['sentences_with_actions']}")

    print(f"\n📊 Raw estimate: {min_est}-{max_est} use cases")

    # Improved logic based on text characteristics
    char_count = details["char_count"]
    unique_actions = details["unique_actions"]
    conjunction_actions = details["conjunction_action_count"]

    # 🔥 FIXED: Prioritize conjunction detection for short compound text
    if char_count < 150 and conjunction_actions >= 2:
        smart_max = conjunction_actions
        print(
            f"   Based on {conjunction_actions} compound actions (detected 'and' separator)"
        )
    # For long descriptive text (>2000 chars), be more generous
    elif char_count > 2000:
        smart_max = max_est
        print(f"   Long text detected ({char_count} chars) - using upper estimate")
    elif unique_actions > 0:
        # For normal text, use unique actions with multiplier
        smart_max = min(int(unique_actions * 1.5), max_est)
        print(f"   Based on {unique_actions} unique actions")
    else:
        # Fallback to minimum
        smart_max = min_est
        print(f"   Using minimum estimate (no clear actions detected)")

    # Apply size-based caps
    if char_count < 150 and conjunction_actions >= 2:
        smart_max = max(smart_max, conjunction_actions)
    elif char_count < 100:
        smart_max = min(smart_max, 2)
    elif char_count < 500:
        smart_max = min(smart_max, 5)
    elif char_count < 2000:
        smart_max = min(smart_max, 10)
    else:
        smart_max = min(smart_max, 20)

    # FIXED: Adaptive minimum based on text size and action count
    if char_count < 50 and unique_actions <= 1:
        # Very short text with single action: allow exactly 1
        smart_max = max(1, smart_max)
        print(f"   Single action detected - allowing 1 use case")
    elif char_count < 200:
        # Short text: minimum 1 use case
        smart_max = max(1, smart_max)
    else:
        # Longer text: minimum 2 use cases (might have implicit requirements)
        smart_max = max(2, smart_max)

    smart_max = min(smart_max, 20)  # Max 20

    print(f"✅ Final estimate: {smart_max} use cases")
    print(f"{'='*80}\n")

    return smart_max

def get_smart_token_budget(text: str, estimated_use_cases: int) -> int:
    """Calculate appropriate token budget based on estimated use cases"""

    base_tokens = estimated_use_cases * 120
    overhead = 80
    token_budget = base_tokens + overhead
    token_budget = max(300, min(token_budget, 1200))

    print(
        f"💰 Token budget: {token_budget} tokens ({estimated_use_cases} use cases × 120 + overhead)\n"
    )

    return token_budget

def flatten_use_case(data: dict) -> dict:
    """Convert nested use case data to flat structure"""
    flat = {"title": data.get("title", "Untitled")}

    def ensure_list(value, placeholder=None):
        if isinstance(value, list):
            return [str(v) if not isinstance(v, str) else v for v in value] or (
                [placeholder] if placeholder else []
            )
        elif isinstance(value, dict):
            return [f"{k}: {v}" for k, v in value.items()] or (
                [placeholder] if placeholder else []
            )
        elif value:
            return [str(value)]
        return [placeholder] if placeholder else []

    flat["preconditions"] = ensure_list(
        data.get("preconditions"), "User is authenticated"
    )
    flat["main_flow"] = ensure_list(data.get("main_flow"), "Action performed")
    flat["sub_flows"] = ensure_list(
        data.get("sub_flows"), "Optional features available"
    )
    flat["alternate_flows"] = ensure_list(
        data.get("alternate_flows"), "Error handling included"
    )
    flat["outcomes"] = ensure_list(data.get("outcomes"), "Task completed successfully")
    flat["stakeholders"] = ensure_list(data.get("stakeholders"), "User")

    return flat


def compute_usecase_embedding(use_case: UseCaseSchema):
    """Combine title and main_flow into embedding vector"""
    text = use_case.title + " " + " ".join(use_case.main_flow)
    embedder = getEmbedder()
    return embedder.encode(text, convert_to_tensor=True)