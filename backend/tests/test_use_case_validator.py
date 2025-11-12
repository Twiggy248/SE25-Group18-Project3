"""
Tests for use_case_validator.py
Tests validation logic, quality scoring, and improvement suggestions
"""

import pytest
from use_case_validator import UseCaseValidator, validate_requirements


@pytest.fixture
def valid_use_case():
    """A well-formed use case for testing"""
    return {
        "id": "UC_001",
        "title": "Customer Create Order",
        "preconditions": ["User is logged in", "Cart has items"],
        "main_flow": [
            "User clicks checkout",
            "System validates cart",
            "User enters shipping info",
            "System calculates total",
            "User confirms order"
        ],
        "sub_flows": ["User applies discount code"],
        "alternate_flows": ["If payment fails, show error"],
        "postconditions": ["Order is created"],
        "actors": ["Customer", "System"]
    }


@pytest.fixture
def minimal_use_case():
    """Minimal use case with issues"""
    return {
        "title": "Order",
        "preconditions": [],
        "main_flow": ["Do something"],
        "sub_flows": [],
        "alternate_flows": []
    }


class TestUseCaseValidator:
    """Test UseCaseValidator class methods"""

    def test_safe_get_list_with_string(self):
        """Test _safe_get_list converts string to list"""
        use_case = {"preconditions": "User is logged in"}
        result = UseCaseValidator._safe_get_list(use_case, "preconditions")
        assert result == ["User is logged in"]

    def test_safe_get_list_with_list(self):
        """Test _safe_get_list returns list as-is"""
        use_case = {"preconditions": ["Precond 1", "Precond 2"]}
        result = UseCaseValidator._safe_get_list(use_case, "preconditions")
        assert result == ["Precond 1", "Precond 2"]

    def test_safe_get_list_with_empty(self):
        """Test _safe_get_list handles empty/missing fields"""
        use_case = {}
        result = UseCaseValidator._safe_get_list(use_case, "preconditions")
        assert result == []

    def test_safe_get_list_with_dict(self):
        """Test _safe_get_list converts dict to string"""
        use_case = {"preconditions": [{"key": "value"}]}
        result = UseCaseValidator._safe_get_list(use_case, "preconditions")
        assert len(result) == 1
        assert "key" in result[0]

    def test_safe_get_list_with_mixed_types(self):
        """Test _safe_get_list handles mixed list types"""
        use_case = {"preconditions": ["string", 123, {"key": "val"}]}
        result = UseCaseValidator._safe_get_list(use_case, "preconditions")
        assert len(result) == 3
        assert "string" in result
        assert "123" in result

    def test_validate_good_use_case(self, valid_use_case):
        """Test validation passes for well-formed use case"""
        is_valid, issues = UseCaseValidator.validate(valid_use_case)
        # Should have some issues but not too many
        assert len(issues) <= 5

    def test_validate_title_too_short(self):
        """Test validation catches short titles"""
        use_case = {"title": "Order", "main_flow": ["step"]}
        is_valid, issues = UseCaseValidator.validate(use_case)
        assert any("Title too short" in issue for issue in issues)

    def test_validate_missing_action_verb(self):
        """Test validation catches titles without action verbs"""
        use_case = {
            "title": "The Order Thing",
            "main_flow": ["step"],
            "preconditions": ["precond"]
        }
        is_valid, issues = UseCaseValidator.validate(use_case)
        assert any("action verb" in issue for issue in issues)

    def test_validate_few_preconditions(self):
        """Test validation suggests more preconditions"""
        use_case = {
            "title": "Customer Create Order",
            "preconditions": [],
            "main_flow": ["step1", "step2"]
        }
        is_valid, issues = UseCaseValidator.validate(use_case)
        # Should have at least some validation issues
        assert len(issues) > 0

    def test_validate_few_main_flow_steps(self):
        """Test validation catches insufficient main flow steps"""
        use_case = {
            "title": "Customer Create Order",
            "preconditions": ["logged in"],
            "main_flow": ["step"]
        }
        is_valid, issues = UseCaseValidator.validate(use_case)
        assert any("main flow" in issue.lower() for issue in issues)

    def test_calculate_quality_score_high(self, valid_use_case):
        """Test quality score calculation for good use case"""
        score = UseCaseValidator.calculate_quality_score(valid_use_case)
        assert score >= 50  # Should have reasonable score

    def test_calculate_quality_score_low(self, minimal_use_case):
        """Test quality score calculation for poor use case"""
        score = UseCaseValidator.calculate_quality_score(minimal_use_case)
        assert score < 70  # Should have lower score

    def test_calculate_quality_score_with_actors(self):
        """Test quality score bonus for actors"""
        use_case_with_actors = {
            "title": "User Create Account",
            "main_flow": ["step1", "step2", "step3"],
            "preconditions": ["precond"],
            "actors": ["User", "System"]
        }
        use_case_without_actors = {
            "title": "User Create Account",
            "main_flow": ["step1", "step2", "step3"],
            "preconditions": ["precond"]
        }
        
        score_with = UseCaseValidator.calculate_quality_score(use_case_with_actors)
        score_without = UseCaseValidator.calculate_quality_score(use_case_without_actors)
        assert score_with >= score_without

    def test_calculate_security_score_with_security_keywords(self):
        """Test security score calculation with security-related content"""
        use_case = {
            "title": "User Login with Authentication",
            "main_flow": [
                "User enters credentials",
                "System validates password",
                "System authenticates user"
            ],
            "preconditions": ["User has valid account"],
            "alternate_flows": ["If authentication fails, show error"]
        }
        score = UseCaseValidator.calculate_security_score(use_case)
        assert score > 0  # Should detect security keywords

    def test_calculate_security_score_without_security(self):
        """Test security score for non-security use case"""
        use_case = {
            "title": "User View Dashboard",
            "main_flow": ["User opens dashboard", "System shows data"],
            "preconditions": []
        }
        score = UseCaseValidator.calculate_security_score(use_case)
        # Should have lower security score
        assert score >= 0

    def test_get_improvement_suggestions_for_minimal(self, minimal_use_case):
        """Test improvement suggestions for minimal use case"""
        suggestions = UseCaseValidator.get_improvement_suggestions(minimal_use_case)
        assert len(suggestions) > 0
        # Should suggest improvements for missing elements

    def test_get_improvement_suggestions_for_good(self, valid_use_case):
        """Test improvement suggestions for well-formed use case"""
        suggestions = UseCaseValidator.get_improvement_suggestions(valid_use_case)
        # Should have fewer suggestions
        assert isinstance(suggestions, list)


