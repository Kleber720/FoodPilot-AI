"""Testes automatizados para o motor determinístico de métricas (RN-03, RN-04, RN-05 e RN-06)."""

from typing import Any

from data_pipeline import calculate_metrics, validate_and_parse_csv


def _make_record(
    order_id: str = "ORD-001",
    timestamp: str = "2026-11-01T18:00:00Z",
    item_name: str = "Burger Classico",
    category: str = "Burgers",
    quantity: int = 1,
    unit_price: float = 30.0,
    discount: float = 0.0,
    prep_time_minutes: float = 15.0,
    status: str = "completed",
    channel: str = "balcao",
) -> dict[str, Any]:
    """Cria um registro válido de item de pedido para montagem de cenários de teste."""
    return {
        "order_id": order_id,
        "timestamp": timestamp,
        "item_name": item_name,
        "category": category,
        "quantity": quantity,
        "unit_price": unit_price,
        "discount": discount,
        "prep_time_minutes": prep_time_minutes,
        "status": status,
        "channel": channel,
    }


# ============================================================================
# RN-03 — Faturamento Bruto, Descontos, Faturamento Líquido e Perda
# ============================================================================


def test_rn03_canonical_dataset_financial_metrics(sample_csv_bytes: bytes) -> None:
    """
    Prova que o cálculo financeiro em `data/sample_orders.csv` produz exatamente os
    valores auditados no Data Card (`gross_revenue=5000.0`, `discount_total=250.0`,
    `net_revenue=4750.0`, `canceled_revenue_loss=514.0`).
    """
    df = validate_and_parse_csv(sample_csv_bytes)
    result = calculate_metrics(df)

    fin = result["financials"]
    summary = result["summary_metrics"]

    assert result["total_rows"] == 82
    assert fin["gross_revenue"] == 5000.0
    assert fin["discount_total"] == 250.0
    assert fin["net_revenue"] == 4750.0
    assert fin["canceled_revenue_loss"] == 514.0
    assert round(fin["gross_revenue"] - fin["discount_total"], 2) == fin["net_revenue"]

    assert summary["gross_revenue"] == 5000.0
    assert summary["discount_total"] == 250.0
    assert summary["net_revenue"] == 4750.0
    assert summary["canceled_revenue_loss"] == 514.0


def test_rn03_canceled_orders_never_contaminate_revenue_or_discounts() -> None:
    """
    Prova a Invariante de Segregação de Cancelados (RN-03):
    itens com status == 'canceled' jamais somam em gross_revenue, discount_total ou net_revenue.
    """
    records = [
        _make_record(
            order_id="ORD-VALID",
            item_name="Burger Duplo",
            quantity=2,
            unit_price=50.0,
            discount=10.0,
            status="completed",
        ),
        _make_record(
            order_id="ORD-CANC-1",
            item_name="Combo Familia",
            quantity=5,
            unit_price=100.0,
            discount=50.0,
            status="canceled",
        ),
        _make_record(
            order_id="ORD-CANC-2",
            item_name="Sobremesa",
            quantity=3,
            unit_price=20.0,
            discount=5.0,
            status="canceled",
        ),
    ]
    result = calculate_metrics(records)
    fin = result["financials"]

    assert fin["gross_revenue"] == 100.0
    assert fin["discount_total"] == 10.0
    assert fin["net_revenue"] == 90.0
    assert fin["canceled_revenue_loss"] == 560.0


def test_rn03_only_canceled_orders_returns_zero_revenues() -> None:
    """
    Prova o caso limite de RN-03: se o lote contiver apenas pedidos cancelados,
    gross_revenue, discount_total e net_revenue são 0.0.
    """
    records = [
        _make_record(
            order_id="ORD-C1",
            quantity=2,
            unit_price=45.0,
            discount=5.0,
            status="canceled",
        ),
        _make_record(
            order_id="ORD-C2",
            quantity=1,
            unit_price=30.0,
            discount=0.0,
            status="canceled",
        ),
    ]
    result = calculate_metrics(records)
    fin = result["financials"]

    assert fin["valid_orders_count"] == 0
    assert fin["canceled_orders_count"] == 2
    assert fin["gross_revenue"] == 0.0
    assert fin["discount_total"] == 0.0
    assert fin["net_revenue"] == 0.0
    assert fin["canceled_revenue_loss"] == 120.0
    assert result["abc_curve"] == []
    assert result["summary_metrics"]["top_abc_item"] is None


