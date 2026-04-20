from dataclasses import dataclass
from typing import Optional, List

@dataclass
class ShoppingItem:
    name: str
    preferred_brand: Optional[str] = None
    preferred_type: Optional[str] = None
    exclude_terms: Optional[List[str]] = None