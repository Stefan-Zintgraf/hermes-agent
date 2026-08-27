"""Behavior contract for opt-in retries of transient provider cron failures."""

from datetime import datetime, timedelta

from hermes_time import now as hermes_now


def test_transient_provider_overload_gets_first_delayed_retry():
    """An opted-in overload schedules retry 1 five minutes later."""
    from cron.scheduler import plan_transient_job_retry

    job = {
        "id": "retry-job",
        "retry_policy": {
            "max_retries": 2,
            "delay_seconds": 300,
        },
    }
    now = hermes_now()
    plan = plan_transient_job_retry(
        job,
        {"origin": "provider", "reason": "overloaded", "retryable": True},
        now=now,
    )

    assert plan == {
        "retries_used": 1,
        "next_run_at": (now + timedelta(minutes=5)).isoformat(),
    }


def test_non_transient_failure_never_gets_a_whole_job_retry():
    """Invalid credentials/configuration cannot be repaired by another run."""
    from cron.scheduler import plan_transient_job_retry

    job = {"id": "retry-job", "retry_policy": {"max_retries": 2, "delay_seconds": 300}}
    assert plan_transient_job_retry(
        job,
        {"origin": "provider", "reason": "auth_permanent", "retryable": False},
        now=hermes_now(),
    ) is None


def test_retry_budget_is_bounded_across_persisted_attempts():
    """After two scheduled retries the original schedule resumes normally."""
    from cron.scheduler import plan_transient_job_retry

    job = {
        "id": "retry-job",
        "retry_policy": {"max_retries": 2, "delay_seconds": 300},
        "retry_state": {"retries_used": 2},
    }
    assert plan_transient_job_retry(
        job,
        {"origin": "provider", "reason": "server_error", "retryable": True},
        now=datetime(2026, 8, 27, 10, 30),
    ) is None
