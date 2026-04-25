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

    print(f"🛒 Lista carregada: {len(shopping_items)} item(ns)")
    print(f"🏪 Mercados habilitados: {len(clients)}")

    for client in clients:
        market_name = client.get_market_name()

        print(f"\n🏪 Consultando mercado: {market_name}")
        print("   → Verificando cobertura...")
        coverage = client.check_coverage(address)

        print("   → Consultando frete/prazo...")
        shipping = client.get_shipping_info(address)

        market_result = MarketResult(
            market_name=market_name,
            coverage=coverage,
            shipping=shipping,
        )

        if not coverage.has_delivery:
            print("   ⚠️ Mercado sem entrega disponível para este endereço.")
            run_result.markets.append(market_result)
            continue

        for index, shopping_item in enumerate(shopping_items, start=1):
            print(
                f"   🔎 [{index}/{len(shopping_items)}] "
                f"Buscando: {shopping_item.name}..."
            )

            offers = client.search_products(shopping_item, address)
            offers = filter_offers(shopping_item, offers)

            print(f"      ✓ {len(offers)} oferta(s) válida(s) encontrada(s)")

            market_result.items.append(
                ItemResult(
                    item_name=shopping_item.name,
                    offers=offers,
                )
            )

        run_result.markets.append(market_result)

    return run_result

def run_multi_market() -> RunResult:
    print("📍 Carregando endereço...")
    address = load_address()

    print("📝 Carregando lista de compras...")
    shopping_items = load_shopping_items()

    if not shopping_items:
        print("Nenhum item válido encontrado em shopping_list.json")
        return RunResult()

    print("\n🚀 Iniciando cotação multi-mercado...")
    run_result = build_run_result(address, shopping_items)

    if not run_result.markets:
        print("Nenhum mercado habilitado.")
        return run_result

    print("\n📦 Gerando arquivos de saída...")
    JsonExporter().export(run_result)
    print("   ✓ data/last_run.json")

    CsvExporter().export(run_result)
    print("   ✓ data/market_comparison.csv")

    print("\n📋 Resultado da cotação:")
    TerminalPresenter().present(run_result)

    return run_result


def main() -> None:
    run_multi_market()