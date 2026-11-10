"""Aplicação FastAPI principal e rotas da API REST v1 do FoodPilot AI."""

from contextlib import asynccontextmanager
from datetime import datetime, timezone
import json
from typing import Any
import uuid

from fastapi import Depends, FastAPI, File, HTTPException, Request, UploadFile, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database import get_db, init_db
from backend.models import OrderItem, RecommendationRun, Upload
from backend.schemas import (
    AiStatusSchema,
    ExecutiveReportResponseSchema,
    HealthResponse,
    RecommendationsResponseSchema,
    UploadListResponseSchema,
    UploadMetricsResponseSchema,
    UploadResponseSchema,
)
from backend.ai import LLMClient, OllamaClient, RecommendationService
from data_pipeline import CSVValidationError, calculate_metrics, validate_and_parse_csv


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Inicializa o schema do banco de dados SQLite na subida da aplicação."""
    init_db()
    yield


app = FastAPI(
    title="FoodPilot AI API",
    description=(
        "API REST local de inteligência operacional e financeira para restaurantes, "
        "com processamento determinístico em pandas e persistência transacional SQLite."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def custom_request_validation_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Garante retorno 400 Bad Request padronizado quando o campo 'file' é inválido em /api/v1/uploads."""
    if request.url.path.rstrip("/") == "/api/v1/uploads" and request.method == "POST":
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "detail": "Nenhum arquivo CSV foi enviado no campo 'file'.",
                "errors": [],
            },
        )
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )


@app.get(
    "/api/v1/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    tags=["Health"],
)
def health_check() -> HealthResponse:
    """Verifica a disponibilidade do servidor FastAPI local."""
    return HealthResponse(status="ok")


@app.post(
    "/api/v1/uploads",
    response_model=UploadResponseSchema,
    status_code=status.HTTP_201_CREATED,
    tags=["Uploads"],
)
async def create_upload(
    file: UploadFile | None = File(default=None),
    db: Session = Depends(get_db),
) -> Any:
    """
    Recebe um arquivo CSV de pedidos, valida integralmente seu schema e domínio (RN-01),
    persiste atomicamente no SQLite (RN-02) e retorna o resumo do lote (RN-03, RN-04).
    """
    if file is None or not file.filename or not file.filename.strip():
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "detail": "Nenhum arquivo CSV foi enviado no campo 'file'.",
                "errors": [],
            },
        )

    raw_bytes = await file.read()

    try:
        df = validate_and_parse_csv(raw_bytes)
    except CSVValidationError as exc:
        return JSONResponse(
            status_code=422,
            content=exc.to_dict(),
        )

    metrics_payload = calculate_metrics(df)

    upload_id = str(uuid.uuid4())
    created_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    clean_filename = file.filename.strip()

    try:
        upload_entity = Upload(
            upload_id=upload_id,
            filename=clean_filename,
            created_at=created_at,
            total_rows=int(metrics_payload["total_rows"]),
            valid_orders_count=int(metrics_payload["valid_orders_count"]),
            canceled_orders_count=int(metrics_payload["canceled_orders_count"]),
            summary_metrics_json=json.dumps(
                metrics_payload["summary_metrics"], ensure_ascii=False
            ),
        )
        db.add(upload_entity)

        records = df.to_dict(orient="records")
        order_items = [
            OrderItem(
                upload_id=upload_id,
                order_id=str(rec["order_id"]),
                timestamp=str(rec["timestamp"]),
                item_name=str(rec["item_name"]),
                category=str(rec["category"]),
                quantity=int(rec["quantity"]),
                unit_price=float(rec["unit_price"]),
                discount=float(rec["discount"]),
                prep_time_minutes=float(rec["prep_time_minutes"]),
                status=str(rec["status"]),
                channel=str(rec["channel"]),
            )
            for rec in records
        ]
        db.add_all(order_items)
        db.commit()
        db.refresh(upload_entity)
    except Exception:
        db.rollback()
        raise

    return UploadResponseSchema(
        upload_id=upload_entity.upload_id,
        filename=upload_entity.filename,
        created_at=upload_entity.created_at,
        total_rows=upload_entity.total_rows,
        valid_orders_count=upload_entity.valid_orders_count,
        canceled_orders_count=upload_entity.canceled_orders_count,
        summary_metrics=upload_entity.summary_metrics,
    )


