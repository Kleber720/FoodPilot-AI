"""Motor determinístico de cálculo de métricas financeiras, Curva ABC e gargalos (RN-03 a RN-06)."""

from collections.abc import Mapping, Sequence
from typing import Any

import pandas as pd

from data_pipeline.validator import REQUIRED_COLUMNS

PREP_TIME_THRESHOLD_MINUTES: int = 30
CANCELLATION_RATE_THRESHOLD_PCT: float = 10.0


def _ensure_dataframe(
    df_or_records: pd.DataFrame | Sequence[Mapping[str, Any]],
) -> pd.DataFrame:
    """Converte entrada (DataFrame ou sequência de mapeamentos) em um DataFrame normalizado."""
    if isinstance(df_or_records, pd.DataFrame):
        if df_or_records.empty:
            return pd.DataFrame(columns=list(REQUIRED_COLUMNS))
        df = df_or_records.copy()
    else:
        records_list = list(df_or_records)
        if not records_list:
            return pd.DataFrame(columns=list(REQUIRED_COLUMNS))
        df = pd.DataFrame(records_list)

    df["order_id"] = df["order_id"].astype(str).str.strip()
    df["timestamp"] = df["timestamp"].astype(str).str.strip()
    df["item_name"] = df["item_name"].astype(str).str.strip()
    df["category"] = df["category"].astype(str).str.strip()
    df["quantity"] = df["quantity"].astype("int64")
    df["unit_price"] = df["unit_price"].astype("float64")
    df["discount"] = df["discount"].astype("float64")
    df["prep_time_minutes"] = df["prep_time_minutes"].astype("float64")
    df["status"] = df["status"].astype(str).str.strip()
    df["channel"] = df["channel"].astype(str).str.strip()

    return df


