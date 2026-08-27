"""Agent-visible opt-in policy for transient whole-job cron retries."""

import json


def test_cronjob_schema_exposes_bounded_transient_retry_controls():
    """The model learns the feature from the stable cronjob tool schema."""
    from tools.cronjob_tools import CRONJOB_SCHEMA

    props = CRONJOB_SCHEMA["parameters"]["properties"]
    assert props["retry_count"]["type"] == "integer"
    assert "transient" in props["retry_count"]["description"].lower()
    assert props["retry_delay_seconds"]["type"] == "integer"


def test_create_and_update_persist_retry_policy(tmp_path, monkeypatch):
    """A policy is opt-in per job and can be changed through the agent tool."""
    monkeypatch.setattr("cron.jobs.CRON_DIR", tmp_path / "cron")
    monkeypatch.setattr("cron.jobs.JOBS_FILE", tmp_path / "cron" / "jobs.json")

    from cron.jobs import get_job
    from tools.cronjob_tools import cronjob

    created = json.loads(
        cronjob(
            action="create",
            prompt="Check the status.",
            schedule="every 1h",
            retry_count=2,
            retry_delay_seconds=300,
        )
    )
    job_id = created["job_id"]
    assert get_job(job_id)["retry_policy"] == {
        "max_retries": 2,
        "delay_seconds": 300,
    }

    updated = json.loads(
        cronjob(
            action="update",
            job_id=job_id,
            retry_count=1,
            retry_delay_seconds=600,
        )
    )
    assert updated["success"] is True
    assert get_job(job_id)["retry_policy"] == {
        "max_retries": 1,
        "delay_seconds": 600,
    }
