from __future__ import annotations

import json
from pathlib import Path

from app.core.entities.address import Address
from app.core.entities.shopping_item import ShoppingItem
from app.core.markets.market_registry import build_clients
from app.core.matching.offer_filter import filter_offers
from app.core.presentation.csv_exporter import CsvExporter
from app.core.presentation.json_exporter import JsonExporter
from app.core.presentation.models import ItemResult, MarketResult, RunResult
from app.core.presentation.terminal_presenter import TerminalPresenter

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


def build_run_result(address: Address, shopping_items: list[ShoppingItem]) -> RunResult:
    """
    Executa o fluxo multi-mercado e retorna um resultado consolidado, sem
    qualquer responsabilidade de apresentação.
    """
    clients = build_clients(
        enabled_markets=[
            "savegnago",
            "covabra",
        ]
    )

    run_result = RunResult()

    for client in clients:
        coverage = client.check_coverage(address)
        shipping = client.get_shipping_info(address)

        market_result = MarketResult(
            market_name=client.get_market_name(),
            coverage=coverage,
            shipping=shipping,
        )

        if coverage.has_delivery:
            for shopping_item in shopping_items:
                offers = client.search_products(shopping_item, address)
                offers = filter_offers(shopping_item, offers)

                market_result.items.append(
                    ItemResult(
                        item_name=shopping_item.name,
                        offers=offers,
                    )
                )

        run_result.markets.append(market_result)

    return run_result


def main() -> None:
    address = load_address()
    shopping_items = load_shopping_items()

    if not shopping_items:
        print("Nenhum item válido encontrado em shopping_list.json")
        return

    run_result = build_run_result(address, shopping_items)

    if not run_result.markets:
        print("Nenhum mercado habilitado.")
        return

    TerminalPresenter().present(run_result)
    JsonExporter().export(run_result)
    CsvExporter().export(run_result)

    print("\nArquivos gerados:")
    print("- data/last_run.json")
    print("- data/market_comparison.csv")


if __name__ == "__main__":
    main()