# ============================================================================
# RN-04 — Ticket Médio por Pedido Concluído Único (order_id)
# ============================================================================


def test_rn04_canonical_dataset_average_ticket_and_order_counts(
    sample_csv_bytes: bytes,
) -> None:
    """
    Prova em `data/sample_orders.csv` que valid_orders_count == 50, canceled_orders_count == 5,
    average_ticket_gross == 100.0 e average_ticket_net == 95.0.
    """
    df = validate_and_parse_csv(sample_csv_bytes)
    result = calculate_metrics(df)
    fin = result["financials"]

    assert fin["valid_orders_count"] == 50
    assert fin["canceled_orders_count"] == 5
    assert fin["average_ticket_gross"] == 100.0
    assert fin["average_ticket_net"] == 95.0


def test_rn04_multi_item_order_counts_as_single_order_in_denominator() -> None:
    """
    Prova que o denominador do ticket médio é a contagem de `order_id` distintos concluídos,
    e NUNCA o número de linhas (`total_rows`) nem a soma de `quantity`.
    """
    records = [
        # Pedido 1 (ORD-10): 3 linhas de itens -> Bruto = 60 + 20 + 30 = 110.0, Desconto = 10.0, Líquido = 100.0
        _make_record(order_id="ORD-10", item_name="Item A", quantity=2, unit_price=30.0, discount=10.0),
        _make_record(order_id="ORD-10", item_name="Item B", quantity=1, unit_price=20.0, discount=0.0),
        _make_record(order_id="ORD-10", item_name="Item C", quantity=3, unit_price=10.0, discount=0.0),
        # Pedido 2 (ORD-20): 1 linha de item -> Bruto = 90.0, Desconto = 0.0, Líquido = 90.0
        _make_record(order_id="ORD-20", item_name="Item D", quantity=1, unit_price=90.0, discount=0.0),
    ]
    result = calculate_metrics(records)
    fin = result["financials"]

    assert result["total_rows"] == 4
    assert fin["valid_orders_count"] == 2
    assert fin["gross_revenue"] == 200.0
    assert fin["net_revenue"] == 190.0
    # Se dividisse por 4 linhas daria 50.0; se dividisse por 7 unidades daria 28.57; por 2 pedidos dá 100.0
    assert fin["average_ticket_gross"] == 100.0
    assert fin["average_ticket_net"] == 95.0


def test_rn04_zero_valid_orders_returns_zero_ticket_without_division_error() -> None:
    """Prova que quando valid_orders_count == 0, o ticket médio retorna 0.0 sem ZeroDivisionError."""
    only_canceled = [
        _make_record(order_id="ORD-C99", status="canceled", quantity=2, unit_price=40.0),
    ]
    res_canceled = calculate_metrics(only_canceled)
    assert res_canceled["financials"]["average_ticket_gross"] == 0.0
    assert res_canceled["financials"]["average_ticket_net"] == 0.0

    res_empty = calculate_metrics([])
    assert res_empty["financials"]["average_ticket_gross"] == 0.0
    assert res_empty["financials"]["average_ticket_net"] == 0.0


# ============================================================================
# RN-05 — Curva ABC de Produtos
# ============================================================================