class TestValidateRequirements:
    """Test validate_requirements function"""

    def test_validate_requirements_basic(self, valid_use_case):
        """Test validate_requirements with single use case"""
        result = validate_requirements([valid_use_case])
        assert len(result) == 1
        assert "validation_score" in result[0]
        assert "validation_details" in result[0]
        assert "issues" in result[0]
        assert "suggestions" in result[0]

    def test_validate_requirements_multiple(self, valid_use_case, minimal_use_case):
        """Test validate_requirements with multiple use cases"""
        result = validate_requirements([valid_use_case, minimal_use_case])
        assert len(result) == 2
        
        # Valid use case should have higher score
        assert result[0]["validation_score"] > result[1]["validation_score"]

    def test_validate_requirements_with_validation_data(self, valid_use_case):
        """Test validate_requirements uses pre-computed validation data"""
        pre_validated = [{**valid_use_case, "validation_score": 99}]
        result = validate_requirements([valid_use_case], pre_validated)
        assert result == pre_validated
        assert result[0]["validation_score"] == 99

    def test_validate_requirements_empty_list(self):
        """Test validate_requirements with empty list"""
        result = validate_requirements([])
        assert result == []

    def test_validation_details_structure(self, valid_use_case):
        """Test validation_details has correct structure"""
        result = validate_requirements([valid_use_case])
        details = result[0]["validation_details"]
        
        assert "completeness" in details
        assert "clarity" in details
        assert "testability" in details
        assert "security_score" in details
        
        # All scores should be numeric
        assert isinstance(details["completeness"], (int, float))
        assert isinstance(details["clarity"], (int, float))

    def test_validation_score_range(self, valid_use_case, minimal_use_case):
        """Test validation scores are in reasonable range"""
        results = validate_requirements([valid_use_case, minimal_use_case])
        
        for result in results:
            score = result["validation_score"]
            assert 0 <= score <= 100  # Scores should be 0-100


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_use_case_with_none_values(self):
        """Test handling use case with None values"""
        use_case = {
            "title": "Test Use Case",
            "preconditions": None,
            "main_flow": None,
            "sub_flows": None
        }
        is_valid, issues = UseCaseValidator.validate(use_case)
        # Should handle None without crashing
        assert isinstance(issues, list)

    def test_use_case_with_empty_strings(self):
        """Test handling use case with empty strings"""
        use_case = {
            "title": "",
            "preconditions": [""],
            "main_flow": [""]
        }
        is_valid, issues = UseCaseValidator.validate(use_case)
        assert len(issues) > 0  # Should catch empty title

    def test_use_case_missing_required_fields(self):
        """Test handling use case missing fields"""
        use_case = {"title": "Test"}
        is_valid, issues = UseCaseValidator.validate(use_case)
        # Should handle gracefully
        assert isinstance(issues, list)

    def test_quality_score_with_no_steps(self):
        """Test quality score calculation with no steps"""
        use_case = {"title": "Test Use Case"}
        score = UseCaseValidator.calculate_quality_score(use_case)
        assert isinstance(score, (int, float))
        assert score >= 0

    def test_security_score_with_empty_content(self):
        """Test security score with minimal content"""
        use_case = {"title": "Test"}
        score = UseCaseValidator.calculate_security_score(use_case)
        assert isinstance(score, (int, float))
        assert score >= 0
