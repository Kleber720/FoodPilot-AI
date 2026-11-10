"""Validação estrutural e de domínio do CSV de pedidos (RN-01)."""

import csv
import io
import math
from typing import Any

import pandas as pd

from data_pipeline.exceptions import CSVValidationError

REQUIRED_COLUMNS: tuple[str, ...] = (
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
)

VALID_STATUSES: frozenset[str] = frozenset({"completed", "canceled"})
VALID_CHANNELS: frozenset[str] = frozenset({"balcao", "delivery", "app"})


def _parse_int_strict(raw_value: str) -> int | None:
    """Converte string para int estrito (rejeita decimais como '1.5' ou '2.0' e booleanos)."""
    cleaned = raw_value.strip()
    if not cleaned:
        return None
    try:
        return int(cleaned)
    except ValueError:
        return None


def _parse_float_strict(raw_value: str) -> float | None:
    """Converte string para float finito (rejeita NaN, Inf e strings inválidas)."""
    cleaned = raw_value.strip()
    if not cleaned:
        return None
    try:
        val = float(cleaned)
    except ValueError:
        return None
    if math.isnan(val) or math.isinf(val):
        return None
    return val


def _is_valid_timestamp(raw_value: str) -> bool:
    """Verifica se a string representa uma data/hora válida (ISO-8601 ou formato padrão)."""
    cleaned = raw_value.strip()
    if not cleaned or len(cleaned) < 8:
        return False
    # Rejeita números puros que pandas interpretaria como epoch nanoseconds
    if cleaned.lstrip("+-").isdigit():
        return False
    try:
        parsed = pd.to_datetime(cleaned, errors="raise")
        return not pd.isna(parsed)
    except (ValueError, TypeError):
        return False


