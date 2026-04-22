from __future__ import annotations

import json
from pathlib import Path

from app.core.entities.address import Address
from app.core.entities.shopping_item import ShoppingItem
from app.markets.savegnago.savegnago_client import SavegnagoClient
from app.core.matching.offer_filter import filter_offers

BASE_DIR = Path(__file__).resolve().parent
CONFIG_DIR = BASE_DIR / "app" / "config"


def load_address() -> Address:
    address_file = CONFIG_DIR / "address.json"

    with address_file.open("r", encoding="utf-8") as file:
        data = json.load(file)

    return Address(
        postal_code=data["zip_code"],
    )


def load_shopping_items() -> list[ShoppingItem]:
    shopping_list_file = CONFIG_DIR / "shopping_list.json"

    with shopping_list_file.open("r", encoding="utf-8") as file:
        data = json.load(file)

    items = data.get("items", [])
    shopping_items: list[ShoppingItem] = []

    for item in items:
        name = item.get("name")
        if not isinstance(name, str) or not name.strip():
            continue

        shopping_items.append(
            ShoppingItem(
                name=name.strip(),
                preferred_brand=item.get("preferred_brand"),
                preferred_type=item.get("preferred_type"),
                exclude_terms=item.get("exclude_terms"),
            )
        )

    return shopping_items


def main() -> None:
    client = SavegnagoClient()

    address = load_address()
    shopping_items = load_shopping_items()

    coverage = client.check_coverage(address)
    shipping = client.get_shipping_info(address)

    print("COVERAGE:")
    print(coverage)

    print("\nENTREGA:")
    print(f"- Frete: {'R$ ' + format(shipping.price, '.2f') if shipping.price is not None else 'N/A'}")
    print(f"- Prazo: {shipping.delivery_estimate or 'N/A'}")

    if not shopping_items:
        print("\nNenhum item válido encontrado em shopping_list.json")
        return

    for shopping_item in shopping_items:
        print(f"\n{'=' * 80}")
        print(f"ITEM: {shopping_item.name}")
        print(f"{'=' * 80}")

        offers = client.search_products(shopping_item, address)
        offers = filter_offers(shopping_item, offers)

        if not offers:
            print("Nenhuma oferta encontrada.")
            continue

        print(f"\nEncontrados: {len(offers)} produtos válidos\n")
        for offer in offers[:10]:
            print(f"- {offer.product_name}")
            print(f"  Marca: {offer.brand or 'N/A'}")
            print(f"  Preço: R$ {offer.price:.2f}")
            print()


if __name__ == "__main__":
    main()