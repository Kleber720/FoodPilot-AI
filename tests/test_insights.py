"""Testes unitários para a Ficha de Fatos determinística (RN-07) e Fallback de Recomendações (RN-09, RN-10)."""

from pathlib import Path

from data_pipeline import (
    build_fact_sheet,
    build_fallback_recommendations,
    calculate_metrics,
    validate_and_parse_csv,
)


def test_build_fact_sheet_with_sample_orders(sample_csv_path: Path):
    """Verifica se a Ficha de Fatos atômica é gerada deterministicamente com todos os fatos previstos."""
    raw_bytes = sample_csv_path.read_bytes()
    df = validate_and_parse_csv(raw_bytes)
    metrics = calculate_metrics(df)

    facts = build_fact_sheet(metrics)
    assert isinstance(facts, list)
    assert len(facts) >= 20  # Dezenas de fatos hierárquicos

    facts_by_id = {f["fact_id"]: f for f in facts}

    # 1. Verifica limiares
    assert "thr.prep_time_minutes" in facts_by_id
    assert facts_by_id["thr.prep_time_minutes"]["value"] == 30.0
    assert facts_by_id["thr.prep_time_minutes"]["unit"] == "min"

    assert "thr.cancellation_rate_pct" in facts_by_id
    assert facts_by_id["thr.cancellation_rate_pct"]["value"] == 10.0
    assert facts_by_id["thr.cancellation_rate_pct"]["unit"] == "%"

    # 2. Verifica métricas financeiras consolidadas (gabarito de sample_orders.csv)
    assert facts_by_id["fin.total_rows"]["value"] == 82
    assert facts_by_id["fin.valid_orders_count"]["value"] == 50
    assert facts_by_id["fin.canceled_orders_count"]["value"] == 5
    assert facts_by_id["fin.gross_revenue"]["value"] == 5000.00
    assert facts_by_id["fin.gross_revenue"]["unit"] == "BRL"
    assert facts_by_id["fin.gross_revenue"]["formatted"] == "R$ 5000.00"
    assert facts_by_id["fin.net_revenue"]["value"] == 4750.00
    assert facts_by_id["fin.canceled_revenue_loss"]["value"] == 514.00

    # 3. Verifica gargalos operacionais
    assert facts_by_id["bot.delayed_orders_count"]["value"] == 5
    assert facts_by_id["bot.delayed_items_count"]["value"] == 6
    assert facts_by_id["bot.average_prep_time_minutes"]["value"] == 18.55
    assert facts_by_id["bot.max_prep_time_minutes"]["value"] == 46.00

    # 4. Verifica canais específicos (ex: delivery)
    assert "chan.delivery.cancellation_rate_pct" in facts_by_id
    assert facts_by_id["chan.delivery.cancellation_rate_pct"]["value"] == 20.0
    assert facts_by_id["chan.delivery.canceled_orders_count"]["value"] == 4


def test_build_fallback_recommendations_properties(sample_csv_path: Path):
    """Verifica se o motor de fallback gera exatamente 3 recomendações válidas e ordenadas."""
    raw_bytes = sample_csv_path.read_bytes()
    df = validate_and_parse_csv(raw_bytes)
    metrics = calculate_metrics(df)
    facts = build_fact_sheet(metrics)

    recs = build_fallback_recommendations(facts)

    assert isinstance(recs, list)
    assert len(recs) == 3

    # Ranks devem ser 1, 2, 3
    ranks = [r["rank"] for r in recs]
    assert ranks == [1, 2, 3]

    # Temas devem cobrir cancelamento/receita, operacao, mix
    themes = [r["theme"] for r in recs]
    assert themes in (["receita", "operacao", "mix"], ["cancelamento", "operacao", "mix"])

    facts_ids = {f["fact_id"] for f in facts}

    for rec in recs:
        assert rec["title"]
        assert rec["diagnosis"]
        assert rec["action"]
        assert rec["expected_impact"]
        assert isinstance(rec["evidence"], list)
        assert len(rec["evidence"]) >= 1

        # Todas as evidências devem apontar para fatos reais existentes na ficha
        for ev in rec["evidence"]:
            assert ev["fact_id"] in facts_ids
            assert ev["label"]
            assert ev["unit"] in {"BRL", "%", "min", "count"}
            assert isinstance(ev["value"], (int, float))
