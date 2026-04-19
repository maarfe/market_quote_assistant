"""Unit tests for the Savegnago coverage provider."""

from __future__ import annotations

import requests

from app.domain.delivery_address import DeliveryAddress
from app.providers.coverage.savegnago_coverage_provider import (
    SavegnagoCoverageProvider,
)


class FakeResponse:
    """Simple fake HTTP response for provider tests."""

    def __init__(self, payload: dict, status_code: int = 200) -> None:
        self._payload = payload
        self.status_code = status_code

    def raise_for_status(self) -> None:
        """Raise an HTTP error when status code is not successful."""
        if self.status_code >= 400:
            raise requests.HTTPError(f"HTTP {self.status_code}")

    def json(self) -> dict:
        """Return the configured JSON payload."""
        return self._payload


class FakeSession:
    """Simple fake requests session for provider tests."""

    def __init__(
        self,
        get_response: FakeResponse | None = None,
        post_response: FakeResponse | None = None,
        post_exception: Exception | None = None,
    ) -> None:
        self.get_response = get_response or FakeResponse({})
        self.post_response = post_response or FakeResponse({})
        self.post_exception = post_exception
        self.last_post_json = None

    def get(self, *args, **kwargs) -> FakeResponse:
        """Return the configured GET response."""
        return self.get_response

    def post(self, *args, **kwargs) -> FakeResponse:
        """Return the configured POST response or raise the configured error."""
        self.last_post_json = kwargs.get("json")

        if self.post_exception is not None:
            raise self.post_exception

        return self.post_response


def create_delivery_address() -> DeliveryAddress:
    """Create a delivery address for provider tests."""
    return DeliveryAddress(
        label="casa",
        recipient_name="Matheus Felipe",
        street="Rua Exemplo",
        number="123",
        complement="",
        neighborhood="Centro",
        city="Campinas",
        state="SP",
        postal_code="13056-682",
        country="BR",
    )


def test_check_coverage_should_return_covered_when_delivery_sla_exists():
    session = FakeSession(
        post_response=FakeResponse(
            {
                "logisticsInfo": [
                    {
                        "slas": [
                            {
                                "id": "Entrega",
                                "deliveryChannel": "delivery",
                            }
                        ]
                    }
                ]
            }
        )
    )
    provider = SavegnagoCoverageProvider(session=session)

    result = provider.check_coverage(create_delivery_address())

    assert len(result) == 1
    assert result[0].market_name == "Savegnago"
    assert result[0].is_covered is True
    assert result[0].supports_delivery is True
    assert result[0].coverage_status == "covered"


def test_check_coverage_should_return_not_covered_when_slas_are_empty():
    session = FakeSession(
        post_response=FakeResponse(
            {
                "logisticsInfo": [
                    {
                        "slas": [],
                    }
                ]
            }
        )
    )
    provider = SavegnagoCoverageProvider(session=session)

    result = provider.check_coverage(create_delivery_address())

    assert len(result) == 1
    assert result[0].is_covered is False
    assert result[0].supports_delivery is False
    assert result[0].coverage_status == "not_covered"


def test_check_coverage_should_return_unknown_when_request_fails():
    session = FakeSession(
        post_exception=requests.RequestException("network failure")
    )
    provider = SavegnagoCoverageProvider(session=session)

    result = provider.check_coverage(create_delivery_address())

    assert len(result) == 1
    assert result[0].market_name == "Savegnago"
    assert result[0].coverage_status == "unknown"


def test_check_coverage_should_send_normalized_postal_code_in_payload():
    session = FakeSession(
        post_response=FakeResponse(
            {
                "logisticsInfo": [
                    {
                        "slas": [],
                    }
                ]
            }
        )
    )
    provider = SavegnagoCoverageProvider(session=session)

    provider.check_coverage(create_delivery_address())

    assert session.last_post_json is not None
    assert session.last_post_json["postalCode"] == "13056682"
    assert session.last_post_json["country"] == "BRA"