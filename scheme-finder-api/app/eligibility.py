"""Pure rule-based eligibility calculation engine."""

from typing import Any, Dict, List, Optional, Tuple, Union
from app.models import Profile, Scheme, SchemeCriterion


SUPPORTED_OPERATORS = {"<=", ">=", "==", "in"}


def _get_profile_value(profile: Optional[Union[Profile, Dict[str, Any]]], field: str) -> Any:
    """Retrieve field value from profile or dict, unwrapping enums if present."""
    if profile is None:
        return None

    if isinstance(profile, dict):
        val = profile.get(field)
    else:
        val = getattr(profile, field, None)

    if hasattr(val, "value"):
        return val.value
    return val


def check_scheme(
    scheme: Union[Scheme, Dict[str, Any]],
    profile: Optional[Union[Profile, Dict[str, Any]]] = None,
) -> Tuple[str, List[str]]:
    """Evaluate a scheme against a profile.
    
    Returns:
        (verdict, missing_fields):
            verdict: "eligible", "possibly_eligible", or "not_eligible"
            missing_fields: list of missing profile field names needed for full determination.
    """
    raw_criteria = scheme.criteria if hasattr(scheme, "criteria") else scheme.get("criteria", [])
    
    missing_fields_set: List[str] = []

    for item in raw_criteria:
        field = item.field if hasattr(item, "field") else item["field"]
        op = item.op if hasattr(item, "op") else item["op"]
        rule_val = item.value if hasattr(item, "value") else item["value"]

        if op not in SUPPORTED_OPERATORS:
            raise ValueError(f"Unsupported operator '{op}' in criterion for field '{field}'")

        profile_val = _get_profile_value(profile, field)

        if profile_val is None:
            if field not in missing_fields_set:
                missing_fields_set.append(field)
            continue

        # Evaluate deterministic rule
        is_satisfied = False
        if op == "==":
            is_satisfied = (profile_val == rule_val)
        elif op == "<=":
            is_satisfied = (profile_val <= rule_val)
        elif op == ">=":
            is_satisfied = (profile_val >= rule_val)
        elif op == "in":
            if isinstance(rule_val, (list, tuple, set)):
                is_satisfied = (profile_val in rule_val)
            else:
                is_satisfied = (profile_val == rule_val)

        if not is_satisfied:
            # If any criterion fails, the verdict is immediately not_eligible
            return ("not_eligible", [])

    if missing_fields_set:
        return ("possibly_eligible", missing_fields_set)

    return ("eligible", [])