def validate_and_parse_csv(content: bytes | str) -> pd.DataFrame:
    """
    Valida o conteúdo bruto de um arquivo CSV de pedidos e retorna um DataFrame tipado.

    Cumpre integralmente a regra RN-01:
    - Aceita `bytes` (decodificando em `utf-8-sig` / `utf-8`) ou `str`.
    - Verifica se o arquivo não está vazio e se possui cabeçalho com as 10 colunas obrigatórias.
    - Coleta todos os erros de validação por linha/coluna (1-indexed, cabeçalho = 1, dados >= 2).
    - Valida consistência intra-pedido (`status` e `channel` únicos por `order_id`).
    - Retorna um `pd.DataFrame` tipado e limpo.
    """
    if isinstance(content, bytes):
        if len(content) == 0 or content.strip() == b"":
            raise CSVValidationError(
                detail="Arquivo CSV inválido: foram encontrados erros de validação.",
                errors=[
                    {
                        "row": None,
                        "column": None,
                        "message": "O arquivo CSV enviado está vazio.",
                    }
                ],
            )
        try:
            text = content.decode("utf-8-sig")
        except UnicodeDecodeError as exc:
            raise CSVValidationError(
                detail="Arquivo CSV inválido: codificação de caracteres não suportada (esperado UTF-8).",
                errors=[
                    {
                        "row": None,
                        "column": None,
                        "message": "Não foi possível decodificar o arquivo como texto UTF-8 válido.",
                    }
                ],
            ) from exc
    elif isinstance(content, str):
        text = content.lstrip("\ufeff")
        if not text.strip():
            raise CSVValidationError(
                detail="Arquivo CSV inválido: foram encontrados erros de validação.",
                errors=[
                    {
                        "row": None,
                        "column": None,
                        "message": "O arquivo CSV enviado está vazio.",
                    }
                ],
            )
    else:
        raise CSVValidationError(
            detail="Arquivo CSV inválido: conteúdo em formato inesperado.",
            errors=[
                {
                    "row": None,
                    "column": None,
                    "message": "O conteúdo do arquivo deve ser bytes ou string UTF-8.",
                }
            ],
        )

    try:
        reader = list(csv.reader(io.StringIO(text)))
    except csv.Error as exc:
        raise CSVValidationError(
            detail="Arquivo CSV inválido: falha de formatação estrutural do CSV.",
            errors=[
                {
                    "row": None,
                    "column": None,
                    "message": f"Erro de leitura da estrutura CSV: {exc}",
                }
            ],
        ) from exc

    if not reader:
        raise CSVValidationError(
            detail="Arquivo CSV inválido: foram encontrados erros de validação.",
            errors=[
                {
                    "row": None,
                    "column": None,
                    "message": "O arquivo CSV enviado está vazio.",
                }
            ],
        )

    raw_header = reader[0]
    header = [col.strip() for col in raw_header]

    # 1. Validar presença de todas as 10 colunas obrigatórias no cabeçalho
    missing_errors: list[dict[str, Any]] = []
    header_set = set(header)
    for req_col in REQUIRED_COLUMNS:
        if req_col not in header_set:
            missing_errors.append(
                {
                    "row": None,
                    "column": req_col,
                    "message": f"Coluna obrigatória '{req_col}' ausente no cabeçalho do CSV.",
                }
            )

    if missing_errors:
        raise CSVValidationError(
            detail="Arquivo CSV inválido: foram encontrados erros de validação.",
            errors=missing_errors,
        )

    # Mapear índice de cada coluna obrigatória no cabeçalho
    col_idx: dict[str, int] = {col_name: header.index(col_name) for col_name in REQUIRED_COLUMNS}

    # Filtrar linhas de dados (ignorando apenas linhas 100% em branco sem separadores, ex.: newline final)
    data_rows: list[tuple[int, list[str]]] = []
    for row_num, row_values in enumerate(reader[1:], start=2):
        if len(row_values) == 0:
            continue
        data_rows.append((row_num, row_values))

    if not data_rows:
        raise CSVValidationError(
            detail="Arquivo CSV inválido: foram encontrados erros de validação.",
            errors=[
                {
                    "row": None,
                    "column": None,
                    "message": "O arquivo CSV contém apenas o cabeçalho e nenhuma linha de dados.",
                }
            ],
        )

    errors: list[dict[str, Any]] = []
    parsed_records: list[dict[str, Any]] = []

    # Rastreamento para Invariante de Consistência Intra-Pedido (order_id -> (status, channel))
    order_status_seen: dict[str, str] = {}
    order_channel_seen: dict[str, str] = {}

    expected_cols_count = len(header)

    for row_num, row_values in data_rows:
        if len(row_values) != expected_cols_count:
            errors.append(
                {
                    "row": row_num,
                    "column": None,
                    "message": (
                        f"Número incorreto de colunas na linha {row_num}: "
                        f"esperado {expected_cols_count}, recebido {len(row_values)}."
                    ),
                }
            )
            continue

        raw_order_id = row_values[col_idx["order_id"]].strip()
        raw_timestamp = row_values[col_idx["timestamp"]].strip()
        raw_item_name = row_values[col_idx["item_name"]].strip()
        raw_category = row_values[col_idx["category"]].strip()
        raw_quantity = row_values[col_idx["quantity"]].strip()
        raw_unit_price = row_values[col_idx["unit_price"]].strip()
        raw_discount = row_values[col_idx["discount"]].strip()
        raw_prep_time = row_values[col_idx["prep_time_minutes"]].strip()
        raw_status = row_values[col_idx["status"]].strip()
        raw_channel = row_values[col_idx["channel"]].strip()

        row_has_error = False

        # 1. order_id
        if not raw_order_id:
            errors.append(
                {
                    "row": row_num,
                    "column": "order_id",
                    "message": "O campo 'order_id' é obrigatório e não pode ser vazio.",
                }
            )
            row_has_error = True

        # 2. timestamp
        if not raw_timestamp:
            errors.append(
                {
                    "row": row_num,
                    "column": "timestamp",
                    "message": "O campo 'timestamp' é obrigatório e não pode ser vazio.",
                }
            )
            row_has_error = True
        elif not _is_valid_timestamp(raw_timestamp):
            errors.append(
                {
                    "row": row_num,
                    "column": "timestamp",
                    "message": f"Formato de data/hora inválido em 'timestamp' (recebido: '{raw_timestamp}').",
                }
            )
            row_has_error = True

        # 3. item_name
        if not raw_item_name:
            errors.append(
                {
                    "row": row_num,
                    "column": "item_name",
                    "message": "O campo 'item_name' é obrigatório e não pode ser vazio.",
                }
            )
            row_has_error = True

        # 4. category
        if not raw_category:
            errors.append(
                {
                    "row": row_num,
                    "column": "category",
                    "message": "O campo 'category' é obrigatório e não pode ser vazio.",
                }
            )
            row_has_error = True

        # 5. quantity (int >= 1)
        qty_val: int | None = None
        if not raw_quantity:
            errors.append(
                {
                    "row": row_num,
                    "column": "quantity",
                    "message": "O campo 'quantity' é obrigatório e não pode ser vazio.",
                }
            )
            row_has_error = True
        else:
            qty_val = _parse_int_strict(raw_quantity)
            if qty_val is None:
                errors.append(
                    {
                        "row": row_num,
                        "column": "quantity",
                        "message": (
                            f"O campo 'quantity' deve ser um número inteiro estritamente positivo "
                            f"(recebido: '{raw_quantity}')."
                        ),
                    }
                )
                row_has_error = True
            elif qty_val < 1:
                errors.append(
                    {
                        "row": row_num,
                        "column": "quantity",
                        "message": (
                            f"Valor numérico em 'quantity' deve ser maior ou igual a 1 "
                            f"(recebido: {qty_val})."
                        ),
                    }
                )
                row_has_error = True

        # 6. unit_price (float > 0.0)
        unit_price_val: float | None = None
        if not raw_unit_price:
            errors.append(
                {
                    "row": row_num,
                    "column": "unit_price",
                    "message": "O campo 'unit_price' é obrigatório e não pode ser vazio.",
                }
            )
            row_has_error = True
        else:
            unit_price_val = _parse_float_strict(raw_unit_price)
            if unit_price_val is None:
                errors.append(
                    {
                        "row": row_num,
                        "column": "unit_price",
                        "message": f"O campo 'unit_price' deve ser um valor numérico válido (recebido: '{raw_unit_price}').",
                    }
                )
                row_has_error = True
            elif unit_price_val <= 0.0:
                errors.append(
                    {
                        "row": row_num,
                        "column": "unit_price",
                        "message": f"Valor numérico deve ser estritamente maior que zero (recebido: {unit_price_val}).",
                    }
                )
                row_has_error = True

        # 7. discount (0.0 <= discount <= quantity * unit_price)
        discount_val: float | None = None
        if not raw_discount:
            errors.append(
                {
                    "row": row_num,
                    "column": "discount",
                    "message": "O campo 'discount' é obrigatório e não pode ser vazio.",
                }
            )
            row_has_error = True
        else:
            discount_val = _parse_float_strict(raw_discount)
            if discount_val is None:
                errors.append(
                    {
                        "row": row_num,
                        "column": "discount",
                        "message": f"O campo 'discount' deve ser um valor numérico válido (recebido: '{raw_discount}').",
                    }
                )
                row_has_error = True
            elif discount_val < 0.0:
                errors.append(
                    {
                        "row": row_num,
                        "column": "discount",
                        "message": f"O campo 'discount' não pode ser negativo (recebido: {discount_val}).",
                    }
                )
                row_has_error = True
            elif (
                qty_val is not None
                and qty_val >= 1
                and unit_price_val is not None
                and unit_price_val > 0.0
            ):
                line_subtotal = round(qty_val * unit_price_val, 6)
                if discount_val > line_subtotal + 1e-9:
                    errors.append(
                        {
                            "row": row_num,
                            "column": "discount",
                            "message": (
                                f"O desconto ({discount_val}) não pode ser maior que o subtotal "
                                f"da linha ({round(line_subtotal, 2)})."
                            ),
                        }
                    )
                    row_has_error = True

        # 8. prep_time_minutes (float >= 0.0)
        prep_time_val: float | None = None
        if not raw_prep_time:
            errors.append(
                {
                    "row": row_num,
                    "column": "prep_time_minutes",
                    "message": "O campo 'prep_time_minutes' é obrigatório e não pode ser vazio.",
                }
            )
            row_has_error = True
        else:
            prep_time_val = _parse_float_strict(raw_prep_time)
            if prep_time_val is None:
                errors.append(
                    {
                        "row": row_num,
                        "column": "prep_time_minutes",
                        "message": (
                            f"O campo 'prep_time_minutes' deve ser um valor numérico válido "
                            f"(recebido: '{raw_prep_time}')."
                        ),
                    }
                )
                row_has_error = True
            elif prep_time_val < 0.0:
                errors.append(
                    {
                        "row": row_num,
                        "column": "prep_time_minutes",
                        "message": (
                            f"O campo 'prep_time_minutes' não pode ser negativo "
                            f"(recebido: {prep_time_val})."
                        ),
                    }
                )
                row_has_error = True

        # 9. status ('completed' | 'canceled')
        status_valid = False
        if not raw_status:
            errors.append(
                {
                    "row": row_num,
                    "column": "status",
                    "message": "O campo 'status' é obrigatório e não pode ser vazio.",
                }
            )
            row_has_error = True
        elif raw_status not in VALID_STATUSES:
            errors.append(
                {
                    "row": row_num,
                    "column": "status",
                    "message": (
                        f"Valor inválido para 'status' (recebido: '{raw_status}'). "
                        "Valores permitidos: 'completed', 'canceled'."
                    ),
                }
            )
            row_has_error = True
        else:
            status_valid = True

        # 10. channel ('balcao' | 'delivery' | 'app')
        channel_valid = False
        if not raw_channel:
            errors.append(
                {
                    "row": row_num,
                    "column": "channel",
                    "message": "O campo 'channel' é obrigatório e não pode ser vazio.",
                }
            )
            row_has_error = True
        elif raw_channel not in VALID_CHANNELS:
            errors.append(
                {
                    "row": row_num,
                    "column": "channel",
                    "message": (
                        f"Valor inválido para 'channel' (recebido: '{raw_channel}'). "
                        "Valores permitidos: 'balcao', 'delivery', 'app'."
                    ),
                }
            )
            row_has_error = True
        else:
            channel_valid = True

        # 11. Consistência intra-pedido (mesmo order_id deve ter mesmo status e mesmo channel)
        if raw_order_id and status_valid:
            if raw_order_id in order_status_seen:
                expected_status = order_status_seen[raw_order_id]
                if raw_status != expected_status:
                    errors.append(
                        {
                            "row": row_num,
                            "column": "status",
                            "message": (
                                f"Inconsistência intra-pedido para order_id '{raw_order_id}': "
                                f"status '{raw_status}' diverge de '{expected_status}' no mesmo pedido."
                            ),
                        }
                    )
                    row_has_error = True
            else:
                order_status_seen[raw_order_id] = raw_status

        if raw_order_id and channel_valid:
            if raw_order_id in order_channel_seen:
                expected_channel = order_channel_seen[raw_order_id]
                if raw_channel != expected_channel:
                    errors.append(
                        {
                            "row": row_num,
                            "column": "channel",
                            "message": (
                                f"Inconsistência intra-pedido para order_id '{raw_order_id}': "
                                f"channel '{raw_channel}' diverge de '{expected_channel}' no mesmo pedido."
                            ),
                        }
                    )
                    row_has_error = True
            else:
                order_channel_seen[raw_order_id] = raw_channel

        if not row_has_error:
            parsed_records.append(
                {
                    "order_id": raw_order_id,
                    "timestamp": raw_timestamp,
                    "item_name": raw_item_name,
                    "category": raw_category,
                    "quantity": int(qty_val),  # type: ignore[arg-type]
                    "unit_price": float(unit_price_val),  # type: ignore[arg-type]
                    "discount": float(discount_val),  # type: ignore[arg-type]
                    "prep_time_minutes": float(prep_time_val),  # type: ignore[arg-type]
                    "status": raw_status,
                    "channel": raw_channel,
                }
            )

    if errors:
        raise CSVValidationError(
            detail="Arquivo CSV inválido: foram encontrados erros de validação.",
            errors=errors,
        )

    df = pd.DataFrame(parsed_records, columns=list(REQUIRED_COLUMNS))
    df["order_id"] = df["order_id"].astype(str)
    df["timestamp"] = df["timestamp"].astype(str)
    df["item_name"] = df["item_name"].astype(str)
    df["category"] = df["category"].astype(str)
    df["quantity"] = df["quantity"].astype("int64")
    df["unit_price"] = df["unit_price"].astype("float64")
    df["discount"] = df["discount"].astype("float64")
    df["prep_time_minutes"] = df["prep_time_minutes"].astype("float64")
    df["status"] = df["status"].astype(str)
    df["channel"] = df["channel"].astype(str)

    return df