@app.get(
    "/api/v1/uploads",
    response_model=UploadListResponseSchema,
    status_code=status.HTTP_200_OK,
    tags=["Uploads"],
)
def list_uploads(db: Session = Depends(get_db)) -> UploadListResponseSchema:
    """Lista os lotes de CSV importados, ordenados por `created_at` decrescente."""
    stmt = select(Upload).order_by(Upload.created_at.desc())
    uploads = list(db.scalars(stmt).all())

    items = [
        UploadResponseSchema(
            upload_id=u.upload_id,
            filename=u.filename,
            created_at=u.created_at,
            total_rows=u.total_rows,
            valid_orders_count=u.valid_orders_count,
            canceled_orders_count=u.canceled_orders_count,
            summary_metrics=u.summary_metrics,
        )
        for u in uploads
    ]
    return UploadListResponseSchema(items=items, total=len(items))


@app.get(
    "/api/v1/uploads/{upload_id}/metrics",
    response_model=UploadMetricsResponseSchema,
    status_code=status.HTTP_200_OK,
    tags=["Uploads"],
)
def get_upload_metrics(
    upload_id: str,
    db: Session = Depends(get_db),
) -> UploadMetricsResponseSchema:
    """
    Calcula e retorna o relatório determinístico completo de métricas (financeiro,
    Curva ABC, gargalos, por canal e por categoria) para o `upload_id` informado.
    """
    stmt = select(Upload).where(Upload.upload_id == upload_id)
    upload_entity = db.scalar(stmt)

    if upload_entity is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Upload '{upload_id}' não encontrado.",
        )

    records = [item.to_record() for item in upload_entity.items]
    metrics_payload = calculate_metrics(records)

    return UploadMetricsResponseSchema(
        upload_id=upload_entity.upload_id,
        filename=upload_entity.filename,
        created_at=upload_entity.created_at,
        total_rows=upload_entity.total_rows,
        financials=metrics_payload["financials"],
        abc_curve=metrics_payload["abc_curve"],
        bottlenecks=metrics_payload["bottlenecks"],
        by_channel=metrics_payload["by_channel"],
        by_category=metrics_payload["by_category"],
    )


def get_llm_client() -> LLMClient:
    """Provedor padrão do cliente LLM (OllamaClient). Sobrescrevível em testes via app.dependency_overrides."""
    return OllamaClient()


@app.get(
    "/api/v1/ai/status",
    response_model=AiStatusSchema,
    status_code=status.HTTP_200_OK,
    tags=["AI"],
)
def get_ai_status(
    llm_client: LLMClient = Depends(get_llm_client),
) -> AiStatusSchema:
    """Retorna o status de conectividade do Ollama local e disponibilidade do modelo."""
    info = llm_client.health()
    return AiStatusSchema(
        ollama_reachable=bool(info.get("ollama_reachable", False)),
        base_url=str(info.get("base_url", "")),
        model=str(info.get("model", "")),
        model_available=bool(info.get("model_available", False)),
    )


@app.post(
    "/api/v1/uploads/{upload_id}/recommendations",
    response_model=RecommendationsResponseSchema,
    status_code=status.HTTP_201_CREATED,
    tags=["AI"],
)
def generate_recommendations_endpoint(
    upload_id: str,
    db: Session = Depends(get_db),
    llm_client: LLMClient = Depends(get_llm_client),
) -> RecommendationsResponseSchema:
    """
    Gera 3 recomendações executivas fundamentadas na Ficha de Fatos do lote via IA local (ou fallback),
    persistindo a rodada de execução no banco SQLite (RN-07 a RN-10).
    """
    stmt = select(Upload).where(Upload.upload_id == upload_id)
    upload_entity = db.scalar(stmt)

    if upload_entity is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Upload '{upload_id}' não encontrado.",
        )

    records = [item.to_record() for item in upload_entity.items]
    metrics_payload = calculate_metrics(records)

    service = RecommendationService(llm_client)
    recs, source, model, prompt_version, warnings = service.generate_recommendations(metrics_payload)

    run_id = str(uuid.uuid4())
    generated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    run_entity = RecommendationRun(
        run_id=run_id,
        upload_id=upload_id,
        generated_at=generated_at,
        source=source,
        model=model,
        prompt_version=prompt_version,
        payload_json=json.dumps(recs, ensure_ascii=False),
        warnings_json=json.dumps(warnings, ensure_ascii=False),
    )
    db.add(run_entity)
    db.commit()

    return RecommendationsResponseSchema(
        run_id=run_id,
        upload_id=upload_id,
        generated_at=generated_at,
        source=source,  # type: ignore[arg-type]
        model=model,
        prompt_version=prompt_version,
        recommendations=recs,  # type: ignore[arg-type]
        warnings=warnings,
    )


