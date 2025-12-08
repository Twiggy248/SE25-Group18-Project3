# -----------------------------------------------------------------------------
# File: use_case_validator.py
# Description: Use case validator for ReqEngine - validates use case quality 
#              and completeness with safe type handling and scoring metrics.
# -----------------------------------------------------------------------------

"""
Use Case Validator - FIXED VERSION
Validates use case quality and completeness with safe type handling
"""

from typing import List, Tuple
from ..utilities.key_values import ACTION_VERBS, SECURITY


def validate_requirements(use_cases: list, validation_data: list = None) -> list:
    """
    Validate a list of use cases and return validation results with scores.

    Args:
        use_cases: List of use case dictionaries
        validation_data: Optional list of pre-computed validation results

    Returns:
        List of validated use cases with added validation scores and details
    """
    if validation_data and len(validation_data) == len(use_cases):
        return validation_data

    validator = UseCaseValidator()
    validated_cases = []

    for use_case in use_cases:
        is_valid, issues = validator.validate(use_case)
        suggestions = validator.get_improvement_suggestions(use_case)
        score = validator.calculate_quality_score(use_case)
        security_score = validator.calculate_security_score(use_case)
        completeness = min(len(use_case.get("steps", [])) * 10, 100)

        # Calculate combined score
        validation_score = (score + security_score + completeness) / 3

        validated_case = {
            **use_case,
            "validation_score": validation_score,
            "validation_details": {
                "completeness": completeness,
                "clarity": score,
                "testability": score if is_valid else score * 0.8,
                "security_score": security_score,
            },
            "issues": issues,
            "suggestions": suggestions,
        }
        validated_cases.append(validated_case)

    return validated_cases


