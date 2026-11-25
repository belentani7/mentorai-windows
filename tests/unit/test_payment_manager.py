"""Tests unitarios del gestor de licencias y del procesador de pagos simulado."""

from __future__ import annotations

import hashlib
import hmac
import json

from core.payment_manager import LicenseManager, StripePaymentProcessor


def _processor(tmp_path):
    return StripePaymentProcessor(app_dir=tmp_path)


def _signed_event(processor, event):
    return hmac.new(
        processor.webhook_secret.encode(),
        json.dumps(event).encode(),
        hashlib.sha256,
    ).hexdigest()


def test_webhook_with_valid_signature_activates_license(tmp_path):
    processor = _processor(tmp_path)
    event = {
        "type": "checkout.session.completed",
        "data": {"object": {"customer_email": "cliente@example.com"}},
    }
    assert processor.process_webhook(event, _signed_event(processor, event)) is True
    info = processor.license_manager.get_license_info()
    assert info["email"] == "cliente@example.com"
    assert processor.license_manager.validate_license(info["license_key"]) is True


def test_webhook_with_invalid_signature_is_rejected(tmp_path):
    processor = _processor(tmp_path)
    event = {
        "type": "checkout.session.completed",
        "data": {"object": {"customer_email": "atacante@example.com"}},
    }
    assert processor.process_webhook(event, "00" * 32) is False
    assert processor.license_manager.get_license_info() is None


def test_webhook_with_truncated_signature_is_rejected(tmp_path):
    processor = _processor(tmp_path)
    event = {"type": "noop"}
    good = _signed_event(processor, event)
    assert processor.process_webhook(event, good[:8]) is False


def test_validate_license_fails_closed_on_corrupted_file(tmp_path):
    manager = LicenseManager(tmp_path)
    manager.license_file.write_text("{ no es json válido", encoding="utf-8")
    assert manager.validate_license("MNT-CUALQUIERA") is False

    manager.license_file.write_text(
        json.dumps({"license_key": "MNT-X", "expiry_date": "no-es-fecha"}),
        encoding="utf-8",
    )
    assert manager.validate_license("MNT-X") is False


def test_validate_license_rejects_tampered_key(tmp_path):
    manager = LicenseManager(tmp_path)
    assert manager.activate_license("MNT-LEGITIMA", "dueno@example.com") is True
    assert manager.validate_license("MNT-ADULTERADA") is False


def test_validate_license_rejects_expired_license(tmp_path):
    manager = LicenseManager(tmp_path)
    manager.activate_license("MNT-CADUCADA", "dueno@example.com", days=0)
    assert manager.validate_license("MNT-CADUCADA") is False


def test_session_ids_are_unique(tmp_path):
    processor = _processor(tmp_path)
    first = processor.create_payment_session("a@example.com", "mentorai_pro", 2999)
    second = processor.create_payment_session("a@example.com", "mentorai_pro", 2999)
    assert first["session_id"] != second["session_id"]
    assert first["session_id"].startswith("cs_")
