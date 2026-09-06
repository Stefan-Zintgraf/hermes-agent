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


def test_recognizes_english_whatsapp_reminder_request():
    assert is_explicit_whatsapp_send_request("Remind me on WhatsApp in 10 minutes.")


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
