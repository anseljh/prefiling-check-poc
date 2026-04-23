import tomllib
from typing import Dict, Any, List, Tuple
from courtlistener import CourtListener
import re

def get_api_token() -> str:
    try:
        with open("settings.toml", "rb") as f:
            settings = tomllib.load(f)
            return settings.get("courtlistener", {}).get("api_token", "")
    except Exception:
        return ""

def check_citations(text: str) -> Dict[str, Any]:
    token = get_api_token()
    if not token or token == "YOUR_API_TOKEN_HERE":
        raise ValueError("Valid CourtListener API token not found in settings.toml. Please copy settings-example.toml to settings.toml and add your API key.")

    client = CourtListener(api_token=token)
    
    results = {
        "total": 0,
        "verified_correct": [],
        "verified_incorrect": [],
        "not_verified": []
    }
    
    try:
        api_results = client.citation_lookup.lookup_text_batched(text)
    except Exception as e:
        raise RuntimeError(f"Error calling CourtListener API: {e}")

    results["total"] = len(api_results)
    
    for r in api_results:
        status = r.get("status")
        citation_str = r.get("citation")
        start_idx = r.get("start_index", 0)
        end_idx = r.get("end_index", 0)
        
        # Context before citation is typically the case name
        context_before = text[max(0, start_idx - 100):start_idx]
        # Context after citation is typically the court and year, e.g. "(9th Cir. 2010)"
        context_after = text[end_idx:min(len(text), end_idx + 50)]
        
        if status in (404, 400):
            reason = "No match in CourtListener database" if status == 404 else "Invalid citation reporter"
            results["not_verified"].append({
                "citation": citation_str,
                "reason": r.get("error_message", reason),
                "context": context_before.strip()
            })
            continue
            
        elif status in (200, 300):
            clusters = r.get("clusters", [])
            if not clusters:
                results["not_verified"].append({
                    "citation": citation_str,
                    "reason": "API returned OK but no clusters found",
                    "context": context_before.strip()
                })
                continue
            
            cluster = clusters[0]
            is_correct, mismatch_reasons = verify_cluster(context_before, context_after, citation_str, cluster)
            if is_correct:
                results["verified_correct"].append({
                    "citation": citation_str,
                    "case_name": cluster.get("case_name", ""),
                    "context": context_before.strip()
                })
            else:
                results["verified_incorrect"].append({
                    "citation": citation_str,
                    "expected": cluster.get("case_name", ""),
                    "reasons": mismatch_reasons,
                    "context": context_before.strip()
                })
        elif status == 429:
            results["not_verified"].append({
                "citation": citation_str,
                "reason": "Throttled by API",
                "context": context_before.strip()
            })
            
    return results

def verify_cluster(context_before: str, context_after: str, citation_str: str, cluster: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Evaluate facially correct criteria:
    - Case name is at least partially correct
    - Year of decision is correct
    """
    mismatch_reasons = []
    
    # 1. Match case name
    case_name = cluster.get("case_name", "")
    if case_name:
        if not match_case_name(context_before, case_name):
            mismatch_reasons.append(f"Different case name (expected: {case_name})")
            
    # 2. Match year
    date_filed = cluster.get("date_filed", "")
    if date_filed:
        year = date_filed.split("-")[0]
        # Look for the year in the 50 characters following the citation
        if year not in context_after:
            mismatch_reasons.append(f"Different year (expected: {year})")
            
    return len(mismatch_reasons) == 0, mismatch_reasons

def match_case_name(context: str, expected_name: str) -> bool:
    """
    Implements rule: Name is at least partially correct 
    (at least one word on each side of "v." matches, or for cases without "v." 
    then at least one word of the name matches, excluding "In", "re", "ex", "rel")
    """
    expected_lower = expected_name.lower()
    context_lower = context.lower()
    
    excluded = {"in", "re", "ex", "rel", "the", "of", "and", "v"}
    
    def get_words(s: str) -> set:
        return {w for w in re.findall(r'[a-z]+', s) if w not in excluded and len(w) > 2}
    
    if " v. " in expected_lower or " v " in expected_lower:
        splitter = " v. " if " v. " in expected_lower else " v "
        parts = expected_lower.split(splitter, 1)
        left_words = get_words(parts[0])
        right_words = get_words(parts[1])
        
        context_words = get_words(context_lower)
        
        left_match = any(w in context_words for w in left_words) if left_words else True
        right_match = any(w in context_words for w in right_words) if right_words else True
        return left_match and right_match
    else:
        expected_words = get_words(expected_lower)
        context_words = get_words(context_lower)
        return any(w in context_words for w in expected_words) if expected_words else True
