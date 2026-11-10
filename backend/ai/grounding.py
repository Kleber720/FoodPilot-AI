"""Módulo de ancoragem factual (grounding) e auditoria anti-alucinação de recomendações (RN-07, RN-08)."""

from collections.abc import Mapping, Sequence
import math
import re
from typing import Any

# Regex para captura de números em textos no padrão pt-BR ou internacional (inteiros, decimais e percentuais)
_NUMBER_PATTERN = re.compile(
    r"(?<![a-zA-Z0-9_])(?:R\$\s*)?(\d{1,3}(?:\.\d{3})*,\d+|\d+(?:[.,]\d+)?)(?:\s*%)?(?![a-zA-Z0-9_])"
)

# Números neutros/operacionais permitidos em ações de texto (ex: dias da semana, metas redondas de minutos, ranks)
_ALLOWED_COMMON_NUMBERS = {
    1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 10.0, 15.0, 20.0, 30.0, 45.0, 60.0
}


def parse_extracted_number(raw: str) -> float | None:
    """Converte uma string numérica extraída do texto para float float nativo."""
    clean = raw.strip().replace("R$", "").replace("%", "").strip()
    if not clean:
        return None
    # Converte padrão pt-BR (1.234,56 -> 1234.56 ou 18,5 -> 18.5)
    if "," in clean:
        clean = clean.replace(".", "").replace(",", ".")
    try:
        val = float(clean)
        return val if math.isfinite(val) else None
    except ValueError:
        return None


def extract_numbers_from_text(text: str) -> list[float]:
    """Extrai todos os números reais contidos no texto."""
    if not text:
        return []
    matches = _NUMBER_PATTERN.findall(text)
    numbers: list[float] = []
    for match in matches:
        parsed = parse_extracted_number(match)
        if parsed is not None:
            numbers.append(parsed)
    return numbers


def _matches_any_fact(
    number: float,
    fact_values: Sequence[float],
    tolerance: float = 0.05,
) -> bool:
    """Verifica se um número extraído coincide com algum fato conhecido ou número operacional comum."""
    if any(math.isclose(number, allowed, abs_tol=0.01) for allowed in _ALLOWED_COMMON_NUMBERS):
        return True
    return any(math.isclose(number, f_val, abs_tol=tolerance) for f_val in fact_values)


def validate_recommendations(
    payload: Mapping[str, Any],
    facts: list[dict[str, Any]],
) -> tuple[bool, list[str], list[dict[str, Any]]]:
    """
    Audita e higieniza as recomendações produzidas pelo LLM contra a Ficha de Fatos (RN-07 e RN-08).

    Retorna:
        (is_valid: bool, errors: list[str], sanitized_recommendations: list[dict[str, Any]])
    """
    errors: list[str] = []
    sanitized: list[dict[str, Any]] = []

    if not isinstance(payload, Mapping):
        return False, ["O payload de recomendações não é um objeto JSON válido."], []

    raw_recs = payload.get("recommendations")
    if not isinstance(raw_recs, list):
        return False, ["O campo 'recommendations' deve ser uma lista."], []

    if len(raw_recs) != 3:
        errors.append(f"Devem ser fornecidas exatamente 3 recomendações (recebidas {len(raw_recs)}).")

    # Mapeamento oficial dos fatos
    facts_by_id = {str(f["fact_id"]): f for f in facts if "fact_id" in f}
    known_fact_values: list[float] = []
    for f in facts:
        val = f.get("value")
        if isinstance(val, (int, float)) and math.isfinite(val):
            known_fact_values.append(float(val))

    seen_ranks: set[int] = set()
    valid_themes = {
        "delivery",
        "prep_time",
        "mix_products",
        "cancelamento",
        "operacao",
        "mix",
        "receita",
    }

    for idx, raw_rec in enumerate(raw_recs, start=1):
        if not isinstance(raw_rec, Mapping):
            errors.append(f"Recomendação #{idx} não é um objeto JSON válido.")
            continue

        rank = raw_rec.get("rank")
        if not isinstance(rank, int):
            errors.append(f"Recomendação #{idx} deve ter um 'rank' inteiro.")
        else:
            if rank in seen_ranks:
                errors.append(f"Rank duplicado: {rank}.")
            seen_ranks.add(rank)

        title = str(raw_rec.get("title", "")).strip()
        if not title:
            errors.append(f"Recomendação #{idx} tem 'title' vazio.")

        theme = str(raw_rec.get("theme", "")).strip()
        if theme not in valid_themes:
            errors.append(
                f"Recomendação #{idx} possui theme '{theme}' inválido. Válidos: {sorted(valid_themes)}."
            )

        diagnosis = str(raw_rec.get("diagnosis", "")).strip()
        if not diagnosis:
            errors.append(f"Recomendação #{idx} tem 'diagnosis' vazio.")

        action = str(raw_rec.get("action", "")).strip()
        if not action:
            errors.append(f"Recomendação #{idx} tem 'action' vazio.")

        expected_impact = str(raw_rec.get("expected_impact", "")).strip()
        if not expected_impact:
            errors.append(f"Recomendação #{idx} tem 'expected_impact' vazio.")

        # Auditoria de evidências
        raw_evidence = raw_rec.get("evidence")
        if not isinstance(raw_evidence, list) or len(raw_evidence) == 0:
            errors.append(f"Recomendação #{idx} deve conter ao menos uma evidência formal em 'evidence'.")
            sanitized_evidence: list[dict[str, Any]] = []
        else:
            sanitized_evidence = []
            for ev_idx, ev in enumerate(raw_evidence, start=1):
                if not isinstance(ev, Mapping):
                    errors.append(f"Recomendação #{idx}, evidência #{ev_idx} inválida.")
                    continue
                fact_id = str(ev.get("fact_id", "")).strip()
                if fact_id not in facts_by_id:
                    errors.append(
                        f"Recomendação #{idx} referencia fact_id '{fact_id}' inexistente na Ficha de Fatos."
                    )
                    continue

                official_fact = facts_by_id[fact_id]
                # Sobrescreve deterministicamente campos vitais com os dados oficiais do fato (RN-07)
                sanitized_evidence.append(
                    {
                        "fact_id": official_fact["fact_id"],
                        "label": official_fact["label"],
                        "value": official_fact["value"],
                        "unit": official_fact["unit"],
                    }
                )

        # Auditoria de números inventados no texto livre (RN-07 / RN-08)
        combined_text = f"{diagnosis} {action} {expected_impact}"
        extracted_numbers = extract_numbers_from_text(combined_text)
        for num in extracted_numbers:
            if not _matches_any_fact(num, known_fact_values):
                errors.append(
                    f"Recomendação #{idx} cita número não ancorado na Ficha de Fatos: {num}."
                )

        sanitized.append(
            {
                "rank": rank if isinstance(rank, int) else idx,
                "title": title,
                "theme": theme if theme in valid_themes else "delivery",
                "diagnosis": diagnosis,
                "action": action,
                "expected_impact": expected_impact,
                "evidence": sanitized_evidence,
            }
        )

    # Verifica se os ranks formam o conjunto {1, 2, 3}
    if seen_ranks != {1, 2, 3} and len(raw_recs) == 3:
        errors.append(f"Os ranks devem cobrir exatamente [1, 2, 3]. Encontrados: {sorted(seen_ranks)}.")

    sanitized.sort(key=lambda r: r["rank"])
    is_valid = len(errors) == 0
    return is_valid, errors, sanitized
