"""Testes automatizados para a regra RN-01: Validação Estrutural e de Domínio do CSV de Pedidos."""

import pandas as pd
import pytest

from data_pipeline import CSVValidationError, validate_and_parse_csv

CSV_HEADER = (
    "order_id,timestamp,item_name,category,quantity,unit_price,"
    "discount,prep_time_minutes,status,channel"
)


def test_rn01_valid_sample_csv_returns_typed_dataframe(sample_csv_bytes: bytes) -> None:
    """Prova que o dataset canônico `data/sample_orders.csv` é aceito e retorna 82 linhas tipadas."""
    df = validate_and_parse_csv(sample_csv_bytes)

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 82
    assert list(df.columns) == [
        "order_id",
        "timestamp",
        "item_name",
        "category",
        "quantity",
        "unit_price",
        "discount",
        "prep_time_minutes",
        "status",
        "channel",
    ]
    assert pd.api.types.is_integer_dtype(df["quantity"])
    assert pd.api.types.is_float_dtype(df["unit_price"])
    assert pd.api.types.is_float_dtype(df["discount"])
    assert pd.api.types.is_float_dtype(df["prep_time_minutes"])


def test_rn01_valid_boundary_values_zero_discount_zero_prep_and_full_discount() -> None:
    """
    Prova os limites válidos de RN-01:
    - discount == 0.0 e prep_time_minutes == 0.0 são aceitos;
    - discount == quantity * unit_price (100% de desconto na linha) é aceito;
    - UTF-8 com BOM é aceito.
    """
    csv_content = (
        "\ufeff"
        f"{CSV_HEADER}\n"
        "ORD-100,2026-11-01T12:00:00Z,Agua Mineral,Bebidas,2,5.00,0.00,0.0,completed,balcao\n"
        "ORD-101,2026-11-01T12:05:00Z,Burger Cortesia,Burgers,2,30.00,60.00,15.0,completed,app\n"
    )
    df = validate_and_parse_csv(csv_content.encode("utf-8"))
    assert len(df) == 2
    assert float(df.loc[0, "discount"]) == 0.0
    assert float(df.loc[0, "prep_time_minutes"]) == 0.0
    assert float(df.loc[1, "discount"]) == 60.0


@pytest.mark.parametrize("empty_payload", [b"", b"   \n\t  ", "", "   \n  "])
def test_rn01_rejects_empty_csv_file(empty_payload: bytes | str) -> None:
    """Prova que arquivo CSV vazio (0 bytes ou apenas espaços) levanta CSVValidationError."""
    with pytest.raises(CSVValidationError) as exc_info:
        validate_and_parse_csv(empty_payload)

    err_dict = exc_info.value.to_dict()
    assert "detail" in err_dict
    assert len(err_dict["errors"]) == 1
    assert err_dict["errors"][0]["row"] is None
    assert err_dict["errors"][0]["column"] is None


def test_rn01_rejects_header_only_without_data_rows() -> None:
    """Prova que CSV contendo apenas cabeçalho e nenhuma linha de dados é rejeitado."""
    csv_content = f"{CSV_HEADER}\n\n"
    with pytest.raises(CSVValidationError) as exc_info:
        validate_and_parse_csv(csv_content)

    errors = exc_info.value.errors
    assert len(errors) == 1
    assert errors[0]["row"] is None
    assert errors[0]["column"] is None


def test_rn01_rejects_missing_required_columns() -> None:
    """Prova que a ausência de colunas obrigatórias no cabeçalho rejeita o CSV identificando cada coluna."""
    incomplete_header = "order_id,timestamp,item_name,category,quantity,unit_price,discount,status\n"
    row = "ORD-001,2026-11-01T18:00:00Z,Burger,Burgers,1,30.0,0.0,completed\n"

    with pytest.raises(CSVValidationError) as exc_info:
        validate_and_parse_csv(incomplete_header + row)

    errors = exc_info.value.errors
    missing_cols = {err["column"] for err in errors}
    assert missing_cols == {"prep_time_minutes", "channel"}
    assert all(err["row"] is None for err in errors)


