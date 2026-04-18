"""Custom exception types for the Market Quote Assistant project."""


class MarketQuoteAssistantError(Exception):
    """
    Base exception for all custom application errors.
    """


class InvalidShoppingListError(MarketQuoteAssistantError):
    """
    Raised when a shopping list file is structurally invalid.
    """


class InvalidDeliveryFeeConfigError(MarketQuoteAssistantError):
    """
    Raised when a delivery fee configuration file is structurally invalid.
    """


class InvalidMarketSourceConfigError(MarketQuoteAssistantError):
    """
    Raised when a market source configuration file is structurally invalid.
    """


class UnsupportedUnitError(MarketQuoteAssistantError):
    """
    Raised when a provided unit cannot be normalized.
    """