from app.core.markets.market_client import MarketClient
from app.markets.savegnago.savegnago_client import SavegnagoClient
from app.markets.covabra.covabra_client import CovabraClient


def build_clients(enabled_markets: list[str]) -> list[MarketClient]:
    clients: list[MarketClient] = []

    if "savegnago" in enabled_markets:
        clients.append(SavegnagoClient())

    if "covabra" in enabled_markets:
        clients.append(CovabraClient())

    return clients