"""Construção determinística da Ficha de Fatos (RN-07) e Fallback de Recomendações (RN-09, RN-10)."""

from collections.abc import Mapping, Sequence
from typing import Any

from data_pipeline.metrics import (
    CANCELLATION_RATE_THRESHOLD_PCT,
    PREP_TIME_THRESHOLD_MINUTES,
)


def _format_fact_value(value: int | float, unit: str) -> str:
    """Formata o valor numérico de um fato segundo sua unidade oficial."""
    if unit == "BRL":
        return f"R$ {float(value):.2f}"
    if unit == "%":
        return f"{round(float(value), 2)}%"
    if unit == "min":
        return f"{round(float(value), 2)} min"
    return f"{int(value)}"


def _make_fact(
    fact_id: str,
    category: str,
    label: str,
    value: int | float,
    unit: str,
) -> dict[str, Any]:
    """Cria um dicionário de fato atômico padronizado com tipos nativos Python."""
    normalized_value: int | float
    if unit == "count":
        normalized_value = int(value)
    else:
        normalized_value = round(float(value), 2)

    return {
        "fact_id": str(fact_id),
        "category": str(category),
        "label": str(label),
        "value": normalized_value,
        "unit": str(unit),
        "formatted": _format_fact_value(normalized_value, unit),
    }


def _to_evidence(fact: Mapping[str, Any]) -> dict[str, Any]:
    """Extrai os campos de evidência exigidos pelo contrato a partir de um fato."""
    return {
        "fact_id": str(fact["fact_id"]),
        "label": str(fact["label"]),
        "value": int(fact["value"]) if fact["unit"] == "count" else round(float(fact["value"]), 2),
        "unit": str(fact["unit"]),
    }


