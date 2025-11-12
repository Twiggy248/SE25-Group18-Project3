import json
import os
from datetime import datetime

import pytest

from export_utils import (_build_jira_description, _convert_to_jira_issue,
                          export_to_docx, export_to_format, export_to_json,
                          export_to_markdown, export_to_plantuml)


@pytest.fixture
def sample_use_case():
    return {
        "title": "Test Use Case",
        "actor": "Test User",
        "goal": "Accomplish something",
        "preconditions": ["System is running", "User is logged in"],
        "main_flow": [
            "User initiates action",
            "System validates input",
            "System processes request",
        ],
        "sub_flows": ["User can view details", "User can cancel operation"],
        "alternate_flows": ["If validation fails, show error message"],
        "outcomes": ["Action is completed", "Database is updated"],
        "stakeholders": ["User", "System", "Admin"],
    }


@pytest.fixture
def sample_session_context():
    return {
        "project_context": "Test Project",
        "domain": "Test Domain",
        "user_preferences": {},
    }


def test_export_to_json(sample_use_case, sample_session_context):
    use_cases = [sample_use_case]
    result = export_to_json(use_cases, sample_session_context)

    assert isinstance(result, dict)
    assert "metadata" in result
    assert "use_cases" in result
    assert (
        result["metadata"]["project_context"]
        == sample_session_context["project_context"]
    )
    assert result["metadata"]["domain"] == sample_session_context["domain"]
    assert len(result["use_cases"]) == 1
    assert result["use_cases"][0] == sample_use_case


def test_export_to_plantuml(sample_use_case):
    use_cases = [sample_use_case]
    result = export_to_plantuml(use_cases)

    assert "@startuml" in result
    assert "@enduml" in result
    assert "actor" in result.lower()
    assert "usecase" in result.lower()

    # Verify all stakeholders are included
    for stakeholder in sample_use_case["stakeholders"]:
        assert stakeholder.replace(" ", "_") in result


def test_convert_to_jira_issue(sample_use_case):
    result = _convert_to_jira_issue(sample_use_case)

    assert isinstance(result, dict)
    assert result["summary"] == sample_use_case["title"]
    assert result["issuetype"] == "Story"
    assert "description" in result
    assert isinstance(result["description"], str)
    assert "labels" in result
    assert "use-case" in result["labels"]


def test_build_jira_description(sample_use_case):
    result = _build_jira_description(sample_use_case)

    assert isinstance(result, str)
    assert "h3. Preconditions" in result
    assert "h3. Main Flow" in result

    # Verify content is included
    for step in sample_use_case["main_flow"]:
        assert step in result
    for precond in sample_use_case["preconditions"]:
        assert precond in result


def test_export_to_format_json(sample_use_case):
    use_cases = [sample_use_case]
    result = export_to_format(use_cases, "json")

    assert result["status"] == "success"
    assert "JSON" in result["formats"]
    assert "data" in result
    assert isinstance(result["data"], dict)


def test_export_to_format_jira(sample_use_case):
    use_cases = [sample_use_case]
    result = export_to_format(use_cases, "jira")

    assert result["status"] == "success"
    assert "JIRA" in result["formats"]
    assert "data" in result
    assert "issues" in result["data"]
    assert isinstance(result["data"]["issues"], list)
    assert len(result["data"]["issues"]) == 1


def test_export_to_format_plantuml(sample_use_case):
    use_cases = [sample_use_case]
    result = export_to_format(use_cases, "plantuml")

    assert result["status"] == "success"
    assert "PlantUML" in result["formats"]
    assert "data" in result
    assert isinstance(result["data"], str)
    assert "@startuml" in result["data"]


def test_export_to_format_unsupported():
    with pytest.raises(ValueError) as exc:
        export_to_format([], "unsupported_format")
    assert "Unsupported format" in str(exc.value)


def test_export_to_html(sample_use_case):
    use_cases = [sample_use_case]
    result = export_to_format(use_cases, "html")

    assert result["status"] == "success"
    assert "HTML" in result["formats"]
    assert "data" in result
    html_content = result["data"]
    assert isinstance(html_content, str)
    assert "<!DOCTYPE html>" in html_content
    assert sample_use_case["title"] in html_content
    assert sample_use_case["actor"] in html_content
    assert sample_use_case["goal"] in html_content

    # Check for all main flow steps
    for step in sample_use_case["main_flow"]:
        assert step in html_content


def test_export_to_json_without_session_context(sample_use_case):
    use_cases = [sample_use_case]
    result = export_to_json(use_cases, None)

    assert isinstance(result, dict)
    assert "metadata" in result
    assert "use_cases" in result
    assert result["metadata"]["project_context"] == ""
    assert result["metadata"]["domain"] == ""
    assert len(result["use_cases"]) == 1
    assert result["use_cases"][0] == sample_use_case


def test_jira_description_with_missing_fields():
    minimal_use_case = {"title": "Minimal Use Case"}
    description = _build_jira_description(minimal_use_case)
    assert isinstance(description, str)
    assert (
        len(description) == 0
    )  # Should return empty string when no required fields exist