def test_rn05_canonical_dataset_abc_curve_classification_and_ordering(
    sample_csv_bytes: bytes,
) -> None:
    """
    Prova a Curva ABC exata sobre `data/sample_orders.csv` conforme seção 5.2 do Data Card.
    """
    df = validate_and_parse_csv(sample_csv_bytes)
    result = calculate_metrics(df)
    abc = result["abc_curve"]

    assert result["summary_metrics"]["top_abc_item"] == "Combo Burger Duplo Artesanal"
    assert len(abc) == 8

    expected_abc = [
        ("Combo Burger Duplo Artesanal", "Combos", 25, 2000.0, 40.0, 40.0, "A"),
        ("Burger Trilogia Defumado", "Burgers", 24, 1200.0, 24.0, 64.0, "A"),
        ("Smash Bacon Duplo", "Burgers", 19, 760.0, 15.2, 79.2, "A"),
        ("Porcao Batata Rustica Trufada", "Porcoes", 14, 490.0, 9.8, 89.0, "B"),
        ("Milkshake Pistache Artesanal", "Sobremesas", 11, 275.0, 5.5, 94.5, "B"),
        ("Onion Rings Crocante", "Porcoes", 6, 150.0, 3.0, 97.5, "C"),
        ("Brownie Belga com Sorvete", "Sobremesas", 4, 80.0, 1.6, 99.1, "C"),
        ("Refrigerante Lata 350ml", "Bebidas", 5, 45.0, 0.9, 100.0, "C"),
    ]

    for actual, (name, cat, qty, rev, share, cum_share, abc_cls) in zip(
        abc, expected_abc, strict=True
    ):
        assert actual["item_name"] == name
        assert actual["category"] == cat
        assert actual["quantity_sold"] == qty
        assert actual["revenue"] == rev
        assert actual["revenue_share_pct"] == share
        assert actual["cumulative_share_pct"] == cum_share
        assert actual["abc_class"] == abc_cls

    # Fechamento contábil da Curva ABC
    assert round(sum(item["revenue"] for item in abc), 2) == result["financials"]["gross_revenue"]
    assert abc[-1]["cumulative_share_pct"] == 100.0


def test_rn05_tie_breaking_by_item_name_ascending_and_excludes_canceled_items() -> None:
    """
    Prova que itens empatados em revenue são ordenados por item_name crescente
    e itens que só aparecem em pedidos cancelados não entram na Curva ABC.
    """
    records = [
        _make_record(order_id="ORD-1", item_name="Zeta Burger", quantity=1, unit_price=50.0, status="completed"),
        _make_record(order_id="ORD-2", item_name="Alfa Burger", quantity=2, unit_price=25.0, status="completed"),
        _make_record(order_id="ORD-3", item_name="Item Cancelado Exclusivo", quantity=10, unit_price=100.0, status="canceled"),
    ]
    result = calculate_metrics(records)
    abc = result["abc_curve"]

    assert [item["item_name"] for item in abc] == ["Alfa Burger", "Zeta Burger"]
    assert abc[0]["revenue"] == 50.0
    assert abc[1]["revenue"] == 50.0


def test_rn05_single_leader_above_80_pct_still_gets_class_a() -> None:
    """
    Prova o caso limite de RN-05: se o produto líder no índice 0 concentrar sozinho 85.0%
    do faturamento (> 80.0%), ainda assim recebe abc_class == 'A'.
    """
    records = [
        _make_record(order_id="ORD-1", item_name="Carro Chefe", quantity=1, unit_price=850.0),
        _make_record(order_id="ORD-2", item_name="Segundo Lugar", quantity=1, unit_price=100.0),
        _make_record(order_id="ORD-3", item_name="Terceiro Lugar", quantity=1, unit_price=50.0),
    ]
    result = calculate_metrics(records)
    abc = result["abc_curve"]

    assert abc[0]["item_name"] == "Carro Chefe"
    assert abc[0]["cumulative_share_pct"] == 85.0
    assert abc[0]["abc_class"] == "A"

    assert abc[1]["item_name"] == "Segundo Lugar"
    assert abc[1]["cumulative_share_pct"] == 95.0
    assert abc[1]["abc_class"] == "B"

    assert abc[2]["item_name"] == "Terceiro Lugar"
    assert abc[2]["cumulative_share_pct"] == 100.0
    assert abc[2]["abc_class"] == "C"


