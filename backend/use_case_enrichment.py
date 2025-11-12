# -----------------------------------------------------------------------------
# File: use_case_enrichment.py
# Description: Use case enrichment and merging utilities - post-processes 
#              extracted use cases to improve quality and remove duplicates.
# Author: Pradyumna Chacham
# Date: November 2025
# Copyright (c) 2025 Pradyumna Chacham. All rights reserved.
# License: MIT License - see LICENSE file in the root directory.
# -----------------------------------------------------------------------------

"""
Use Case Enrichment and Merging
Post-processes extracted use cases to improve quality
"""

import re
from typing import Dict, List


async def enrich_use_cases(use_cases: list) -> list:
    """
    Enrich multiple use cases with additional context.

    Args:
        use_cases: List of use cases to enrich

    Returns:
        List of enriched use cases
    """
    enriched = []
    for uc in use_cases:
        enriched.append(enrich_use_case(uc, ""))
    return enriched


def enrich_use_case(use_case: dict, original_text: str) -> dict:
    """
    ENHANCED enrichment - ensures high quality scores
    Fills in missing fields with intelligent defaults
    """
    enriched = use_case.copy()

    # ===== TITLE QUALITY =====
    title = enriched.get("title", "")

    # Ensure title follows "Actor Verb Object" pattern
    if len(title.split()) < 3:
        # Try to extract actor from stakeholders
        stakeholders = enriched.get("stakeholders", [])
        if stakeholders and isinstance(stakeholders, list):
            actor = stakeholders[0] if stakeholders[0] != "System" else "User"
            # Keep existing title but prepend actor
            enriched["title"] = f"{actor} {title}"

    # ===== PRECONDITIONS ENRICHMENT =====
    preconditions = enriched.get("preconditions", [])

    if not preconditions or len(preconditions) < 2:
        # Add intelligent defaults
        default_preconditions = [
            "User is authenticated and authorized",
            "System is operational and available",
            "Required data and services are accessible",
        ]

        # Merge with existing
        existing = set([str(p).lower() for p in preconditions if p])
        enriched["preconditions"] = []

        for default in default_preconditions:
            if default.lower() not in existing:
                enriched["preconditions"].append(default)
                if len(enriched["preconditions"]) >= 2:
                    break

        # Add back originals
        enriched["preconditions"].extend([p for p in preconditions if p])

    # ===== MAIN FLOW ENRICHMENT =====
    main_flow = enriched.get("main_flow", [])

    if not main_flow or len(main_flow) < 4:
        # Build a complete flow based on title
        title_lower = title.lower()

        # Extract action from title
        action_verbs = [
            "view",
            "search",
            "add",
            "create",
            "update",
            "delete",
            "download",
            "upload",
            "login",
            "register",
            "pay",
            "submit",
            "confirm",
            "verify",
            "select",
            "filter",
            "manage",
            "configure",
        ]

        action = next(
            (verb for verb in action_verbs if verb in title_lower), "perform action"
        )

        # Extract actor (first word usually)
        actor = title.split()[0] if title else "User"

        # Build comprehensive flow
        comprehensive_flow = [
            f"{actor} navigates to the relevant section",
            f"{actor} initiates {action} operation",
            "System validates the request and user permissions",
            f"System processes the {action} request",
            "System updates relevant data and logs the action",
            "System confirms successful completion",
            f"{actor} receives confirmation message",
        ]

        # Merge with existing flow
        if main_flow:
            # Keep existing and append missing
            enriched["main_flow"] = main_flow.copy()
            for step in comprehensive_flow:
                if len(enriched["main_flow"]) >= 5:
                    break
                # Check if similar step already exists
                if not any(
                    step.lower()[:20] in str(existing).lower()[:20]
                    for existing in enriched["main_flow"]
                ):
                    enriched["main_flow"].append(step)
        else:
            enriched["main_flow"] = comprehensive_flow[:6]

    # ===== SUB FLOWS ENRICHMENT =====
    sub_flows = enriched.get("sub_flows", [])

    if not sub_flows or len(sub_flows) < 2:
        # Extract from original text
        optional_features = extract_optional_features(original_text, title)

        if optional_features:
            enriched["sub_flows"] = optional_features
        else:
            # Generic but reasonable sub-flows
            actor = title.split()[0] if title else "User"
            enriched["sub_flows"] = [
                f"{actor} can view additional details and information",
                f"{actor} can customize settings and preferences",
                f"{actor} can save work and return later",
            ]

    # ===== ALTERNATE FLOWS ENRICHMENT =====
    alternate_flows = enriched.get("alternate_flows", [])

    if not alternate_flows or len(alternate_flows) < 2:
        # Extract from original text
        error_cases = extract_error_cases(original_text, title)

        if error_cases:
            enriched["alternate_flows"] = error_cases
        else:
            # Comprehensive error handling
            actor = title.split()[0] if title else "User"
            enriched["alternate_flows"] = [
                f"If validation fails: System displays specific error message and prompts {actor} to correct input",
                f"If system timeout: System retries operation automatically and notifies {actor}",
                f"If {actor} lacks required permissions: System denies access and logs attempt",
                "If network error: System caches request and retries when connection is restored",
            ]

    # ===== OUTCOMES ENRICHMENT =====
    outcomes = enriched.get("outcomes", [])

    if not outcomes or len(outcomes) < 1:
        # Infer from title
        enriched["outcomes"] = [
            f"{title} is completed successfully",
            "System state is updated appropriately",
            "All changes are logged for audit purposes",
        ]

    # ===== STAKEHOLDERS ENRICHMENT =====
    stakeholders = enriched.get("stakeholders", [])

    if not stakeholders or len(stakeholders) < 2:
        # Extract actor from title
        actor = title.split()[0] if title else "User"

        # Build stakeholder list
        default_stakeholders = [actor, "System", "Database"]

        # Add specific ones based on content
        if "admin" in title.lower() or "manage" in title.lower():
            default_stakeholders.append("Administrator")
        if "pay" in title.lower() or "purchase" in title.lower():
            default_stakeholders.extend(["Payment Gateway", "Financial System"])
        if "email" in title.lower() or "notification" in title.lower():
            default_stakeholders.append("Email Service")
        if "report" in title.lower() or "analytics" in title.lower():
            default_stakeholders.append("Analytics System")

        # Merge with existing
        existing_lower = [str(s).lower() for s in stakeholders]
        enriched["stakeholders"] = list(stakeholders)

        for stakeholder in default_stakeholders:
            if stakeholder.lower() not in existing_lower:
                enriched["stakeholders"].append(stakeholder)
                if len(enriched["stakeholders"]) >= 3:
                    break

    return enriched