@app.get(
    "/api/v1/uploads/{upload_id}/recommendations",
    response_model=RecommendationsResponseSchema,
    status_code=status.HTTP_200_OK,
    tags=["AI"],
)
def get_recommendations_endpoint(
    upload_id: str,
    db: Session = Depends(get_db),
    llm_client: LLMClient = Depends(get_llm_client),
) -> RecommendationsResponseSchema:
    """
    Recupera a última execução de recomendações gerada para o lote, ou gera a primeira caso ainda não exista.
    """
    stmt_upload = select(Upload).where(Upload.upload_id == upload_id)
    upload_entity = db.scalar(stmt_upload)

    if upload_entity is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Upload '{upload_id}' não encontrado.",
        )

    stmt_run = (
        select(RecommendationRun)
        .where(RecommendationRun.upload_id == upload_id)
        .order_by(RecommendationRun.generated_at.desc())
    )
    latest_run = db.scalar(stmt_run)

    if latest_run is not None:
        return RecommendationsResponseSchema(
            run_id=latest_run.run_id,
            upload_id=latest_run.upload_id,
            generated_at=latest_run.generated_at,
            source=latest_run.source,  # type: ignore[arg-type]
            model=latest_run.model,
            prompt_version=latest_run.prompt_version,
            recommendations=latest_run.recommendations,  # type: ignore[arg-type]
            warnings=latest_run.warnings,
        )

    return generate_recommendations_endpoint(upload_id=upload_id, db=db, llm_client=llm_client)


def _build_markdown_report(
    upload_id: str,
    filename: str,
    generated_at: str,
    financials: dict[str, Any],
    top_abc_items: list[dict[str, Any]],
    anomalies: list[dict[str, Any]],
    recommendations: list[dict[str, Any]],
    source: str,
) -> str:
    """Gera um relatório executivo formatado em Markdown pronto para compartilhamento ou exportação."""
    gross = float(financials.get("gross_revenue", 0.0))
    net = float(financials.get("net_revenue", 0.0))
    discount = float(financials.get("discount_total", 0.0))
    ticket = float(financials.get("average_ticket_net", 0.0))
    loss = float(financials.get("canceled_revenue_loss", 0.0))
    valid_orders = int(financials.get("valid_orders_count", 0))
    canceled_orders = int(financials.get("canceled_orders_count", 0))

    source_label = (
        "Agente de IA Local (qwen3:4b-instruct)"
        if source in {"llm", "ollama"}
        else "Regras Determinísticas de Contingência (Fallback)"
    )

    lines = [
        f"# Relatório Executivo de Inteligência Operacional — FoodPilot AI",
        f"",
        f"- **Lote Analisado:** `{upload_id}`",
        f"- **Arquivo:** `{filename}`",
        f"- **Data de Emissão:** {generated_at}",
        f"- **Origem da Análise:** {source_label}",
        f"",
        f"---",
        f"",
        f"## 1. Resumo Executivo e Indicadores Financeiros",
        f"",
        f"| Indicador | Valor Oficial | Detalhe |",
        f"| :--- | :--- | :--- |",
        f"| **Faturamento Bruto** | R$ {gross:,.2f} | Vendas totais de pedidos concluídos |",
        f"| **Descontos Concedidos** | R$ {discount:,.2f} | Abatimentos aplicados |",
        f"| **Faturamento Líquido** | R$ {net:,.2f} | Receita efetiva realizada |",
        f"| **Ticket Médio Líquido** | R$ {ticket:,.2f} | Média por pedido concluído |",
        f"| **Pedidos Concluídos** | {valid_orders} | Transações finalizadas |",
        f"| **Pedidos Cancelados** | {canceled_orders} | Transações não convertidas |",
        f"| **Perda por Cancelamento** | R$ {loss:,.2f} | Receita perdida em cancelamentos |",
        f"",
        f"---",
        f"",
        f"## 2. Liderança de Cardápio (Curva ABC — Classe A)",
        f"",
    ]

    if top_abc_items:
        lines.append("| Produto | Categoria | Vendas (Qtd) | Receita (R$) | Participação |")
        lines.append("| :--- | :--- | :--- | :--- | :--- |")
        for item in top_abc_items:
            lines.append(
                f"| **{item['item_name']}** | {item['category']} | {item['quantity_sold']} | R$ {float(item['revenue']):,.2f} | {float(item['revenue_share_pct']):.1f}% |"
            )
    else:
        lines.append("Nenhum item classificado na Classe A para este lote.")

    lines.extend([
        f"",
        f"---",
        f"",
        f"## 3. Alertas Operacionais e Anomalias Detectadas",
        f"",
    ])

    if anomalies:
        for a in anomalies:
            sev_badge = "🔴 CRÍTICO" if a.get("severity") == "critical" else "🟡 ATENÇÃO"
            lines.append(
                f"- **[{sev_badge}]** {a.get('description')} (Medido: `{a.get('metric_value')}` | Limiar: `{a.get('threshold_value')}`)"
            )
    else:
        lines.append("Nenhuma anomalia operacional detectada acima dos limiares tolerados.")

    lines.extend([
        f"",
        f"---",
        f"",
        f"## 4. Recomendações Práticas Fundamentadas em Fatos",
        f"",
    ])

    for r in sorted(recommendations, key=lambda x: x.get("rank", 1)):
        rank = r.get("rank")
        title = r.get("title")
        diagnosis = r.get("diagnosis")
        action = r.get("action")
        impact = r.get("expected_impact")
        lines.append(f"### #{rank} — {title}")
        lines.append(f"- **Diagnóstico:** {diagnosis}")
        lines.append(f"- **Ação Imediata:** {action}")
        lines.append(f"- **Impacto Esperado:** {impact}")
        ev_items = r.get("evidence", [])
        if ev_items:
            ev_str = ", ".join(f"`{e.get('label')}: {e.get('value')} {e.get('unit')}`" for e in ev_items)
            lines.append(f"- **Evidências Fatuais:** {ev_str}")
        lines.append(f"")

    lines.extend([
        f"---",
        f"*Relatório gerado deterministicamente pelo FoodPilot AI. Os cálculos monetários e operacionais foram processados exclusivamente via Python e pandas; a IA interpreta e fundamenta as recomendações exclusivamente sobre a Ficha de Fatos auditada.*",
    ])

    return "\n".join(lines)


