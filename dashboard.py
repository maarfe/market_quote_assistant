from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Market Quote — Comparação de Preços",
    page_icon="🛒",
    layout="wide",
)

CSV_PATH = Path("data/market_comparison.csv")
JSON_PATH = Path("data/last_run.json")

_PACKAGE_PATTERN = re.compile(
    r"(\d+(?:[.,]\d+)?\s*(?:kg|g|ml|l|un|unidade|unidades|lt|lts))",
    re.IGNORECASE,
)

# ---------------------------------------------------------------------------
# Load & prepare
# ---------------------------------------------------------------------------

@st.cache_data
def load_shipping(path: Path) -> dict[str, dict]:
    """Lê last_run.json e retorna {market_lower: {price, delivery_estimate}}."""
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    result = {}
    for m in data.get("markets", []):
        name = m.get("market_name", "").lower()
        shipping = m.get("shipping", {})
        price = shipping.get("price")
        raw_date = shipping.get("delivery_estimate", "")
        # Formatar data: "2026-04-24T11:00:00-03:00" → "24/04"
        try:
            dt = datetime.fromisoformat(raw_date)
            delivery_fmt = dt.strftime("%d/%m %H:%M")
        except Exception:
            delivery_fmt = raw_date or "—"
        result[name] = {"price": price, "delivery": delivery_fmt}
    return result


def detect_package(product_name: str) -> str:
    match = _PACKAGE_PATTERN.search(product_name)
    return match.group(1).lower().replace(" ", "") if match else "—"