def calculate_metrics(
    df_or_records: pd.DataFrame | Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """
    Calcula deterministicamente todas as métricas financeiras, Curva ABC, gargalos e agregações.

    Cumpre integralmente as regras RN-03, RN-04, RN-05, RN-06 e Seção 5 de
    `docs/dominio/pedidos-e-metricas.md` e o formato da Seção 3 de `docs/contrato.md`.
    Retorna exclusivamente tipos nativos Python prontos para serialização JSON.
    """
    df = _ensure_dataframe(df_or_records)
    total_rows = int(len(df))

    if total_rows == 0:
        return {
            "total_rows": 0,
            "valid_orders_count": 0,
            "canceled_orders_count": 0,
            "summary_metrics": {
                "gross_revenue": 0.0,
                "discount_total": 0.0,
                "net_revenue": 0.0,
                "average_ticket_gross": 0.0,
                "average_ticket_net": 0.0,
                "canceled_revenue_loss": 0.0,
                "top_abc_item": None,
            },
            "financials": {
                "gross_revenue": 0.0,
                "discount_total": 0.0,
                "net_revenue": 0.0,
                "valid_orders_count": 0,
                "canceled_orders_count": 0,
                "canceled_revenue_loss": 0.0,
                "average_ticket_gross": 0.0,
                "average_ticket_net": 0.0,
            },
            "abc_curve": [],
            "bottlenecks": {
                "prep_time_threshold_minutes": int(PREP_TIME_THRESHOLD_MINUTES),
                "delayed_orders_count": 0,
                "delayed_items_count": 0,
                "average_prep_time_minutes": 0.0,
                "max_prep_time_minutes": 0.0,
                "delayed_by_category": [],
                "canceled_by_channel": [],
                "canceled_by_item": [],
                "anomalies": [],
            },
            "by_channel": [],
            "by_category": [],
        }

    df["line_gross"] = df["quantity"] * df["unit_price"]

    completed_df = df[df["status"] == "completed"].copy()
    canceled_df = df[df["status"] == "canceled"].copy()

    # RN-04: Contagem de pedidos únicos por order_id
    valid_orders_count = int(completed_df["order_id"].nunique()) if not completed_df.empty else 0
    canceled_orders_count = int(canceled_df["order_id"].nunique()) if not canceled_df.empty else 0

    # RN-03: Indicadores financeiros
    if not completed_df.empty:
        gross_revenue = round(float(completed_df["line_gross"].sum()), 2)
        discount_total = round(float(completed_df["discount"].sum()), 2)
        net_revenue = round(float(gross_revenue - discount_total), 2)
    else:
        gross_revenue = 0.0
        discount_total = 0.0
        net_revenue = 0.0

    if not canceled_df.empty:
        canceled_revenue_loss = round(float(canceled_df["line_gross"].sum()), 2)
    else:
        canceled_revenue_loss = 0.0

    # RN-04: Ticket Médio por pedido concluído único
    if valid_orders_count > 0:
        average_ticket_gross = round(float(gross_revenue / valid_orders_count), 2)
        average_ticket_net = round(float(net_revenue / valid_orders_count), 2)
    else:
        average_ticket_gross = 0.0
        average_ticket_net = 0.0

    # RN-05: Curva ABC (Pareto) de produtos em pedidos concluídos
    abc_curve: list[dict[str, Any]] = []
    top_abc_item: str | None = None

    if not completed_df.empty and gross_revenue > 0.0:
        grouped_abc = (
            completed_df.groupby("item_name", as_index=False)
            .agg(
                category=("category", "first"),
                quantity_sold=("quantity", "sum"),
                raw_revenue=("line_gross", "sum"),
            )
        )
        grouped_abc["revenue"] = grouped_abc["raw_revenue"].apply(lambda v: round(float(v), 2))
        grouped_abc = grouped_abc.sort_values(
            by=["revenue", "item_name"],
            ascending=[False, True],
            kind="mergesort",
        ).reset_index(drop=True)

        cumulative_revenue = 0.0
        total_items_abc = len(grouped_abc)

        for idx, row in grouped_abc.iterrows():
            item_rev = round(float(row["revenue"]), 2)
            cumulative_revenue = round(cumulative_revenue + item_rev, 2)
            rev_share_pct = round(float((item_rev / gross_revenue) * 100.0), 2)

            if int(idx) == total_items_abc - 1:
                cum_share_pct = 100.0
            else:
                cum_share_pct = round(float((cumulative_revenue / gross_revenue) * 100.0), 2)
                if cum_share_pct > 100.0:
                    cum_share_pct = 100.0

            if int(idx) == 0 or cum_share_pct <= 80.0:
                abc_class = "A"
            elif cum_share_pct <= 95.0:
                abc_class = "B"
            else:
                abc_class = "C"

            abc_curve.append(
                {
                    "item_name": str(row["item_name"]),
                    "category": str(row["category"]),
                    "quantity_sold": int(row["quantity_sold"]),
                    "revenue": float(item_rev),
                    "revenue_share_pct": float(rev_share_pct),
                    "cumulative_share_pct": float(cum_share_pct),
                    "abc_class": str(abc_class),
                }
            )

        if abc_curve:
            top_abc_item = str(abc_curve[0]["item_name"])

    # RN-06: Gargalos operacionais e anomalias
    delayed_by_category: list[dict[str, Any]] = []
    if not completed_df.empty:
        average_prep_time_minutes = round(float(completed_df["prep_time_minutes"].mean()), 2)
        max_prep_time_minutes = round(float(completed_df["prep_time_minutes"].max()), 2)

        delayed_df = completed_df[
            completed_df["prep_time_minutes"] > float(PREP_TIME_THRESHOLD_MINUTES)
        ]
        delayed_items_count = int(len(delayed_df))
        delayed_orders_count = int(delayed_df["order_id"].nunique()) if not delayed_df.empty else 0

        if not delayed_df.empty:
            grouped_delayed_cat = (
                delayed_df.groupby("category", as_index=False)
                .agg(
                    delayed_items_count=("prep_time_minutes", "count"),
                    avg_prep_time_minutes=("prep_time_minutes", "mean"),
                )
            )
            grouped_delayed_cat["avg_prep_time_minutes"] = grouped_delayed_cat[
                "avg_prep_time_minutes"
            ].apply(lambda v: round(float(v), 2))
            grouped_delayed_cat = grouped_delayed_cat.sort_values(
                by=["delayed_items_count", "category"],
                ascending=[False, True],
                kind="mergesort",
            ).reset_index(drop=True)

            for _, row in grouped_delayed_cat.iterrows():
                delayed_by_category.append(
                    {
                        "category": str(row["category"]),
                        "delayed_items_count": int(row["delayed_items_count"]),
                        "avg_prep_time_minutes": float(row["avg_prep_time_minutes"]),
                    }
                )
    else:
        average_prep_time_minutes = 0.0
        max_prep_time_minutes = 0.0
        delayed_items_count = 0
        delayed_orders_count = 0

    # Cancelamentos por canal (considerando todos os canais presentes no CSV)
    canceled_by_channel: list[dict[str, Any]] = []
    channels_present = df["channel"].unique()
    for ch in channels_present:
        ch_df = df[df["channel"] == ch]
        ch_canceled_df = ch_df[ch_df["status"] == "canceled"]

        ch_total_orders = int(ch_df["order_id"].nunique())
        ch_canceled_orders = int(ch_canceled_df["order_id"].nunique()) if not ch_canceled_df.empty else 0
        ch_rate_pct = (
            round(float((ch_canceled_orders / ch_total_orders) * 100.0), 2)
            if ch_total_orders > 0
            else 0.0
        )
        ch_loss = (
            round(float(ch_canceled_df["line_gross"].sum()), 2)
            if not ch_canceled_df.empty
            else 0.0
        )
        canceled_by_channel.append(
            {
                "channel": str(ch),
                "canceled_orders_count": int(ch_canceled_orders),
                "total_orders_count": int(ch_total_orders),
                "cancellation_rate_pct": float(ch_rate_pct),
                "canceled_revenue_loss": float(ch_loss),
            }
        )

    canceled_by_channel.sort(
        key=lambda item: (-item["cancellation_rate_pct"], item["channel"])
    )

    # Cancelamentos por item
    canceled_by_item: list[dict[str, Any]] = []
    if not canceled_df.empty:
        grouped_canc_item = (
            canceled_df.groupby("item_name", as_index=False)
            .agg(
                category=("category", "first"),
                canceled_quantity=("quantity", "sum"),
                canceled_revenue_loss=("line_gross", "sum"),
            )
        )
        grouped_canc_item["canceled_revenue_loss"] = grouped_canc_item[
            "canceled_revenue_loss"
        ].apply(lambda v: round(float(v), 2))
        grouped_canc_item = grouped_canc_item.sort_values(
            by=["canceled_revenue_loss", "item_name"],
            ascending=[False, True],
            kind="mergesort",
        ).reset_index(drop=True)

        for _, row in grouped_canc_item.iterrows():
            canceled_by_item.append(
                {
                    "item_name": str(row["item_name"]),
                    "category": str(row["category"]),
                    "canceled_quantity": int(row["canceled_quantity"]),
                    "canceled_revenue_loss": float(row["canceled_revenue_loss"]),
                }
            )

    # Anomalias determinísticas (RN-06)
    anomalies: list[dict[str, Any]] = []
    for cat_entry in delayed_by_category:
        cat_name = str(cat_entry["category"])
        del_count = int(cat_entry["delayed_items_count"])
        avg_prep = float(cat_entry["avg_prep_time_minutes"])
        severity = "critical" if (avg_prep > 45.0 or del_count >= 5) else "warning"
        item_word = "item" if del_count == 1 else "itens"
        verb_word = "ultrapassou" if del_count == 1 else "ultrapassaram"
        anomalies.append(
            {
                "type": "high_prep_time",
                "severity": str(severity),
                "dimension": cat_name,
                "description": (
                    f"{del_count} {item_word} na categoria '{cat_name}' {verb_word} "
                    f"o limite de {PREP_TIME_THRESHOLD_MINUTES} minutos de preparo."
                ),
                "metric_value": float(avg_prep),
                "threshold_value": float(PREP_TIME_THRESHOLD_MINUTES),
            }
        )

    for ch_entry in canceled_by_channel:
        ch_name = str(ch_entry["channel"])
        rate_pct = float(ch_entry["cancellation_rate_pct"])
        if rate_pct > CANCELLATION_RATE_THRESHOLD_PCT:
            severity = "critical" if rate_pct >= 20.0 else "warning"
            anomalies.append(
                {
                    "type": "high_cancellation_rate",
                    "severity": str(severity),
                    "dimension": ch_name,
                    "description": (
                        f"Taxa de cancelamento no canal '{ch_name}' atingiu {rate_pct}%, "
                        f"acima do limite tolerado de {CANCELLATION_RATE_THRESHOLD_PCT}%."
                    ),
                    "metric_value": float(rate_pct),
                    "threshold_value": float(CANCELLATION_RATE_THRESHOLD_PCT),
                }
            )

    # Seção 5: Agregações complementares (by_channel e by_category para status == 'completed')
    by_channel: list[dict[str, Any]] = []
    if not completed_df.empty:
        for ch_name, group in completed_df.groupby("channel", as_index=False):
            ch_valid_orders = int(group["order_id"].nunique())
            ch_qty = int(group["quantity"].sum())
            ch_gross = round(float(group["line_gross"].sum()), 2)
            ch_disc = round(float(group["discount"].sum()), 2)
            ch_net = round(float(ch_gross - ch_disc), 2)
            ch_share = (
                round(float((ch_net / net_revenue) * 100.0), 2)
                if net_revenue > 0.0
                else 0.0
            )
            ch_avg_ticket_net = (
                round(float(ch_net / ch_valid_orders), 2)
                if ch_valid_orders > 0
                else 0.0
            )
            by_channel.append(
                {
                    "channel": str(ch_name),
                    "valid_orders_count": int(ch_valid_orders),
                    "quantity_sold": int(ch_qty),
                    "gross_revenue": float(ch_gross),
                    "discount_total": float(ch_disc),
                    "net_revenue": float(ch_net),
                    "revenue_share_pct": float(ch_share),
                    "average_ticket_net": float(ch_avg_ticket_net),
                }
            )
        by_channel.sort(key=lambda item: (-item["net_revenue"], item["channel"]))

    by_category: list[dict[str, Any]] = []
    if not completed_df.empty:
        for cat_name, group in completed_df.groupby("category", as_index=False):
            cat_qty = int(group["quantity"].sum())
            cat_gross = round(float(group["line_gross"].sum()), 2)
            cat_disc = round(float(group["discount"].sum()), 2)
            cat_net = round(float(cat_gross - cat_disc), 2)
            cat_share = (
                round(float((cat_net / net_revenue) * 100.0), 2)
                if net_revenue > 0.0
                else 0.0
            )
            cat_avg_prep = round(float(group["prep_time_minutes"].mean()), 2)
            by_category.append(
                {
                    "category": str(cat_name),
                    "quantity_sold": int(cat_qty),
                    "gross_revenue": float(cat_gross),
                    "discount_total": float(cat_disc),
                    "net_revenue": float(cat_net),
                    "revenue_share_pct": float(cat_share),
                    "average_prep_time_minutes": float(cat_avg_prep),
                }
            )
        by_category.sort(key=lambda item: (-item["net_revenue"], item["category"]))

    return {
        "total_rows": int(total_rows),
        "valid_orders_count": int(valid_orders_count),
        "canceled_orders_count": int(canceled_orders_count),
        "summary_metrics": {
            "gross_revenue": float(gross_revenue),
            "discount_total": float(discount_total),
            "net_revenue": float(net_revenue),
            "average_ticket_gross": float(average_ticket_gross),
            "average_ticket_net": float(average_ticket_net),
            "canceled_revenue_loss": float(canceled_revenue_loss),
            "top_abc_item": top_abc_item,
        },
        "financials": {
            "gross_revenue": float(gross_revenue),
            "discount_total": float(discount_total),
            "net_revenue": float(net_revenue),
            "valid_orders_count": int(valid_orders_count),
            "canceled_orders_count": int(canceled_orders_count),
            "canceled_revenue_loss": float(canceled_revenue_loss),
            "average_ticket_gross": float(average_ticket_gross),
            "average_ticket_net": float(average_ticket_net),
        },
        "abc_curve": abc_curve,
        "bottlenecks": {
            "prep_time_threshold_minutes": int(PREP_TIME_THRESHOLD_MINUTES),
            "delayed_orders_count": int(delayed_orders_count),
            "delayed_items_count": int(delayed_items_count),
            "average_prep_time_minutes": float(average_prep_time_minutes),
            "max_prep_time_minutes": float(max_prep_time_minutes),
            "delayed_by_category": delayed_by_category,
            "canceled_by_channel": canceled_by_channel,
            "canceled_by_item": canceled_by_item,
            "anomalies": anomalies,
        },
        "by_channel": by_channel,
        "by_category": by_category,
    }