class UseCaseValidator:
    """Validate use case quality and structure"""

    @staticmethod
    def _safe_get_list(use_case: dict, key: str) -> List[str]:
        """Safely get a list field, converting dicts/other types to strings"""
        value = use_case.get(key, [])

        if not value:
            return []

        if isinstance(value, str):
            return [value]

        if isinstance(value, list):
            result = []
            for item in value:
                if isinstance(item, str):
                    result.append(item)
                elif isinstance(item, dict):
                    result.append(str(item))
                else:
                    result.append(str(item))
            return result

        return [str(value)]

    @staticmethod
    def validate(use_case: dict) -> Tuple[bool, List[str]]:
        """
        Validate a use case and return issues

        Returns:
            (is_valid, list_of_issues)
        """
        issues = []

        # Title validation
        title = use_case.get("title", "")
        if len(title.split()) < 3:
            issues.append(
                "Title too short - should follow 'Actor Action Object' pattern"
            )

        # Check for verb in title
        if not any(verb in title.lower() for verb in ACTION_VERBS):
            issues.append("Title should contain an action verb")

        # Preconditions validation (safe list extraction)
        preconditions = UseCaseValidator._safe_get_list(use_case, "preconditions")
        if not preconditions or preconditions == ["No preconditions"]:
            issues.append("Use case should have at least one precondition")
        elif len(preconditions) < 1:
            issues.append("Consider adding more preconditions")

        # Main flow validation
        main_flow = UseCaseValidator._safe_get_list(use_case, "main_flow")
        if not main_flow or main_flow == ["No main flow"]:
            issues.append("Main flow is required")
        elif len(main_flow) < 2:
            issues.append("Main flow should have at least 2 steps")
        elif len(main_flow) < 3:
            issues.append("Consider adding more detail to main flow")

        # Sub flows validation
        sub_flows = UseCaseValidator._safe_get_list(use_case, "sub_flows")
        if sub_flows == ["No subflows"] or not sub_flows:
            issues.append("Consider adding optional/alternative sub-flows")

        # Alternate flows validation
        alternate_flows = UseCaseValidator._safe_get_list(use_case, "alternate_flows")
        if alternate_flows == ["No alternate flows"] or not alternate_flows:
            issues.append("Consider adding error handling and alternate paths")

        # Outcomes validation
        outcomes = UseCaseValidator._safe_get_list(use_case, "outcomes")
        if not outcomes or outcomes == ["No outcomes"]:
            issues.append("Use case should define expected outcomes")

        # Stakeholders validation (safe handling)
        stakeholders = UseCaseValidator._safe_get_list(use_case, "stakeholders")
        if not stakeholders or stakeholders == ["No stakeholders"]:
            issues.append("Use case should identify stakeholders")
        elif len(stakeholders) < 2:
            issues.append("Consider identifying more stakeholders (actors, systems)")

        # Check for "System" in stakeholders (with safe string conversion)
        stakeholder_strings = [str(s).lower() for s in stakeholders]
        if not any("system" in s for s in stakeholder_strings):
            issues.append("Consider adding 'System' as a stakeholder")

        return len(issues) == 0, issues

    @staticmethod
    def calculate_quality_score(use_case: dict) -> float:
        """
        Calculate a quality score (0-100) for a use case

        Scoring:
        - Title quality: 10 points
        - Preconditions: 15 points
        - Main flow: 25 points
        - Sub flows: 15 points
        - Alternate flows: 15 points
        - Outcomes: 10 points
        - Stakeholders: 10 points
        """
        score = 0

        # Title (10 points)
        title = use_case.get("title", "")
        words = title.split()
        if len(words) >= 3:
            score += 5
            # Check for action verb
            if any(verb in [w.lower() for w in words] for verb in ACTION_VERBS):
                score += 5

        # Preconditions (15 points)
        preconditions = UseCaseValidator._safe_get_list(use_case, "preconditions")
        if preconditions and preconditions != ["No preconditions"]:
            score += min(len(preconditions) * 5, 15)

        # Main flow (25 points)
        main_flow = UseCaseValidator._safe_get_list(use_case, "main_flow")
        if main_flow and main_flow != ["No main flow"]:
            if len(main_flow) >= 5:
                score += 25
            elif len(main_flow) >= 3:
                score += 20
            elif len(main_flow) >= 2:
                score += 15
            else:
                score += 10

        # Sub flows (15 points)
        sub_flows = UseCaseValidator._safe_get_list(use_case, "sub_flows")
        if sub_flows and sub_flows != ["No subflows"]:
            score += min(len(sub_flows) * 5, 15)

        # Alternate flows (15 points)
        alternate_flows = UseCaseValidator._safe_get_list(use_case, "alternate_flows")
        if alternate_flows and alternate_flows != ["No alternate flows"]:
            score += min(len(alternate_flows) * 5, 15)

        # Outcomes (10 points)
        outcomes = UseCaseValidator._safe_get_list(use_case, "outcomes")
        if outcomes and outcomes != ["No outcomes"]:
            score += min(len(outcomes) * 5, 10)

        # Stakeholders (10 points)
        stakeholders = UseCaseValidator._safe_get_list(use_case, "stakeholders")
        if stakeholders and stakeholders != ["No stakeholders"]:
            score += min(len(stakeholders) * 3, 10)

        return min(score, 100)

    @staticmethod
    def calculate_security_score(use_case: dict) -> int:
        """Calculate security score based on security-related content in the use case"""
        score = 60  # Base score

        # Check for security-related keywords in all text fields

        # Convert use case to string for keyword search
        use_case_text = str(use_case).lower()

        # Add points for each security keyword found
        for keyword in SECURITY:
            if keyword in use_case_text:
                score += 5

        # Check for specific security features in flows
        flows = UseCaseValidator._safe_get_list(
            use_case, "main_flow"
        ) + UseCaseValidator._safe_get_list(use_case, "alternate_flows")

        security_patterns = ["validat", "authent", "authoriz", "check", "verify"]

        for flow in flows:
            if any(pattern in str(flow).lower() for pattern in security_patterns):
                score += 5

        # Cap at 100
        return min(score, 100)

    @staticmethod
    def get_improvement_suggestions(use_case: dict) -> List[str]:
        """Get specific suggestions for improving the use case"""
        suggestions = []

        is_valid, issues = UseCaseValidator.validate(use_case)

        if not is_valid:
            for issue in issues:
                if "title" in issue.lower():
                    suggestions.append(
                        "Rewrite title in format: 'Actor ActionVerb Object' (e.g., 'Customer searches for books')"
                    )
                elif "precondition" in issue.lower():
                    suggestions.append(
                        "Add preconditions like: user authentication state, system availability, data prerequisites"
                    )
                elif "main flow" in issue.lower():
                    suggestions.append(
                        "Break down the main flow into more detailed steps, each describing a specific action"
                    )
                elif "sub flow" in issue.lower():
                    suggestions.append(
                        "Add optional features, filters, or sorting capabilities as sub-flows"
                    )
                elif "alternate flow" in issue.lower():
                    suggestions.append(
                        "Add error handling: what happens on validation failure, timeout, or system error?"
                    )
                elif "outcome" in issue.lower():
                    suggestions.append(
                        "Define clear success criteria and what the actor achieves"
                    )
                elif "stakeholder" in issue.lower():
                    suggestions.append(
                        "Identify all involved parties: primary actor, secondary actors, external systems"
                    )

        # Check quality score
        quality_score = UseCaseValidator.calculate_quality_score(use_case)
        if quality_score < 60:
            suggestions.append(
                f"Quality score is {quality_score:.0f}/100. Consider enriching all sections for better completeness."
            )

        return suggestions