def extract_optional_features(text: str, title: str) -> List[str]:
    """Extract optional features/sub-flows from requirement text"""
    optional_features = []

    # Keywords that indicate optional features
    optional_patterns = [
        r"users? can (?:also\s+)?([^.]+)",  # Match "User can" or "Users can" with optional "also"
        r"(?:can also|optionally|may also)\s+([^.]+)",
        r"able to\s+([^.]+)",
        r"option to\s+([^.]+)",
        r"can\s+(?:filter|sort|customize|configure|modify)\s+([^.]+)",
    ]

    text_lower = text.lower()
    for pattern in optional_patterns:
        matches = re.findall(pattern, text_lower)
        for match in matches:
            feature = match.strip()
            if 10 < len(feature) < 100:
                # Capitalize first letter
                feature = feature[0].upper() + feature[1:]
                if not feature.endswith("."):
                    feature = feature
                # Don't duplicate "User can" if already present
                if feature.lower().startswith("can "):
                    optional_features.append(f"User {feature}")
                else:
                    optional_features.append(f"User can {feature}")

    # Look for specific keywords
    keyword_features = {
        "filter": "User can apply filters to refine results",
        "sort": "User can sort results by different criteria",
        "export": "User can export data in various formats",
        "customize": "User can customize display settings",
        "save": "User can save searches for later use",
    }

    for keyword, feature in keyword_features.items():
        if keyword in text_lower and feature not in optional_features:
            optional_features.append(feature)

    # Remove duplicates
    seen = set()
    unique_features = []
    for feature in optional_features:
        feature_lower = feature.lower()
        if feature_lower not in seen:
            seen.add(feature_lower)
            unique_features.append(feature)

    return unique_features[:4]  # Limit to 4


