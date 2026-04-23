import pytest
from src.checker import match_case_name, verify_cluster

def test_match_case_name_good_v():
    # Known good citation case name
    context = "As established in Obergefell v. Hodges,"
    expected = "Obergefell v. Hodges"
    assert match_case_name(context, expected) == True

def test_match_case_name_bad_v():
    # Bad case name where one side is completely wrong
    context = "As established in Smith v. Hodges,"
    expected = "Obergefell v. Hodges"
    assert match_case_name(context, expected) == False

def test_match_case_name_no_v_good():
    context = "See In re Gault,"
    expected = "In re Gault"
    assert match_case_name(context, expected) == True

def test_match_case_name_no_v_bad():
    context = "See In re Smith,"
    expected = "In re Gault"
    assert match_case_name(context, expected) == False

def test_verify_cluster_correct():
    context_before = "In the landmark case Obergefell v. Hodges, "
    context_after = " (2015), the court ruled..."
    citation_str = "576 U.S. 644"
    cluster = {
        "case_name": "Obergefell v. Hodges",
        "date_filed": "2015-06-26"
    }
    
    is_correct, reasons = verify_cluster(context_before, context_after, citation_str, cluster)
    assert is_correct == True
    assert len(reasons) == 0

def test_verify_cluster_wrong_year():
    context_before = "In Obergefell v. Hodges, "
    context_after = " (2014), the court ruled..." # Wrong year
    citation_str = "576 U.S. 644"
    cluster = {
        "case_name": "Obergefell v. Hodges",
        "date_filed": "2015-06-26"
    }
    
    is_correct, reasons = verify_cluster(context_before, context_after, citation_str, cluster)
    assert is_correct == False
    assert "Different year (expected: 2015)" in reasons

def test_verify_cluster_wrong_name():
    context_before = "In Smith v. Hodges, " # Wrong name
    context_after = " (2015), the court ruled..."
    citation_str = "576 U.S. 644"
    cluster = {
        "case_name": "Obergefell v. Hodges",
        "date_filed": "2015-06-26"
    }
    
    is_correct, reasons = verify_cluster(context_before, context_after, citation_str, cluster)
    assert is_correct == False
    assert "Different case name (expected: Obergefell v. Hodges)" in reasons