def build_fact_sheet(metrics: Mapping[str, Any]) -> list[dict[str, Any]]:
    """
    Transforma o dicionário retornado por `calculate_metrics` em uma lista ordenada,
    pura e determinística de fatos atômicos rastreáveis por `fact_id` (RN-07).

    Segue estritamente o catálogo de identificadores da Seção 3.2 de `docs/contrato.md`.
    """
    facts: list[dict[str, Any]] = []

    financials: Mapping[str, Any] = metrics.get("financials", {})
    bottlenecks: Mapping[str, Any] = metrics.get("bottlenecks", {})
    by_channel: Sequence[Mapping[str, Any]] = metrics.get("by_channel", [])
    by_category: Sequence[Mapping[str, Any]] = metrics.get("by_category", [])
    abc_curve: Sequence[Mapping[str, Any]] = metrics.get("abc_curve", [])

    # 1. Limiares Operacionais (category = "threshold")
    prep_threshold = float(
        bottlenecks.get("prep_time_threshold_minutes", PREP_TIME_THRESHOLD_MINUTES)
    )
    facts.append(
        _make_fact(
            fact_id="thr.prep_time_minutes",
            category="threshold",
            label="Limite de tempo de preparo",
            value=prep_threshold,
            unit="min",
        )
    )
    facts.append(
        _make_fact(
            fact_id="thr.cancellation_rate_pct",
            category="threshold",
            label="Limite tolerado de taxa de cancelamento",
            value=float(CANCELLATION_RATE_THRESHOLD_PCT),
            unit="%",
        )
    )

    # 2. Indicadores Financeiros e Contagens Globais (category = "financials")
    total_rows = int(metrics.get("total_rows", 0))
    valid_orders = int(
        financials.get("valid_orders_count", metrics.get("valid_orders_count", 0))
    )
    canceled_orders = int(
        financials.get("canceled_orders_count", metrics.get("canceled_orders_count", 0))
    )
    gross_revenue = float(financials.get("gross_revenue", 0.0))
    discount_total = float(financials.get("discount_total", 0.0))
    net_revenue = float(financials.get("net_revenue", 0.0))
    canceled_loss = float(financials.get("canceled_revenue_loss", 0.0))
    avg_ticket_gross = float(financials.get("average_ticket_gross", 0.0))
    avg_ticket_net = float(financials.get("average_ticket_net", 0.0))

    facts.extend(
        [
            _make_fact(
                fact_id="fin.total_rows",
                category="financials",
                label="Total de itens registrados no lote",
                value=total_rows,
                unit="count",
            ),
            _make_fact(
                fact_id="fin.gross_revenue",
                category="financials",
                label="Faturamento bruto",
                value=gross_revenue,
                unit="BRL",
            ),
            _make_fact(
                fact_id="fin.discount_total",
                category="financials",
                label="Total de descontos",
                value=discount_total,
                unit="BRL",
            ),
            _make_fact(
                fact_id="fin.net_revenue",
                category="financials",
                label="Faturamento líquido",
                value=net_revenue,
                unit="BRL",
            ),
            _make_fact(
                fact_id="fin.valid_orders_count",
                category="financials",
                label="Pedidos concluídos",
                value=valid_orders,
                unit="count",
            ),
            _make_fact(
                fact_id="fin.canceled_orders_count",
                category="financials",
                label="Pedidos cancelados",
                value=canceled_orders,
                unit="count",
            ),
            _make_fact(
                fact_id="fin.canceled_revenue_loss",
                category="financials",
                label="Perda total por cancelamentos",
                value=canceled_loss,
                unit="BRL",
            ),
            _make_fact(
                fact_id="fin.average_ticket_gross",
                category="financials",
                label="Ticket médio bruto",
                value=avg_ticket_gross,
                unit="BRL",
            ),
            _make_fact(
                fact_id="fin.average_ticket_net",
                category="financials",
                label="Ticket médio líquido",
                value=avg_ticket_net,
                unit="BRL",
            ),
        ]
    )

    # 3. Gargalos Globais e por Categoria (category = "bottlenecks")
    facts.extend(
        [
            _make_fact(
                fact_id="bot.delayed_orders_count",
                category="bottlenecks",
                label="Pedidos concluídos com atraso de preparo",
                value=int(bottlenecks.get("delayed_orders_count", 0)),
                unit="count",
            ),
            _make_fact(
                fact_id="bot.delayed_items_count",
                category="bottlenecks",
                label="Itens concluídos com preparo acima do limite",
                value=int(bottlenecks.get("delayed_items_count", 0)),
                unit="count",
            ),
            _make_fact(
                fact_id="bot.average_prep_time_minutes",
                category="bottlenecks",
                label="Tempo médio global de preparo",
                value=float(bottlenecks.get("average_prep_time_minutes", 0.0)),
                unit="min",
            ),
            _make_fact(
                fact_id="bot.max_prep_time_minutes",
                category="bottlenecks",
                label="Tempo máximo de preparo registrado",
                value=float(bottlenecks.get("max_prep_time_minutes", 0.0)),
                unit="min",
            ),
        ]
    )

    for delay_entry in bottlenecks.get("delayed_by_category", []):
        cat_name = str(delay_entry["category"])
        facts.append(
            _make_fact(
                fact_id=f"bot.delay_cat.{cat_name}.delayed_items_count",
                category="bottlenecks",
                label=f"Itens atrasados em {cat_name}",
                value=int(delay_entry["delayed_items_count"]),
                unit="count",
            )
        )
        facts.append(
            _make_fact(
                fact_id=f"bot.delay_cat.{cat_name}.avg_prep_time_minutes",
                category="bottlenecks",
                label=f"Tempo médio dos itens atrasados em {cat_name}",
                value=float(delay_entry["avg_prep_time_minutes"]),
                unit="min",
            )
        )

    # 4. Cancelamentos por Canal (category = "channel_cancellation")
    for canc_ch in bottlenecks.get("canceled_by_channel", []):
        ch_name = str(canc_ch["channel"])
        facts.extend(
            [
                _make_fact(
                    fact_id=f"chan.{ch_name}.canceled_orders_count",
                    category="channel_cancellation",
                    label=f"Pedidos cancelados no canal {ch_name}",
                    value=int(canc_ch["canceled_orders_count"]),
                    unit="count",
                ),
                _make_fact(
                    fact_id=f"chan.{ch_name}.total_orders_count",
                    category="channel_cancellation",
                    label=f"Total de pedidos no canal {ch_name}",
                    value=int(canc_ch["total_orders_count"]),
                    unit="count",
                ),
                _make_fact(
                    fact_id=f"chan.{ch_name}.cancellation_rate_pct",
                    category="channel_cancellation",
                    label=f"Taxa de cancelamento no canal {ch_name}",
                    value=float(canc_ch["cancellation_rate_pct"]),
                    unit="%",
                ),
                _make_fact(
                    fact_id=f"chan.{ch_name}.canceled_revenue_loss",
                    category="channel_cancellation",
                    label=f"Perda por cancelamento no canal {ch_name}",
                    value=float(canc_ch["canceled_revenue_loss"]),
                    unit="BRL",
                ),
            ]
        )

    # 5. Desempenho de Vendas Concluídas por Canal (category = "by_channel")
    for ch_entry in by_channel:
        ch_name = str(ch_entry["channel"])
        facts.extend(
            [
                _make_fact(
                    fact_id=f"chan.{ch_name}.valid_orders_count",
                    category="by_channel",
                    label=f"Pedidos concluídos no canal {ch_name}",
                    value=int(ch_entry["valid_orders_count"]),
                    unit="count",
                ),
                _make_fact(
                    fact_id=f"chan.{ch_name}.quantity_sold",
                    category="by_channel",
                    label=f"Unidades vendidas no canal {ch_name}",
                    value=int(ch_entry["quantity_sold"]),
                    unit="count",
                ),
                _make_fact(
                    fact_id=f"chan.{ch_name}.gross_revenue",
                    category="by_channel",
                    label=f"Receita bruta no canal {ch_name}",
                    value=float(ch_entry["gross_revenue"]),
                    unit="BRL",
                ),
                _make_fact(
                    fact_id=f"chan.{ch_name}.discount_total",
                    category="by_channel",
                    label=f"Descontos no canal {ch_name}",
                    value=float(ch_entry["discount_total"]),
                    unit="BRL",
                ),
                _make_fact(
                    fact_id=f"chan.{ch_name}.net_revenue",
                    category="by_channel",
                    label=f"Receita líquida no canal {ch_name}",
                    value=float(ch_entry["net_revenue"]),
                    unit="BRL",
                ),
                _make_fact(
                    fact_id=f"chan.{ch_name}.revenue_share_pct",
                    category="by_channel",
                    label=f"Participação na receita líquida do canal {ch_name}",
                    value=float(ch_entry["revenue_share_pct"]),
                    unit="%",
                ),
                _make_fact(
                    fact_id=f"chan.{ch_name}.average_ticket_net",
                    category="by_channel",
                    label=f"Ticket médio líquido no canal {ch_name}",
                    value=float(ch_entry["average_ticket_net"]),
                    unit="BRL",
                ),
            ]
        )

    # 6. Desempenho de Vendas Concluídas por Categoria (category = "by_category")
    for cat_entry in by_category:
        cat_name = str(cat_entry["category"])
        facts.extend(
            [
                _make_fact(
                    fact_id=f"cat.{cat_name}.quantity_sold",
                    category="by_category",
                    label=f"Unidades vendidas na categoria {cat_name}",
                    value=int(cat_entry["quantity_sold"]),
                    unit="count",
                ),
                _make_fact(
                    fact_id=f"cat.{cat_name}.gross_revenue",
                    category="by_category",
                    label=f"Receita bruta da categoria {cat_name}",
                    value=float(cat_entry["gross_revenue"]),
                    unit="BRL",
                ),
                _make_fact(
                    fact_id=f"cat.{cat_name}.discount_total",
                    category="by_category",
                    label=f"Descontos da categoria {cat_name}",
                    value=float(cat_entry["discount_total"]),
                    unit="BRL",
                ),
                _make_fact(
                    fact_id=f"cat.{cat_name}.net_revenue",
                    category="by_category",
                    label=f"Receita líquida da categoria {cat_name}",
                    value=float(cat_entry["net_revenue"]),
                    unit="BRL",
                ),
                _make_fact(
                    fact_id=f"cat.{cat_name}.revenue_share_pct",
                    category="by_category",
                    label=f"Participação na receita líquida da categoria {cat_name}",
                    value=float(cat_entry["revenue_share_pct"]),
                    unit="%",
                ),
                _make_fact(
                    fact_id=f"cat.{cat_name}.average_prep_time_minutes",
                    category="by_category",
                    label=f"Tempo médio de preparo da categoria {cat_name}",
                    value=float(cat_entry["average_prep_time_minutes"]),
                    unit="min",
                ),
            ]
        )

    # 7. Curva ABC (category = "abc_curve")
    class_a_count = sum(1 for item in abc_curve if item.get("abc_class") == "A")
    class_b_count = sum(1 for item in abc_curve if item.get("abc_class") == "B")
    class_c_count = sum(1 for item in abc_curve if item.get("abc_class") == "C")

    facts.extend(
        [
            _make_fact(
                fact_id="abc.class_a.items_count",
                category="abc_curve",
                label="Quantidade de produtos na Classe A",
                value=class_a_count,
                unit="count",
            ),
            _make_fact(
                fact_id="abc.class_b.items_count",
                category="abc_curve",
                label="Quantidade de produtos na Classe B",
                value=class_b_count,
                unit="count",
            ),
            _make_fact(
                fact_id="abc.class_c.items_count",
                category="abc_curve",
                label="Quantidade de produtos na Classe C",
                value=class_c_count,
                unit="count",
            ),
        ]
    )

    for rank_idx, abc_item in enumerate(abc_curve, start=1):
        item_name = str(abc_item["item_name"])
        facts.extend(
            [
                _make_fact(
                    fact_id=f"abc.rank{rank_idx}.revenue",
                    category="abc_curve",
                    label=f"Receita bruta ABC #{rank_idx} ({item_name})",
                    value=float(abc_item["revenue"]),
                    unit="BRL",
                ),
                _make_fact(
                    fact_id=f"abc.rank{rank_idx}.revenue_share_pct",
                    category="abc_curve",
                    label=f"Participação na receita bruta ABC #{rank_idx} ({item_name})",
                    value=float(abc_item["revenue_share_pct"]),
                    unit="%",
                ),
                _make_fact(
                    fact_id=f"abc.rank{rank_idx}.cumulative_share_pct",
                    category="abc_curve",
                    label=f"Participação acumulada ABC #{rank_idx} ({item_name})",
                    value=float(abc_item["cumulative_share_pct"]),
                    unit="%",
                ),
                _make_fact(
                    fact_id=f"abc.rank{rank_idx}.quantity_sold",
                    category="abc_curve",
                    label=f"Unidades vendidas ABC #{rank_idx} ({item_name})",
                    value=int(abc_item["quantity_sold"]),
                    unit="count",
                ),
            ]
        )

    return facts