def extract_error_cases(text: str, title: str) -> List[str]:
    """Extract error cases and alternate flows from requirement text"""
    error_cases = []

    # Keywords that indicate error handling
    error_patterns = [
        (
            r"if\s+([^,]+?)\s+fails,\s+([^.]+)",
            "If {}: {}",
        ),  # For "If X fails, do Y" pattern
        (
            r"when\s+([^.]+?)\s+(?:unavailable|not available)",
            "If {} is unavailable: System displays message and suggests alternatives",
        ),
        (r"if\s+no\s+([^.]+)", "If no {}: System notifies user and provides guidance"),
        (
            r"unable to\s+([^.]+)",
            "If unable to {}: System logs issue and notifies administrator",
        ),
        (r"cannot\s+([^.]+)", "If cannot {}: System provides fallback option"),
        (r"timeout", "If timeout occurs: System retries operation and notifies user"),
        (
            r"invalid\s+([^.]+)",
            "If invalid {}: System displays validation error with specific guidance",
        ),
        (
            r"(?:if|when)\s+(?:the\s+)?([^,]+?)(?:\s+fails?|\s+errors?|\s+is\s+unavailable)",
            "If {}: System handles the failure appropriately",
        ),
    ]

    text_lower = text.lower()

    # Process each error pattern
    for pattern, template in error_patterns:
        matches = re.finditer(
            pattern, text, re.IGNORECASE
        )  # Changed to finditer and removed .lower()
        for match in matches:
            groups = match.groups()
            if len(groups) == 1:
                error_case = template.format(groups[0].strip())
            elif len(groups) == 2:
                error_case = template.format(groups[0].strip(), groups[1].strip())
            if len(error_case) < 150:  # Reasonable length limit
                error_cases.append(error_case)

    # Add specific error cases based on keywords if none found
    if not error_cases:
        keyword_errors = {
            "fail": "If operation fails: System displays error message and logs the failure",
            "error": "If error occurs: System shows user-friendly message and notifies support",
            "unavailable": "If service is unavailable: System retries and provides status updates",
            "invalid": "If invalid input: System highlights errors and guides correction",
        }

        for keyword, error in keyword_errors.items():
            if keyword in text.lower() and error not in error_cases:
                error_cases.append(error)

    # Add common error scenarios if still none found
    if not error_cases:
        actor = title.split()[0] if title else "User"
        error_cases = [
            f"If validation fails: System displays specific error message and prompts {actor} to correct input",
            f"If system error occurs: System logs error, notifies support team, and displays user-friendly message",
            "If network timeout: System automatically retries and informs user of delay",
        ]

    # Remove duplicates
    seen = set()
    unique_errors = []
    for error in error_cases:
        error_lower = error.lower()[:50]  # Compare first 50 chars
        if error_lower not in seen:
            seen.add(error_lower)
            unique_errors.append(error)

    return unique_errors[:4]  # Limit to 4


def should_merge_use_cases(uc1: dict, uc2: dict) -> bool:
    """
    Determine if two use cases should be merged

    Args:
        uc1: First use case
        uc2: Second use case

    Returns:
        True if they should be merged
    """
    title1 = uc1.get("title", "").lower()
    title2 = uc2.get("title", "").lower()

    # Extract words from titles
    words1 = set(title1.split())
    words2 = set(title2.split())

    # Remove common stop words
    stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for"}
    words1 = words1 - stop_words
    words2 = words2 - stop_words

    if not words1 or not words2:
        return False

    # Calculate overlap
    overlap = len(words1 & words2) / min(len(words1), len(words2))

    # High overlap suggests they should be merged
    if overlap > 0.6:
        return True

    # Check if one is a subset/variation of the other
    # e.g., "Search books" and "Filter search results"
    if (
        any(word in words2 for word in ["filter", "sort", "refine"])
        and "search" in words1
    ):
        return True

    # Check if same primary actor and similar action
    # Extract potential actors (first word or two)
    actor1 = title1.split()[0] if title1 else ""
    actor2 = title2.split()[0] if title2 else ""

    if actor1 == actor2:
        # Same actor, check if actions are related
        action_words = ["add", "remove", "update", "delete", "modify", "edit"]
        has_related_action = any(
            action in title1 and action in title2 for action in action_words
        )
        if has_related_action and overlap > 0.4:
            return True

    return False


