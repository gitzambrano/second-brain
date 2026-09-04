import pytest


def test_visual_audit_budget_expires_without_sleeping():
    from check_site_pages import AuditBudget, audit

    budget = AuditBudget(max_seconds=0, now=lambda: 100.0)

    assert budget.expired
    with pytest.raises(TimeoutError):
        budget.timeout_ms(20_000)

    result = audit(max_seconds=0)
    assert any(issue.code == "AUDIT_TIME_BUDGET_EXCEEDED" for issue in result.issues)
