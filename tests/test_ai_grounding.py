"""Testes de validação de ancoragem factual e auditoria anti-alucinação (RN-07, RN-08)."""

from backend.ai.grounding import (
    extract_numbers_from_text,
    validate_recommendations,
)


def _make_sample_facts():
    return [
        {"fact_id": "fin.gross_revenue", "label": "Faturamento Bruto", "value": 4789.50, "unit": "BRL"},
        {"fact_id": "fin.net_revenue", "label": "Faturamento Líquido", "value": 4549.50, "unit": "BRL"},
        {"fact_id": "channel.delivery.cancellation_rate_pct", "label": "Taxa Cancelamento Delivery", "value": 18.75, "unit": "%"},
        {"fact_id": "bot.delayed_orders_count", "label": "Pedidos Atrasados", "value": 18, "unit": "count"},
        {"fact_id": "thr.prep_time_minutes", "label": "Limite de Tempo", "value": 45.0, "unit": "min"},
    ]


def test_extract_numbers_from_text():
    """Valida a extração de números em formatos pt-BR e internacional com símbolos monetários e percentuais."""
    text = "O faturamento foi de R$ 4.789,50 com taxa de 18,75% e 18 pedidos atrasados em mais de 45 min."
    numbers = extract_numbers_from_text(text)
    assert 4789.50 in numbers
    assert 18.75 in numbers
    assert 18.0 in numbers
    assert 45.0 in numbers


def test_validate_recommendations_valid_payload():
    """Payload perfeitamente ancorado deve passar na validação."""
    facts = _make_sample_facts()
    payload = {
        "recommendations": [
            {
                "rank": 1,
                "title": "Reduzir cancelamentos no delivery",
                "theme": "delivery",
                "diagnosis": "O delivery apresenta taxa de cancelamento de 18,75%.",
                "action": "Ajustar o raio de entrega e tempo de resposta.",
                "expected_impact": "Recuperar parte da receita perdida.",
                "evidence": [
                    {"fact_id": "channel.delivery.cancellation_rate_pct", "label": "Taxa", "value": 18.75, "unit": "%"}
                ],
            },
            {
                "rank": 2,
                "title": "Mitigar atrasos na cozinha",
                "theme": "prep_time",
                "diagnosis": "Tivemos 18 pedidos atrasados acima de 45 min.",
                "action": "Reorganizar o mise en place.",
                "expected_impact": "Reduzir tempo de espera.",
                "evidence": [
                    {"fact_id": "bot.delayed_orders_count", "label": "Atrasos", "value": 18, "unit": "count"}
                ],
            },
            {
                "rank": 3,
                "title": "Otimizar cardápio",
                "theme": "mix_products",
                "diagnosis": "O faturamento líquido atingiu 4549.50.",
                "action": "Revisar precificação.",
                "expected_impact": "Aumentar faturamento bruto acima de 4789.50.",
                "evidence": [
                    {"fact_id": "fin.gross_revenue", "label": "Bruto", "value": 4789.50, "unit": "BRL"}
                ],
            },
        ]
    }

    is_valid, errors, sanitized = validate_recommendations(payload, facts)
    assert is_valid is True
    assert len(errors) == 0
    assert len(sanitized) == 3


def test_validate_recommendations_rejects_hallucinated_fact_id():
    """Rejeita recomendação que invente um fact_id inexistente."""
    facts = _make_sample_facts()
    payload = {
        "recommendations": [
            {
                "rank": 1,
                "title": "Investir em marketing",
                "theme": "delivery",
                "diagnosis": "Precisamos de mais clientes.",
                "action": "Gastar mais no Google Ads.",
                "expected_impact": "Mais pedidos.",
                "evidence": [
                    {"fact_id": "marketing.roi_inexistente", "label": "ROI Fake", "value": 100, "unit": "%"}
                ],
            },
            {
                "rank": 2,
                "title": "Ajustar cozinha",
                "theme": "prep_time",
                "diagnosis": "Atrasos operacionais.",
                "action": "Treinamento.",
                "expected_impact": "Melhoria.",
                "evidence": [{"fact_id": "thr.prep_time_minutes", "label": "Tempo", "value": 45, "unit": "min"}],
            },
            {
                "rank": 3,
                "title": "Revisar mix",
                "theme": "mix_products",
                "diagnosis": "Cardápio.",
                "action": "Cortar itens.",
                "expected_impact": "Margem.",
                "evidence": [{"fact_id": "fin.net_revenue", "label": "Líquido", "value": 4549.50, "unit": "BRL"}],
            },
        ]
    }

    is_valid, errors, _ = validate_recommendations(payload, facts)
    assert is_valid is False
    assert any("marketing.roi_inexistente" in err for err in errors)


