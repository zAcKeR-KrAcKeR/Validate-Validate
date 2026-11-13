from dataclasses import dataclass

@dataclass
class Score:
    developer: int = 0
    validator: int = 0

def score_finding(severity: str, accepted: bool) -> int:
    if not accepted:
        return -10
    return {"critical": 25, "high": 15, "medium": 10, "low": 5}.get(severity.lower(), 5)

def score_fix(attempt: int, regression_passed: bool) -> int:
    if not regression_passed:
        return -5
    return (15 if attempt == 1 else 10 if attempt == 2 else 5) + 10