def test_rn01_rejects_empty_or_null_values_in_required_fields() -> None:
    """Prova que valores vazios/nulos em campos obrigatórios são rejeitados com linha 1-indexed."""
    csv_content = (
        f"{CSV_HEADER}\n"
        ",2026-11-01T18:00:00Z,,   ,1,25.0,0.0,10.0,completed,balcao\n"
    )
    with pytest.raises(CSVValidationError) as exc_info:
        validate_and_parse_csv(csv_content)

    errors = exc_info.value.errors
    failed_cols = {err["column"] for err in errors}
    assert {"order_id", "item_name", "category"}.issubset(failed_cols)
    assert all(err["row"] == 2 for err in errors)


@pytest.mark.parametrize("invalid_qty", ["0", "-1", "-10", "1.5", "2.0", "abc"])
def test_rn01_rejects_invalid_quantity(invalid_qty: str) -> None:
    """Prova que quantity <= 0, decimal ('1.5') ou não numérico é rejeitado na coluna 'quantity'."""
    csv_content = (
        f"{CSV_HEADER}\n"
        f"ORD-001,2026-11-01T18:00:00Z,Burger,Burgers,{invalid_qty},25.0,0.0,10.0,completed,balcao\n"
    )
    with pytest.raises(CSVValidationError) as exc_info:
        validate_and_parse_csv(csv_content)

    errors = exc_info.value.errors
    assert any(err["row"] == 2 and err["column"] == "quantity" for err in errors)


@pytest.mark.parametrize("invalid_price", ["0", "0.0", "-0.01", "-15.0", "caro"])
def test_rn01_rejects_non_positive_unit_price(invalid_price: str) -> None:
    """Prova que unit_price <= 0 ou não numérico é rejeitado na coluna 'unit_price'."""
    csv_content = (
        f"{CSV_HEADER}\n"
        f"ORD-001,2026-11-01T18:00:00Z,Burger,Burgers,1,{invalid_price},0.0,10.0,completed,balcao\n"
    )
    with pytest.raises(CSVValidationError) as exc_info:
        validate_and_parse_csv(csv_content)

    errors = exc_info.value.errors
    assert any(err["row"] == 2 and err["column"] == "unit_price" for err in errors)


@pytest.mark.parametrize(
    ("qty", "unit_price", "invalid_discount"),
    [
        ("1", "30.0", "-0.01"),
        ("1", "30.0", "-5.0"),
        ("2", "25.0", "50.01"),
        ("1", "40.0", "100.0"),
    ],
)
def test_rn01_rejects_negative_or_excessive_discount(
    qty: str, unit_price: str, invalid_discount: str
) -> None:
    """Prova que discount < 0 ou discount > quantity * unit_price é rejeitado."""
    csv_content = (
        f"{CSV_HEADER}\n"
        f"ORD-001,2026-11-01T18:00:00Z,Burger,Burgers,{qty},{unit_price},{invalid_discount},10.0,completed,balcao\n"
    )
    with pytest.raises(CSVValidationError) as exc_info:
        validate_and_parse_csv(csv_content)

    errors = exc_info.value.errors
    assert any(err["row"] == 2 and err["column"] == "discount" for err in errors)


def test_rn01_rejects_negative_prep_time_minutes() -> None:
    """Prova que prep_time_minutes < 0 é rejeitado na coluna 'prep_time_minutes'."""
    csv_content = (
        f"{CSV_HEADER}\n"
        "ORD-001,2026-11-01T18:00:00Z,Burger,Burgers,1,30.0,0.0,-0.5,completed,balcao\n"
    )
    with pytest.raises(CSVValidationError) as exc_info:
        validate_and_parse_csv(csv_content)

    errors = exc_info.value.errors
    assert len(errors) == 1
    assert errors[0]["row"] == 2
    assert errors[0]["column"] == "prep_time_minutes"