# ============================================================================
# RN-06 — Gargalos Operacionais, Anomalias e Quebras por Canal/Categoria
# ============================================================================


def test_rn06_canonical_dataset_bottlenecks_anomalies_and_breakdowns(
    sample_csv_bytes: bytes,
) -> None:
    """
    Prova em `data/sample_orders.csv` todos os indicadores de `bottlenecks`, `anomalies`,
    `by_channel` e `by_category` documentados nas seções 5.3 e 5.4 do Data Card.
    """
    df = validate_and_parse_csv(sample_csv_bytes)
    result = calculate_metrics(df)

    bottlenecks = result["bottlenecks"]
    assert bottlenecks["prep_time_threshold_minutes"] == 30
    assert bottlenecks["delayed_orders_count"] == 5
    assert bottlenecks["delayed_items_count"] == 6
    assert bottlenecks["average_prep_time_minutes"] == 18.55
    assert bottlenecks["max_prep_time_minutes"] == 46.0

    assert bottlenecks["delayed_by_category"] == [
        {"category": "Burgers", "delayed_items_count": 4, "avg_prep_time_minutes": 39.0},
        {"category": "Combos", "delayed_items_count": 2, "avg_prep_time_minutes": 40.0},
    ]

    assert bottlenecks["canceled_by_channel"] == [
        {
            "channel": "delivery",
            "canceled_orders_count": 4,
            "total_orders_count": 20,
            "cancellation_rate_pct": 20.0,
            "canceled_revenue_loss": 474.0,
        },
        {
            "channel": "app",
            "canceled_orders_count": 1,
            "total_orders_count": 20,
            "cancellation_rate_pct": 5.0,
            "canceled_revenue_loss": 40.0,
        },
        {
            "channel": "balcao",
            "canceled_orders_count": 0,
            "total_orders_count": 15,
            "cancellation_rate_pct": 0.0,
            "canceled_revenue_loss": 0.0,
        },
    ]

    assert bottlenecks["canceled_by_item"] == [
        {
            "item_name": "Combo Burger Duplo Artesanal",
            "category": "Combos",
            "canceled_quantity": 3,
            "canceled_revenue_loss": 240.0,
        },
        {
            "item_name": "Burger Trilogia Defumado",
            "category": "Burgers",
            "canceled_quantity": 3,
            "canceled_revenue_loss": 150.0,
        },
        {
            "item_name": "Smash Bacon Duplo",
            "category": "Burgers",
            "canceled_quantity": 2,
            "canceled_revenue_loss": 80.0,
        },
        {
            "item_name": "Porcao Batata Rustica Trufada",
            "category": "Porcoes",
            "canceled_quantity": 1,
            "canceled_revenue_loss": 35.0,
        },
        {
            "item_name": "Refrigerante Lata 350ml",
            "category": "Bebidas",
            "canceled_quantity": 1,
            "canceled_revenue_loss": 9.0,
        },
    ]

    assert len(bottlenecks["anomalies"]) == 3
    assert bottlenecks["anomalies"][0]["type"] == "high_prep_time"
    assert bottlenecks["anomalies"][0]["severity"] == "warning"
    assert bottlenecks["anomalies"][0]["dimension"] == "Burgers"
    assert bottlenecks["anomalies"][0]["metric_value"] == 39.0

    assert bottlenecks["anomalies"][1]["type"] == "high_prep_time"
    assert bottlenecks["anomalies"][1]["severity"] == "warning"
    assert bottlenecks["anomalies"][1]["dimension"] == "Combos"
    assert bottlenecks["anomalies"][1]["metric_value"] == 40.0

    assert bottlenecks["anomalies"][2]["type"] == "high_cancellation_rate"
    assert bottlenecks["anomalies"][2]["severity"] == "critical"
    assert bottlenecks["anomalies"][2]["dimension"] == "delivery"
    assert bottlenecks["anomalies"][2]["metric_value"] == 20.0

    assert result["by_channel"] == [
        {
            "channel": "delivery",
            "valid_orders_count": 16,
            "quantity_sold": 43,
            "gross_revenue": 2128.0,
            "discount_total": 90.0,
            "net_revenue": 2038.0,
            "revenue_share_pct": 42.91,
            "average_ticket_net": 127.38,
        },
        {
            "channel": "app",
            "valid_orders_count": 19,
            "quantity_sold": 41,
            "gross_revenue": 1823.0,
            "discount_total": 90.0,
            "net_revenue": 1733.0,
            "revenue_share_pct": 36.48,
            "average_ticket_net": 91.21,
        },
        {
            "channel": "balcao",
            "valid_orders_count": 15,
            "quantity_sold": 24,
            "gross_revenue": 1049.0,
            "discount_total": 70.0,
            "net_revenue": 979.0,
            "revenue_share_pct": 20.61,
            "average_ticket_net": 65.27,
        },
    ]

    assert result["by_category"] == [
        {
            "category": "Combos",
            "quantity_sold": 25,
            "gross_revenue": 2000.0,
            "discount_total": 120.0,
            "net_revenue": 1880.0,
            "revenue_share_pct": 39.58,
            "average_prep_time_minutes": 26.88,
        },
        {
            "category": "Burgers",
            "quantity_sold": 43,
            "gross_revenue": 1960.0,
            "discount_total": 85.0,
            "net_revenue": 1875.0,
            "revenue_share_pct": 39.47,
            "average_prep_time_minutes": 22.5,
        },
        {
            "category": "Porcoes",
            "quantity_sold": 20,
            "gross_revenue": 640.0,
            "discount_total": 30.0,
            "net_revenue": 610.0,
            "revenue_share_pct": 12.84,
            "average_prep_time_minutes": 12.5,
        },
        {
            "category": "Sobremesas",
            "quantity_sold": 15,
            "gross_revenue": 355.0,
            "discount_total": 15.0,
            "net_revenue": 340.0,
            "revenue_share_pct": 7.16,
            "average_prep_time_minutes": 6.89,
        },
        {
            "category": "Bebidas",
            "quantity_sold": 5,
            "gross_revenue": 45.0,
            "discount_total": 0.0,
            "net_revenue": 45.0,
            "revenue_share_pct": 0.95,
            "average_prep_time_minutes": 2.0,
        },
    ]