@app.get(
    "/api/v1/uploads/{upload_id}/report",
    response_model=ExecutiveReportResponseSchema,
    status_code=status.HTTP_200_OK,
    tags=["Reports"],
)
def get_executive_report(
    upload_id: str,
    db: Session = Depends(get_db),
    llm_client: LLMClient = Depends(get_llm_client),
) -> ExecutiveReportResponseSchema:
    """
    Consolida o relatório executivo completo do restaurante com KPIs, anomalias,
    Curva ABC e recomendações da IA em payload estruturado e formato Markdown.
    """
    stmt_upload = select(Upload).where(Upload.upload_id == upload_id)
    upload_entity = db.scalar(stmt_upload)

    if upload_entity is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Upload '{upload_id}' não encontrado.",
        )

    records = [item.to_record() for item in upload_entity.items]
    metrics_payload = calculate_metrics(records)

    # Obtém as recomendações persistidas ou gera se ainda não existirem
    stmt_run = (
        select(RecommendationRun)
        .where(RecommendationRun.upload_id == upload_id)
        .order_by(RecommendationRun.generated_at.desc())
    )
    latest_run = db.scalar(stmt_run)

    if latest_run is None:
        recs_response = generate_recommendations_endpoint(
            upload_id=upload_id, db=db, llm_client=llm_client
        )
        recommendations = [r.model_dump() for r in recs_response.recommendations]
        rec_source = recs_response.source
    else:
        recommendations = latest_run.recommendations
        rec_source = latest_run.source

    top_abc_items = [
        item for item in metrics_payload["abc_curve"] if item["abc_class"] == "A"
    ]
    anomalies = metrics_payload["bottlenecks"]["anomalies"]
    generated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    report_markdown = _build_markdown_report(
        upload_id=upload_id,
        filename=upload_entity.filename,
        generated_at=generated_at,
        financials=metrics_payload["financials"],
        top_abc_items=top_abc_items,
        anomalies=anomalies,
        recommendations=recommendations,
        source=rec_source,
    )

    return ExecutiveReportResponseSchema(
        upload_id=upload_id,
        filename=upload_entity.filename,
        generated_at=generated_at,
        financials=metrics_payload["financials"],
        top_abc_items=top_abc_items,
        anomalies=anomalies,
        recommendations=recommendations,  # type: ignore[arg-type]
        recommendations_source=rec_source,  # type: ignore[arg-type]
        report_markdown=report_markdown,
    )


