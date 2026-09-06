"""Regression tests for deterministic WhatsApp skill routing."""

from gateway.whatsapp_intent import is_explicit_whatsapp_send_request


def test_recognizes_german_scheduled_whatsapp_request():
    assert is_explicit_whatsapp_send_request(
        'Schick mir morgen um 9:00 Uhr eine WhatsApp mit der Message "Pössl".'
    )


def test_recognizes_german_immediate_whatsapp_request():
    assert is_explicit_whatsapp_send_request(
        'Bitte sende mir per WhatsApp die Nachricht "Tagesschau".'
    )


def test_recognizes_abbreviated_german_scheduled_whatsapp_request():
    assert is_explicit_whatsapp_send_request("WhatsApp morgen um 09:00 Uhr: Pössl")


def test_recognizes_english_whatsapp_reminder_request():
    assert is_explicit_whatsapp_send_request("Remind me on WhatsApp in 10 minutes.")


def test_auto_loaded_skill_does_not_replace_persisted_user_message(monkeypatch):
    from types import SimpleNamespace

    from agent import skill_commands, skill_utils
    from gateway.run import GatewayRunner

    monkeypatch.setattr(skill_utils, "get_disabled_skill_names", lambda **_kwargs: set())
    monkeypatch.setattr(
        skill_commands,
        "_load_skill_payload",
        lambda *_args, **_kwargs: ({"content": "skill"}, None, "WhatsApp"),
    )
    monkeypatch.setattr(
        skill_commands,
        "_build_skill_message",
        lambda *_args, **_kwargs: "[auto-loaded WhatsApp skill]",
    )

    runner = object.__new__(GatewayRunner)
    original = "Schick mir per WhatsApp eine Nachricht mit Pössl."
    model_message, persisted_message = runner._prepend_whatsapp_skill_for_explicit_request(
        original,
        source=SimpleNamespace(platform=None),
        session_key="test-session",
    )

    assert model_message.endswith(original)
    assert persisted_message == original


def test_does_not_route_generic_reminder_without_whatsapp_channel():
    assert not is_explicit_whatsapp_send_request("Erinnere mich morgen um 9 Uhr an Pössl.")


def test_does_not_route_whatsapp_status_question():
    assert not is_explicit_whatsapp_send_request("Warum kam meine WhatsApp nicht an?")


def test_does_not_route_explicit_slash_command():
    assert not is_explicit_whatsapp_send_request("/whatsapp morgen 9:00 Pössl")


def test_does_not_route_whatsapp_information_requests():
    messages = [
        "What WhatsApp messages arrived today?",
        "Why is WhatsApp unavailable today?",
        "Can WhatsApp send a message?",
        "I got a WhatsApp message today.",
        "Please explain WhatsApp message scheduling.",
    ]
    assert all(not is_explicit_whatsapp_send_request(message) for message in messages)