def test_rn06_boundary_conditions_prep_time_30_and_cancellation_rate_10() -> None:
    """
    Prova os casos limites estritos de fronteira da RN-06:
    - prep_time_minutes == 30.0 NÃO é atraso (apenas > 30.0 é atraso);
    - cancellation_rate_pct == 10.0% (1 em 10 pedidos) NÃO dispara anomalia (apenas > 10.0% dispara);
    - cancellation_rate_pct == 15.0% dispara 'warning' e >= 20.0% dispara 'critical'.
    """
    records = [
        # 9 pedidos concluídos no delivery com prep_time exato de 30.0 min (fronteira sem atraso)
        *[
            _make_record(
                order_id=f"ORD-DEL-{i}",
                prep_time_minutes=30.0,
                status="completed",
                channel="delivery",
            )
            for i in range(1, 10)
        ],
        # 1 pedido cancelado no delivery -> total = 10 pedidos, 1 cancelado = 10.0% exatos
        _make_record(
            order_id="ORD-DEL-10",
            prep_time_minutes=48.0,  # mesmo com 48 min, como é canceled, não entra em atraso de preparo
            status="canceled",
            channel="delivery",
        ),
    ]

    result = calculate_metrics(records)
    bottlenecks = result["bottlenecks"]

    assert bottlenecks["delayed_orders_count"] == 0
    assert bottlenecks["delayed_items_count"] == 0
    assert bottlenecks["delayed_by_category"] == []
    assert bottlenecks["canceled_by_channel"][0]["cancellation_rate_pct"] == 10.0
    assert bottlenecks["anomalies"] == []
