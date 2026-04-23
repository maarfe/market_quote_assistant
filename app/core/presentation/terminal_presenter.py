from __future__ import annotations

from app.core.entities.coverage import CoverageStatus
from app.core.presentation.models import RunResult


class TerminalPresenter:
    """
    Responsável por apresentar no terminal o resultado consolidado da execução.
    """

    SEPARATOR = "=" * 80

    def present(self, run_result: RunResult) -> None:
        """
        Exibe a visão detalhada por mercado e, ao final, um comparativo simples
        por item.
        """
        for market_result in run_result.markets:
            self._print_market_block(market_result)

        self._print_item_comparison(run_result)

    def _print_market_block(self, market_result) -> None:
        print(f"\n{self.SEPARATOR}")
        print(f"MERCADO: {market_result.market_name}")
        print(self.SEPARATOR)

        print(f"Cobertura: {self._format_coverage(market_result.coverage.status)}")
        print(f"Entrega disponível: {'Sim' if market_result.coverage.has_delivery else 'Não'}")
        print(f"Frete: {self._format_price(market_result.shipping.price)}")
        print(f"Prazo: {market_result.shipping.delivery_estimate or 'N/A'}")

        if not market_result.coverage.has_delivery:
            print("\nSem entrega disponível para este mercado.")
            return

        for item_result in market_result.items:
            print(f"\nITEM: {item_result.item_name}")
            print(f"Encontrados: {item_result.offer_count} produtos válidos")

            if not item_result.offers:
                print("Nenhuma oferta encontrada.")
                continue

            for index, offer in enumerate(item_result.offers, start=1):
                print(f"\n{index}. {offer.product_name}")
                print(f"   Marca: {offer.brand or 'N/A'}")
                print(f"   Preço: {self._format_price(offer.price)}")
                print(f"   URL: {offer.product_url}")

    def _print_item_comparison(self, run_result: RunResult) -> None:
        comparison_map: dict[str, list[tuple[str, float | None]]] = {}

        for market_result in run_result.markets:
            for item_result in market_result.items:
                comparison_map.setdefault(item_result.item_name, []).append(
                    (market_result.market_name, item_result.lowest_price)
                )

        if not comparison_map:
            return

        print(f"\n{self.SEPARATOR}")
        print("COMPARATIVO POR ITEM")
        print(self.SEPARATOR)

        for item_name, market_prices in comparison_map.items():
            print(f"\nITEM: {item_name}")

            for market_name, lowest_price in market_prices:
                if lowest_price is None:
                    print(f"- {market_name}: sem ofertas")
                    continue

                print(f"- {market_name}: a partir de {self._format_price(lowest_price)}")

    @staticmethod
    def _format_price(price: float | None) -> str:
        if price is None:
            return "N/A"
        return f"R$ {price:.2f}"

    @staticmethod
    def _format_coverage(status: CoverageStatus) -> str:
        if status == CoverageStatus.COVERED:
            return "OK"
        if status == CoverageStatus.NOT_COVERED:
            return "Sem cobertura"
        return "Desconhecido"