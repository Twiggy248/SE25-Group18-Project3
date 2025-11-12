import pytest

from use_case_enrichment import (enrich_use_case, enrich_use_cases,
                                 extract_error_cases,
                                 extract_optional_features, merge_use_cases,
                                 normalize_use_case, should_merge_use_cases)


@pytest.fixture
def minimal_use_case():
    return {"title": "Search Books", "actor": "User"}


@pytest.fixture
def complete_use_case():
    return {
        "title": "Search and Filter Books",
        "actor": "Library User",
        "goal": "Find specific books in the library catalog",
        "preconditions": ["User is logged in", "Library catalog is accessible"],
        "main_flow": [
            "User navigates to search page",
            "User enters search criteria",
            "System displays results",
            "User reviews results",
        ],
        "sub_flows": ["User can apply filters", "User can sort results"],
        "alternate_flows": [
            "If no results found: System suggests alternatives",
            "If search fails: System displays error message",
        ],
        "outcomes": ["User finds desired books", "Search results are displayed"],
        "stakeholders": ["Library User", "System", "Library Staff"],
    }


@pytest.mark.asyncio
async def test_enrich_use_cases():
    """Test enriching multiple use cases"""
    use_cases = [{"title": "Search Books"}, {"title": "Add Book"}]
    enriched = await enrich_use_cases(use_cases)
    assert len(enriched) == 2
    for uc in enriched:
        assert "preconditions" in uc
        assert "main_flow" in uc
        assert "stakeholders" in uc


def test_enrich_use_case_minimal(minimal_use_case):
    """Test enriching a minimal use case"""
    enriched = enrich_use_case(minimal_use_case, "")

    # Check all required fields are added
    assert "preconditions" in enriched
    assert len(enriched["preconditions"]) >= 2

    assert "main_flow" in enriched
    assert len(enriched["main_flow"]) >= 4

    assert "sub_flows" in enriched
    assert len(enriched["sub_flows"]) >= 2

    assert "alternate_flows" in enriched
    assert len(enriched["alternate_flows"]) >= 2

    assert "outcomes" in enriched
    assert len(enriched["outcomes"]) >= 1

    assert "stakeholders" in enriched
    assert len(enriched["stakeholders"]) >= 2
    assert "System" in enriched["stakeholders"]


def test_enrich_use_case_preserves_existing(complete_use_case):
    """Test that enrichment preserves existing content"""
    enriched = enrich_use_case(complete_use_case, "")

    # Original content should be preserved
    assert enriched["title"] == complete_use_case["title"]
    assert all(
        p in enriched["preconditions"] for p in complete_use_case["preconditions"]
    )
    assert all(s in enriched["stakeholders"] for s in complete_use_case["stakeholders"])
    assert all(f in enriched["main_flow"] for f in complete_use_case["main_flow"])


def test_extract_optional_features():
    """Test extracting optional features from text"""
    text = """
    Users can also export results to PDF.
    The system may also generate reports.
    Users are able to customize display settings.
    Users have the option to save searches.
    Users can filter results by date.
    Users can sort by relevance.
    """
    features = extract_optional_features(text, "Search Results")

    assert len(features) > 0
    assert any("export" in f.lower() for f in features)
    assert any("filter" in f.lower() for f in features)
    assert any("sort" in f.lower() for f in features)


def test_extract_error_cases():
    """Test extracting error cases from text"""
    text = """
    If search fails, show error message.
    When database is unavailable, retry.
    If no results found, suggest alternatives.
    If invalid input, show validation error.
    """
    errors = extract_error_cases(text, "Search")

    # Current implementation focuses on full error flows
    assert len(errors) > 0
    assert any("error" in e.lower() for e in errors)
    assert any("unavailable" in e.lower() for e in errors)
    assert any("no results" in e.lower() for e in errors)


def test_should_merge_use_cases():
    """Test use case merge detection"""
    uc1 = {"title": "Search Books"}
    uc2 = {"title": "Filter Search Results"}

    assert should_merge_use_cases(uc1, uc2)

    # Different functionality shouldn't merge
    uc3 = {"title": "Add New User"}
    assert not should_merge_use_cases(uc1, uc3)

    # Similar actions should merge
    uc4 = {"title": "User Add Book"}
    uc5 = {"title": "User Delete Book"}
    assert should_merge_use_cases(uc4, uc5)


def test_merge_use_cases():
    """Test merging two use cases"""
    uc1 = {
        "title": "Search Books",
        "preconditions": ["User is logged in"],
        "main_flow": ["User enters search"],
        "stakeholders": ["User"],
    }

    uc2 = {
        "title": "Filter Search Results",
        "preconditions": ["Search results exist"],
        "main_flow": ["User applies filters"],
        "stakeholders": ["User", "System"],
    }

    merged = merge_use_cases(uc1, uc2)

    # Should combine unique elements
    assert len(merged["preconditions"]) == 2
    assert len(merged["main_flow"]) == 2
    assert len(merged["stakeholders"]) == 2
    assert merged["title"] == "Filter Search Results"  # Longer title


def test_normalize_use_case():
    """Test normalizing a use case"""
    use_case = {
        "title": "Search Books",
        "preconditions": ["No preconditions", "User is logged in"],
        "sub_flows": ["No subflows"],
        "alternate_flows": ["No alternate flows", "If search fails, retry"],
        "outcomes": ["Found books", "Found books"],  # Duplicate
        "stakeholders": ["User", "user"],  # Case difference
    }

    normalized = normalize_use_case(use_case)

    # Should remove placeholders when real content exists
    assert "No preconditions" not in normalized["preconditions"]
    assert len(normalized["preconditions"]) == 1

    # Should keep placeholders when no other content
    assert normalized["sub_flows"] == ["No subflows"]

    # Should remove duplicates (case-insensitive)
    assert len(normalized["outcomes"]) == 1
    assert len(normalized["stakeholders"]) == 1


def test_enrichment_with_empty_fields():
    """Test enrichment handles empty fields gracefully"""
    empty_use_case = {
        "title": "",
        "preconditions": [],
        "main_flow": [],
        "stakeholders": [],
    }

    enriched = enrich_use_case(empty_use_case, "")

    # Should add default content to empty fields
    assert len(enriched["preconditions"]) > 0
    assert len(enriched["main_flow"]) > 0
    assert len(enriched["stakeholders"]) > 0
