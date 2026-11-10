"""Templates de prompt e schemas de saída estruturada para o agente de recomendações (RN-07, RN-08)."""

from typing import Any

PROMPT_VERSION = "rec-v1"

RECOMMENDATION_JSON_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "recommendations": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "rank": {"type": "integer"},
                    "title": {"type": "string"},
                    "theme": {
                        "type": "string",
                        "enum": ["delivery", "prep_time", "mix_products"],
                    },
                    "diagnosis": {"type": "string"},
                    "action": {"type": "string"},
                    "expected_impact": {"type": "string"},
                    "evidence": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "fact_id": {"type": "string"},
                                "label": {"type": "string"},
                                "value": {"type": "number"},
                                "unit": {"type": "string"},
                            },
                            "required": ["fact_id", "label", "value", "unit"],
                        },
                    },
                },
                "required": [
                    "rank",
                    "title",
                    "theme",
                    "diagnosis",
                    "action",
                    "expected_impact",
                    "evidence",
                ],
            },
        }
    },
    "required": ["recommendations"],
}


def build_system_prompt() -> str:
    """Retorna as instruções de sistema com persona, diretrizes de negócio e restrições anti-alucinação."""
    return (
        "Você é o Consultor Sênior de Operações e Finanças do FoodPilot AI, especializado em restaurantes e delivery.\n"
        "Sua missão é analisar os dados operacionais calculados e gerar exatamente 3 recomendações práticas, "
        "priorizadas por impacto financeiro e operacional.\n\n"
        "DIRETRIZES FUNDAMENTAIS (INEGOCIÁVEIS):\n"
        "1. GROUNDING TOTAL (RN-07 e RN-08): Todos os números, diagnósticos e impactos devem basear-se ESTRITAMENTE "
        "na Ficha de Fatos fornecida pelo usuário. Você NUNCA deve inventar números, supor estatísticas ou recalcular métricas.\n"
        "2. VINCULAÇÃO DE EVIDÊNCIAS: Cada recomendação deve conter no mínimo 1 evidência formal referenciando um 'fact_id' "
        "válido presente na Ficha de Fatos. Os campos 'value' e 'unit' devem corresponder aos do fato.\n"
        "3. COBERTURA DE TEMAS: Forneça exatamente 3 recomendações com ranks 1, 2 e 3:\n"
        "   - Rank 1: Foco no canal de entrega/delivery ou cancelamentos com maior perda financeira.\n"
        "   - Rank 2: Foco em gargalos de tempo de preparo e atrasos na cozinha.\n"
        "   - Rank 3: Foco no mix de cardápio, Curva ABC e itens da Classe C.\n"
        "4. AÇÃO PRÁTICA: O campo 'action' deve conter passos operacionais claros e aplicáveis na rotina do restaurante.\n"
        "5. SAÍDA RESTRITA: Retorne EXCLUSIVAMENTE o payload JSON conforme o schema estrito exigido, sem textos explicativos fora do JSON."
    )


def build_user_message(
    facts: list[dict[str, Any]],
    corrective_notes: list[str] | None = None,
) -> str:
    """
    Constrói a mensagem do usuário contendo a Ficha de Fatos formatada e eventuais notas corretivas para retry.
    """
    facts_lines = [
        f"- [{f['fact_id']}] ({f['category']}) {f['label']}: {f['formatted']} [valor: {f['value']}, unidade: {f['unit']}]"
        for f in facts
    ]
    facts_text = "\n".join(facts_lines)

    user_msg = (
        "Abaixo está a Ficha de Fatos oficial extraída deterministicamente dos pedidos do restaurante:\n\n"
        "=== FICHA DE FATOS ===\n"
        f"{facts_text}\n"
        "=== FIM DA FICHA DE FATOS ===\n\n"
        "Gere exatamente 3 recomendações fundamentadas (ranks 1, 2 e 3) cobrindo 'delivery', 'prep_time' e 'mix_products'."
    )

    if corrective_notes:
        notes_text = "\n".join(f"- {note}" for note in corrective_notes)
        user_msg += (
            "\n\nATENÇÃO: A sua resposta anterior falhou na auditoria rigorosa de fatos e integridade com as seguintes inconformidades:\n"
            f"{notes_text}\n\n"
            "Corrija rigorosamente esses pontos. Use exclusivamente fact_ids existentes e certifique-se de que qualquer valor citado seja real."
        )

    return user_msg