def merge_use_cases(uc1: dict, uc2: dict) -> dict:
    """
    Merge two related use cases into one comprehensive use case

    Args:
        uc1: First use case
        uc2: Second use case

    Returns:
        Merged use case
    """
    merged = uc1.copy()

    # Merge title - use the more comprehensive one
    if len(uc2["title"]) > len(uc1["title"]):
        merged["title"] = uc2["title"]

    # Merge preconditions (avoid duplicates)
    merged["preconditions"] = list(
        set(merged.get("preconditions", []) + uc2.get("preconditions", []))
    )
    # Remove generic placeholders if we have real content
    if len(merged["preconditions"]) > 1:
        merged["preconditions"] = [
            p for p in merged["preconditions"] if p != "No preconditions"
        ]

    # Merge main_flow (preserve order, avoid duplicates)
    existing_flows = set(merged.get("main_flow", []))
    for flow in uc2.get("main_flow", []):
        if flow not in existing_flows and flow != "No main flow":
            merged["main_flow"].append(flow)
            existing_flows.add(flow)

    # Merge sub_flows
    existing_subs = set(merged.get("sub_flows", []))
    for sub in uc2.get("sub_flows", []):
        if sub not in existing_subs and sub != "No subflows":
            if merged["sub_flows"] == ["No subflows"]:
                merged["sub_flows"] = []
            merged["sub_flows"].append(sub)
            existing_subs.add(sub)

    # Merge alternate_flows
    existing_alts = set(merged.get("alternate_flows", []))
    for alt in uc2.get("alternate_flows", []):
        if alt not in existing_alts and alt != "No alternate flows":
            if merged["alternate_flows"] == ["No alternate flows"]:
                merged["alternate_flows"] = []
            merged["alternate_flows"].append(alt)
            existing_alts.add(alt)

    # Merge outcomes
    merged["outcomes"] = list(set(merged.get("outcomes", []) + uc2.get("outcomes", [])))
    if len(merged["outcomes"]) > 1:
        merged["outcomes"] = [o for o in merged["outcomes"] if o != "No outcomes"]

    # Merge stakeholders
    merged["stakeholders"] = list(
        set(merged.get("stakeholders", []) + uc2.get("stakeholders", []))
    )
    if len(merged["stakeholders"]) > 1:
        merged["stakeholders"] = [
            s for s in merged["stakeholders"] if s != "No stakeholders"
        ]

    return merged


def normalize_use_case(use_case: dict) -> dict:
    """
    Normalize a use case by removing placeholder text and cleaning up

    Args:
        use_case: Use case to normalize

    Returns:
        Normalized use case
    """
    normalized = use_case.copy()

    # Remove placeholders if there's real content
    for field in [
        "preconditions",
        "sub_flows",
        "alternate_flows",
        "outcomes",
        "stakeholders",
    ]:
        items = normalized.get(field, [])

        # Define placeholders for each field
        placeholders = {
            "preconditions": "No preconditions",
            "sub_flows": "No subflows",
            "alternate_flows": "No alternate flows",
            "outcomes": "No outcomes",
            "stakeholders": "No stakeholders",
        }

        placeholder = placeholders.get(field, "")

        # Remove placeholder if there are other items
        if len(items) > 1 and placeholder in items:
            normalized[field] = [item for item in items if item != placeholder]

    # Clean up duplicates
    for field in [
        "preconditions",
        "sub_flows",
        "alternate_flows",
        "outcomes",
        "stakeholders",
    ]:
        if field in normalized:
            # Preserve order while removing duplicates
            seen = set()
            unique = []
            for item in normalized[field]:
                item_lower = item.lower().strip()
                if item_lower not in seen:
                    seen.add(item_lower)
                    unique.append(item)
            normalized[field] = unique

    return normalized
