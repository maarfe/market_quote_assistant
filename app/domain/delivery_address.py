"""Domain model for delivery address configuration."""

from dataclasses import dataclass


@dataclass(slots=True)
class DeliveryAddress:
    """
    Represents a delivery address used for market coverage checks.

    Attributes:
        label: Logical name for the address, such as 'home'.
        recipient_name: Name of the person receiving the delivery.
        street: Street name.
        number: Street/building number.
        complement: Optional address complement.
        neighborhood: Neighborhood or district.
        city: City name.
        state: State code.
        postal_code: Postal code in string format.
        country: Country code.
    """

    label: str
    recipient_name: str
    street: str
    number: str
    complement: str
    neighborhood: str
    city: str
    state: str
    postal_code: str
    country: str