def test_validate_recommendations_rejects_hallucinated_number_in_text():
    """Detecta números inventados no diagnóstico/ação que não batem com nenhum fato."""
    facts = _make_sample_facts()
    payload = {
        "recommendations": [
            {
                "rank": 1,
                "title": "Título",
                "theme": "delivery",
                "diagnosis": "Tivemos um prejuízo absurdo de R$ 99.850,00 no delivery.",  # Alucinação!
                "action": "Ação",
                "expected_impact": "Impacto",
                "evidence": [{"fact_id": "fin.gross_revenue", "label": "Bruto", "value": 4789.50, "unit": "BRL"}],
            },
            {
                "rank": 2,
                "title": "Título 2",
                "theme": "prep_time",
                "diagnosis": "Diagnóstico 2",
                "action": "Ação 2",
                "expected_impact": "Impacto 2",
                "evidence": [{"fact_id": "thr.prep_time_minutes", "label": "Tempo", "value": 45, "unit": "min"}],
            },
            {
                "rank": 3,
                "title": "Título 3",
                "theme": "mix_products",
                "diagnosis": "Diagnóstico 3",
                "action": "Ação 3",
                "expected_impact": "Impacto 3",
                "evidence": [{"fact_id": "fin.net_revenue", "label": "Líquido", "value": 4549.50, "unit": "BRL"}],
            },
        ]
    }

    is_valid, errors, _ = validate_recommendations(payload, facts)
    assert is_valid is False
    assert any("99850" in err for err in errors)


def test_validate_recommendations_sanitizes_evidence():
    """Evidências no payload têm seus campos value, label e unit sobrescritos com os oficiais da ficha de fatos."""
    facts = [
        {"fact_id": "fin.gross_revenue", "label": "Faturamento Bruto Oficial", "value": 4789.50, "unit": "BRL"},
        {"fact_id": "thr.prep_time_minutes", "label": "Limite Oficial", "value": 45.0, "unit": "min"},
        {"fact_id": "fin.net_revenue", "label": "Líquido Oficial", "value": 4549.50, "unit": "BRL"},
    ]
    payload = {
        "recommendations": [
            {
                "rank": 1,
                "title": "T1",
                "theme": "delivery",
                "diagnosis": "D1",
                "action": "A1",
                "expected_impact": "E1",
                "evidence": [
                    # O LLM enviou um valor ligeiramente diferente ou label alterado:
                    {"fact_id": "fin.gross_revenue", "label": "Outro Label", "value": 4789.0, "unit": "reais"}
                ],
            },
            {
                "rank": 2,
                "title": "T2",
                "theme": "prep_time",
                "diagnosis": "D2",
                "action": "A2",
                "expected_impact": "E2",
                "evidence": [{"fact_id": "thr.prep_time_minutes", "label": "L", "value": 45, "unit": "m"}],
            },
            {
                "rank": 3,
                "title": "T3",
                "theme": "mix_products",
                "diagnosis": "D3",
                "action": "A3",
                "expected_impact": "E3",
                "evidence": [{"fact_id": "fin.net_revenue", "label": "L2", "value": 4549.5, "unit": "R$"}],
            },
        ]
    }

    is_valid, errors, sanitized = validate_recommendations(payload, facts)
    assert is_valid is True
    # Sanitização deve ter forçado os valores oficiais
    ev0 = sanitized[0]["evidence"][0]
    assert ev0["fact_id"] == "fin.gross_revenue"
    assert ev0["label"] == "Faturamento Bruto Oficial"
    assert ev0["value"] == 4789.50
    assert ev0["unit"] == "BRL"