@st.cache_data
def load_data(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df = df[df["product_name"].notna() & (df["product_name"] != "")]
    for col in ("market", "item_name", "product_name", "brand"):
        df[col] = df[col].str.strip().str.lower()
    df["package"] = df["product_name"].apply(detect_package)
    return df


def build_comparison(df: pd.DataFrame, markets: list[str]) -> pd.DataFrame:
    """
    Pivô: item_name + brand + package → uma linha.
    Por mercado: coluna de preço (float) + coluna de URL (str).
    """
    groups = (
        df.groupby(["item_name", "brand", "package"], sort=False)
        .apply(
            lambda g: {
                row["market"]: (row["price"], row["product_url"])
                for _, row in g.iterrows()
            }
        )
        .reset_index(name="market_data")
    )

    rows = []
    for _, row in groups.iterrows():
        r: dict = {
            "_item_key": f"{row['item_name']}|{row['brand']}|{row['package']}",  # chave única por linha
            "Produto": row["item_name"].title(),
            "Marca": row["brand"].title(),
            "Embalagem": row["package"],
        }
        for market in markets:
            data = row["market_data"].get(market)
            price_col = market.title()
            url_col = f"_url_{market}"
            if data:
                price, url = data
                r[price_col] = float(price)
                r[url_col] = url or ""
            else:
                r[price_col] = None
                r[url_col] = ""
        rows.append(r)

    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

st.title("🛒 Comparação de Preços entre Mercados")

if not CSV_PATH.exists():
    st.error(f"Arquivo não encontrado: `{CSV_PATH}`. Execute o scraper primeiro.")
    st.stop()

df = load_data(CSV_PATH)
markets = sorted(df["market"].unique())

# Session state: set de chaves únicas item_name|brand|package
if "selected_items" not in st.session_state:
    st.session_state.selected_items = set()
else:
    # Limpa chaves antigas sem formato composto (migração)
    st.session_state.selected_items = {k for k in st.session_state.selected_items if "|" in k}

# --- Sidebar ---
with st.sidebar:
    st.header("Filtros")

    item_options = ["Todos"] + sorted(df["item_name"].unique())
    selected_item = st.selectbox("Item", item_options)

    brand_pool = df if selected_item == "Todos" else df[df["item_name"] == selected_item]
    brand_options = ["Todas"] + sorted(brand_pool["brand"].unique())
    selected_brand = st.selectbox("Marca", brand_options)

    st.divider()

    # Lista de compras
    st.header("🛍️ Lista de compras")
    if st.session_state.selected_items:
        for item in sorted(st.session_state.selected_items):
            col_a, col_b = st.columns([4, 1])
            parts = item.split("|")
            label = f"{parts[0].title()} · {parts[1].title()} · {parts[2]}" if len(parts) == 3 else item.title()
            col_a.write(f"✅ {label}")
            if col_b.button("✕", key=f"remove_{item}", help="Remover da lista"):
                st.session_state.selected_items.discard(item)
                st.rerun()
        st.divider()
        if st.button("🗑️ Limpar lista", use_container_width=True):
            st.session_state.selected_items.clear()
            st.rerun()
    else:
        st.caption("Nenhum item selecionado ainda.")

    st.divider()
    st.caption(f"Mercados: {', '.join(m.title() for m in markets)}")
    st.caption(f"{len(df)} ofertas carregadas")

# --- Filtrar ---
filtered = df.copy()
if selected_item != "Todos":
    filtered = filtered[filtered["item_name"] == selected_item]
if selected_brand != "Todas":
    filtered = filtered[filtered["brand"] == selected_brand]

if filtered.empty:
    st.info("Nenhum resultado para os filtros selecionados.")
    st.stop()

# ---------------------------------------------------------------------------
# Tabela comparativa
# ---------------------------------------------------------------------------

st.subheader("Comparativo por produto")

cmp = build_comparison(filtered, markets)

# Remove itens já marcados na lista de compras
cmp = cmp[~cmp["_item_key"].isin(st.session_state.selected_items)]

if cmp.empty:
    st.success("Todos os itens foram adicionados à lista de compras! 🎉")
    st.stop()

price_cols = [m.title() for m in markets]
url_cols = [f"_url_{m}" for m in markets]
display_cols = ["✓", "Produto", "Marca", "Embalagem"] + price_cols + url_cols

display_df = cmp[["_item_key"] + display_cols[1:]].copy()

# Ordena por menor preço entre os mercados disponíveis na linha
display_df["_min_price"] = display_df[price_cols].min(axis=1)
display_df = display_df.sort_values(["Produto", "_min_price"]).drop(columns=["_min_price"])

display_df.insert(0, "✓", False)

column_config: dict = {
    "✓": st.column_config.CheckboxColumn("✓", width="small", default=False),
    "Produto": st.column_config.TextColumn("Produto", width="medium"),
    "Marca": st.column_config.TextColumn("Marca", width="small"),
    "Embalagem": st.column_config.TextColumn("Embalagem", width="small"),
}

for market in markets:
    price_col = market.title()
    url_col = f"_url_{market}"
    column_config[price_col] = st.column_config.NumberColumn(
        price_col,
        format="R$ %.2f",
        width="small",
    )
    column_config[url_col] = st.column_config.LinkColumn(
        f"🔗 {price_col}",
        display_text="abrir",
        width="small",
    )

edited = st.data_editor(
    display_df[display_cols],
    column_config=column_config,
    column_order=display_cols,
    use_container_width=True,
    hide_index=True,
    height=min(80 + len(display_df) * 38, 600),
    key="comparison_table",
)

st.caption("Marque ✓ na linha desejada para mover para a lista · Clique no header para ordenar · 'abrir' abre o produto no site")

# Processar checkboxes marcados
checked_mask = edited["✓"] == True
if checked_mask.any():
    checked_keys = display_df.loc[checked_mask.values, "_item_key"].tolist()
    for key in checked_keys:
        st.session_state.selected_items.add(key)
    st.rerun()

# ---------------------------------------------------------------------------
# Resumo por mercado
# ---------------------------------------------------------------------------

st.divider()
st.subheader("Resumo por mercado")

shipping_info = load_shipping(JSON_PATH)

cols = st.columns(len(markets))
for col, market in zip(cols, markets):
    mdf = filtered[filtered["market"] == market]
    info = shipping_info.get(market, {})
    frete = info.get("price")
    delivery = info.get("delivery", "—")
    with col:
        st.markdown(f"#### {market.title()}")
        frete_label = f"R$ {frete:.2f}" if frete is not None else "—"
        st.metric(label="🚚 Frete", value=frete_label)
        st.caption(f"📅 Entrega prevista: {delivery}")
        st.caption(f"📦 {len(mdf)} ofertas encontradas")

# ---------------------------------------------------------------------------
# Lista de compras — tabela sempre visível
# ---------------------------------------------------------------------------

st.divider()
st.subheader("🛍️ Lista de compras")

if not st.session_state.selected_items:
    st.caption("Nenhum item selecionado ainda. Marque ✓ na tabela acima.")
else:
    cmp_all = build_comparison(df, markets)
    cart = cmp_all[cmp_all["_item_key"].isin(st.session_state.selected_items)].copy()

    cart_display_cols = ["Produto", "Marca", "Embalagem"] + price_cols + url_cols
    cart_df = cart[cart_display_cols].copy()

    cart_column_config: dict = {
        "Produto": st.column_config.TextColumn("Produto", width="medium"),
        "Marca": st.column_config.TextColumn("Marca", width="small"),
        "Embalagem": st.column_config.TextColumn("Embalagem", width="small"),
    }
    for market in markets:
        cart_column_config[market.title()] = st.column_config.NumberColumn(
            market.title(), format="R$ %.2f", width="small"
        )
        cart_column_config[f"_url_{market}"] = st.column_config.LinkColumn(
            f"🔗 {market.title()}", display_text="abrir", width="small"
        )

    cart_df.insert(0, "🗑️", False)
    cart_column_config["🗑️"] = st.column_config.CheckboxColumn("🗑️", width="small", default=False)
    cart_display_cols_with_remove = ["🗑️"] + cart_display_cols

    cart_edited = st.data_editor(
        cart_df[cart_display_cols_with_remove],
        column_config=cart_column_config,
        column_order=cart_display_cols_with_remove,
        use_container_width=True,
        hide_index=True,
        height=min(80 + len(cart_df) * 38, 400),
        key="cart_table",
    )

    # Processar remoções
    remove_mask = cart_edited["🗑️"] == True
    if remove_mask.any():
        keys_to_remove = cart[remove_mask.values]["_item_key"].tolist()
        for key in keys_to_remove:
            st.session_state.selected_items.discard(key)
        st.rerun()

    if st.button("🗑️ Limpar lista", key="clear_cart"):
        st.session_state.selected_items.clear()
        st.rerun()