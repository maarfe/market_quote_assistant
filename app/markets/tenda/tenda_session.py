from __future__ import annotations

import time
from typing import Any

import requests

TENDA_BASE_URL = "https://www.tendaatacado.com.br"
TENDA_API_BASE_URL = "https://api.tendaatacado.com.br"

TENDA_REFRESH_TOKEN = "2cf80127460cec8daff0e862de831d6e"
TENDA_CLIENT_ID = "79ggnm96dwlojly6mqulzval0h4b94gc"
TENDA_CLIENT_SECRET = (
    "ix2tid1exrsvc8u4ta2tys1p495sa3sk3h6o6fgp0kdpu7xgmb595b8525m9rfvj"
)


class TendaSession:
    """
    Mantém a sessão HTTP necessária para a API própria do Tenda.

    Responsável por:
    - inicializar cookies/JSESSIONID
    - obter Bearer token público
    - obter cartId/orderId
    - montar headers autenticados
    """

    def __init__(self, timeout: int = 20) -> None:
        self.session = requests.Session()
        self.timeout = timeout
        self.access_token: str | None = None
        self.token_expires_at: float = 0
        self.cart_id: int | None = None

    def ensure_ready(self) -> None:
        self._prime_session()
        self._ensure_token()
        self._ensure_cart()

    def get_authenticated_headers(self) -> dict[str, str]:
        self._ensure_token()

        token = self.access_token or ""

        return {
            "accept": "application/json, text/plain, */*",
            "authorization": f"Bearer {token}",
            "x-authorization": f"Bearer {token}",
            "desktop-platform": "true",
            "origin": TENDA_BASE_URL,
            "referer": f"{TENDA_BASE_URL}/",
            "user-agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/137.0.0.0 Safari/537.36"
            ),
        }

    def _prime_session(self) -> None:
        response = self.session.get(
            TENDA_BASE_URL,
            headers={
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "referer": f"{TENDA_BASE_URL}/",
                "user-agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/137.0.0.0 Safari/537.36"
                ),
            },
            timeout=self.timeout,
        )
        response.raise_for_status()

    def _ensure_token(self) -> None:
        if self.access_token and time.time() < self.token_expires_at:
            return

        response = self.session.post(
            f"{TENDA_API_BASE_URL}/api/public/oauth/access-token",
            data={
                "refresh_token": TENDA_REFRESH_TOKEN,
                "client_id": TENDA_CLIENT_ID,
                "client_secret": TENDA_CLIENT_SECRET,
                "grant_type": "refresh_token",
            },
            headers={
                "accept": "application/json, text/plain, */*",
                "content-type": "application/x-www-form-urlencoded",
                "referer": f"{TENDA_BASE_URL}/",
            },
            timeout=self.timeout,
        )
        response.raise_for_status()

        data = response.json()
        self.access_token = str(data["access_token"])
        expires_in = int(data.get("expires_in", 10800))
        self.token_expires_at = time.time() + expires_in - 60

    def _ensure_cart(self) -> None:
        if self.cart_id is not None:
            return

        response = self.session.get(
            f"{TENDA_API_BASE_URL}/api/shopping-cart/",
            headers=self.get_authenticated_headers(),
            timeout=self.timeout,
        )
        response.raise_for_status()

        data: dict[str, Any] = response.json()
        cart_id = data.get("id") or data.get("shoppingCartId")

        if not cart_id:
            raise ValueError("Tenda cartId/orderId não encontrado.")

        self.cart_id = int(cart_id)