def build_fallback_recommendations(
    metrics: Mapping[str, Any] | Sequence[Mapping[str, Any]],
    facts: Sequence[Mapping[str, Any]] | Mapping[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """
    Gera deterministicamente exatamente 3 recomendações práticas ranqueadas (ranks 1, 2, 3)
    a partir das métricas e da ficha de fatos, sem uso de LLM (RN-09, RN-10).

    Garante que todo número citado nos textos venha exclusivamente dos fatos de `build_fact_sheet`.
    """
    resolved_metrics: Mapping[str, Any]
    resolved_facts: list[dict[str, Any]]

    if isinstance(metrics, (list, tuple)):
        resolved_facts = [dict(f) for f in metrics]
        if isinstance(facts, Mapping):
            resolved_metrics = facts
        else:
            resolved_metrics = {}
    else:
        resolved_metrics = metrics
        if facts is not None and isinstance(facts, (list, tuple)):
            resolved_facts = [dict(f) for f in facts]
        else:
            resolved_facts = build_fact_sheet(metrics)

    facts_by_id: dict[str, Mapping[str, Any]] = {
        str(f["fact_id"]): f for f in resolved_facts
    }

    bottlenecks: Mapping[str, Any] = resolved_metrics.get("bottlenecks", {})
    by_category: Sequence[Mapping[str, Any]] = resolved_metrics.get("by_category", [])
    abc_curve: Sequence[Mapping[str, Any]] = resolved_metrics.get("abc_curve", [])
    canceled_by_channel: Sequence[Mapping[str, Any]] = bottlenecks.get(
        "canceled_by_channel", []
    )
    delayed_by_category: Sequence[Mapping[str, Any]] = bottlenecks.get(
        "delayed_by_category", []
    )

    recommendations: list[dict[str, Any]] = []

    # -------------------------------------------------------------------------
    # Recomendação Rank 1: Cancelamentos por Canal (ou Proteção de Receita)
    # -------------------------------------------------------------------------
    top_canc_channel = canceled_by_channel[0] if canceled_by_channel else None
    if top_canc_channel is not None and int(top_canc_channel.get("canceled_orders_count", 0)) > 0:
        ch_name = str(top_canc_channel["channel"])
        f_rate = facts_by_id[f"chan.{ch_name}.cancellation_rate_pct"]
        f_loss = facts_by_id[f"chan.{ch_name}.canceled_revenue_loss"]
        f_thr = facts_by_id["thr.cancellation_rate_pct"]
        f_canc_cnt = facts_by_id[f"chan.{ch_name}.canceled_orders_count"]
        f_tot_loss = facts_by_id["fin.canceled_revenue_loss"]

        rate_val = float(f_rate["value"])
        thr_val = float(f_thr["value"])
        loss_val = float(f_loss["value"])
        tot_loss_val = float(f_tot_loss["value"])
        canc_cnt_val = int(f_canc_cnt["value"])

        threshold_note = (
            f"acima do limite tolerado de {thr_val}%"
            if rate_val > thr_val
            else f"frente ao limite tolerado de {thr_val}%"
        )

        recommendations.append(
            {
                "rank": 1,
                "title": f"Conter cancelamentos críticos no canal {ch_name}",
                "theme": "cancelamento",
                "diagnosis": (
                    f"O canal {ch_name} apresenta taxa de cancelamento de {rate_val}% "
                    f"({threshold_note}), gerando perda de R$ {loss_val:.2f} "
                    f"em {canc_cnt_val} pedidos cancelados."
                ),
                "action": (
                    f"Revisar o SLA de confirmação e expedição dos pedidos de {ch_name} "
                    "e alinhar disponibilidade de itens líderes antes do pico noturno."
                ),
                "expected_impact": (
                    f"Reduzir a perda por cancelamentos no {ch_name}, hoje em R$ {loss_val:.2f} "
                    f"de um total de R$ {tot_loss_val:.2f} perdidos no lote."
                ),
                "evidence": [
                    _to_evidence(f_rate),
                    _to_evidence(f_loss),
                    _to_evidence(f_thr),
                ],
            }
        )
    else:
        f_gross = facts_by_id["fin.gross_revenue"]
        f_disc = facts_by_id["fin.discount_total"]
        f_net = facts_by_id["fin.net_revenue"]
        recommendations.append(
            {
                "rank": 1,
                "title": "Preservar margem líquida e governança de descontos promocionais",
                "theme": "receita",
                "diagnosis": (
                    f"O lote registrou faturamento bruto de R$ {float(f_gross['value']):.2f} "
                    f"com R$ {float(f_disc['value']):.2f} em descontos concedidos, "
                    f"resultando em receita líquida de R$ {float(f_net['value']):.2f}."
                ),
                "action": (
                    "Vincular descontos promocionais a metas de valor mínimo por pedido "
                    "para proteger a margem operacional."
                ),
                "expected_impact": (
                    f"Sustentar e expandir o faturamento líquido atual de R$ {float(f_net['value']):.2f}."
                ),
                "evidence": [
                    _to_evidence(f_net),
                    _to_evidence(f_gross),
                    _to_evidence(f_disc),
                ],
            }
        )

    # -------------------------------------------------------------------------
    # Recomendação Rank 2: Gargalos de Tempo de Preparo (Operação)
    # -------------------------------------------------------------------------
    f_del_items = facts_by_id["bot.delayed_items_count"]
    f_del_orders = facts_by_id["bot.delayed_orders_count"]
    f_thr_prep = facts_by_id["thr.prep_time_minutes"]
    f_avg_prep = facts_by_id["bot.average_prep_time_minutes"]
    f_max_prep = facts_by_id["bot.max_prep_time_minutes"]

    if int(f_del_items["value"]) > 0 and len(delayed_by_category) >= 2:
        cat1 = str(delayed_by_category[0]["category"])
        cat2 = str(delayed_by_category[1]["category"])
        f_c1_cnt = facts_by_id[f"bot.delay_cat.{cat1}.delayed_items_count"]
        f_c1_avg = facts_by_id[f"bot.delay_cat.{cat1}.avg_prep_time_minutes"]
        f_c2_cnt = facts_by_id[f"bot.delay_cat.{cat2}.delayed_items_count"]
        f_c2_avg = facts_by_id[f"bot.delay_cat.{cat2}.avg_prep_time_minutes"]

        recommendations.append(
            {
                "rank": 2,
                "title": "Eliminar gargalo de tempo de preparo na chapa e montagem",
                "theme": "operacao",
                "diagnosis": (
                    f"Foram registrados {int(f_del_items['value'])} itens atrasados em "
                    f"{int(f_del_orders['value'])} pedidos concluídos acima do limite de "
                    f"{float(f_thr_prep['value'])} minutos, concentrados em {cat1} "
                    f"({int(f_c1_cnt['value'])} itens com média de {float(f_c1_avg['value'])} min) "
                    f"e {cat2} ({int(f_c2_cnt['value'])} itens com média de {float(f_c2_avg['value'])} min)."
                ),
                "action": (
                    f"Pré-porcionar insumos das categorias {cat1} e {cat2} e balancear a fila da cozinha "
                    f"quando o tempo de preparo superar {float(f_thr_prep['value'])} minutos."
                ),
                "expected_impact": (
                    f"Aproximar as categorias críticas da média global de preparo de "
                    f"{float(f_avg_prep['value'])} minutos e reduzir o pico máximo de "
                    f"{float(f_max_prep['value'])} minutos."
                ),
                "evidence": [
                    _to_evidence(f_c1_avg),
                    _to_evidence(f_c2_avg),
                    _to_evidence(f_thr_prep),
                ],
            }
        )
    elif int(f_del_items["value"]) > 0 and len(delayed_by_category) == 1:
        cat1 = str(delayed_by_category[0]["category"])
        f_c1_cnt = facts_by_id[f"bot.delay_cat.{cat1}.delayed_items_count"]
        f_c1_avg = facts_by_id[f"bot.delay_cat.{cat1}.avg_prep_time_minutes"]

        recommendations.append(
            {
                "rank": 2,
                "title": f"Eliminar gargalo de tempo de preparo na categoria {cat1}",
                "theme": "operacao",
                "diagnosis": (
                    f"Foram registrados {int(f_del_items['value'])} itens atrasados em "
                    f"{int(f_del_orders['value'])} pedidos concluídos acima do limite de "
                    f"{float(f_thr_prep['value'])} minutos, com {int(f_c1_cnt['value'])} itens "
                    f"e média de {float(f_c1_avg['value'])} min em {cat1}."
                ),
                "action": (
                    f"Pré-porcionar insumos da categoria {cat1} e redistribuir a fila quando "
                    f"o preparo superar {float(f_thr_prep['value'])} minutos."
                ),
                "expected_impact": (
                    f"Convergir o preparo para a média global de {float(f_avg_prep['value'])} minutos "
                    f"e reduzir o pico máximo de {float(f_max_prep['value'])} minutos."
                ),
                "evidence": [
                    _to_evidence(f_c1_avg),
                    _to_evidence(f_del_items),
                    _to_evidence(f_thr_prep),
                ],
            }
        )
    else:
        recommendations.append(
            {
                "rank": 2,
                "title": "Manter estabilidade do tempo de preparo na operação de cozinha",
                "theme": "operacao",
                "diagnosis": (
                    f"A operação registrou {int(f_del_items['value'])} itens acima do limite de "
                    f"{float(f_thr_prep['value'])} minutos, mantendo média global de "
                    f"{float(f_avg_prep['value'])} minutos e pico de {float(f_max_prep['value'])} minutos."
                ),
                "action": (
                    f"Padronizar o pré-preparo antes da abertura de turno para sustentar todas as saídas "
                    f"abaixo do limite de {float(f_thr_prep['value'])} minutos."
                ),
                "expected_impact": (
                    f"Preservar o tempo médio global em {float(f_avg_prep['value'])} minutos "
                    f"e o teto máximo em {float(f_max_prep['value'])} minutos."
                ),
                "evidence": [
                    _to_evidence(f_avg_prep),
                    _to_evidence(f_max_prep),
                    _to_evidence(f_thr_prep),
                ],
            }
        )

    # -------------------------------------------------------------------------
    # Recomendação Rank 3: Mix de Cardápio, Curva ABC e Ticket Médio
    # -------------------------------------------------------------------------
    if by_category and abc_curve:
        lowest_cat = str(by_category[-1]["category"])
        f_cat_share = facts_by_id[f"cat.{lowest_cat}.revenue_share_pct"]
        f_cat_net = facts_by_id[f"cat.{lowest_cat}.net_revenue"]
        f_class_c = facts_by_id["abc.class_c.items_count"]
        f_ticket_net = facts_by_id["fin.average_ticket_net"]
        f_valid_orders = facts_by_id["fin.valid_orders_count"]

        recommendations.append(
            {
                "rank": 3,
                "title": f"Estimular venda cruzada para elevar a participação de {lowest_cat} e itens Classe C",
                "theme": "mix",
                "diagnosis": (
                    f"A categoria {lowest_cat} representa apenas {float(f_cat_share['value'])}% da receita líquida "
                    f"(R$ {float(f_cat_net['value']):.2f}), enquanto {int(f_class_c['value'])} itens do cardápio "
                    "encontram-se na Classe C da Curva ABC."
                ),
                "action": (
                    f"Oferecer sugestão automática de itens da categoria {lowest_cat} e acompanhamentos "
                    "no checkout dos canais digitais junto aos produtos Classe A."
                ),
                "expected_impact": (
                    f"Elevar o ticket médio líquido atual de R$ {float(f_ticket_net['value']):.2f} "
                    f"aproveitando a tração dos {int(f_valid_orders['value'])} pedidos concluídos."
                ),
                "evidence": [
                    _to_evidence(f_cat_share),
                    _to_evidence(f_cat_net),
                    _to_evidence(f_ticket_net),
                ],
            }
        )
    else:
        f_rows = facts_by_id["fin.total_rows"]
        f_canc = facts_by_id["fin.canceled_orders_count"]
        f_loss = facts_by_id["fin.canceled_revenue_loss"]
        recommendations.append(
            {
                "rank": 3,
                "title": "Restabelecer conversão de pedidos para reativar o giro do cardápio",
                "theme": "mix",
                "diagnosis": (
                    f"O lote possui {int(f_rows['value'])} itens registrados sem pedidos concluídos, "
                    f"acumulando R$ {float(f_loss['value']):.2f} em {int(f_canc['value'])} pedidos cancelados."
                ),
                "action": (
                    "Auditar disponibilidade imediata dos itens principais do cardápio e status dos canais de venda."
                ),
                "expected_impact": (
                    f"Recuperar a conversão sobre os R$ {float(f_loss['value']):.2f} perdidos em cancelamentos."
                ),
                "evidence": [
                    _to_evidence(f_rows),
                    _to_evidence(f_canc),
                    _to_evidence(f_loss),
                ],
            }
        )

    return recommendations