def test_export_to_html_empty_list():
    result = export_to_format([], "html")
    assert result["status"] == "success"
    assert "HTML" in result["formats"]
    assert "No Use Cases Available" in result["data"]


def test_export_to_html_with_missing_fields():
    minimal_use_case = {"title": "Minimal Use Case"}
    result = export_to_format([minimal_use_case], "html")
    assert result["status"] == "success"
    assert "HTML" in result["formats"]
    assert "Not specified" in result["data"]
    assert minimal_use_case["title"] in result["data"]


def test_export_to_format_with_null_values():
    use_case = {
        "title": None,
        "actor": None,
        "steps": None,
        "preconditions": None,
        "main_flow": None,
        "alternate_flows": None,
        "outcomes": None,
        "stakeholders": None,
    }
    result = export_to_format([use_case], "json")
    assert result["status"] == "success"
    assert result["data"]["use_cases"][0]["title"] is None


def test_plantuml_with_special_characters():
    use_case = {
        "title": "Test (with) special-chars!",
        "stakeholders": ["User/Admin", "System-DB", "Third Party"],
    }
    result = export_to_plantuml([use_case])
    assert "@startuml" in result
    # Title should be cleaned up
    assert "Test_with_special_chars" in result
    # Actors should be cleaned up
    assert "User_Admin" in result or "UserAdmin" in result
    assert "System_DB" in result or "SystemDB" in result
    assert "Third_Party" in result


@pytest.mark.skip(reason="Requires external filesystem access")
def test_export_to_docx(sample_use_case, sample_session_context):
    use_cases = [sample_use_case]
    result = export_to_format(use_cases, "docx")

    assert result["status"] == "success"
    assert "DOCX" in result["formats"]
    assert "export_path" in result
    assert os.path.exists(result["export_path"])

    # Clean up
    try:
        os.remove(result["export_path"])
    except:
        pass


def test_export_to_markdown(sample_use_case, sample_session_context):
    use_cases = [sample_use_case]
    result = export_to_format(use_cases, "markdown")

    assert result["status"] == "success"
    assert "Markdown" in result["formats"]
    assert "export_path" in result
    assert os.path.exists(result["export_path"])

    # Clean up
    try:
        os.remove(result["export_path"])
    except:
        pass


def test_export_to_docx_without_session_context(sample_use_case):
    """Test DOCX export without session context"""
    from export_utils import export_to_docx
    use_cases = [sample_use_case]
    result = export_to_docx(use_cases, None, "test_session")
    assert os.path.exists(result)
    os.remove(result)


def test_export_to_markdown_without_session_context(sample_use_case):
    """Test Markdown export without session context"""
    from export_utils import export_to_markdown
    use_cases = [sample_use_case]
    result = export_to_markdown(use_cases, None, "test_session")
    assert os.path.exists(result)
    os.remove(result)


def test_export_to_docx_with_empty_fields(sample_session_context):
    """Test DOCX export with use case having empty fields"""
    from export_utils import export_to_docx
    use_case = {
        "id": "UC_EMPTY",
        "title": "Empty Use Case",
        "preconditions": [],
        "main_flow": [],
        "sub_flows": [],
        "alternate_flows": []
    }
    result = export_to_docx([use_case], sample_session_context, "test_session")
    assert os.path.exists(result)
    os.remove(result)


def test_export_to_markdown_with_empty_fields(sample_session_context):
    """Test Markdown export with use case having empty fields"""
    from export_utils import export_to_markdown
    use_case = {
        "id": "UC_EMPTY",
        "title": "Empty Use Case",
        "preconditions": [],
        "main_flow": [],
        "sub_flows": [],
        "alternate_flows": []
    }
    result = export_to_markdown([use_case], sample_session_context, "test_session")
    assert os.path.exists(result)
    os.remove(result)


def test_export_to_docx_multiple_use_cases(sample_use_case, sample_session_context):
    """Test DOCX export with multiple use cases"""
    from export_utils import export_to_docx
    use_case2 = sample_use_case.copy()
    use_case2["id"] = "UC_002"
    use_case2["title"] = "Second Use Case"
    result = export_to_docx([sample_use_case, use_case2], sample_session_context, "test_session")
    assert os.path.exists(result)
    os.remove(result)


def test_export_to_markdown_multiple_use_cases(sample_use_case, sample_session_context):
    """Test Markdown export with multiple use cases"""
    from export_utils import export_to_markdown
    use_case2 = sample_use_case.copy()
    use_case2["id"] = "UC_002"
    use_case2["title"] = "Second Use Case"
    result = export_to_markdown([sample_use_case, use_case2], sample_session_context, "test_session")
    assert os.path.exists(result)
    os.remove(result)


def test_export_to_html(sample_use_case, sample_session_context):
    """Test HTML export functionality"""
    from export_utils import export_to_html
    use_cases = [sample_use_case]
    result = export_to_html(use_cases)
    assert isinstance(result, str)
    assert "<html" in result
    assert sample_use_case["title"] in result
    assert "<!DOCTYPE html>" in result