@pytest.mark.parametrize("invalid_status", ["paid", "cancelled", "delivered", "done", "active"])
def test_rn01_rejects_invalid_status_enum(invalid_status: str) -> None:
    """Prova que status fora de {'completed', 'canceled'} (ex.: 'paid', 'cancelled') é rejeitado."""
    csv_content = (
        f"{CSV_HEADER}\n"
        f"ORD-001,2026-11-01T18:00:00Z,Burger,Burgers,1,30.0,0.0,12.0,{invalid_status},balcao\n"
    )
    with pytest.raises(CSVValidationError) as exc_info:
        validate_and_parse_csv(csv_content)

    errors = exc_info.value.errors
    assert len(errors) == 1
    assert errors[0]["row"] == 2
    assert errors[0]["column"] == "status"


@pytest.mark.parametrize("invalid_channel", ["ifood", "presencial", "loja", "takeaway", "whatsapp"])
def test_rn01_rejects_invalid_channel_enum(invalid_channel: str) -> None:
    """Prova que channel fora de {'balcao', 'delivery', 'app'} (ex.: 'ifood') é rejeitado."""
    csv_content = (
        f"{CSV_HEADER}\n"
        f"ORD-001,2026-11-01T18:00:00Z,Burger,Burgers,1,30.0,0.0,12.0,completed,{invalid_channel}\n"
    )
    with pytest.raises(CSVValidationError) as exc_info:
        validate_and_parse_csv(csv_content)

    errors = exc_info.value.errors
    assert len(errors) == 1
    assert errors[0]["row"] == 2
    assert errors[0]["column"] == "channel"


def test_rn01_rejects_intra_order_inconsistency_for_status_and_channel() -> None:
    """
    Prova a Invariante de Consistência Intra-Pedido (RN-01):
    linhas com o mesmo order_id não podem ter status ou channel divergentes.
    """
    csv_content = (
        f"{CSV_HEADER}\n"
        "ORD-777,2026-11-01T18:00:00Z,Burger,Burgers,1,40.0,0.0,15.0,completed,delivery\n"
        "ORD-777,2026-11-01T18:00:00Z,Batata,Porcoes,1,20.0,0.0,10.0,canceled,app\n"
    )
    with pytest.raises(CSVValidationError) as exc_info:
        validate_and_parse_csv(csv_content)

    errors = exc_info.value.errors
    assert len(errors) == 2
    assert {err["column"] for err in errors} == {"status", "channel"}
    assert all(err["row"] == 3 for err in errors)


def test_rn01_collects_multiple_errors_across_rows_without_truncating() -> None:
    """
    Prova que o validador não interrompe na primeira linha inválida e reporta a numeração
    1-indexed correta (linha 2, linha 4, etc.).
    """
    csv_content = (
        f"{CSV_HEADER}\n"
        "ORD-001,data-invalida,Burger,Burgers,0,30.0,0.0,15.0,completed,delivery\n"
        "ORD-002,2026-11-01T18:10:00Z,Batata,Porcoes,1,20.0,0.0,10.0,completed,balcao\n"
        "ORD-003,2026-11-01T18:20:00Z,Refri,Bebidas,1,-5.0,0.0,-2.0,paid,ifood\n"
    )
    with pytest.raises(CSVValidationError) as exc_info:
        validate_and_parse_csv(csv_content)

    errors = exc_info.value.errors
    row2_cols = {e["column"] for e in errors if e["row"] == 2}
    row4_cols = {e["column"] for e in errors if e["row"] == 4}

    assert row2_cols == {"timestamp", "quantity"}
    assert row4_cols == {"unit_price", "prep_time_minutes", "status", "channel"}
    assert not any(e["row"] == 3 for e in errors)
