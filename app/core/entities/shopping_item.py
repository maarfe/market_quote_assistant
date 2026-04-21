from dataclasses import dataclass
from typing import Optional


@dataclass
class ShoppingItem:
    name: str
    preferred_brand: Optional[str] = None
    preferred_type: Optional[str | list[str]] = None
    exclude_terms: Optional[list[str]] = None